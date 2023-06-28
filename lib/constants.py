import sys
import xbmcaddon

ADDON = xbmcaddon.Addon()

PLUGIN_ID = int(sys.argv[1])
PLUGIN_URL = sys.argv[0]
PLUGIN_NAME = PLUGIN_URL.replace("plugin://","")

DEVICE_MODEL = "[ODD] SmartHub 208BW"
