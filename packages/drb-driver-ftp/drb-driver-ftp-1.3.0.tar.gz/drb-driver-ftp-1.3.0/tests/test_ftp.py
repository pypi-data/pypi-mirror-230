import io
import time
import unittest
from multiprocessing import Process
import re
from unittest.mock import patch

from drb.exceptions.core import DrbException
from keyring.credentials import SimpleCredential
from requests.auth import HTTPBasicAuth

from drb.drivers.ftp import DrbFtpNode
from tests.utility import PORT, PATH, start_serve

def my_credential(pwd):
    return SimpleCredential("user", "12345")

class TestFtp(unittest.TestCase):
    process = Process(target=start_serve)
    url_ok = 'ftp://localhost:' + str(PORT) + PATH
    url_false = 'ftp://localhost:' + str(PORT) + PATH + '/NOT_HERE'
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.process.start()
        time.sleep(5)
        cls.node = DrbFtpNode(cls.url_ok, auth=HTTPBasicAuth("user", "12345"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.process.kill()
        cls.node.close()

    def test_check_class(self):
        self.assertTrue(issubclass(DrbFtpNode, DrbFtpNode))

    def test_not_found(self):
        with self.assertRaises(DrbException):
            DrbFtpNode(self.url_false,
                          auth=HTTPBasicAuth("user", "12345"))

    def test_name(self):
        self.assertEqual('resources', self.node.name)

    def test_namespace_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_parent(self):
        self.assertIsNone(self.node.parent)
        child = self.node.children[0]
        self.assertEqual(self.node, child.parent)

    def test_attributes(self):
        self.assertTrue(self.node.get_attribute(
           'directory'))
        self.assertTrue(self.node @ 'directory')
        self.assertIsNotNone(self.node.get_attribute(
            'size'))
        children = self.node['test_file1.txt']
        self.assertFalse(children.get_attribute(
            'directory'))
        self.assertFalse(children @ 'directory')

        self.assertEqual(24, children.get_attribute(
            'size'))
        self.assertEqual(24, children @ 'size')

        self.assertIsNotNone(children @ 'modified')

    def test_children(self):
        self.assertEqual(3, len(self.node.children))

    def test_download(self):
        with self.node['test_file1.txt'].get_impl(io.BytesIO) as stream:
            self.assertEqual('This is my awesome test.',
                             stream.read().decode())
        with self.node['test_file1.txt'].get_impl(io.BytesIO) as stream:
            self.assertEqual('T',
                             stream.read(1).decode())

    @patch(target="keyring.get_credential", new=my_credential)
    def test_keyring_auth(self):
        node = DrbFtpNode(path=self.url_ok)['test_file1.txt']

        self.assertEqual('This is my awesome test.',
                         node.get_impl(io.BytesIO).read().decode())
        node.close()
