import json
from importlib import import_module
from typing import Any

from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from pydantic import BaseModel, ValidationError


class PydanticFormField(forms.JSONField):
    def prepare_value(self, value):
        return super().prepare_value(_json_ready(value))

    def has_changed(self, initial, data):
        return super().has_changed(_json_ready(initial), data)


def _json_ready(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value


class PydanticField(models.JSONField):
    def __init__(self, pydantic_model: type[BaseModel] | str, **kwargs):
        self._pydantic_model: type[BaseModel] | None = None
        self._pydantic_model_path: str | None = None
        if isinstance(pydantic_model, str):
            self._pydantic_model_path = pydantic_model
        else:
            self._pydantic_model = pydantic_model
            self._pydantic_model_path = f"{pydantic_model.__module__}.{pydantic_model.__qualname__}"
        super().__init__(**kwargs)

    @property
    def pydantic_model(self) -> type[BaseModel]:
        if self._pydantic_model is None and self._pydantic_model_path:
            module_path, class_name = self._pydantic_model_path.rsplit(".", 1)
            module = import_module(module_path)
            self._pydantic_model = getattr(module, class_name)
        if self._pydantic_model is None:
            msg = "pydantic_model is not set"
            raise RuntimeError(msg)
        return self._pydantic_model

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> BaseModel | None:
        if value is None:
            return None
        if isinstance(value, str):
            return self.pydantic_model.model_validate_json(value)
        return self.pydantic_model.model_validate(value)

    def to_python(self, value: Any) -> BaseModel | None:
        if value is None:
            return None
        if isinstance(value, self.pydantic_model):
            return value
        try:
            return self.pydantic_model.model_validate(value)
        except ValidationError as e:
            raise DjangoValidationError(str(e)) from e

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, self.pydantic_model):
            return super().get_prep_value(value.model_dump())
        return super().get_prep_value(value)

    def validate(self, value: Any, model_instance: Any) -> None:
        models.Field.validate(self, value, model_instance)
        try:
            json.dumps(_json_ready(value), cls=self.encoder)
        except TypeError as e:
            raise DjangoValidationError(self.error_messages["invalid"], code="invalid") from e

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["pydantic_model"] = self._pydantic_model_path
        return name, path, args, kwargs

    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field | None:
        return super().formfield(
            form_class=PydanticFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
