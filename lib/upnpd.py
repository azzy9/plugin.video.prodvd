#   Copyright 2014 Dan Krause
#   Has been modified
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import urllib2, urllib, re
import socket, httplib, StringIO
import xbmc
from urlparse import urlparse

class SSDPResponse(object):

    class _FakeSocket(StringIO.StringIO):
        def makefile(self, *args, **kw):
            return self

    def __init__(self, response):
        r = httplib.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self.location = r.getheader("location")
        self.domain = urlparse( r.getheader("location") ).hostname
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
        sock.sendto(message.format(*group, st=service, mx=mx), group)
        while True:
            try:
                response = SSDPResponse(sock.recv(1024))
                responses[response.location] = response
            except socket.timeout:
                break
    return responses.values()

#get the xml file
def XmlGet(url):
    response = urllib2.urlopen(url)
    xml = response.read()
    return xml

#parse xml to get the UUID
def UUIDGet(xml):
    match = re.search('<UDN>uuid:([a-z0-9-]+)</UDN>', xml)
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
    request = urllib2.Request(host + path, soap_body, headers)
    response = urllib2.urlopen(request)

    return response.read()
