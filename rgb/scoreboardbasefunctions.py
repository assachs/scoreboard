from rgbmatrix import graphics
from netifaces import interfaces, ifaddresses, AF_INET

class Scoreboardbasefunctions(object):
    fonts = {}

    colors = {'w': graphics.Color(255, 255, 255),
              'y': graphics.Color(255, 255, 0),
              'r': graphics.Color(255, 0, 0)}

    def __init__(self):
        pass

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

    def drawtextLeft(self, offscreen_canvas, fontKey, x, y, colorKey, text):
        col = self.colors[colorKey]
        font = self.getfont(fontKey)
        graphics.DrawText(offscreen_canvas, font, x, y, col, text)

    def drawtextCenter(self, offscreen_canvas, fontKey, x, y, colorKey, text):
        font = self.getfont(fontKey)
        width = self.getTextWidth(font, text)
        width = width / 2
        self.drawtextLeft(offscreen_canvas, fontKey, x - width, y, colorKey, text)

    def drawpoint(self, offscreen_canvas, x, y, colkey):
        col = self.colors[colkey]
        graphics.DrawLine(offscreen_canvas, x, y, x, y, col)

    def drawline(self, offscreen_canvas, x1, x2, liney, start, colkey):
        col = self.colors[colkey]
        graphics.DrawLine(offscreen_canvas, x1 + start, liney, x2 + start, liney, col)
        graphics.DrawLine(offscreen_canvas, x1 + start, liney + 1, x2 + start, liney + 1, col)

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
            col = self.colors[colornormal]
            if i == activepos:
                col = self.colors[coloractive]
            graphics.DrawText(offscreen_canvas, font, start, y, col, text)
            width = self.getTextWidth(font, text)

            start = start + width

            if len(texte) > i + 1:
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

