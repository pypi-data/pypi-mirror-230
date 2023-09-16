use bstr::Finder;
use pyo3::ffi;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyFrame;
use pyo3::types::PyList;
use pyo3::types::PyTuple;
use pyo3::AsPyPointer;
use serde_json::json;
use std::cell::RefCell;
use std::collections::HashMap;
use std::os::raw::c_int;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use thread_local::ThreadLocal;
use ulid::Ulid;

use super::filters;
use super::utils;

#[pyclass(module = "kolo._kolo", frozen)]
pub struct KoloProfiler {
    db_path: String,
    one_trace_per_test: bool,
    trace_id: Mutex<String>,
    frames_of_interest: Mutex<Vec<serde_json::Value>>,
    frames: Mutex<HashMap<usize, Vec<serde_json::Value>>>,
    config: PyObject,
    include_frames: Vec<Finder<'static>>,
    ignore_frames: Vec<Finder<'static>>,
    default_include_frames: Vec<PyObject>,
    call_frames: ThreadLocal<RefCell<Vec<(PyObject, String)>>>,
    timestamp: f64,
    _frame_ids: ThreadLocal<RefCell<HashMap<usize, String>>>,
    start_test_index: AtomicUsize,
    start_test_indices: Mutex<HashMap<usize, usize>>,
    main_thread_id: usize,
    source: String,
}

#[pymethods]
impl KoloProfiler {
    fn save_request_in_db(&self) -> Result<(), PyErr> {
        Python::with_gil(|py| self.save_in_db(py))
    }

    fn register_threading_profiler(
        slf: PyRef<'_, Self>,
        _frame: PyObject,
        _event: PyObject,
        _arg: PyObject,
    ) -> Result<(), PyErr> {
        // Safety:
        //
        // PyEval_SetProfile takes two arguments:
        //  * trace_func: Option<Py_tracefunc>
        //  * arg1:       *mut PyObject
        //
        // `profile_callback` matches the signature of a `Py_tracefunc`, so we only
        // need to wrap it in `Some`.
        // `slf.into_ptr()` is a pointer to our Rust profiler instance as a Python
        // object.
        //
        // We must also hold the GIL, which we do because we're called from python.
        //
        // https://docs.rs/pyo3-ffi/latest/pyo3_ffi/fn.PyEval_SetProfile.html
        // https://docs.python.org/3/c-api/init.html#c.PyEval_SetProfile
        unsafe {
            ffi::PyEval_SetProfile(Some(profile_callback), slf.into_ptr());
        }
        Ok(())
    }
}

impl KoloProfiler {
    pub fn new_from_python(py: Python, py_profiler: &PyAny) -> Result<Self, PyErr> {
        let config = py_profiler.getattr(intern!(py, "config"))?;
        let filters = config.get_item("filters");
        let include_frames = match filters {
            Ok(filters) => match filters.get_item("include_frames") {
                Ok(include_frames) => include_frames
                    .extract::<Vec<&str>>()?
                    .iter()
                    .map(Finder::new)
                    .map(|finder| finder.into_owned())
                    .collect(),
                Err(_) => Vec::new(),
            },
            Err(_) => Vec::new(),
        };
        let ignore_frames = match filters {
            Ok(filters) => match filters.get_item("ignore_frames") {
                Ok(ignore_frames) => ignore_frames
                    .extract::<Vec<&str>>()?
                    .iter()
                    .map(Finder::new)
                    .map(|finder| finder.into_owned())
                    .collect(),
                Err(_) => Vec::new(),
            },
            Err(_) => Vec::new(),
        };
        let threading = PyModule::import(py, "threading")?;
        let main_thread = threading.call_method0(intern!(py, "main_thread"))?;
        let main_thread_id = main_thread.getattr(intern!(py, "native_id"))?;
        let main_thread_id = main_thread_id.extract()?;
        Ok(Self {
            db_path: py_profiler
                .getattr(intern!(py, "db_path"))?
                .str()?
                .extract()?,
            one_trace_per_test: py_profiler
                .getattr(intern!(py, "one_trace_per_test"))?
                .extract()?,
            trace_id: py_profiler
                .getattr(intern!(py, "trace_id"))?
                .extract::<String>()?
                .into(),
            source: py_profiler
                .getattr(intern!(py, "source"))?
                .extract::<String>()?,
            frames: HashMap::new().into(),
            frames_of_interest: Vec::new().into(),
            config: config.into(),
            include_frames,
            ignore_frames,
            default_include_frames: py_profiler
                .getattr(intern!(py, "_default_include_frames"))?
                .extract()?,
            call_frames: ThreadLocal::new(),
            timestamp: utils::timestamp(),
            _frame_ids: ThreadLocal::new(),
            start_test_index: 0.into(),
            start_test_indices: HashMap::new().into(),
            main_thread_id,
        })
    }

    fn save_in_db(&self, py: Python) -> Result<(), PyErr> {
        let version = PyModule::import(py, "kolo.version")?
            .getattr(intern!(py, "__version__"))?
            .extract::<String>()?;
        let commit_sha = PyModule::import(py, "kolo.git")?
            .getattr(intern!(py, "COMMIT_SHA"))?
            .extract::<Option<String>>()?;
        let argv = PyModule::import(py, "sys")?
            .getattr(intern!(py, "argv"))?
            .extract::<Vec<String>>()?;
        let frames_of_interest = &self.frames_of_interest.lock().unwrap()
            [self.start_test_index.load(Ordering::Acquire)..];
        let frames = self.frames.lock().unwrap();
        let thread_frames: HashMap<_, _> = frames
            .iter()
            .map(|(thread_id, frames)| {
                (
                    thread_id,
                    &frames[*self
                        .start_test_indices
                        .lock()
                        .unwrap()
                        .get(thread_id)
                        .unwrap_or(&0)..],
                )
            })
            .collect();
        let data = json!({
            "command_line_args": argv,
            "current_commit_sha": commit_sha,
            "frames": thread_frames,
            "frames_of_interest": frames_of_interest,
            "main_thread_id": format!("{}", self.main_thread_id),
            "meta": {"version": version, "source": self.source, "use_frame_boundaries": true},
            "timestamp": self.timestamp,
            "trace_id": self.trace_id,
        });
        let config = self.config.as_ref(py);
        let wal_mode = match config.get_item("wal_mode") {
            Ok(wal_mode) => Some(wal_mode),
            Err(_) => None,
        };
        let timeout = match config.get_item("sqlite_busy_timeout") {
            Err(_) => 60,
            Ok(timeout) => timeout.extract()?,
        };
        let db = PyModule::import(py, "kolo.db")?;
        let save = db.getattr(intern!(py, "save_invocation_in_sqlite"))?;
        let trace_id = self.trace_id.lock().unwrap().clone();
        let kwargs = PyDict::new(py);
        kwargs.set_item("wal_mode", wal_mode).unwrap();
        kwargs.set_item("timeout", timeout).unwrap();
        save.call((&self.db_path, &trace_id, data.to_string()), Some(kwargs))?;
        Ok(())
    }

    fn process_frame(
        &self,
        frame: PyObject,
        event: &str,
        arg: PyObject,
        py: Python,
    ) -> Result<(), PyErr> {
        let (thread_name, native_id) = utils::current_thread(py)?;
        let user_code_call_site = match event {
            "call" => match self.call_frames.get_or_default().borrow().last() {
                Some((call_frame, call_frame_id)) => {
                    let pyframe = call_frame.downcast::<PyFrame>(py)?;
                    Some(json!({
                        "call_frame_id": call_frame_id,
                        "line_number": pyframe.getattr(intern!(py, "f_lineno"))?.extract::<i32>()?,
                    }))
                }
                None => None,
            },
            _ => None,
        };
        let pyframe = frame.downcast::<PyFrame>(py)?;
        let arg = arg.downcast::<PyAny>(py)?;
        let f_code = pyframe.getattr(intern!(py, "f_code"))?;
        let co_name = f_code.getattr(intern!(py, "co_name"))?;
        let name = co_name.extract::<String>()?;
        let pyframe_id = pyframe.as_ptr() as usize;
        let path = utils::frame_path(pyframe, py)?;
        let qualname = utils::get_qualname(pyframe, py)?;
        let locals = pyframe.getattr(intern!(py, "f_locals"))?;
        let locals = locals.downcast::<PyDict>().unwrap();
        let locals = match locals.get_item("__builtins__") {
            Some(_) => {
                let locals = locals.copy().unwrap();
                locals.del_item("__builtins__").unwrap();
                locals
            }
            None => locals,
        };
        let json_locals = utils::dump_json(py, locals)?;

        match event {
            "call" => {
                let frame_ulid = Ulid::new();
                let frame_id = format!("frm_{}", frame_ulid.to_string());
                self._frame_ids
                    .get_or_default()
                    .borrow_mut()
                    .insert(pyframe_id, frame_id);
                let frame_id = format!("frm_{}", frame_ulid.to_string());
                self.call_frames
                    .get_or_default()
                    .borrow_mut()
                    .push((frame, frame_id));
            }
            "return" => {
                if let Some(e) = self.call_frames.get() {
                    e.borrow_mut().pop();
                }
            }
            _ => {}
        }

        let frame_data = json!({
            "path": path,
            "co_name": name,
            "qualname": qualname,
            "event": event,
            "frame_id": self._frame_ids.get_or_default().borrow().get(&pyframe_id).cloned(),
            "arg": utils::dump_json(py, arg)?,
            "locals": json_locals,
            "thread": thread_name,
            "thread_native_id": native_id,
            "timestamp": utils::timestamp(),
            "type": "frame",
            "user_code_call_site": user_code_call_site,
        });

        self.push_frame_data(py, frame_data)
    }

    fn push_frame_data(&self, py: Python, json_data: serde_json::Value) -> Result<(), PyErr> {
        let use_threading = match self.config.as_ref(py).get_item("threading") {
            Ok(threading) => threading.extract::<bool>().unwrap_or(false),
            Err(_) => false,
        };
        let (_, native_id) = utils::current_thread(py)?;
        if !use_threading || native_id == self.main_thread_id {
            self.frames_of_interest.lock().unwrap().push(json_data);
        } else {
            self.frames
                .lock()
                .unwrap()
                .entry(native_id)
                .or_default()
                .push(json_data);
        };
        Ok(())
    }

    fn process_include_frames(&self, filename: &str) -> bool {
        self.include_frames
            .iter()
            .any(|finder| finder.find(filename).is_some())
    }

    fn process_ignore_frames(&self, filename: &str) -> bool {
        self.ignore_frames
            .iter()
            .any(|finder| finder.find(filename).is_some())
    }

    fn process_default_ignore_frames(
        &self,
        pyframe: &PyFrame,
        co_filename: &str,
        py: Python,
    ) -> Result<bool, PyErr> {
        if filters::library_filter(co_filename) {
            return Ok(true);
        }

        if filters::frozen_filter(co_filename) {
            return Ok(true);
        }

        if filters::kolo_filter(co_filename) {
            return Ok(true);
        }

        if filters::exec_filter(co_filename) {
            return Ok(true);
        }

        // We don't need a match block here because the
        // return value is already in the right format
        filters::attrs_filter(co_filename, pyframe, py)
    }

    fn process_default_include_frames(
        &self,
        py: Python,
        frame: &PyObject,
        pyframe: &PyFrame,
        event: &str,
        arg: &PyObject,
        name: &str,
        filename: &str,
    ) -> Result<bool, PyErr> {
        let filter = match name {
            "get_response" => {
                if filters::use_django_filter(filename) {
                    self.default_include_frames[0].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "render" => {
                if filters::use_django_template_filter(filename) {
                    self.default_include_frames[1].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "apply_async" => {
                if filters::use_celery_filter(filename) {
                    self.default_include_frames[2].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "execute" => {
                let huey_filter = self.default_include_frames[3].as_ref(py);
                if filters::use_huey_filter(filename, huey_filter, py, pyframe)? {
                    huey_filter
                } else {
                    return Ok(false);
                }
            }
            "send" => {
                if filters::use_requests_filter(filename) {
                    self.default_include_frames[4].as_ref(py)
                } else if filters::use_httpx_filter(filename) {
                    self.default_include_frames[12].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "do_open" => {
                if filters::use_urllib_filter(filename) {
                    self.default_include_frames[5].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "urlopen" => {
                if filters::use_urllib3_filter(filename) {
                    self.default_include_frames[6].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "handle_uncaught_exception" => {
                if filters::use_exception_filter(filename, event) {
                    self.default_include_frames[7].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "_log" => {
                if filters::use_logging_filter(filename, event) {
                    self.default_include_frames[8].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "execute_sql" => {
                let sql_filter = self.default_include_frames[9].as_ref(py);
                if filters::use_sql_filter(filename, sql_filter, py, pyframe)? {
                    sql_filter
                } else {
                    return Ok(false);
                }
            }
            "startTest" => {
                if filters::use_unittest_filter(filename, event) {
                    self.default_include_frames[10].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "stopTest" => {
                if filters::use_unittest_filter(filename, event) {
                    self.default_include_frames[10].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "pytest_runtest_logstart" => {
                if filters::use_pytest_filter(filename, event) {
                    self.default_include_frames[11].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "pytest_runtest_logfinish" => {
                if filters::use_pytest_filter(filename, event) {
                    self.default_include_frames[11].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "setup" => {
                if filters::use_django_setup_filter(filename) {
                    self.default_include_frames[13].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "run_checks" => {
                if filters::use_django_checks_filter(filename) {
                    self.default_include_frames[14].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            "create_test_db" => {
                if filters::use_django_test_db_filter(filename) {
                    self.default_include_frames[15].as_ref(py)
                } else {
                    return Ok(false);
                }
            }
            _ => return Ok(false),
        };

        let py_event = event.to_object(py);
        let call_frames = self.call_frames.get_or_default().borrow().clone();
        let call_frames = PyList::new(py, call_frames);
        let args = PyTuple::new(py, [frame, &py_event, arg, &call_frames.into()]);
        let data = filter.call_method1("process", args)?;
        if data.is_none() {
            return Ok(true);
        }

        let json_data = utils::dump_json(py, data)?;

        let frame_type = json_data["type"].clone();
        if self.one_trace_per_test && frame_type == "start_test" {
            let trace_id = Ulid::new();
            let trace_id = format!("trc_{}", trace_id.to_string());
            let mut self_trace_id = self.trace_id.lock().unwrap();
            *self_trace_id = trace_id;

            self.start_test_index.store(
                self.frames_of_interest.lock().unwrap().len(),
                Ordering::Release,
            );
            let mut start_test_indices = self.start_test_indices.lock().unwrap();
            *start_test_indices = self
                .frames
                .lock()
                .unwrap()
                .iter()
                .map(|(thread_id, frames)| (*thread_id, frames.len()))
                .collect::<HashMap<usize, usize>>();
        }

        self.push_frame_data(py, json_data)?;

        if self.one_trace_per_test && frame_type == "end_test" {
            self.save_in_db(py)?;
        }
        Ok(true)
    }

    fn profile(
        &self,
        frame: PyObject,
        arg: PyObject,
        event: &str,
        py: Python,
    ) -> Result<(), PyErr> {
        let pyframe = frame.as_ref(py);
        let pyframe = pyframe.downcast::<PyFrame>()?;
        let f_code = pyframe.getattr(intern!(py, "f_code"))?;
        let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
        let filename = co_filename.extract::<String>()?;

        if self.process_include_frames(&filename) {
            self.process_frame(frame, event, arg, py)?;
            return Ok(());
        };

        if self.process_ignore_frames(&filename) {
            return Ok(());
        }

        let co_name = f_code.getattr(intern!(py, "co_name"))?;
        let name = co_name.extract::<String>()?;

        if self
            .process_default_include_frames(py, &frame, pyframe, event, &arg, &name, &filename)?
        {
            return Ok(());
        }

        if self.process_default_ignore_frames(pyframe, &filename, py)? {
            return Ok(());
        }

        self.process_frame(frame, event, arg, py)
    }
}

// Safety:
//
// We match the type signature of `Py_tracefunc`.
//
// https://docs.rs/pyo3-ffi/latest/pyo3_ffi/type.Py_tracefunc.html
pub extern "C" fn profile_callback(
    _obj: *mut ffi::PyObject,
    _frame: *mut ffi::PyFrameObject,
    what: c_int,
    _arg: *mut ffi::PyObject,
) -> c_int {
    let event = match what {
        ffi::PyTrace_CALL => "call",
        ffi::PyTrace_RETURN => "return",
        _ => return 0,
    };
    let _frame = _frame as *mut ffi::PyObject;
    Python::with_gil(|py| {
        // Safety:
        //
        // `from_borrowed_ptr_or_err` must be called in an unsafe block.
        //
        // `_obj` is a reference to our `KoloProfiler` wrapped up in a Python object, so
        // we can safely convert it from an `ffi::PyObject` to a `PyObject`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_err
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let obj = match unsafe { PyObject::from_borrowed_ptr_or_err(py, _obj) } {
            Ok(obj) => obj,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };
        let profiler = match obj.extract::<PyRef<KoloProfiler>>(py) {
            Ok(profiler) => profiler,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };

        // Safety:
        //
        // `from_borrowed_ptr_or_err` must be called in an unsafe block.
        //
        // `_frame` is an `ffi::PyFrameObject` which can be converted safely
        // to a `PyObject`. We can later convert it into a `pyo3::types::PyFrame`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_err
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let frame = match unsafe { PyObject::from_borrowed_ptr_or_err(py, _frame) } {
            Ok(frame) => frame,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };

        // Safety:
        //
        // `from_borrowed_ptr_or_opt` must be called in an unsafe block.
        //
        // `_arg` is either a `Py_None` (PyTrace_CALL) or any PyObject (PyTrace_RETURN) or
        // NULL (PyTrace_RETURN). The first two can be unwrapped as a PyObject. `NULL` we
        // convert to a `py.None()`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_opt
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let arg = match unsafe { PyObject::from_borrowed_ptr_or_opt(py, _arg) } {
            Some(arg) => arg,
            // TODO: Perhaps better exception handling here?
            None => py.None(),
        };

        match profiler.profile(frame, arg, event, py) {
            Ok(_) => 0,
            Err(err) => {
                let logging = PyModule::import(py, "logging").unwrap();
                let logger = logging.call_method1("getLogger", ("kolo",)).unwrap();
                let kwargs = PyDict::new(py);
                kwargs.set_item("exc_info", err).unwrap();
                logger
                    .call_method("warning", ("Unexpected exception in Rust:",), Some(kwargs))
                    .unwrap();
                0
            }
        }
    })
}
