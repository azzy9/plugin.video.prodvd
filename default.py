import sys, os, re
import xbmc, xbmcgui
import binascii, tempfile
import six

from six.moves import urllib
from lib import telnet_control, upnpd, ProDVD

addon_id='plugin.video.prodvd'
device_model = "[ODD] SmartHub 208BW"
ProDVDServer = False

ProDVDServerTest = False
#ProDVDServerTest = True
ProDVDSectorBuffer = 1000

#params being set
params = dict( urllib.parse.parse_qsl(sys.argv[2].replace('?','')) )
action = params.get('action')
fileid = params.get('fileid')

#method to start a ProDVD server
def ProDVD_start():

    #initiate ProDVDServer
    ProDVDServer = False

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
        match = re.findall(r'item(?:\s+)id="(?P<fileid>[^"]+)"(?:(?:.|\n|\r)+?)(?P<url>' + urllib.parse.urlparse( url ).scheme + "://" + urllib.parse.urlparse( url ).netloc + '[^"]+.vob)', soap)
        if match:
            xbmc.log(dvd_title)
            playlist_create(dvd_title, match)
            xbmc.log("ProDVD_play RAN!!!!!!")

    return UUID

def playlist_create( dvd_title, list ):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for fileid, url in list:
        listitem = xbmcgui.ListItem(dvd_title)
        listitem.setInfo( type="Video", infoLabels={ "Title": dvd_title } )
        if ProDVDServerTest == True :
            url = "plugin://" + addon_id + "/?action=play_file&fileid=" + fileid
            xbmc.executebuiltin('RunPlugin(%s)' % url)
            return

        playlist.add( urllib.parse.unquote_plus( url ), listitem)

    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

def play_file( fileid ):
    xbmc.log("Play File Test Start")
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
        UUID = upnpd.UUIDGet(upnpd.XmlGet(ProDVDServer))
        if UUID != False:

            fd, path = tempfile.mkstemp()

            with os.fdopen(fd, 'wb') as tmp:

                for x in range(0, 20):
                    sectors = ProDVD.readDataByFileOffset(UUID, ProDVDServer, fileid, str( ProDVDSectorBuffer * x ), str( ( ProDVDSectorBuffer * ( x + 1 ) ) - 1 ))
                    binary_string = binascii.unhexlify(sectors)
                    # do stuff with temp file
                    tmp.write(binary_string)

                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                listitem = xbmcgui.ListItem(fileid)
                xbmc.log( str( fd ), xbmc.LOGWARNING )
                xbmc.log( str( path ), xbmc.LOGWARNING )
                playlist.add( str( path ), listitem)
                xbmcPlayer = xbmc.Player()
                xbmcPlayer.play(playlist)
                #xbmc.log(sectors, xbmc.LOGWARNING)

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

if action == 'play_file':
    play_file( urllib.parse.unquote_plus( fileid ) )
else:
    #let's start
    main()
