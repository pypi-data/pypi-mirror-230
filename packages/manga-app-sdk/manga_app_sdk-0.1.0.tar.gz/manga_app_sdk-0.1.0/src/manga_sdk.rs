use pyo3::{exceptions::PyTypeError, prelude::*};
pub enum MangaHost {
    KOMIKCAST,
}

impl ToString for MangaHost {
    fn to_string(&self) -> String {
        match self {
            MangaHost::KOMIKCAST => "https://apk.nijisan.my.id".to_owned(),
        }
    }
}

#[pyclass]
pub struct MangaAPI {
    host: String,
    client: reqwest::blocking::Client,
}

#[pymethods]
impl MangaAPI {
    #[new]
    pub fn new() -> Self {
        let client = reqwest::blocking::Client::new();
        Self {
            host: MangaHost::KOMIKCAST.to_string(),
            client,
        }
    }

    pub fn list(&mut self, page: usize) -> PyResult<String> {
        let page_one: usize = ((page - 1) % 4) + 1;
        let page_two: usize = (page as f32 / 4.0).ceil() as usize;

        let url = format!(
            "{}/premium/home/latest/{}/{}",
            self.host.to_string(),
            page_one,
            page_two
        );

        self.client
            .get(url)
            .send()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))?
            .text()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))
    }

    pub fn detail(&mut self, manga_id: String) -> PyResult<String> {
        let url = format!("{}/komik/info/{}", self.host.to_string(), manga_id);
        self.client
            .get(url)
            .send()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))?
            .text()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))
    }

    pub fn chapters(&mut self, manga_id: String, page: usize) -> PyResult<String> {
        let url = format!(
            "{}/komik/info/{}/ch?page={}&limit=50&desc=1",
            self.host.to_string(),
            manga_id,
            page
        );
        self.client
            .get(url)
            .send()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))?
            .text()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))
    }

    pub fn chapter_detail(&mut self, chapter_id: String) -> PyResult<String> {
        let url = format!("{}/komik/baca/{}", self.host.to_string(), chapter_id);
        self.client
            .get(url)
            .send()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))?
            .text()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))
    }

    pub fn search(&mut self, query: String) -> PyResult<String> {
        let url = format!("{}/komik/search/{}", self.host.to_string(), query);
        self.client
            .get(url)
            .send()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))?
            .text()
            .map_err(|err| PyErr::from(PyTypeError::new_err(err.to_string())))
    }
}
