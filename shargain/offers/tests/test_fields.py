"""Tests for PydanticField."""

import json

import pytest
from django.core.exceptions import ValidationError
from pydantic import BaseModel

from shargain.offers.db_fields import PydanticField, PydanticFormField


class SampleModel(BaseModel):
    name: str
    count: int = 0


pytestmark = pytest.mark.django_db


class TestPydanticField:
    def test_from_db_value_returns_none_for_null(self):
        field = PydanticField(pydantic_model=SampleModel, null=True)
        assert field.from_db_value(None, None, None) is None

    def test_from_db_value_validates_and_returns_model(self):
        field = PydanticField(pydantic_model=SampleModel)
        result = field.from_db_value({"name": "test", "count": 5}, None, None)
        assert isinstance(result, SampleModel)
        assert result.name == "test"
        assert result.count == 5

    def test_to_python_accepts_model_instance(self):
        field = PydanticField(pydantic_model=SampleModel)
        model = SampleModel(name="test")
        result = field.to_python(model)
        assert result is model

    def test_to_python_converts_dict_to_model(self):
        field = PydanticField(pydantic_model=SampleModel)
        result = field.to_python({"name": "test"})
        assert isinstance(result, SampleModel)
        assert result.name == "test"

    def test_to_python_validates_and_raises_on_invalid(self):
        field = PydanticField(pydantic_model=SampleModel)
        with pytest.raises(ValidationError):
            field.to_python({})

    def test_get_prep_value_returns_none_for_none(self):
        field = PydanticField(pydantic_model=SampleModel, null=True)
        assert field.get_prep_value(None) is None

    def test_get_prep_value_dumps_model_to_json_string(self):
        field = PydanticField(pydantic_model=SampleModel)
        model = SampleModel(name="test", count=3)
        result = field.get_prep_value(model)
        assert isinstance(result, str)
        assert json.loads(result) == {"name": "test", "count": 3}

    def test_get_prep_value_serializes_raw_dict_to_json_string(self):
        field = PydanticField(pydantic_model=SampleModel)
        result = field.get_prep_value({"name": "x"})
        assert isinstance(result, str)
        assert json.loads(result) == {"name": "x"}

    def test_deconstruct_includes_pydantic_model_path(self):
        field = PydanticField(pydantic_model=SampleModel, null=True)
        name, path, args, kwargs = field.deconstruct()
        assert "pydantic_model" in kwargs
        assert "tests.test_fields.SampleModel" in kwargs["pydantic_model"]


class TestPydanticFieldForm:
    def test_formfield_uses_pydantic_form_field(self):
        field = PydanticField(pydantic_model=SampleModel)
        assert isinstance(field.formfield(), PydanticFormField)

    def test_prepare_value_serializes_model(self):
        field = PydanticField(pydantic_model=SampleModel)
        form_field = field.formfield()
        model = SampleModel(name="test", count=3)
        prepared = form_field.prepare_value(model)
        assert json.loads(prepared) == {"name": "test", "count": 3}

    def test_prepare_value_passes_through_json_ready_value(self):
        field = PydanticField(pydantic_model=SampleModel)
        form_field = field.formfield()
        assert form_field.prepare_value({"name": "test"}) == '{"name": "test"}'

    def test_to_python_parses_json_string_to_dict(self):
        field = PydanticField(pydantic_model=SampleModel)
        form_field = field.formfield()
        assert form_field.to_python('{"name": "test", "count": 1}') == {"name": "test", "count": 1}

    def test_has_changed_accepts_model_initial(self):
        field = PydanticField(pydantic_model=SampleModel)
        form_field = field.formfield()
        model = SampleModel(name="test", count=3)
        assert form_field.has_changed(model, '{"name": "test", "count": 4}') is True
        assert form_field.has_changed(model, '{"name": "test", "count": 3}') is False
