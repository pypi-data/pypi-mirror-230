use pyo3::exceptions::PyAttributeError;
use pyo3::exceptions::PyKeyError;
use pyo3::exceptions::PyValueError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyFrame;
use pyo3::types::PyTuple;
use pyo3::types::PyType;
use std::env::current_dir;
use std::path::Path;
use std::time::SystemTime;

pub fn timestamp() -> f64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .expect("System time is before unix epoch")
        .as_secs_f64()
}

fn filename_with_lineno(frame: &PyFrame, py: Python) -> Result<(String, usize), PyErr> {
    let f_code = frame.getattr(intern!(py, "f_code"))?;
    let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
    let filename = co_filename.extract::<String>()?;
    let lineno = frame.getattr(intern!(py, "f_lineno"))?;
    let lineno = lineno.extract()?;
    Ok((filename, lineno))
}

fn format_frame_path(filename: &str, lineno: usize) -> String {
    let path = match Path::new(filename).canonicalize() {
        Ok(path) => path,
        Err(_) => return format!("{}:{}", filename, lineno),
    };
    let dir = current_dir()
        .expect("Current directory is invalid")
        .canonicalize()
        .expect("Current directory cannot be canonicalized");
    let relative_path = match path.strip_prefix(&dir) {
        Ok(relative_path) => relative_path,
        Err(_) => &path,
    };
    format!("{}:{}", relative_path.display(), lineno)
}

pub fn frame_path(frame: &PyFrame, py: Python) -> Result<String, PyErr> {
    let (filename, lineno) = filename_with_lineno(frame, py)?;
    Ok(format_frame_path(&filename, lineno))
}

pub fn get_qualname(frame: &PyFrame, py: Python) -> Result<Option<String>, PyErr> {
    let f_code = frame.getattr(intern!(py, "f_code"))?;
    match f_code.getattr(intern!(py, "co_qualname")) {
        Ok(qualname) => {
            let globals = frame.getattr(intern!(py, "f_globals"))?;
            let module = globals.get_item("__name__")?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyAttributeError>(py) => {}
        Err(err) => return Err(err),
    }

    let co_name = f_code.getattr(intern!(py, "co_name"))?;
    let name = co_name.extract::<String>()?;
    if name.as_str() == "<module>" {
        let globals = frame.getattr(intern!(py, "f_globals"))?;
        let module = globals.get_item("__name__")?;
        return Ok(Some(format!("{}.<module>", module)));
    }

    match _get_qualname_inner(frame, py, co_name) {
        Ok(qualname) => Ok(qualname),
        Err(_) => Ok(None),
    }
}

fn _get_qualname_inner(
    frame: &PyFrame,
    py: Python,
    co_name: &PyAny,
) -> Result<Option<String>, PyErr> {
    let outer_frame = frame.getattr(intern!(py, "f_back"))?;
    if outer_frame.is_none() {
        return Ok(None);
    }

    let outer_frame_locals = outer_frame.getattr(intern!(py, "f_locals"))?;
    match outer_frame_locals.get_item(co_name) {
        Ok(function) => {
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    }

    let locals = frame.getattr(intern!(py, "f_locals"))?;
    let inspect = PyModule::import(py, "inspect")?;
    let getattr_static = inspect.getattr(intern!(py, "getattr_static"))?;
    match locals.get_item("self") {
        Ok(locals_self) => {
            let function = getattr_static.call1((locals_self, co_name))?;
            let builtins = py.import("builtins")?;
            let property = builtins.getattr(intern!(py, "property"))?;
            let property = property.extract()?;
            let function = match function.is_instance(property)? {
                true => function.getattr(intern!(py, "fget"))?,
                false => function,
            };
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    };

    match locals.get_item("cls") {
        Ok(cls) if cls.is_instance_of::<PyType>()? => {
            let function = getattr_static.call1((cls, co_name))?;
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Ok(_) => {}
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    }
    let globals = frame.getattr(intern!(py, "f_globals"))?;
    match locals.get_item("__qualname__") {
        Ok(qualname) => {
            let module = globals.get_item("__name__")?;
            Ok(Some(format!("{}.{}", module, qualname)))
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {
            let function = globals.get_item(co_name)?;
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            Ok(Some(format!("{}.{}", module, qualname)))
        }
        Err(_) => Ok(None),
    }
}

fn py_dump_json(py: Python, data: &PyAny) -> Result<String, PyErr> {
    let serialize = PyModule::import(py, "kolo.serialize")?;
    let args = PyTuple::new(py, [&data]);
    let json_data = serialize.call_method1("dump_json", args)?;
    json_data.extract::<String>()
}

fn load_py_json(data: &str) -> Result<serde_json::Value, PyErr> {
    let json_data = match serde_json::from_str(data) {
        Ok(value) => value,
        Err(err) => {
            eprintln!("Could not load json: {}", data);
            let message = format!("{} {}", err, data);
            let pyerr = PyErr::new::<PyValueError, _>(message);
            return Err(pyerr);
        }
    };
    Ok(json_data)
}

pub fn dump_json(py: Python, data: &PyAny) -> Result<serde_json::Value, PyErr> {
    let json_data = py_dump_json(py, data)?;
    load_py_json(&json_data)
}

pub fn current_thread(py: Python) -> Result<(&str, usize), PyErr> {
    let threading = PyModule::import(py, "threading")?;
    let thread = threading.call_method0("current_thread")?;
    let thread_name = thread.getattr(intern!(py, "name"))?;
    let thread_name = thread_name.extract()?;
    let native_id = thread.getattr(intern!(py, "native_id"))?;
    let native_id = native_id.extract()?;
    Ok((thread_name, native_id))
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::types::PyDict;
    use serde_json::json;

    #[test]
    fn test_dump_json() {
        pyo3::prepare_freethreaded_python();

        let json_data = Python::with_gil(|py| {
            let data = PyDict::new(py);
            dump_json(py, data).unwrap()
        });

        assert_eq!(json_data, json!({}));
    }

    #[test]
    fn test_load_py_json_invalid_json() {
        pyo3::prepare_freethreaded_python();

        let pyerr = load_py_json(r#"{"foo": NaN}"#).unwrap_err();

        Python::with_gil(|py| {
            assert!(pyerr.get_type(py).is(PyType::new::<PyValueError>(py)));
            assert_eq!(
                pyerr.value(py).to_string(),
                "expected value at line 1 column 9 {\"foo\": NaN}"
            );
        });
    }

    #[test]
    fn test_format_frame_path_invalid_path() {
        let frame_path = format_frame_path("<module>", 23);

        assert_eq!(frame_path, "<module>:23");
    }
}
