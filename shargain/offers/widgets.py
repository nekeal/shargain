from django.contrib.admin.widgets import AdminURLFieldWidget
from django_better_admin_arrayfield.forms.widgets import DynamicArrayWidget


class AdminDynamicArrayWidget(DynamicArrayWidget):

    def __init__(self, *args, **kwargs):
        kwargs["subwidget_form"] = AdminURLFieldWidget
        super().__init__(*args, **kwargs)
