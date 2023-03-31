""" Telnet control methods """
import xbmc
import telnetlib

class telnet_control:

    def __init__(self, host=None, port=0):

        self.host = host
        self.port = port
        self.telnet_conn = telnetlib.Telnet(self.host,self.port)

    def login(self, user, password=""):

        """ Method to login to telnet server """

        self.telnet_conn.read_until(b"login: ")
        self.telnet_conn.write(user.encode('ascii') + b"\r\n")
        self.telnet_conn.read_until(b"Password: ")
        self.telnet_conn.write(password.encode('ascii') + b"\r\n")

    def server_start(self):

        """ Method to start the ProDVD server via telnet """

        self.telnet_conn.write(b"SmartHub_DS /mnt/cdrom\r\n")

    def server_stop(self):

        """ Method to stop the ProDVD server via telnet """

        self.telnet_conn.write(b"killall SmartHub_DS \r\n")

    def exit(self):

        """ Method to exit the telnet server """

        self.telnet_conn.write(b"vt100\r\n")

        self.telnet_conn.write(b"ls\r\n")
        self.telnet_conn.write(b"exit\r\n")
        xbmc.log(str(self.telnet_conn.read_all()))
        self.telnet_conn.close()
