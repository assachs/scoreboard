from rgbmatrix import graphics
from netifaces import interfaces, ifaddresses, AF_INET
import json

class SideCanvas(object):
    def __init__(self, offsetX, offsetY, canvas, sbf):
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.canvas = canvas
        self.sbf = sbf

    def drawText(self, configPath, colorKey, text):
        self.sbf.drawtext(self.canvas, configPath, colorKey, text, self.offsetX, self.offsetY)

    def drawTextList(self, configPath, colorKey, lines):
        self.sbf.drawtextlist(self.canvas, configPath, colorKey, lines, self.offsetX, self.offsetY)

    def drawLine(self, configPath, colorKey):
        self.sbf.drawLineConfig(self.canvas, configPath, colorKey, self.offsetX, self.offsetY)


class Scoreboardbasefunctions(object):
    fonts = {}
    config = {}


    colors = {'w': graphics.Color(255, 255, 255),
            'y': graphics.Color(255, 255, 0),
            'r': graphics.Color(255, 0, 0),
            'g': graphics.Color(0, 255, 0)}


    def __init__(self):
        pass

    def readconfig(self, filename):
        with open(filename) as json_file:
            json_data = json.load(json_file)
            self.config = json_data


            #fonts einlesen
            for font in json_data['fonts']:
                self.loadfont(font)

    def getColor(self, color):
        colorKey = color[:1]
        col = self.colors[colorKey]

        rc = graphics.Color(col.red, col.green, col.blue);

        dim = 0

        if len(color) > 1:
            dim = int(color[1:])

        rc.green = max(0,rc.green - dim)
        rc.red = max(0,rc.red - dim)
        rc.blue = max(0,rc.blue - dim)
        return rc

    def getTextWidth(self,font, text):
            width = 0
            for c in text:
                width += font.CharacterWidth(ord(c))
            return width

    def loadfont(self, name):
        font = graphics.Font()
        font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/" + name + ".bdf")
        self.fonts[name] = font

    def getfont(self, name):
        font = self.fonts[name]
        if font is None:
            print("font not found " + name)
        return font

    def getConfigPosition(self, patterns):
        p = self.config
        for pattern in patterns.split("."):
            p = p[pattern]
        return p

    def getCoordinate(self, p):
        c = 0
        if isinstance(p, str):
            if p[:1] == "$":
                key = p[1:]
                c = self.getCoordinate(self.getConfigPosition(key))
            else:
                c = p
        else:
            c = p
        return c
    def  drawLineConfig(self, offscreen_canvas, configPath, colorKey, offsetX, offsetY):
        p = self.getConfigPosition("positions")
        for pattern in configPath.split("."):
            p = p[pattern]

        x = self.getCoordinate(p["x"])
        y = self.getCoordinate(p["y"])
        length = self.getCoordinate(p["length"])
        alignment = p['alignment']

        #alignment = c
        self.drawline(offscreen_canvas, x - length / 2 + offsetX, x + length / 2 + offsetX, y + offsetY, colorKey)

    def drawtextlist(self, offscreen_canvas, configPath, colorKey, list, offsetX, offsetY):
        p = self.getConfigPosition("positions")
        for pattern in configPath.split("."):
            p = p[pattern]

        x = self.getCoordinate(p["x"])
        y = self.getCoordinate(p["y"])

        alignment = p['alignment']

        fontKey = p['font']
        spacing = p['spacing']
        y = y - spacing
        if alignment == "c":
            for text in list:
                y = y + spacing
                self.drawtextCenter(offscreen_canvas, fontKey, x + offsetX, y + offsetY, colorKey, text)
        elif alignment == "l":
            for text in list:
                y = y + spacing
                self.drawtextLeft(offscreen_canvas, fontKey, x + offsetX, y + offsetY, colorKey, text)
                print(y)
                print(text)
        elif alignment == "r":
            x = 192 - x
            for text in list:
                y = y + spacing
                self.drawtextRight(offscreen_canvas, fontKey, x + offsetX, y + offsetY, colorKey, text)
        else:
            print("alignment not recognized")


    def drawtext(self, offscreen_canvas, configPath, colorKey, text, offsetX, offsetY):
        p = self.config['positions']
        for pattern in configPath.split("."):
            p = p[pattern]

        x = self.getCoordinate(p["x"])
        y = self.getCoordinate(p["y"])

        alignment = p['alignment']
        fontKey = p['font']

        if alignment == "c":
            self.drawtextCenter(offscreen_canvas, fontKey, x + offsetX, y + offsetY, colorKey, text)
        elif alignment == "l":
            self.drawtextLeft(offscreen_canvas, fontKey, x + offsetX, y + offsetY, colorKey, text)
        elif alignment == "r":
            x = 192 - x
            self.drawtextRight(offscreen_canvas, fontKey, x + offsetX, y + offsetY, colorKey, text)
        else:
            print("alignment not recognized")


    def drawtextLeft(self, offscreen_canvas, fontKey, x, y, colorKey, text):
        col = self.getColor(colorKey)
        font = self.getfont(fontKey)
        graphics.DrawText(offscreen_canvas, font, x, y, col, text)

    def drawtextRight(self, offscreen_canvas, fontKey, x, y, colorKey, text):
        col = self.getColor(colorKey)
        font = self.getfont(fontKey)
        width = self.getTextWidth(font, text)
        graphics.DrawText(offscreen_canvas, font, x - width, y, col, text)

    def drawtextCenter(self, offscreen_canvas, fontKey, x, y, colorKey, text):
        font = self.getfont(fontKey)
        width = self.getTextWidth(font, text)
        width = width / 2
        self.drawtextLeft(offscreen_canvas, fontKey, x - width, y, colorKey, text)

    def drawpoint(self, offscreen_canvas, x, y, colorKey):
        col = self.getColor(colorKey)
        graphics.DrawLine(offscreen_canvas, x, y, x, y, col)

    def drawline(self, offscreen_canvas, x1, x2, liney, colorKey):
        col = self.getColor(colorKey)
        graphics.DrawLine(offscreen_canvas, x1, liney, x2, liney, col)
        graphics.DrawLine(offscreen_canvas, x1, liney + 1, x2, liney + 1, col)

    def drawtextArray(self, offscreen_canvas, fontKey, x, y, colornormal, coloractive, activepos, texte, sep= " / "):
        font = self.getfont(fontKey)
        komplett = ""
        i = 0
        for text in texte:
            komplett = komplett + text
            if len(texte) > i + 1 :
                komplett = komplett + sep
            i = i + 1

        width = self.getTextWidth(font, komplett)
        width = width / 2
        start = x - width

        i = 0
        for text in texte:
            col = self.getColor(colornormal)
            if i == activepos:
                col = self.getColor(coloractive)
            graphics.DrawText(offscreen_canvas, font, start, y, col, text)
            width = self.getTextWidth(font, text)

            start = start + width

            if len(texte) > i + 1:
                col = self.getColor(colornormal)
                graphics.DrawText(offscreen_canvas, font, start, y, col, sep)
                start = start + self.getTextWidth(font, sep)
            i = i + 1

    def getAdresses(self):
        adr = []
        for interface in interfaces():
            for link in ifaddresses(interface).get(AF_INET, ()):
                if link.get('addr') != "127.0.0.1":
                    adr.append(link['addr'])
        return adr

