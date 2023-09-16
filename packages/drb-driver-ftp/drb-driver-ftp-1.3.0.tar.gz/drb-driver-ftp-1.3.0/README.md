# Ftp driver
This drb-driver-ftp module implements ftp protocol access with DRB data model.

## Ftp Factory and Ftp Node
The module implements the factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The driver name is `ftp`.<br/>
The factory class is encoded into `drb.driver.ftp`.<br/>
The ftp signature id is  `d61c923a-5f1b-11ec-bf63-0242ac130002`<br/>

The Ftp can be instantiated from an uri. The `ParsedPath` class provided in drb core module can help to manage these inputs.

## Using this module
The project is present in https://www.pypi.org service. it can be freely 
loaded into projects with the following command line:

```commandline
pip install drb-driver-ftp
```
## Access Data
`DrbFtpNode` manages the ftp protocol to access remote data. The construction
parameter is an url with the host and an authentication object. Both FTP and FTPS are supported. They allow access the
ftp content.

```python
from drb.drivers.ftp import DrbFtpNode
from requests.auth import HTTPBasicAuth

node = DrbFtpNode("URL", "HOST", auth=HTTPBasicAuth("username", "password"))
```
Ftp protocol allows navigation inside the ftp server. To do so this 
driver is able to provide children of the same FTP type.

## Authentication
FTP node is able to manage Basic authentication based on username and 
password, as well as TLS ans SSL authentication by using the `FTP_TLS.auth()`.<br/>
This method set up a secure control connection.
By default, the node will try to connect with the SSL protocol if you want to change protocol you have to give
You can find all the version of TLS and SSL supported here https://docs.python.org/3/library/ftplib.html#ftplib.FTP_TLS.ssl_version

## Limitations

None

## Documentation

The documentation of this driver can be found here https://drb-python.gitlab.io/impl/ftp