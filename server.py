# coding: utf-8

import io
from wsgiref.simple_server import make_server

from bottle import app, route, request, HTTPResponse
import xbmc

import binascii

from lib.constants import *
from lib import upnpd, ProDVD

PRODVD_SERVER = False

def prodvd_find( retries=1 ):

    """ method to find a ProDVD server """

    #find if an instance of the ProDVD server has been started
    upnp_found = upnpd.discover("urn:schemas-upnp-org:service:ProDVDContentDirectory:1", 5, retries)

    if upnp_found:
        for upnp in upnp_found:
            xbmc.log(upnp.location)
            return upnp.location
    else :
        return False

@route('/stream/{file_id}')
def stream(file_id):

    prodvd_find()

    binary_string = b''

    # get range_header to know what bytes to request
    range_header = request.get_header('Range')
    range_header = range_header.replace( 'bytes=', '' )
    if '-' in range_header:
        ranges = range_header.split( '-' )

        uuid = upnpd.UUIDGet(upnpd.XmlGet(PRODVD_SERVER))
        if uuid is not False:

            sectors = ProDVD.readDataByFileOffset(
                uuid, PRODVD_SERVER, file_id,
                ranges[0],
                ranges[1]
            )
            binary_string = binascii.unhexlify(sectors)

    payload = io.BytesIO(binary_string)

    # Analyze range_header then do payload.seek() to the necessary position
    response = HTTPResponse(body=payload)
    response.add_header('Content-Type', 'video/mp4')
    response.add_header('Accept-Ranges', 'bytes')

    # Add the necessary Content-Range and Content-Length headers
    return response


httpd = make_server('127.0.0.1', 8765, app)
monitor = xbmc.Monitor()
while not monitor.abortRequested():
    httpd.handle_request()
