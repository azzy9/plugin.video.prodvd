import re
import socket
import xbmc
import requests
import six
import io

if six.PY3:
    import http.client
else:
    import httplib

from six.moves import urllib
from six.moves import urllib_parse

class SSDPResponse(object):

    class _FakeSocket(io.BytesIO):
        def makefile(self, *args, **kw):
            return self

    def __init__(self, response):
        if six.PY3:
            r = http.client.HTTPResponse(self._FakeSocket(response))
        else:
            r = httplib.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self.location = r.getheader("location")
        self.domain = urllib_parse.urlparse( r.getheader("location") ).hostname
        self.usn = r.getheader("usn")
        self.st = r.getheader("st")
        self.cache = r.getheader("cache-control").split("=")[1]

    def __repr__(self):
        return "<SSDPResponse({location}, {st}, {usn})>".format(**self.__dict__)

def discover(service, timeout=5, retries=1, mx=3):
    group = ("239.255.255.250", 1900)
    message = "\r\n".join([
        'M-SEARCH * HTTP/1.1',
        'HOST: {0}:{1}',
        'MAN: "ssdp:discover"',
        'ST: {st}','MX: {mx}','',''])
    socket.setdefaulttimeout(timeout)
    responses = {}

    for _ in range(retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message.format(*group, st=service, mx=mx).encode('utf-8'), group)
        while True:
            try:
                response = SSDPResponse(sock.recv(1024))
                responses[response.location] = response
            except socket.timeout:
                break
    return responses.values()

#get the xml file
def XmlGet(url):
    response = urllib.request.urlopen(url)
    return str(response.read())

#parse xml to get the UUID
def UUIDGet(xml):
    match = re.search(r'<UDN>uuid:([a-z0-9-]+)</UDN>', xml)
    if match:
        return match.group(1)

    return False;

#convert an assoc array to xml
def argsXML( args ):
    xml = "";
    for key in args.keys():
        xml += "<" + key + ">" + args[key] + "</" + key + ">"
    return xml

#make a soap call
def SOAPCall( host, path, urn, action, soap_body = "" ):

    soap_body = '''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body><u:''' + action + ''' xmlns:u="''' + urn + '''">''' + soap_body + '''</u:''' + action + '''></s:Body>
</s:Envelope>'''

    headers = {
        'POST': path + " HTTP/1.1",
        'SOAPACTION': urn + "#" + action,
        'Content-Length': len(soap_body),
        'Content-Type': 'text/xml',
        'Content-Encoding': 'utf-8',
        'HOST': host,
        'Connection': 'Keep-Alive',
    }

    xbmc.log(soap_body)
    xbmc.log(host + path)
    request = urllib.request.Request(host + path, soap_body.encode("utf-8"), headers)
    response = urllib.request.urlopen(request)

    return response.read()
