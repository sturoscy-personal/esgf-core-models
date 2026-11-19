"""
Unit tests for the STAC Transaction request models vendored from stac-fastapi.
"""

import unittest

from esgf_core_models._vendor.stac_fastapi import (
    BasePartial,
    PartialItem,
    PatchAddReplaceTest,
    PatchMoveCopy,
    PatchRemove,
)


class TestPatchOperations(unittest.TestCase):
    def test_json_value(self):
        op = PatchAddReplaceTest(op="add", path="/properties/foo", value={"a": 1})
        self.assertEqual(op.json_value, '{"a": 1}')

    def test_move_copy_from_alias(self):
        op = PatchMoveCopy.model_validate(
            {"op": "move", "path": "/properties/foo", "from": "/properties/bar"}
        )
        self.assertEqual(op.from_, "/properties/bar")
        self.assertEqual(op.model_dump()["from"], "/properties/bar")


class TestMergeToOperations(unittest.TestCase):
    def test_converts_merge_patch(self):
        operations = BasePartial.merge_to_operations(
            {"title": None, "properties": {"foo": "bar"}, "id": "x"}
        )
        self.assertEqual(len(operations), 3)

        remove, nested_add, add = operations
        self.assertIsInstance(remove, PatchRemove)
        self.assertEqual(remove.path, "/title")

        self.assertIsInstance(nested_add, PatchAddReplaceTest)
        self.assertEqual(
            (nested_add.op, nested_add.path, nested_add.value),
            ("add", "/properties/foo", "bar"),
        )

        self.assertEqual((add.op, add.path, add.value), ("add", "/id", "x"))

    def test_partial_item_dump(self):
        item = PartialItem(properties={"foo": None})
        operations = BasePartial.merge_to_operations(item.model_dump())
        self.assertEqual(
            [(o.op, o.path) for o in operations], [("remove", "/properties/foo")]
        )
