from typing import Any

from django import forms
from django.db import models


class HttpURLField(models.URLField):
    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field | None:
        kwargs["assume_scheme"] = "http"
        if form_class is not None:
            kwargs["form_class"] = form_class
        if choices_form_class is not None:
            kwargs["choices_form_class"] = choices_form_class
        return super().formfield(**kwargs)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
