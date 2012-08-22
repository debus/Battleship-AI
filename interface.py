#! /usr/bin/python

import sys
import socket
import string
import os
import subprocess
import re
import threading
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


def Write( strang, proc ):
    old_stdout = sys.stdout
    sys.stdout = proc.stdin
    proc.stdin.write(strang)
    proc.stdin.flush()
    sys.stdout = old_stdout
    return
def Read( proc ):
    old_stdin = sys.stdin
    sys.stdin = proc.stdout
    str = raw_input()
    sys.stdin = old_stdin
    return str
def ReadNoWait( out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)

class irc_client_message(object):
    match_strings = (r"^([^ :]+) :([^:]+):(.*)$" , )
    compiled_regexes = (re.compile(match_strings[0]) ,)
    def __init__(self, strang=None, msg_type="PRIVMSG", recipient=None, params=None, message=None):
        self.msg_type = msg_type
        self.message = message
        self.params = params
        self.parsed = False
        if(strang != None):
            self.parsed = self.parse_string(strang)
    def parse_string(self, strang):
        print strang
        matches = irc_client_message.compiled_regexes[0].match(strang)
        if(matches == None or len(matches.groups("")) < 3):
            print "ERROR irc_client_message:<" + strang + ">"
            self.parsed = False
            return False
        groups = matches.groups("")
        self.msg_type = groups[0]
        params = groups[1].split(' ')
        self.recipient = params[0]
        self.params = params[1:]
        self.message = groups[2]
        self.parsed = True
        return True
class irc_server_message(object):
    match_strings = (r"^([^ :]*) {0,1}:([^ ]+) {0,1}([^:]*):{0,1}([^\n]*)$", r"^([^ !]+)")
    compiled_regexes = (re.compile(match_strings[0]), re.compile(match_strings[1]) )

    def __init__(self, strang=None, command="", sender="", msg_type="", recipient="", message="", extra_params=""):
        self.command = command
        self.sender = sender
        self.msg_type = msg_type
        self.recipient = recipient
        self.message = message
        self.extra_params = extra_params
        if(strang != None):
            self.parse_string(strang)
    def parse_string(self, strang):
        matches = irc_server_message.compiled_regexes[0].match(strang)
        if(matches == None):
            print "ERROR " + strang
            return self
        self.command = matches.group(1)
        self.sender = irc_server_message.compiled_regexes[1].match(matches.group(2)).group(1)
        params = matches.group(3).split(' ')
        length = len(params)
        if(length > 0):
            self.msg_type = params[0]
            if(length > 1):
                self.recipient = params[1]
                if(length > 2):
                    self.extra_params = params[2:length-1]
        self.message = matches.group(4)
        return self
class irc_connection(object):
    def __init__(self, host="irc.freenode.net" , port=6667, nick=None, ident="BOT_IDENT", realname="dBOT", owner="Philipp McBadass", channels=[]):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.owner = owner
        self.channels = channels
        self.s = socket.socket()
        self.joined = False
        self.cached_lines = None
    def connect(self, host=None, port=None):
        self.host = irc_connection.__merge_def_(host, self.host)
        self.port = irc_connection.__merge_def_(port, self.port)
        self.s.connect((self.host, self.port))
    def join(self, channel, key = ""):
        if(self.channels.count(channel) > 0):
            return True
        this_join = False
        while(not this_join):
            self.s.send("JOIN " + channel + " " + key + " \n")
            buff = irc_connection.__receive_buffer_(self.s)
            lines = irc_connection.__split_lines_(buff)
            i = 0
            l = len(lines)
            while(i<l):
                msg = irc_server_message(strang=lines[i])
                if(msg.msg_type == "JOIN"):
                    print "JOINED " + channel
                    this_join = True
                    break
                i += 1          
            if(i != l and this_join == True):
                self.channels.append(channel)     
                self.cached_lines = lines[i+1:]
        return True
    @staticmethod
    def __receive_buffer_(sock, buffer_size=512):
        inp = sock.recv(buffer_size)
        while((len(inp)%buffer_size) == 0):
            inp += sock.recv(buffer_size) # recieve the server messages
        return inp
    @staticmethod
    def __split_lines_(inp, print_lines=True):
        lines = inp.splitlines()
        l = len(lines)
        i = 1
        while (i < l):
            if(lines[i][0] != ":"):
                lines[i-1] = lines[i-1] + "\n" + lines[i]
                del(lines[i])
                l -= 1
                continue
            i += 1
        if(print_lines):
            for line in lines:
                print "<" + line + ">"
        return lines
    @staticmethod
    def __merge_def_(new=None, old=None):
        if(new == None):
            return old
        else:
            return new
    def get_next_line(self):
        line = None
        if(self.cached_lines != None and len(self.cached_lines) > 0):
            line = self.cached_lines[0:1][0]
            del(self.cached_lines[0])
            if(len(self.cached_lines) == 0):
                self.cached_lines = None
        else:
            lines = irc_connection.__split_lines_(irc_connection.__receive_buffer_(self.s))
            if(lines != None and len(lines) > 0):
                line = lines[0:1][0]
                self.cached_lines = lines[1:]
        return line
    def set_connection_password(self, password):
        self.s.send("PASS " + password + " \n")
    def register_nick(self, nick):
        self.nick = nick
        self.s.send("NICK " + nick + "\n")
        return True
    def register_ident(self, ident, realname):
        self.ident = ident
        self.realname = realname
        self.s.send("USER "+self.ident+" "+self.host+" NAME "+self.realname+"\n")
        return True
    def get_next_message(self):
        return irc_server_message(strang = self.get_next_line())
    def send_message(self, msg):
        self.s.send(msg.msg_type + " " + msg.recipient + " :" + msg.message + "\n")
    def quit(self,  message="", do_action=False, action="Quitting!!!"):
        if(do_action):
            for channel in self.channels:
                self.send_message(irc_server_message(msg_type="PRIVMSG", recipient=channel, message = chr(1)+"ACTION " + action + chr(1)))
        self.channels = []
        self.cached_lines = None
        self.s.send("QUIT " + message + " \n")
    def leave_channel(self, channel, message=""):
        if(self.channels.count(channel) > 0):
            self.channels.remove(channel)
            self.s.send("PART " + channel + " " + message + " \n")
    def leave_channels(self, channels, message=""):
        for channel in channels:
            self.leave_channel(channel, message)
    def register_service(self, info, distribution="*"):
        self.s.send("SERVICE " + self.nick + "  * " + distribution + " 0 0 :" + info + " \n")
class irc_server_thread(threading.Thread):
    def __init__(self, connection):
        self.connection = connection
        self.Dexecuting = False
        threading.Thread.__init__(self)
    def run(self):
        print "Server thread"
        self.Dexecuting = True
        while True:
            line = self.connection.get_next_line()
            msg = irc_server_message(strang = line)
            if(self.handle_server_message(msg) == False):
                self.Dexecuting = False
                print "/Server thread"
                return   
    def handle_server_message(self, msg):
        if(msg.command == "PING"):
            self.connection.s.send("PONG "+msg.sender+"\n")
            print "PONG "+msg.sender
            return True
        if(msg.message == "$4COCK"):
            self.connection.quit(do_action = True)
            Write("[quit]", proc)
            return False
        Write(msg.msg_type + ":"  + msg.sender + ":"+ msg.recipient + ":" + msg.message + "\n", proc)
        return True         
class irc_client_thread(threading.Thread):
    def __init__(self, connection, qu):
        self.connection = connection
        self.qu = qu
        threading.Thread.__init__(self)
    def run(self):
        print "client thread"
        while True:
            try:
                line = self.qu.get_nowait()
            except Empty:
                pass
            else:
                msg = irc_client_message(strang=line)
                connection.send_message(msg)
        print "/client thread"
class msg_read_thread(threading.Thread):
    def __init__(self, qu, out):
        self.qu = qu
        self.out = out
        threading.Thread.__init__(self)
    def run(self):
        while True:
            ReadNoWait(self.out, self.qu)

def main(): 
    connection.connect(host="irc.freenode.net", port=6667)
    connection.register_nick("GHB578645")
    connection.register_ident(ident="GHB578645_BOT_IDENT", realname="GHB578645_BOT_REALNAME")
    connection.join("#battleship_testing")
    qu = Queue()
    server_thread = irc_server_thread(connection)
    msg_thread = msg_read_thread(qu, proc.stdout)

    server_thread.daemon = True
    msg_thread.daemon = True
    server_thread.start()
    msg_thread.start()
    connection.register_service("This is a test of the service registration module, nothing to see here, move along.")
    while(server_thread.isAlive()):
        try:
            line = qu.get_nowait()
        except Empty:
            pass
        else:
            msg = irc_client_message(strang=line)
            connection.send_message(msg)
    print "/main"
    return 0

proc = subprocess.Popen(sys.argv[1], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
connection = irc_connection()
if __name__=="__main__":
    sys.exit(main())
