import sys, os, re
import urlparse
import xbmc,xbmcaddon,xbmcgui,xbmcplugin
import urllib
from lib import telnet_control, upnpd, ProDVD
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

        dvd_title = ProDVD.getMediaName(UUID, url)

        soap = ProDVD.browse(UUID, url)
        match = re.findall('(' + urlparse.urlparse( url ).scheme + "://" + urlparse.urlparse( url ).netloc + '[^"]+.vob)', soap)
        if match:
            #check 2nd url, as the first track usually at least returns something
            if urllib.urlopen(match[2]).getcode() == 200:
                playlist_create(dvd_title, match)
                xbmc.log("ProDVD_play RAN!!!!!!")
            else :
                xbmc.log("Method failed, attempting via soap (Experimental)")
    return UUID

def playlist_create( dvd_title, list ):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for url in list:
        listitem = xbmcgui.ListItem(dvd_title)
        listitem.setInfo( type="Video", infoLabels={ "Title": dvd_title } )
        playlist.add(url, listitem)

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
