import unittest
from unittest.mock import patch

from drb.core import DrbNode
from keyring.credentials import SimpleCredential

import drb.drivers.ftp
from drb.drivers.ftp import DrbFtpNode, DrbFtpFactory


def nothing(self):
    return None


class TestFtpFactory(unittest.TestCase):

    @patch('drb.drivers.ftp.DrbFtpNode._init_attr', new=nothing)
    def test_create(self):
        factory = DrbFtpFactory()
        node = factory.create('ftp://localhost:1026')
        self.assertIsInstance(node, (DrbFtpNode, DrbNode))
