from django.conf import settings

import xmlrpclib
import lxml.html
import re
from StringIO import StringIO
from urllib2 import urlopen

PYPI_LIST_URL = "http://pypi.python.org/pypi?:action=browse&show=all&c=385"
PYPI_XML_URL = "http://pypi.python.org/pypi"

def get_release_list():
    f = urlopen(PYPI_LIST_URL)
    try:
        data = f.read()
    finally:
        f.close()

    releases = []
    tree = lxml.html.parse(StringIO(data))
    nodes = tree.xpath('//a')
    for node in nodes:
        m = re.match(r"^/pypi/([^/]+)/([^/]+)$", node.attrib.get('href', ''))
        if m:
            releases.append((m.group(1), m.group(2)))
    return releases

def get_info(package_name, version):
    client = xmlrpclib.ServerProxy(PYPI_XML_URL)
    return client.release_data(package_name, version)

