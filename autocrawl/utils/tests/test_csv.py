import codecs
import csv
import json

import pytest
from pkg_resources import resource_stream, resource_string

from ..csv_export import CSVExporter


class TestCSV:
    @pytest.mark.parametrize(
        "case_name, adjusted_properties, array_limits",
        [
            ("articles_xod_test", {}, {}),
            (
                "items_recursive_test",
                {
                    "named_array_field": {
                        "named": True,
                        "name": "name",
                        "grouped": False,
                    }
                },
                {},
            ),
            (
                "products_full_schema_test",
                {
                    "gtin": {"named": True, "name": "type", "grouped": False},
                    "additionalProperty": {
                        "named": True,
                        "name": "name",
                        "grouped": False,
                    },
                    "ratingHistogram": {
                        "named": True,
                        "name": "ratingOption",
                        "grouped": False,
                    },
                },
                {"offers": 1},
            ),
            (
                "products_simple_xod_test",
                {
                    "gtin": {"named": True, "name": "type", "grouped": False},
                    "additionalProperty": {
                        "named": True,
                        "name": "name",
                        "grouped": False,
                    },
                },
                {"offers": 1},
            ),
            (
                "products_xod_test",
                {
                    "gtin": {"named": True, "name": "type", "grouped": False},
                    "additionalProperty": {
                        "named": True,
                        "name": "name",
                        "grouped": False,
                    },
                },
                {"offers": 1},
            ),
        ],
    )
    def test_csv_export(self, case_name, adjusted_properties, array_limits):
        # Load item list from JSON (simulate API response)
        item_list = json.loads(
            resource_string(__name__, f"assets/{case_name}.json").decode("utf-8")
        )
        csv_exporter = CSVExporter(adjusted_properties, array_limits, [])
        # Collect stats
        for it in item_list:
            csv_exporter.process_object(it)
        csv_exporter.limit_headers_meta()
        csv_exporter.flatten_headers()
        # Compare with pre-processed data
        csv_data = list(
            csv.reader(
                codecs.getreader("utf-8")(
                    resource_stream(__name__, f"assets/{case_name}.csv")
                )
            )
        )
        assert len([csv_exporter.headers] + item_list) == len(csv_data)
        # Comparing row by row
        for item, row in zip(item_list, csv_data[1:]):
            # Stringify all values because to match string data from csv
            assert [str(x) for x in csv_exporter.export_item(item)] == row
