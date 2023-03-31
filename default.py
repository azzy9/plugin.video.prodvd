""" Main code for running plugin"""
import sys
import os
import re

import binascii
import tempfile

import xbmc
import xbmcgui

import six

from six.moves import urllib
from lib import telnet_control, upnpd, ProDVD

ADDON_ID='plugin.video.prodvd'
DEVICE_MODEL = "[ODD] SmartHub 208BW"
PRODVD_SERVER = False

PRODVD_SERVER_TEST = False
#PRODVD_SERVER_TEST = True
PRODVD_SECTOR_BUFFER = 1000

#params being set
params = dict( urllib.parse.parse_qsl(sys.argv[2].replace('?','')) )
action = params.get('action')
fileid = params.get('fileid')

def prodvd_start():

    """ method to start a ProDVD server """

    #initiate PRODVD_SERVER
    PRODVD_SERVER = False

    #use SDPP to find a server to start
    xbmc.log("Starting UPNP search")
    upnp_found = upnpd.discover("urn:schemas-upnp-org:device:MediaServer")

    xbmc.log("Looping Results")
    if upnp_found:
        for upnp in upnp_found:
            #not sure if I like how it is doing this, but it work
            if DEVICE_MODEL in upnpd.XmlGet(upnp.location):
                #we found what we are looking for
                PRODVD_SERVER = upnp.domain
                break

    if PRODVD_SERVER is not False:
        #start the server
        tnc = telnet_control.telnet_control(PRODVD_SERVER, 23)
        tnc.login("root")
        #start the UPNP ProDVD server
        tnc.server_start()
        tnc.exit()

def prodvd_find( retries=1 ):

    """ method to find a ProDVD server """

    #find if an instance of the ProDVD server has been started
    upnp_found = upnpd.discover("urn:schemas-upnp-org:service:ProDVDContentDirectory:1", 5, retries)

    if upnp_found:
        xbmc.log("ProDVD server found")
        for upnp in upnp_found:
            xbmc.log(upnp.location)
            return upnp.location
    else :
        return False

def prodvd_play( url ):

    """ method to play from the ProDVD server """

    uuid = upnpd.UUIDGet(upnpd.XmlGet(url))
    if uuid is not False:

        dvd_title = ProDVD.getMediaName(uuid, url)

        soap = ProDVD.browse(uuid, url)
        match = re.findall(r'item(?:\s+)id="(?P<fileid>[^"]+)"(?:(?:.|\n|\r)+?)(?P<url>'
                           + urllib.parse.urlparse( url ).scheme
                           + "://" + urllib.parse.urlparse( url ).netloc + '[^"]+.vob)', soap)
        if match:
            xbmc.log(dvd_title)
            playlist_create(dvd_title, match)
            xbmc.log("ProDVD_play RAN!!!!!!")

    return uuid

def playlist_create( dvd_title, play_list ):

    """ Method to create playlist """

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for file_id, url in play_list:
        listitem = xbmcgui.ListItem(dvd_title)
        listitem.setInfo( type="Video", infoLabels={ "Title": dvd_title } )
        if PRODVD_SERVER_TEST is True :
            url = "plugin://" + ADDON_ID + "/?action=play_file&fileid=" + file_id
            xbmc.executebuiltin('RunPlugin(%s)' % url)
            return

        playlist.add( urllib.parse.unquote_plus( url ), listitem)

    xbmc_player = xbmc.Player()
    xbmc_player.play(playlist)

def play_file( file_id ):

    """ Play Files (test) """

    xbmc.log("Play File Test Start")

    PRODVD_SERVER = prodvd_find()

    if PRODVD_SERVER is False:
        prodvd_start()
        #let's try this again
        #increase retries as server just started
        #may need some time to warm up
        PRODVD_SERVER = prodvd_find(3)

    if PRODVD_SERVER is False:
        #oh no!
        xbmc.log("ProDVD server can not be found / started")
    else:
        uuid = upnpd.UUIDGet(upnpd.XmlGet(PRODVD_SERVER))
        if uuid is not False:

            fdir, path = tempfile.mkstemp()

            with os.fdopen(fdir, 'wb') as tmp:

                for b_num in range(0, 20):
                    sectors = ProDVD.readDataByFileOffset(
                        uuid, PRODVD_SERVER, file_id,
                        str( PRODVD_SECTOR_BUFFER * b_num ),
                        str( ( PRODVD_SECTOR_BUFFER * ( b_num + 1 ) ) - 1 )
                    )
                    binary_string = binascii.unhexlify(sectors)
                    # do stuff with temp file
                    tmp.write(binary_string)

                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                listitem = xbmcgui.ListItem(file_id)
                xbmc.log( str( fdir ), xbmc.LOGWARNING )
                xbmc.log( str( path ), xbmc.LOGWARNING )
                playlist.add( str( path ), listitem)
                xbmc_player = xbmc.Player()
                xbmc_player.play(playlist)
                #xbmc.log(sectors, xbmc.LOGWARNING)

def main():

    """ Main method """

    PRODVD_SERVER = prodvd_find()

    if PRODVD_SERVER is False:
        prodvd_start()
        #let's try this again
        #increase retries as server just started
        #may need some time to warm up
        PRODVD_SERVER = prodvd_find(3)
    if PRODVD_SERVER is False:
        #oh no!
        xbmc.log("ProDVD server can not be found / started")
    else:
        #all is fine now, phew
        prodvd_play(PRODVD_SERVER)

if action == 'play_file':
    play_file( urllib.parse.unquote_plus( fileid ) )
else:
    #let's start
    main()
