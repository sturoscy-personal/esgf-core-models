# The Patch operations, BasePartial and PartialItem are from
# stac-fastapi-extensions 7.1.1 (https://github.com/stac-utils/stac-fastapi),

import json
from typing import Any, Literal

from pydantic import ConfigDict, Field
from stac_pydantic.shared import BBox, StacBaseModel


class PatchAddReplaceTest(StacBaseModel):
    """Add, Replace or Test Operation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"op": "add", "path": "/properties/foo", "value": "bar"},
                {"op": "replace", "path": "/properties/foo", "value": "bar"},
                {"op": "test", "path": "/properties/foo", "value": "bar"},
            ]
        }
    )

    path: str
    op: Literal["add", "replace", "test"]
    value: Any

    @property
    def json_value(self) -> str:
        """JSON dump of value field.

        Returns:
            str: JSON-ised value
        """
        return json.dumps(self.value)


class PatchRemove(StacBaseModel):
    """Remove Operation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "op": "remove",
                    "path": "/properties/foo",
                }
            ]
        }
    )

    path: str
    op: Literal["remove"]


class PatchMoveCopy(StacBaseModel):
    """Move or Copy Operation."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "op": "copy",
                    "path": "/properties/foo",
                    "from": "/properties/bar",
                },
                {
                    "op": "move",
                    "path": "/properties/foo",
                    "from": "/properties/bar",
                },
            ]
        },
    )

    path: str
    op: Literal["move", "copy"]
    from_: str = Field(alias="from")


PatchOperation = PatchAddReplaceTest | PatchMoveCopy | PatchRemove


class BasePartial(StacBaseModel):
    """Base Partial Class."""

    @staticmethod
    def merge_to_operations(data: dict) -> list[PatchOperation]:
        """Convert merge operation to list of RF6902 operations.

        Args:
            data: dictionary to convert.

        Returns:
            List: list of RF6902 operations.
        """
        operations: list[PatchOperation] = []

        for key, value in data.copy().items():
            if value is None:
                operations.append(PatchRemove(op="remove", path=f"/{key}"))

            elif isinstance(value, dict):
                nested_operations = BasePartial.merge_to_operations(value)

                for nested_operation in nested_operations:
                    nested_operation.path = f"/{key}{nested_operation.path}"
                    operations.append(nested_operation)

            else:
                operations.append(
                    PatchAddReplaceTest(op="add", path=f"/{key}", value=value)
                )

        return operations


class PartialItem(BasePartial):
    """Partial STAC Item."""

    type: Literal["Feature"] | None = None
    stac_version: str | None = None
    stac_extensions: list[str] | None = None
    id: str | None = None
    geometry: dict[str, Any] | None = None
    bbox: BBox | None = None
    properties: dict[str, Any] | None = None
    links: list[dict[str, Any]] | None = None
    assets: dict[str, Any] | None = None
    collection: str | None = None
