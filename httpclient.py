#!/usr/bin/env python
# Copyright 2013 Abram Hindle
# Copyright 2014 Joshua Dunsmuir
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
            
    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    def get_code(self, data):
        broken = data.split()
        print broken[1]
        return int(broken[1])

    def get_headers(self,data):
        first = data.split("//")
        if len(first) > 1:
            second = first[1].split("/")
            setpath = first[1]
        else:
            second = first[0].split("/")
            setpath = first[0]
        host = second[0]
        if len(second) > 1:
            path = setpath[len(host):]
        else:
            path = "/"
        parts = [path, host]
        return parts

    def get_body(self, data):
        broken = data.split("\r")
        body = ""
        check = False
        for line in broken:
            if line == "\n":
                check = True
            if check:
                body = body + line
        return body[2:]

    def get_port(self, data):
        parts = data.split(":")
        if len(parts) < 1:
            return parts
        else:
            parts.insert(1, 80)
        return parts
    
    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        parts = self.get_headers(url)
        path = parts[0]
        host = self.get_port(parts[1])
        if args != None:
            encargs = urllib.urlencode(args)
            path = path + "?" + encargs
        request = "GET " + path + " HTTP/1.1\r\nHost:" + parts[1] + "\r\nAccept:*/*\r\n\r\n"
        sock = self.connect(host[0], host[1])
        sock.sendall(request)
        response = self.recvall(sock)
        code = self.get_code(response)
        body = self.get_body(response)
        print body
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        parts = self.get_headers(url)
        host = self.get_port(parts[1])
        request = "POST " + parts[0] + " HTTP/1.1\r\nHost:" + parts[1] + "\r\nContent-type:application/x-www-form-urlencoded\r\ncontent-length:"
        if args != None:
            encargs = urllib.urlencode(args)
            request = request + str(len(encargs)) + "\r\n\r\n" + encargs
        else:
            request = request + "0" + "\r\n\r\n"
        sock = self.connect(host[0], host[1])
        sock.sendall(request)
        response = self.recvall(sock)
        code = self.get_code(response)
        body = self.get_body(response)
        print body
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    else:
        print client.command(sys.argv[1])

