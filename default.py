""" Main code for running plugin """

import sys
import os
import re

import binascii
import tempfile

import xbmc
import xbmcgui
import xbmcplugin

import six

from six.moves import urllib
from lib import telnet_control, upnpd, ProDVD
from lib.constants import *
from lib.general import *

PRODVD_SERVER = False

# if we are testing
PRODVD_SERVER_TEST = ADDON.getSetting('is_testing') == 'true'
# sector buffer amount
PRODVD_SECTOR_BUFFER = int( ADDON.getSetting('sector_buffer') )

PLUGIN_ID = int(sys.argv[1])

#params being set
params = dict( urllib.parse.parse_qsl(sys.argv[2].replace('?','')) )
action = params.get('action')
fileid = params.get('fileid')

def main_menu():

    """ The main menu for the plugin """

    xbmcplugin.addDirectoryItem(PLUGIN_ID, build_url({'action':'main'}), xbmcgui.ListItem('Play DVD'), True)
    xbmcplugin.addDirectoryItem(PLUGIN_ID, build_url({'action':'settings'}), xbmcgui.ListItem('Settings'), True)

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
            url = build_url({'action':'play_file', 'fileid':file_id})
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

def settings():

    """ method to open plugin settings """

    ADDON.openSettings()

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

if action == 'main':
    main()
elif action == 'play_file':
    play_file( urllib.parse.unquote_plus( fileid ) )
elif action == 'settings':
    settings()
else:
    #let's start
    main_menu()
