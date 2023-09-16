from typing import Type, Union

from fastgenerateapi.settings.register_settings import settings

from fastgenerateapi.pydantic_utils.base_model import Config
from pydantic import create_model
from tortoise import Model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta, \
    get_validate_dict_from_fields


def create_schema_factory(
        model_class: Type[Model],
        include: Union[list, tuple, set] = None,
        extra_include: Union[list, tuple, set] = None,
        exclude: Union[list, tuple, set] = None,
) -> Type[T]:
    """
    Is used to create a CreateSchema
    """
    all_fields_info = get_dict_from_model_fields(model_class)

    include_fields = set()
    exclude_fields = set()
    if hasattr(model_class, "PydanticMeta"):
        if hasattr(model_class.PydanticMeta, "include"):
            include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.include)
            all_fields_info.update(include_fields_dict)
            include_fields.update(include_fields_dict.keys())
        else:
            include_fields.update(all_fields_info.keys())
        if hasattr(model_class.PydanticMeta, "create_include"):
            get_one_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.create_include)
            all_fields_info.update(get_one_include_fields_dict)
            include_fields.update(get_one_include_fields_dict.keys())
        if hasattr(model_class.PydanticMeta, "exclude"):
            exclude_fields.update(model_class.PydanticMeta.exclude)
        if hasattr(model_class.PydanticMeta, "create_exclude"):
            exclude_fields.update(model_class.PydanticMeta.create_exclude)
    else:
        include_fields.update(all_fields_info.keys())

    if include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if extra_include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, extra_include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if exclude:
        exclude_fields.update(exclude)

    all_fields = include_fields.difference(exclude_fields)
    try:
        if settings.app_settings.CREATE_EXCLUDE_ACTIVE_VALUE:
            try:
                all_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
            except Exception:
                ...
        all_fields.remove(model_class._meta.pk_attr)
    except Exception:
        ...

    name = model_class.__name__ + "CreateSchema"
    schema_field_dict = {field: all_fields_info[field] for field in all_fields}
    validators_dict = get_validate_dict_from_fields(schema_field_dict)
    schema: Type[T] = create_model(
        __model_name=name,
        **schema_field_dict,
        __config__=Config,
        __validators__=validators_dict,
    )
    return schema


