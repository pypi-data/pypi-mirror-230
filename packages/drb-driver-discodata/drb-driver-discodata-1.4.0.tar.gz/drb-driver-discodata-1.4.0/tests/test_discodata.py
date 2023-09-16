import io
import os
import unittest

import httpretty
from drb.drivers.discodata import DrbDiscodataServiceNode
from drb.drivers.discodata.discodata import (
    DrbDiscodataDataBaseNode,
    DrbDiscodataTableNode,
)
from drb.exceptions.core import DrbException
import pandas as pd
import xarray as xr
from pandas.testing import assert_frame_equal


def callback_checker(request, uri, headers):
    headers["Content-Type"] = "application/json"
    headers["Content-Length"] = 11722079
    return 200, headers, TestDiscoData.data


def callback_head(request, uri, headers):
    headers["Content-Type"] = "application/json"
    headers["Content-Length"] = len('{"value": test}')
    return 200, headers, '{"value": test}'


class TestDiscoData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.path.join(os.path.dirname(__file__), "resources")
        httpretty.enable()

        path = os.path.join(os.path.dirname(__file__), "resources", "md.json")
        path_page_0 = os.path.join(
            os.path.dirname(__file__), "resources", "page_0.json"
        )
        path_page_35 = os.path.join(
            os.path.dirname(__file__), "resources", "page_35.json"
        )
        path_panda_xarray = os.path.join(
            os.path.dirname(__file__), "resources", "page_panda_xarray.json"
        )

        with open(path_page_0) as f_p:
            cls.data_page_0 = f_p.read()
        with open(path_page_35) as f_p:
            cls.data_page_35 = f_p.read()
        with open(path_panda_xarray) as f_p:
            cls.data_panda_xarray = f_p.read()
        with open(path) as f:
            cls.data = f.read()

    @classmethod
    def tearDownClass(cls) -> None:
        httpretty.disable()

    @classmethod
    def tearDown(cls) -> None:
        httpretty.reset()

    def test_service(self):
        url = "https://discodata.eea.europa.eu/md"

        httpretty.register_uri(httpretty.GET, url, callback_checker)
        httpretty.register_uri(httpretty.HEAD, url, callback_head)

        node = DrbDiscodataServiceNode(path="https://discodata.eea.europa.eu")
        self.assertEqual(node.name, "DISCODATA")

        children = node.children
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(21, len(children))

        self.assertIsNone(node.namespace_uri)
        self.assertIsNone(node.value)
        self.assertIsNot(node.attributes, {})
        self.assertIn(("databases", None), node.attributes)
        databases = node.get_attribute("databases")
        self.assertIsNotNone(databases)
        self.assertEqual(node.path.name, "https://discodata.eea.europa.eu")

        self.assertFalse(node.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbException):
            node.get_attribute("")

        with self.assertRaises(DrbException):
            node.get_impl(io.BufferedIOBase)

        node.close()

    def test_database(self):
        url = "https://discodata.eea.europa.eu/md"

        httpretty.register_uri(httpretty.GET, url, callback_checker)
        httpretty.register_uri(httpretty.HEAD, url, callback_head)

        node = DrbDiscodataServiceNode(path="https://discodata.eea.europa.eu")
        self.assertEqual(node.name, "DISCODATA")

        self.assertTrue(node.has_child("AirQualityDataFlows"))
        tb = node["AirQualityDataFlows"]
        self.assertIsInstance(tb, DrbDiscodataDataBaseNode)

        self.assertEqual(
            tb.path.name, "https://discodata.eea.europa.eu/AirQualityDataFlows"
        )

        self.assertFalse(tb.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbException):
            tb.get_impl(io.BufferedIOBase)

        self.assertIsNone(tb.namespace_uri)
        self.assertIsNone(tb.value)
        self.assertIsNot(tb.attributes, {})
        self.assertIn(("tables", None), tb.attributes)
        tables = tb.get_attribute("tables")
        self.assertIsNotNone(tables)

        with self.assertRaises(DrbException):
            tb.get_attribute("")

        tb.close()

    def test_table(self):
        data = [
            {
                "Country": "France",
                "CountryCode": "FR        ",
                "B2G_Namespace": "FR.LCSQA-INERIS.AQ",
                "AirQualityNetwork": "NET-FR058A",
                "AirQualityNetworkName": "ATMO NOUVELLE-AQUITAINE",
                "AirQualityStation": "STA-FR09301",
                "AirQualityStationEoICode": "FR09301",
            },
            {
                "Country": "France",
                "CountryCode": "FR        ",
                "B2G_Namespace": "FR.LCSQA-INERIS.AQ",
                "AirQualityNetwork": "NET-FR035A",
                "AirQualityNetworkName": "AIR PAYS DE LA LOIRE",
                "AirQualityStation": "STA-FR23124",
                "AirQualityStationEoICode": "FR23124",
            },
        ]
        df = pd.DataFrame(data)
        ds = df.to_xarray()

        url = "https://discodata.eea.europa.eu/md"

        httpretty.register_uri(httpretty.GET, url, callback_checker)
        httpretty.register_uri(httpretty.HEAD, url, callback_head)
        httpretty.register_uri(
            httpretty.POST,
            "https://discomap.eea.europa.eu/App/"
            "DiscodataViewer/"
            "data?"
            "fqn=[AirQualityDataFlows]."
            "[v2r1]."
            "[AirQualityStatistics]",
            body=TestDiscoData.data_panda_xarray,
        )
        node = DrbDiscodataServiceNode(path="https://discodata.eea.europa.eu")
        self.assertEqual(node.name, "DISCODATA")

        tb = node["AirQualityDataFlows"]
        self.assertTrue(tb.has_child("AirQualityStatistics"))
        table = tb["AirQualityStatistics"]
        self.assertIsInstance(table, DrbDiscodataTableNode)
        self.assertEqual(
            table.path.name,
            "https://discodata.eea.europa.eu/"
            "AirQualityDataFlows/AirQualityStatistics",
        )

        self.assertFalse(table.has_impl(io.BufferedIOBase))
        self.assertTrue(table.has_impl(pd.DataFrame))
        self.assertTrue(table.has_impl(xr.Dataset))

        with self.assertRaises(DrbException):
            table.get_impl(io.BufferedIOBase)

        assert_frame_equal(table.get_impl(pd.DataFrame), df)

        self.assertEqual(table.get_impl(xr.Dataset), ds)

        self.assertIsNone(table.namespace_uri)
        self.assertIsNone(table.value)

        self.assertIsNotNone(table.get_attribute("columns"))
        self.assertIsNotNone(table.get_attribute("Country"))
        self.assertIsNotNone(table.get_attribute("Country")["description"])
        self.assertEqual(
            table.get_attribute("Country")["description"],
            "Country or territory name.",
        )

        with self.assertRaises(DrbException):
            table.get_attribute("")
        table.close()

    def test_rows(self):
        url = "https://discodata.eea.europa.eu/md"

        httpretty.register_uri(httpretty.GET, url, callback_checker)
        httpretty.register_uri(httpretty.HEAD, url, callback_head)

        node = DrbDiscodataServiceNode(path="https://discodata.eea.europa.eu")
        self.assertEqual(node.name, "DISCODATA")
        tb = node["AirQualityDataFlows"]
        table = tb["AirQualityStatistics"]

        httpretty.register_uri(
            httpretty.POST,
            "https://discomap.eea.europa.eu/App/"
            "DiscodataViewer/"
            "data?"
            "fqn=[AirQualityDataFlows]."
            "[v2r1]."
            "[AirQualityStatistics]",
            body=TestDiscoData.data_page_0,
        )

        rows = table.children
        self.assertEqual(len(rows), 4090093)

        with self.assertRaises(NotImplementedError):
            rows.reverse()
        with self.assertRaises(NotImplementedError):
            rows.copy()
        with self.assertRaises(NotImplementedError):
            rows.count(None)
        with self.assertRaises(NotImplementedError):
            rows.insert(None, None)
        with self.assertRaises(NotImplementedError):
            rows.remove(None)
        with self.assertRaises(NotImplementedError):
            rows.pop(None)
        with self.assertRaises(NotImplementedError):
            rows.append(None)
        with self.assertRaises(NotImplementedError):
            rows.sort()
        with self.assertRaises(NotImplementedError):
            rows.clear()
        with self.assertRaises(NotImplementedError):
            rows.index(4, 6)
        rows = table[2:5]

        itr = iter(table.children)
        row_one = next(itr)
        row_two = next(itr)
        httpretty.register_uri(
            httpretty.POST,
            "https://discomap.eea.europa.eu/App/"
            "DiscodataViewer/"
            "data?"
            "fqn=[AirQualityDataFlows]."
            "[v2r1]."
            "[AirQualityStatistics]",
            body=TestDiscoData.data_page_35,
        )
        for i in range(1040, 1045):
            row = table[i]
            self.assertTrue(row.has_child("Country"))
