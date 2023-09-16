from typing import Any, Annotated
from collections.abc import Callable
from uuid import UUID
from fastapi import Path, Query
from pydantic_core import core_schema
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue



def handle_instance(instance):
    print(type(instance))
    print(instance)
    print(str(instance))
    new_instance = UUID(str(instance))
    return new_instance

class _PydanticUUIDAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(value: str) -> UUID:
            return handle_instance(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance) if instance else None
            ),
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(UUID),
                    from_str_schema,
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance) if instance else None
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


PydanticUUID = Annotated[UUID, _PydanticUUIDAnnotation]
PydanticUUIDPath = Annotated[PydanticUUID, Path()]
PydanticUUIDQuery = Annotated[PydanticUUID, Query()]