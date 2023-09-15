mod manga_sdk;
pub use manga_sdk::MangaAPI;
use pyo3::prelude::*;

#[pymodule]
fn manga_app_sdk(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MangaAPI>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let mut api = MangaAPI::new();
        let result = api.list(1);
        dbg!(result.unwrap());
    }
}
