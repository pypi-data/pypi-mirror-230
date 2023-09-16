# django-checkbox-normalize

It's NOT a good design to put label after checkbox for BooleanField widget, so let's make it normal.


## Install

```shell
pip install django-checkbox-normalize
```

## Usage

### Settings

Add django_checkbox_normalize to settings.INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    'django_checkbox_normalize',
    ...
]
```

### Normalize for all model admins

Add `DJANGO_CHECKBOX_NORMALIZE_FOR_ALL = True` in pro/settings.py.

```python
DJANGO_CHECKBOX_NORMALIZE_FOR_ALL = True
```

### Normalize for one model admin

Add `DjangoCheckboxNormalizeAdmin` to one modeladmin.

```python
class MyModelAdmin(DjangoCheckboxNormalizeAdmin, admin.ModelAdmin):
    pass
```

#### django-checkbox-normalize preview

![django-checkbox-normalize preview](https://github.com/zencore-dobetter/pypi-images/raw/main/django-checkbox-normalize/django_checkbox_normalize.png)


## Releases

### v0.1.0

- First release.

### v0.1.1

- Fix BooleanField field style under small screen size.

### v0.1.2

- Add LICENSE file.

### v0.2.0

- Instead of using template rewrite, use js dynamic repairing method.
- Add DjangoCheckboxNormalizeAdmin to normalize one site.
- Add `DJANGO_CHECKBOX_NORMALIZE_FOR_ALL = True` to normalize for all modeladmins.

### v0.2.1

- Doc update.
