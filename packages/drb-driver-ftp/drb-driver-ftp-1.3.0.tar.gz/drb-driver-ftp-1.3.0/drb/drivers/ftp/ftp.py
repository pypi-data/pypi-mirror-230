import ftplib
import io
from urllib.parse import urljoin
import ssl
from urllib.parse import urlparse
from ftplib import FTP, error_perm, FTP_TLS
from typing import Any, List

import keyring
from deprecated.classic import deprecated
from drb.core import DrbNode, ParsedPath, DrbFactory
from drb.nodes.abstract_node import AbstractNode

from requests.auth import HTTPBasicAuth

from drb.exceptions.ftp import DrbFtpNodeException


def check_args(*args):
    return len(args) > 0 and isinstance(
        args[0],
        int
    ) and args[0] > 0


def check_response(resp: str):
    if int(resp[0]) >= 3:
        raise DrbFtpNodeException(f'ERROR: {resp}')


class Download(io.BytesIO):

    def __init__(self, path: str, chunk_size: int, ftp: FTP):
        self._chunk_size = chunk_size
        self._ftp = ftp
        self._path = path
        self._buff = bytearray(0)
        self.__res = None
        super().__init__(self.__res)

    def download(self, read: int = None):
        """
        Download all the file you want to download or if you give
        a limit to read in argument,
        juste download part of the file.
        :param read: int
        :return: The status code of the download
        """
        self._ftp.voidcmd('TYPE I')
        with self._ftp.transfercmd('RETR %s' % self._path, None) as conn:
            while 1:
                if read is None:
                    data = conn.recv(self._chunk_size)
                else:
                    data = conn.recv(read)
                    self._buff.extend(data)
                    break
                if not data:
                    break
                self._buff.extend(data)

        return self._ftp.voidresp()

    def read(self, *args, **kwargs):
        if not check_args(*args):
            resp = self.download()
        else:
            resp = self.download(args[0])
        check_response(resp)
        return self._buff


class FtpConnection:
    """
    This class use the singleton pattern to provide too
    much connection to the ftp server
    """
    ftp = None

    def __new__(cls,
                auth: HTTPBasicAuth = None,
                path: str = None,
                host: str = '',
                protocol=None):
        if cls.ftp is None:
            parsed_uri = urlparse(path)
            context = None
            if protocol is not None:
                context = ssl.SSLContext(protocol=protocol)
            tmp = parsed_uri.netloc.split(':')
            cls.ftp = FTP_TLS(context=context, host=host)
            cls.ftp.connect(tmp[0], int(tmp[1]))
            try:
                cls.ftp.auth()
            except error_perm:
                cls.ftp.close()
                cls.ftp = FTP(host)
                cls.ftp.connect(tmp[0], int(tmp[1]))
            if auth is not None:
                cls.ftp.login(auth.username, auth.password)
        return cls.ftp


class DrbFtpNode(AbstractNode):
    ftp = None
    __attributes = [
        'directory', 'size', 'modified']

    def __init__(self, path, host: str = '',
                 parent: DrbNode = None,
                 auth: HTTPBasicAuth = None, protocol=None):
        super().__init__()
        self._original_path = path
        self.name = urlparse(self._original_path).path.split('/')[-1]
        self._host = host
        self.parent = parent
        self._protocol = protocol
        self.add_impl(io.BytesIO, self._to_stream)
        if parent:
            self.ftp = parent.ftp
        self._children: List[DrbNode] = None
        self._auth = auth
        self._init_attr()

    def _init_attr(self):
        try:
            self @= (self.__attributes[0], not self.is_file(self.path.path))

            if self.is_file(self.path.path):
                self.ftp.voidcmd('TYPE I')
                self @= (self.__attributes[1],
                         self.ftp.size(self.path.path))
            else:
                self @= (self.__attributes[1], 0)

            self @= (self.__attributes[2],
                     self.get_modification_date(self.path.path))
        except (ftplib.Error, AttributeError) as e:
            raise DrbFtpNodeException(
                f'Error occurred when retrieving attributes: {e}')

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    def auth(self) -> HTTPBasicAuth:
        if self._auth is None:
            credential = keyring.get_credential(self.path.path)
            if credential is not None:
                self._auth = HTTPBasicAuth(
                    credential.username,
                    credential.password
                )
        return self._auth

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._original_path)

    def is_file(self, filename):
        """
        Check if the file given in argument is not a folder.
        :param filename: str
        :return: True if the filename given in argument is a file
        False otherwise
        """
        self.ftp = FtpConnection(self.auth, self._original_path, self._host)
        current = self.ftp.pwd()
        try:
            self.ftp.cwd(filename)
        except error_perm:
            self.ftp.cwd(current)
            return True
        self.ftp.cwd(current)
        return False

    def check_file_exist(self, filename):
        self.ftp = FtpConnection(self.auth, self._original_path, self._host)
        return filename in self.ftp.nlst()

    def get_modification_date(self, file_name):
        self.ftp = FtpConnection(self.auth, self._original_path, self._host)
        line = []
        self.ftp.dir(file_name, line.append)
        tokens = line[0].split(maxsplit=9)
        return tokens[5] + " " + tokens[6] + " " + tokens[7]

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        self.ftp = FtpConnection(self.auth, self._original_path, self._host)
        if self._children is None:
            self._children = []
            if not self.is_file(self.path.path):
                sorted_child_names = sorted(self.ftp.nlst(self.path.path))
                for filename in sorted_child_names:
                    child = DrbFtpNode(
                        urljoin(self._original_path + "/", filename),
                        parent=self,
                        auth=self.auth)
                    self._children.append(child)
        return self._children

    def close(self) -> None:
        if self.ftp is not None:
            self.ftp.close()

    @staticmethod
    def _to_stream(node: DrbNode, **kwargs) -> io.BytesIO:
        if not isinstance(node, DrbFtpNode):
            raise TypeError(f'Invalid node type: {type(node)}')
        node.ftp = FtpConnection(node.auth, node._original_path, node._host)
        return Download(node.path.path,
                        kwargs.get('chunk_size', 12000),
                        node.ftp)


class DrbFtpFactory(DrbFactory):
    @staticmethod
    def _create_from_uri_of_node(node: DrbNode):
        if isinstance(node, DrbFtpNode):
            return node
        uri = node.path.name
        return DrbFtpNode(uri)

    def _create(self, node: DrbNode) -> DrbNode:
        return self._create_from_uri_of_node(node)
