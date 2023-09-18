# django-static-echarts

Django application contain echarts static files.

## Install

```
pip install django-static-echarts
```

## Lincense

- All resource files of echarts are unzip from apache-echarts-X.Y.Z-src.zip which download from https://echarts.apache.org without any changes.
- All resource files of echarts obey echarts License, see details at https://www.apache.org/licenses/.
- We don't guarantee the latest jQuery version.

## Usage


*pro/settings.py*

```

    INSTALLED_APPS = [
        ...
        "django_static_echarts",
        ...
    ]
```

*app1/chart1.html*

```
    {% load staticfiles %}

    {% block script %}
        <script src="{% static "echarts/echarts.min.js" %}"></script>
        <script src="{% static "echarts/theme/vintage.js" %}"></script>
        <script src="{% static "echarts/map/js/china.js" %}"></script>
    {% endblock %}
```
## About releases

- The first number is our release number.
- The other three numbers are the same with ECHARTS's release version.

## Release

### v3.8.4

- First release.

### v4.0.4.1

- Upgrade echarts to 4.0.4.

### v4.0.4.2

- Doc update.

