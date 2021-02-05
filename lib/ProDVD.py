#ProDVD - methods to make SOAP calls to the ProDVD UPNP servers

import six, re

from lib import upnpd
from six.moves import urllib_parse

#make the SOAP call to the server
def serverCall(UUID, url, dir, URN, action, soap_body = ""):
    return str( upnpd.SOAPCall( urllib_parse.urlparse( url ).scheme + "://" + urllib_parse.urlparse( url ).netloc, "/" + dir + "/" + UUID + "/control.xml", URN, action, soap_body ) )

#calls to the 3 different UPNP server instances
def contentServerCall(UUID, url, action, soap_body = ""):
    return serverCall( UUID, url, "ProDVDContentDirectory", "urn:schemas-upnp-org:service:ProDVDContentDirectory:1", action, soap_body )

def connectionManagerServerCall(UUID, url, action, soap_body = ""):
    return serverCall( UUID, url, "ProDVDConnectionManager", "urn:schemas-upnp-org:service:ProDVDConnectionManager:1", action, soap_body )

def dvdManagerServerCall(UUID, url, action, soap_body = ""):
    return serverCall( UUID, url, "DvdManager", "urn:schemas-upnp-org:service:DvdManager:1", action, soap_body )


#=content server calls=

def browse(UUID, url):
    args = {
        "ObjectID": "0/video_ts",
        "BrowseFlag": "BrowseDirectChildren",
        "Filter": "",
        "StartingIndex": "0",
        "RequestedCount": "0",
        "SortCriteria": ""
    }

    return contentServerCall(UUID, url, "Browse", upnpd.argsXML(args))

def getSortCapabilities(UUID, url):
    return contentServerCall(UUID, url, "GetSortCapabilities")

def getSystemUpdateID(UUID, url):
    return contentServerCall(UUID, url, "GetSystemUpdateID")

def getSearchCapabilities(UUID, url):
    return contentServerCall(UUID, url, "GetSearchCapabilities")

def search(UUID, url):
    args = {
        "ObjectID": "0/video_ts",
        "BrowseFlag": "BrowseDirectChildren",
        "Filter": "",
        "StartingIndex": "0",
        "RequestedCount": "0",
        "SortCriteria": ""
    }

    return contentServerCall(UUID, url, "Search", upnpd.argsXML(args))


#=connection manager server calls=

def getCurrentConnectionInfo(UUID, url):
    return connectionManagerServerCall(UUID, url, "GetCurrentConnectionInfo")

def getProtocolInfo(UUID, url):
    return connectionManagerServerCall(UUID, url, "GetProtocolInfo")

def getCurrentConnectionIDs(UUID, url):
    return connectionManagerServerCall(UUID, url, "GetCurrentConnectionIDs")


#=DVD manager server calls=

def getFileLocation(UUID, url, FileID = "0/video_ts/video_ts.vob"):
    args = {
        "FileID": FileID
    }
 
    return dvdManagerServerCall(UUID, url, "GetFileLocation", upnpd.argsXML(args))

def getTitleKey(UUID, url, FileID = "0/video_ts/video_ts.vob"):
    args = {
        "FileID": FileID
    }

    return dvdManagerServerCall(UUID, url, "GetTitleKey", upnpd.argsXML(args))

def getPlayerRegion(UUID, url):
    return dvdManagerServerCall(UUID, url, "GetPlayerRegion")

def getActiveConnections(UUID, url):
    return dvdManagerServerCall(UUID, url, "GetActiveConnections")

def getMediaName(UUID, url):
    r = re.search(r"<Result>([^<]+)</Result>", dvdManagerServerCall(UUID, url, "GetMediaName"))
    return r.group(1) if r else ""

def setPlayerRegion(UUID, url, RegionNum = "2"):
    args = {
        "RegionNum": RegionNum
    }

    return dvdManagerServerCall(UUID, url, "SetPlayerRegion", upnpd.argsXML(args))

#this is the method we need to look at to get the dvd's data
def readDataByFileOffset(UUID, url, FileID = "0/video_ts/video_ts.vob", startSector = "0", endSector = "2"):
    args = {
        "FileID": FileID,
        "startSector": startSector,
        "endSector": endSector
    }

    return dvdManagerServerCall(UUID, url, "readDataByFileOffset", upnpd.argsXML(args))
