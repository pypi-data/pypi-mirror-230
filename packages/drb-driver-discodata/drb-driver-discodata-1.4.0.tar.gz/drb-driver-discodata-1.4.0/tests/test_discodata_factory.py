import io

import os
import unittest
import httpretty

from drb.drivers.discodata import DiscodataFactory
from drb.nodes.logical_node import DrbLogicalNode


def callback_checker(request, uri, headers):
    headers['Content-Type'] = 'application/json'
    headers['Content-Length'] = 11722079
    return 200, headers, TestDiscoData.data


def callback_head(request, uri, headers):
    headers['Content-Type'] = 'application/json'
    headers['Content-Length'] = len('{"value": test}')
    return 200, headers, '{"value": test}'


class TestDiscoData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.path.join(os.path.dirname(__file__), 'resources')
        httpretty.enable()

        path = os.path.join(os.path.dirname(__file__), 'resources',
                            'md.json')
        path_page_0 = os.path.join(os.path.dirname(__file__), 'resources',
                                   "page_0.json")
        path_page_35 = os.path.join(os.path.dirname(__file__), 'resources',
                                    "page_35.json")

        with open(path_page_0) as f_p:
            cls.data_page_0 = f_p.read()
        with open(path_page_35) as f_p:
            cls.data_page_35 = f_p.read()
        with open(path) as f:
            cls.data = f.read()

    @classmethod
    def tearDownClass(cls) -> None:
        httpretty.disable()
        httpretty.reset()

    def test_create(self):
        url = 'https://discodata.eea.europa.eu/md'

        httpretty.register_uri(httpretty.GET, url, callback_checker)
        httpretty.register_uri(httpretty.HEAD, url, callback_head)

        factory = DiscodataFactory()

        logical_node = factory.create(
            DrbLogicalNode('https+discodata://discodata.eea.europa.eu'))
        node = factory.create(logical_node)

        self.assertEqual(node.name, 'DISCODATA')

        node.close()
