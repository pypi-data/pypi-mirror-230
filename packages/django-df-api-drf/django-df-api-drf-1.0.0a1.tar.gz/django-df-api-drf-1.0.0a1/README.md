# Django DF API DRF

Module for automatic including Djangoflow apps API to your project.

## Installation:

- Install the package

```
pip install django-df-api-drf
```


- Include default settings from `df_api_drf.defaults` to your `settings.py`

```python
from df_api_drf.defaults import DF_API_DRF_INSTALLED_APPS, REST_FRAMEWORK, SPECTACULAR_SETTINGS

INSTALLED_APPS = [
    ...
    *DF_API_DRF_INSTALLED_APPS,
    ...
]

REST_FRAMEWORK = {
    ...
    **REST_FRAMEWORK,
}

SPECTACULAR_SETTINGS = {
    ...
    **SPECTACULAR_SETTINGS,
}
```


- Alternatively, you can include the package to your `INSTALLED_APPS` manually and set up `REST_FRAMEWORK` and `SPECTACULAR_SETTINGS` by yourself:

```
INSTALLED_APPS = [
    ...
    'df_api_drf',
    ...
]

REST_FRAMEWORK = {
    ...
}

SPECTACULAR_SETTINGS = {
    ...
}
```


- Add the package to your urls.py

```
urlpatterns = [
    ...
    path("api/", include("df_api_drf.urls")),
    ...
]
```

## Development

Installing dev requirements:

```
pip install -e .[test]
```

Installing pre-commit hook:

```
pre-commit install
```

Running tests:

```
pytest
```
