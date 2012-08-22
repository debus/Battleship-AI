#! /usr/bin/python

import sys
import socket
import string
import os
import subprocess
import re
import threading

def Write( str, proc ):
    old_stdout = sys.stdout
    sys.stdout = proc.stdin
    print str
    sys.stdout = old_stdout
    return
def Read( proc ):
    old_stdin = sys.stdin
    sys.stdin = proc.stdout
    str = raw_input()
    sys.stdin = old_stdin
    return str

class irc_message:
    match_strings = (r"^([^ :]*) {0,1}:([^ ]+) {0,1}([^:]*):{0,1}([^\n]*)$", r"^([^ !]+)")
    compiled_regexes = (re.compile(match_strings[0]), re.compile(match_strings[1]) )

    def __init__(self, strang="", command="", sender="", msg_type="", recipient="", message="", extra_params=""):
        self.command = command
        self.sender = sender
        self.msg_type = msg_type
        self.recipient = recipient
        self.message = message
        self.extra_params = extra_params
        if(strang != None):
            self.parse_string(strang)
    def parse_string(self, strang):
        matches = irc_message.compiled_regexes[0].match(strang)
        if(matches == None):
            print "ERROR " + strang
            return self
        self.command = matches.group(1)
        self.sender = irc_message.compiled_regexes[1].match(matches.group(2)).group(1)
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

class irc_connection:
    def __init__(self, host="irc.freenode.net" , port=6667, nick=None, ident="BOT_IDENT", realname="dBOT", owner="Philipp McBadass", channels=("#battleship")):
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
    def join(self, channel):
        self.channels = [channel]
        self.joined = False
        while(not self.joined):
            self.s.send("JOIN " + self.channels[0] + " \n")
            buff = irc_connection.__receive_buffer_(self.s)
            lines = irc_connection.__split_lines_(buff)
            i = 0
            l = len(lines)
            while(i<l):
                print "<" + lines[i] + ">"
                msg = irc_message(strang=lines[i])
                if(msg.msg_type == "JOIN"):
                    print "JOINED " + channel
                    self.joined = True
                    break
                i += 1          
            if(i != l and self.joined == True):     
                self.cached_lines = lines[i+1:]
        return True
    @staticmethod
    def __receive_buffer_(sock, buffer_size=512):
        inp = sock.recv(buffer_size)
        while((len(inp)%buffer_size) == 0):
            inp += sock.recv(buffer_size) # recieve the server messages
        return inp
    @staticmethod
    def __split_lines_(inp):
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
        return irc_message(strang = self.get_next_line())
    def send_message(self, msg):
        self.s.send(msg.msg_type + " " + msg.recipient + " :" + msg.message + "\n")

def main(): 
    connection.connect(host="irc.freenode.net", port=6667)
    connection.register_nick("GHB578645")
    connection.register_ident(ident="GHB578645_BOT_IDENT", realname="GHB578645_BOT_REALNAME")
    connection.join("#battleship_testing")
    while True:
        line = connection.get_next_line()
        print "<" + line + ">"
        msg = irc_message(strang = line)
        if(not handle_message(msg, connection)):
            break
    return 0 #unreachable?

def handle_message(msg, connection):
    if(msg.command == "PING"):
        connection.s.send("PONG "+msg.sender+"\n")
        print "PONG "+msg.sender
        return True
    if(msg.message == "$4COCK" and connection.joined):
        connection.send_message(irc_message(msg_type = "PRIVMSG", recipient = msg.recipient, message = chr(1)+"ACTION Quitting!!!!"+chr(1)))
        connection.send_message(irc_message(msg_type = "QUIT", recipient=msg.recipient, message="QUITTING!!!!"))
        Write("[quit]", proc)
        return False
    if(connection.joined):
        Write("<[" + msg.msg_type + ":"  + msg.sender + ":"+ msg.recipient + ":" + msg.message + "]>", proc)
        return True


proc = subprocess.Popen(sys.argv[1], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
connection = irc_connection()
if __name__=="__main__":
    sys.exit(main())
