

#Copyright Jon Berg , turtlemeat.com
import string,cgi,time
import json
from urlparse import urlparse, parse_qs
from os import curdir, sep, system
import BaseHTTPServer
from random import choice
import urllib2
import socket
import struct

#import xbmc

#import pydevd



def wake_on_lan(macaddress):

    """ Switches on remote computers using WOL. """
    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')
 
    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
    send_data = '' 

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data,
                             struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', 7))

class MyHandler(BaseHTTPRequestHandler):

    def __init__(self):
        self.xbmc_host = '192.168.1.178' # xbmc.getIPAddress();

    def _getVars(self):
        return postvars

    def log_message(self, format, *args):
        self.writeLog("Got Request")

    def do_POST(self):
        self.writeLog("do_POST")
        self.send_response(200)
        
        self.end_headers()

        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        print ">> POST", postvars

        self.do_response(postvars)

    def sendCommandToXbmc(self, data):
        headers = {'Content-Type': 'application/json'}
        data["jsonrpc"] = "2.0"
        data["id"] = 1
        data = json.dumps(data)
        
        req = urllib2.Request('http://'+self.xbmc_host+':8080/jsonrpc', data, headers)
        response = urllib2.urlopen(req)
        response = response.read()
        response = json.loads(response)
        #print response
        return response

    def writeLog(self, data):
        xbmc.log("service.vox-control: "+data)
        
    def do_response(self, postvars):
        self.writeLog("do_response")
        """
        args = postvars["cmd"][0].split()
        if args[0].lower() == 'xbmc':
            if args[1] == 'scan':
                self.sendCommandToXbmc({"method": "VideoLibrary.Scan"})
                self.wfile.write("Scanning for new videos")
                return
            if args[1] == 'stop':
                self.sendCommandToXbmc({"method": "Player.Stop", 'params': {'playerid' : 1}})
                self.wfile.write('Stopping playback')
                return
            if args[1] == 'play':
                self.sendCommandToXbmc({"method": "Player.PlayPause", 'params': {'playerid' : 1}})
                self.wfile.write('Resuming playback')
                return
            if args[1] in ['pause', 'cores', 'porn']:
                self.sendCommandToXbmc({"method": "Player.PlayPause", 'params': {'playerid' : 1}})
                self.wfile.write('Pausing playback')
                return
            if args[1] == 'watch':
                latest = False
                random = False
                episode = False
                if args[2] == 'latest':
                    episode = True
                    latest = True
                if args[2] == 'random':
                    episode = True
                    random = True
                if episode:
                    show = " ".join(args[3:])
                    data = self.sendCommandToXbmc({'method': 'VideoLibrary.GetTVShows'})
                    for result in data["result"]['tvshows']:
                        if show in result['label'].lower():
                            shows = self.sendCommandToXbmc({'method': 'VideoLibrary.GetEpisodes', 'params': {'tvshowid': result['tvshowid']}})
                            if latest:
                                ep = shows['result']['episodes'][-1]
                            if random:
                                ep = choice(shows['result']['episodes'])
                            self.sendCommandToXbmc({'method': 'Player.Open', 'params': {'item': {'episodeid': ep['episodeid']}}})
                            self.wfile.write('Playing %s %s' % (result['label'], ep['label']))
                            return
                else:
                    show = " ".join(args[2:])
                    data = self.sendCommandToXbmc({'method': 'VideoLibrary.GetMovies'})
                    for result in data['result']['movies']:
                        if show in result['label'].lower():
                            self.sendCommandToXbmc({'method': 'Player.Open', 'params': {'item': {'movieid': result['movieid']}}})
                            self.wfile.write('Playing %s' % (result['label']))
                            return
                self.wfile.write('I couldn\'t find what you are looking for')
                return

            if args[1] == 'shut' and args[2] == 'down':
                self.sendCommandToXbmc({"method": "System.Suspend"})
                self.wfile.write('Shutting down X B M C')
                return
            if args[1] == 'wake' and args[2] == 'up':
                wake_on_lan('f4:6d:04:91:49:35')
                self.wfile.write('Waking X B M C up')
                return
                """
        #self.wfile.write('Unknown command')
                
            

class VoiceCommandWebServer(HTTPServer):
    def __init__(self):
        self.xbmc_host = 'tv'
        HTTPServer.__init__(self, ('0.0.0.0', 8337), MyHandler)
        sa = self.socket.getsockname()

    def runit(self):
        self.serve_forever()

if __name__ == '__main__':
#    pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    server = VoiceCommandWebServer()
    server.runit()
