# LMU Meteo Data API

The LMU provides free high-quality meteodata through a web API, that can be accessed without authentification. This package should help to acess the API and return the data as dataframe.<br>
The package is published on PyPi for easy installation using pip.

## API documentation
<url>https://www.meteo.physik.uni-muenchen.de/request-beta/</url>

## How to install

```
pip install lmu_meteo_api
```

## For developers

Set up you virtual environment
```bash
python3.10 -m venv .venv
```

Install dependencies
```bash
poetry install
```

(Optional) Publish new package
```bash
poetry build
poetry publish
```