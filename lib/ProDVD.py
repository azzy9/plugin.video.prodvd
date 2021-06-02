#ProDVD - methods to make SOAP calls to the ProDVD UPNP servers

import six, re

from lib import upnpd
from six.moves import urllib

#make the SOAP call to the server
def serverCall(UUID, url, dir, URN, action, soap_body = ""):
    return str( upnpd.SOAPCall( urllib.parse.urlparse( url ).scheme + "://" + urllib.parse.urlparse( url ).netloc, "/" + dir + "/" + UUID + "/control.xml", URN, action, soap_body ) )

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
    return connectionManagerServerCall(UUID, url, r"GetCurrentConnectionInfo")

def getProtocolInfo(UUID, url):
    return connectionManagerServerCall(UUID, url, r"GetProtocolInfo")

def getCurrentConnectionIDs(UUID, url):
    return connectionManagerServerCall(UUID, url, r"GetCurrentConnectionIDs")


#=DVD manager server calls=

def getFileLocation(UUID, url, FileID = "0/video_ts/video_ts.vob"):
    args = {
        "FileID": FileID
    }
 
    r = re.search(r"<Result>([^<]+)</Result>", dvdManagerServerCall(UUID, url, r"GetFileLocation", upnpd.argsXML(args)))
    return r.group(1) if r else ""

def getTitleKey(UUID, url, FileID = "0/video_ts/video_ts.vob"):
    args = {
        "FileID": FileID
    }

    r = re.search(r"<Result>([^<]+)</Result>", dvdManagerServerCall(UUID, url, r"GetTitleKey", upnpd.argsXML(args)))
    return r.group(1) if r else ""

def getPlayerRegion(UUID, url):
    r = re.search(r"<Result>R:([^<]+)\s+C:(?:[0-9])</Result>", dvdManagerServerCall(UUID, url, r"GetPlayerRegion"))
    region_text = r.group(1) if r else False
    if region_text:
        #reverse, turn it into a int, then count the amount of 0's it has, add 1 to get it's region
        return str(int( region_text.replace(",", "")[::-1] )).count('0') + 1
    else:
        return 0

def getActiveConnections(UUID, url):
    return dvdManagerServerCall(UUID, url, r"GetActiveConnections")

def getMediaName(UUID, url):
    r = re.search(r"<Result>([^<]+)</Result>", dvdManagerServerCall(UUID, url, r"GetMediaName"))
    return r.group(1) if r else ""

def setPlayerRegion(UUID, url, RegionNum = "2"):
    args = {
        "RegionNum": RegionNum
    }

    return dvdManagerServerCall(UUID, url, r"SetPlayerRegion", upnpd.argsXML(args))

#this is the method we need to look at to get the dvd's data
def readDataByFileOffset(UUID, url, FileID = "0/video_ts/video_ts.vob", startSector = "0", endSector = "2"):
    args = {
        "FileID": FileID,
        "startSector": startSector,
        "endSector": endSector
    }

    r = re.search(r"<Result>(?:[0-9]):([^<]+)</Result>", dvdManagerServerCall(UUID, url, r"readDataByFileOffset", upnpd.argsXML(args)))
    #just testing??? maybe 000001ba440004 is used to seperate sectors
    return r.group(1).replace( "000001ba440004", "" ) if r else ""
