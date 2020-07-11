import xbmc, telnetlib

class telnet_control:

    def __init__(self, host=None, port=0):

        self.host = host
        self.port = port
        self.telnet_conn = telnetlib.Telnet(self.host,self.port)

    def login(self, user, password=""):
        self.telnet_conn.read_until("login: ")
        self.telnet_conn.write(user + "\r\n")
        self.telnet_conn.read_until("Password: ")
        self.telnet_conn.write(password + "\r\n")

    def server_start(self):
        self.telnet_conn.write("SmartHub_DS /mnt/cdrom\r\n")

    def server_stop(self):
        self.telnet_conn.write("killall SmartHub_DS \r\n")

    def exit(self):
        self.telnet_conn.write("vt100\r\n")

        self.telnet_conn.write("ls\r\n")
        self.telnet_conn.write("exit\r\n")
        xbmc.log(self.telnet_conn.read_all())
        self.telnet_conn.close()
