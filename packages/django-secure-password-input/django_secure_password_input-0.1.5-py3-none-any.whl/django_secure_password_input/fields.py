from django.forms.fields import CharField
from fastutils import rsautils
from .widgets import DjangoSecurePasswordInputWidget
from .settings import encrypted_value_prefix
from .settings import private_key


class DjangoSecurePasswordInput(CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = DjangoSecurePasswordInputWidget()

    def to_python(self, value):
        if value and value.startswith(encrypted_value_prefix):
            value = rsautils.decrypt(value[len(encrypted_value_prefix):], private_key).decode("utf-8")
        return value
