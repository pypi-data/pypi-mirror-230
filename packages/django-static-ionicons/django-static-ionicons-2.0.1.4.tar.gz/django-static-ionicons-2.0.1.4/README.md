# django-static-ionicons


Django application contain ionicons static files


## Install


```
pip install django-static-ionicons
```

## Settings

```
INSTALLED_APPS = [
    ...
    "django_static_ionicons",
    ...
]
```

## Usage

**app/templates/demo.html**

```
{% load staticfiles %}

<link rel="stylesheet" type="text/css" href="{% static "ionicons/css/ionicons.css" %}">
```

## Releases

### v2.0.1 2017/12/21

- First release.

### v2.0.1.1 2018/03/27

- Repackage.

### v2.0.1.2 2020/02/26

- Add demo page.

### v2.0.1.3 2020/09/02

- No depends on django.
- Turn to the package as a pure static wrapper package.

### v2.0.1.4 2023/09/15

- Doc update.
