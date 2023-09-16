from django.contrib import admin


class DjangoCheckboxNormalizeAdmin(admin.ModelAdmin):
    """Boolean字段破坏了表单的一致性显示。我们来修复一下这个问题。
    """
    class Media:
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "django_checkbox_normalize/js/django_checkbox_normalize.js",
            "admin/js/jquery.init.js",
        ]
