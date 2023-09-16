use bstr::Finder;
use once_cell::sync::Lazy;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyFrame;

macro_rules! count {
        // Macro magic to find the length of $path
        // https://youtu.be/q6paRBbLgNw?t=4380
        ($($element:expr),*) => {
            [$(count![@SUBSTR; $element]),*].len()
        };
        (@SUBSTR; $_element:expr) => {()};
    }

macro_rules! finder {
        ($name:ident = $path:expr) => {
            static $name: Lazy<Finder> = Lazy::new(|| Finder::new($path));
        };
        (pub $name:ident = $path:expr) => {
            pub static $name: Lazy<Finder> = Lazy::new(|| Finder::new($path));
        };
        (pub $name:ident = $($path:expr),+ $(,)?) => {
            pub static $name: Lazy<[Finder; count!($($path),*)]> = Lazy::new(|| {
                [
                    $(Finder::new($path),)+
                ]
            });
        };

    }

finder!(CELERY_FINDER = "celery");
finder!(SENTRY_FINDER = "sentry_sdk");
finder!(DJANGO_FINDER = "django");
finder!(FROZEN_FINDER = "<frozen ");
finder!(EXEC_FINDER = "<string>");

#[cfg(target_os = "windows")]
mod windows {
    use bstr::Finder;
    use once_cell::sync::Lazy;
    finder!(pub MIDDLEWARE_FINDER = "\\kolo\\middleware.py");
    finder!(pub DJANGO_CHECKS_FINDER = "django\\core\\checks\\registry.py");
    finder!(pub DJANGO_TEST_DB_FINDER = "django\\db\\backends\\base\\creation.py");
    finder!(pub DJANGO_SETUP_FINDER = "django\\__init__.py");
    finder!(pub TEMPLATE_FINDER = "django\\template\\backends\\django.py");
    finder!(pub HUEY_FINDER = "\\huey\\api.py");
    finder!(pub REQUESTS_FINDER = "requests\\sessions");
    finder!(pub HTTPX_FINDER = "httpx\\_client.py");
    finder!(pub URLLIB_FINDER = "urllib\\request");
    finder!(pub URLLIB3_FINDER = "urllib3\\connectionpool");
    finder!(pub LOGGING_FINDER = "\\logging\\");
    finder!(pub SQL_FINDER = "\\django\\db\\models\\sql\\compiler.py");
    finder!(pub PYTEST_FINDER = "kolo\\pytest_plugin.py");
    finder!(pub UNITTEST_FINDER = "unittest\\result.py");
    finder!(pub LIBRARY_FINDERS = "lib\\python", "\\site-packages\\", "\\x64\\lib\\");
    finder!(pub LOWER_PYTHON_FINDER = "\\python\\");
    finder!(pub UPPER_PYTHON_FINDER = "\\Python\\");
    finder!(pub LOWER_LIB_FINDER = "\\lib\\");
    finder!(pub UPPER_LIB_FINDER = "\\Lib\\");
    finder!(pub KOLO_FINDERS = "\\kolo\\middleware", "\\kolo\\profiler", "\\kolo\\serialize", "\\kolo\\pytest_plugin.py");
}
#[cfg(target_os = "windows")]
use windows::*;

#[cfg(not(target_os = "windows"))]
mod not_windows {
    use bstr::Finder;
    use once_cell::sync::Lazy;
    finder!(pub MIDDLEWARE_FINDER = "/kolo/middleware.py");
    finder!(pub DJANGO_CHECKS_FINDER = "django/core/checks/registry.py");
    finder!(pub DJANGO_TEST_DB_FINDER = "django/db/backends/base/creation.py");
    finder!(pub DJANGO_SETUP_FINDER = "django/__init__.py");
    finder!(pub TEMPLATE_FINDER = "django/template/backends/django.py");
    finder!(pub HUEY_FINDER = "/huey/api.py");
    finder!(pub REQUESTS_FINDER = "requests/sessions");
    finder!(pub HTTPX_FINDER = "httpx/_client.py");
    finder!(pub URLLIB_FINDER = "urllib/request");
    finder!(pub URLLIB3_FINDER = "urllib3/connectionpool");
    finder!(pub LOGGING_FINDER = "/logging/");
    finder!(pub SQL_FINDER = "/django/db/models/sql/compiler.py");
    finder!(pub PYTEST_FINDER = "kolo/pytest_plugin.py");
    finder!(pub UNITTEST_FINDER = "unittest/result.py");
    finder!(pub LIBRARY_FINDERS = "lib/python", "/site-packages/");
    finder!(pub KOLO_FINDERS = "/kolo/middleware", "/kolo/profiler", "/kolo/serialize", "/kolo/pytest_plugin.py");
}
#[cfg(not(target_os = "windows"))]
use not_windows::*;

pub fn use_django_filter(filename: &str) -> bool {
    MIDDLEWARE_FINDER.find(filename).is_some()
}

pub fn use_django_checks_filter(filename: &str) -> bool {
    DJANGO_CHECKS_FINDER.find(filename).is_some()
}

pub fn use_django_test_db_filter(filename: &str) -> bool {
    DJANGO_TEST_DB_FINDER.find(filename).is_some()
}

pub fn use_django_setup_filter(filename: &str) -> bool {
    DJANGO_SETUP_FINDER.find(filename).is_some()
}

pub fn use_django_template_filter(filename: &str) -> bool {
    TEMPLATE_FINDER.find(filename).is_some()
}

pub fn use_celery_filter(filename: &str) -> bool {
    CELERY_FINDER.find(filename).is_some() && SENTRY_FINDER.find(filename).is_none()
}

pub fn use_huey_filter(
    filename: &str,
    huey_filter: &PyAny,
    py: Python,
    pyframe: &PyFrame,
) -> Result<bool, PyErr> {
    if HUEY_FINDER.find(filename).is_some() {
        let task_class = huey_filter.getattr(intern!(py, "klass"))?;
        if task_class.is_none() {
            let huey_api = PyModule::import(py, "huey.api")?;
            let task_class = huey_api.getattr(intern!(py, "Task"))?;
            huey_filter.setattr("klass", task_class)?;
        }

        let task_class = huey_filter.getattr(intern!(py, "klass"))?;
        let task_class = task_class.downcast()?;
        let frame_locals = pyframe.getattr(intern!(py, "f_locals"))?;
        let task = frame_locals.get_item("self")?;
        task.is_instance(task_class)
    } else {
        Ok(false)
    }
}

pub fn use_httpx_filter(filename: &str) -> bool {
    HTTPX_FINDER.find(filename).is_some()
}

pub fn use_requests_filter(filename: &str) -> bool {
    REQUESTS_FINDER.find(filename).is_some()
}

pub fn use_urllib_filter(filename: &str) -> bool {
    URLLIB_FINDER.find(filename).is_some()
}

pub fn use_urllib3_filter(filename: &str) -> bool {
    URLLIB3_FINDER.find(filename).is_some()
}

pub fn use_exception_filter(filename: &str, event: &str) -> bool {
    event == "call" && DJANGO_FINDER.find(filename).is_some()
}

pub fn use_logging_filter(filename: &str, event: &str) -> bool {
    event == "return" && LOGGING_FINDER.find(filename).is_some()
}

pub fn use_sql_filter(
    filename: &str,
    sql_filter: &PyAny,
    py: Python,
    pyframe: &PyFrame,
) -> Result<bool, PyErr> {
    if SQL_FINDER.find(filename).is_some() {
        let sql_filter_class = sql_filter.get_type();
        if sql_filter_class.getattr(intern!(py, "klass"))?.is_none() {
            let compiler = PyModule::import(py, "django.db.models.sql.compiler")?;
            let sql_update_compiler = compiler.getattr(intern!(py, "SQLUpdateCompiler"))?;
            sql_filter_class.setattr("klass", sql_update_compiler)?;
        }
        let f_code = pyframe.getattr(intern!(py, "f_code"))?;
        Ok(!f_code.is(sql_filter_class
            .getattr(intern!(py, "klass"))?
            .getattr(intern!(py, "execute_sql"))?
            .getattr(intern!(py, "__code__"))?))
    } else {
        Ok(false)
    }
}

pub fn use_pytest_filter(filename: &str, event: &str) -> bool {
    event == "call" && PYTEST_FINDER.find(filename).is_some()
}

pub fn use_unittest_filter(filename: &str, event: &str) -> bool {
    event == "call" && UNITTEST_FINDER.find(filename).is_some()
}

pub fn library_filter(co_filename: &str) -> bool {
    for finder in LIBRARY_FINDERS.iter() {
        if finder.find(co_filename).is_some() {
            return true;
        }
    }
    #[cfg(target_os = "windows")]
    {
        (LOWER_PYTHON_FINDER.find(co_filename).is_some()
            || UPPER_PYTHON_FINDER.find(co_filename).is_some())
            && (LOWER_LIB_FINDER.find(co_filename).is_some()
                || UPPER_LIB_FINDER.find(co_filename).is_some())
    }
    #[cfg(not(target_os = "windows"))]
    false
}

pub fn frozen_filter(co_filename: &str) -> bool {
    FROZEN_FINDER.find(co_filename).is_some()
}

pub fn exec_filter(co_filename: &str) -> bool {
    EXEC_FINDER.find(co_filename).is_some()
}

pub fn kolo_filter(co_filename: &str) -> bool {
    KOLO_FINDERS
        .iter()
        .any(|finder| finder.find(co_filename).is_some())
}

pub fn attrs_filter(co_filename: &str, pyframe: &PyFrame, py: Python) -> Result<bool, PyErr> {
    if co_filename.starts_with("<attrs generated") {
        return Ok(true);
    }

    let previous = pyframe.getattr(intern!(py, "f_back"))?;
    if previous.is_none() {
        return Ok(false);
    }

    let f_code = previous.getattr(intern!(py, "f_code"))?;
    let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
    let co_filename = co_filename.extract::<String>()?;

    #[cfg(target_os = "windows")]
    let make_path = "attr\\_make.py";
    #[cfg(not(target_os = "windows"))]
    let make_path = "attr/_make.py";

    if co_filename.is_empty() {
        let previous = previous.getattr(intern!(py, "f_back"))?;
        if previous.is_none() {
            return Ok(false);
        }
        let f_code = previous.getattr(intern!(py, "f_code"))?;
        let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
        let co_filename = co_filename.extract::<String>()?;
        Ok(co_filename.ends_with(make_path))
    } else {
        Ok(co_filename.ends_with(make_path))
    }
}
