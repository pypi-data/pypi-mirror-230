from django.forms.widgets import PasswordInput
from .settings import public_key_text
from .settings import encrypted_value_prefix

class DjangoSecurePasswordInputWidget(PasswordInput):
    def __init__(self, attrs=None, render_value=False):
        attrs = attrs or {}
        attrs["public_key"] = public_key_text
        attrs["prefix"] = encrypted_value_prefix
        if "class" in attrs:
            attrs["class"] += " django-secure-password-input"
        else:
            attrs["class"] = "django-secure-password-input"
        super().__init__(attrs, render_value)

    class Media:
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "django-secure-password-input/js/jsencrypt.js",
            "django-secure-password-input/js/enable-jsencrypt.js",
            "admin/js/jquery.init.js"
        ]
