#!/usr/bin/env -S python  -u
# Display a runtext with double-buffering.
import math
from time import sleep

import sys
sys.path.insert(0, '/home/pi/rpi-rgb-led-matrix/bindings/python/samples/')
sys.path.insert(0, '/home/pi/stomp_ws_py/')

from samplebase import SampleBase
from rgbmatrix import graphics

from stomp_ws.client import Client
import json
import time
from threading import Thread
from scoreboardbasefunctions import *

class RunText(SampleBase):
    apikey = ''
    spiel = ''
    updatetime = 0
    pingtime = 0
    status = -1
    frame = None
    client = None
    auszeiten = [0,0]
    auszeitenvisible = False
    satzende = 0
    satzendevisible = False
    sbf = None

    noswitch = False;
    switchedsetup = False
    noswitchedback = False

    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        self.sbf = Scoreboardbasefunctions()

        self.sbf.loadfont("saetze")
        self.sbf.loadfont("punkte")
        self.sbf.loadfont("doppelpunkt")
        self.sbf.loadfont("teamnamen")
        self.sbf.loadfont("auszeit")

    def message(self, frame):
        self.frame = frame

        data = json.loads(frame.body)
        for z in data['teams'][0]['zusatzdaten']:
            if z['text'] == 'Auszeit':
                self.auszeiten[0] = round(time.time()) + 30
                self.auszeitenvisible = True

        for z in data['teams'][1]['zusatzdaten']:
            if z['text'] == 'Auszeit':
                self.auszeiten[1] = round(time.time()) + 30
                self.auszeitenvisible = True

        self.updatetime = time.time()
        self.pingtime = time.time()
        self.updateStatus()
        self.messageShow()

    def messageShow(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        offscreen_canvas.Clear()
        if self.frame is not None:
            self.draw_side_data(self.frame, offscreen_canvas,0, False)
            self.draw_side_data(self.frame, offscreen_canvas,192, True)
        else:
            self.draw_side_nodata(offscreen_canvas, 0)
            self.draw_side_nodata(offscreen_canvas, 192)
        self.draw_status(offscreen_canvas, 192)
        self.matrix.SwapOnVSync(offscreen_canvas)

    def draw_side_nodata(self, offscreen_canvas, start):
        self.sbf.drawtextLeft(offscreen_canvas, "teamnamen", start, 10, 'w', "keine Daten")
        self.sbf.drawtextLeft(offscreen_canvas, "teamnamen", start, 20, 'w', "-".join(self.spiel.split("-", 3)[:3]) + "-")
        self.sbf.drawtextLeft(offscreen_canvas, "teamnamen", start, 30, 'w', "-".join(self.spiel.split("-", 3)[3:]))
        row=30
        for adr in self.sbf.getAdresses():
            row = row + 10
            self.sbf.drawtextLeft(offscreen_canvas, "teamnamen", start, row, 'w', adr)

    @staticmethod
    def calc_teamname(team):
        teamname = team['bezeichnung']
        if len(teamname) > 16:
            teamname = teamname[:16].strip() + "."
        return teamname

    def draw_side_data(self,frame, offscreen_canvas, start, backside):
        data = json.loads(frame.body)
        a = 0

        switch = False

        if not self.noswitch:
            switch = data['switched']

        if not self.noswitchedback and backside:
            switch = not switch

        if self.switchedsetup:
            switch = not switch

        if switch:
            a = a + 1

        teamA = data['teams'][a]
        teamB = data['teams'][(a+1)%2]
        saetzeA = teamA['saetze']
        saetzeB = teamB['saetze']
        baelleA = teamA['punkteAkt']
        baelleB = teamB['punkteAkt']
        teamlbez = self.calc_teamname(teamA)
        teamrbez = self.calc_teamname(teamB)

        punktel = 53
        punkter = 140

        if self.auszeiten[a] > time.time():
            self.sbf.drawtextCenter(offscreen_canvas, "auszeit", 9 + start, 25, 'y', str(round(self.auszeiten[a] - time.time())))

        if self.auszeiten[(a+1)%2] > time.time():
            self.sbf.drawtextCenter(offscreen_canvas, "auszeit", 187 + start, 25, 'y', str(round(self.auszeiten[(a+1)%2] - time.time())))

        if self.satzendevisible:
            satzende = round(self.satzende -  time.time())
            satzendem = math.floor(satzende / 60)
            satzendes = satzende % 60
            timestr = str(satzendem) + ":" + str(satzendes).zfill(2)
            self.sbf.drawtextCenter(offscreen_canvas, "teamnamen", 96 + start, 25, 'y', timestr)

        self.sbf.drawtextCenter(offscreen_canvas, "saetze", 9 + start, 60, 'y', str(saetzeA))
        self.sbf.drawtextCenter(offscreen_canvas, "saetze", 187 + start, 60, 'y', str(saetzeB))
        self.sbf.drawtextCenter(offscreen_canvas, "punkte", punktel + start, 60, 'w', str(baelleA))
        self.sbf.drawtextCenter(offscreen_canvas, "punkte", punkter + start, 60, 'w', str(baelleB))

        self.sbf.drawtextCenter(offscreen_canvas, "doppelpunkt", 100 + start, 60, 'w', ":")

        self.sbf.drawtextCenter(offscreen_canvas, "teamnamen", 48 + start, 9, 'y', teamlbez)
        self.sbf.drawtextCenter(offscreen_canvas, "teamnamen", 144 + start, 9, 'y', teamrbez)

        liney = 62
        if teamA['service']:
                self.sbf.drawline(offscreen_canvas, 14, 90, liney, start, 'y')

        if teamB['service']:
                self.sbf.drawline(offscreen_canvas, 98, 178, liney, start, 'y')

    def draw_status(self, offscreen_canvas, start):
        if self.status > 0:
            color = 'y'
            if self.status == 3:
                color = 'r'
            self.sbf.drawpoint(offscreen_canvas, start, 63,color)

    def updateStatus(self):
        changed = False
        if (self.status == 0) and (time.time() > self.pingtime + 10):
            self.status = 1
            changed = True
        elif (self.status > 0) and not (time.time() > self.pingtime + 10):
            self.status = 0
            changed = True
        elif self.status == -1:
            self.status = 3
            changed = True

        if (self.auszeiten[0] > time.time() or self.auszeiten[1] > time.time()) and not self.auszeitenvisible:
            self.auszeitenvisible = True
            changed = True
        elif (self.auszeiten[0] <= time.time() and self.auszeiten[1] <= time.time()) and self.auszeitenvisible:
            self.auszeitenvisible = False
            changed = True

        if (self.satzende > time.time()) and not self.satzendevisible:
            self.satzendevisible = True
            changed = True
        elif (self.satzende <= time.time()) and self.satzendevisible:
            self.satzendevisible = False
            changed = True

        if changed or self.auszeitenvisible or self.satzendevisible or self.status==3:
            self.messageShow()

    def refresh(self):
        loop = 0
        while True:
            loop += 1
            loop = loop % 5
            if loop == 0:
                print("refresh")

            if self.status == -1 or loop == 0 or self.auszeitenvisible or self.satzendevisible:
                self.updateStatus()

            if self.auszeitenvisible or self.satzendevisible:
                sleep(0.2)
            else:
                sleep(1)

    def ping(self):
        self.pingtime = time.time()

    def readconfig(self):
        with open("/etc/scoreboard/match.json") as json_file:
            json_data = json.load(json_file)
            self.spiel = json_data['spieluuid']
            self.apikey = json_data['apikey']
            self.noswitch = json_data['noswitch']
            self.switchedsetup = json_data['switchedsetup']
            self.noswitchedback = json_data['noswitchedback']

    def connect(self, frame):
        print("OnConnect")
        self.readconfig()

        self.client.subscribe('/topic/' + self.spiel + '/spielstand', callback=self.message)

        self.updatetime = time.time()
        self.pingtime = time.time()

    def connectclient(self):
        #client = Client("wss://bvv-tv-ws-test.bvv.volley.de:8088/tvgrafik/websocket")
        client = Client("wss://bvv-tv-ws.bvv.volley.de:8088/tvgrafik/websocket")

        self.client = client

        client.connect(login="name",
                       headers={"apikey": self.apikey},
                       timeout=0,
                       connectCallback=self.connect,
                       errorCallback=self.onerror,
                       pingCallback=self.ping)

    def onerror(self, frame):
        print("Error")
        print(frame)
        self.status = 3
        sleep(2)
        self.connectclient()

    def run(self):
        self.readconfig()

        thread = Thread(target=self.refresh)
        thread.daemon = True
        thread.start()

        self.connectclient()

# Main function
if __name__ == "__main__":
    run_text = RunText()
    run_text.process()
    while True:
        sleep(5)
