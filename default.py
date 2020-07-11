import sys, os, re
import urlparse
import xbmc,xbmcaddon,xbmcgui,xbmcplugin
from lib import telnet_control, upnpd
from addon.common.addon import Addon

addon_id='plugin.video.prodvd'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = Addon(addon_id, sys.argv)
addon_name = selfAddon.getAddonInfo('name')
ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ICON       = ADDON.getAddonInfo('icon')
FANART     = ADDON.getAddonInfo('fanart')
VERSION    = ADDON.getAddonInfo('version')

device_model = "[ODD] SmartHub 208BW";
ProDVDServer = False

#method to start a ProDVD server
def ProDVD_start():

    #use SDPP to find a server to start
    xbmc.log("Starting UPNP search")
    UPNP_found = upnpd.discover("urn:schemas-upnp-org:device:MediaServer")

    xbmc.log("Looping Results")
    if UPNP_found:
        for upnp in UPNP_found:
            #not sure if I like how it is doing this, but it work
            if device_model in upnpd.XmlGet(upnp.location):
                #we found what we are looking for
                ProDVDServer = upnp.domain
                break
 
    if ProDVDServer != False:
        #start the server
        tnc = telnet_control.telnet_control(ProDVDServer,23)
        tnc.login("root")
        #start the UPNP ProDVD server
        tnc.server_start()
        tnc.exit()

#method to find a ProDVD server
def ProDVD_find( retries=1 ):
    #find if an instance of the ProDVD server has been started
    UPNP_found = upnpd.discover("urn:schemas-upnp-org:service:ProDVDContentDirectory:1", 5, retries)

    if UPNP_found:
        xbmc.log("ProDVD server found")
        for upnp in UPNP_found: 
            xbmc.log(upnp.location)
            return upnp.location
    else :
        return False

#method to play from the ProDVD server
def ProDVD_play( url ):

    UUID = upnpd.UUIDGet(upnpd.XmlGet(url))
    if UUID != False:
        soap_body = '''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<u:Browse xmlns:u="urn:schemas-upnp-org:service:ProDVDContentDirectory:1"><ObjectID>0/video_ts</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter></Filter><StartingIndex>0</StartingIndex><RequestedCount>0</RequestedCount><SortCriteria></SortCriteria></u:Browse>
</s:Body>
</s:Envelope>'''
        Soap = upnpd.SOAPCall( urlparse.urlparse( url ).scheme + "://" + urlparse.urlparse( url ).netloc, "/ProDVDContentDirectory/" + UUID + "/control.xml", "Browse", soap_body )
        match = re.findall('(' + urlparse.urlparse( url ).scheme + "://" + urlparse.urlparse( url ).netloc + '[^"]+.vob)', Soap)
        if match:
            playlist_create(match)
            xbmc.log("ProDVD_play RAN!!!!!!")
    return UUID

def playlist_create( list ):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for url in list:
        listitem = xbmcgui.ListItem("Movie")
        listitem.setInfo( type="Video", infoLabels={ "Title": "Movie" } )
        playlist.add(url)

    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

def main():
    ProDVDServer = ProDVD_find()

    if ProDVDServer == False:
        ProDVD_start()
        #let's try this again
        #increase retries as server just started
        #may need some time to warm up
        ProDVDServer = ProDVD_find(3)
    if ProDVDServer == False:
        #oh no!
        xbmc.log("ProDVD server can not be found / started")
    else:
        #all is fine now, phew
        ProDVD_play(ProDVDServer)

#let's start
main()
