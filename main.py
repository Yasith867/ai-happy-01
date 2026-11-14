"""Create a cozy, hand-drawn birthday card for the AI judge.

Uses only Python's standard library. Running this file writes a deterministic
RGB PNG to /output/entry.png (or ./entry.png when /output is unavailable).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (255, 238, 207)
INK = (91, 58, 43)


class Canvas:
    def __init__(self, w, h, color):
        self.w, self.h = w, h
        self.p = bytearray(color * (w * h))

    def dot(self, x, y, color):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.p[i:i+3] = bytes(color)

    def disk(self, x, y, r, color):
        x0, x1 = max(0, int(x-r)), min(self.w-1, int(x+r))
        y0, y1 = max(0, int(y-r)), min(self.h-1, int(y+r))
        rr = r*r
        for yy in range(y0, y1+1):
            for xx in range(x0, x1+1):
                if (xx-x)**2 + (yy-y)**2 <= rr:
                    self.dot(xx, yy, color)

    def line(self, a, b, color=INK, width=4):
        x0, y0 = a; x1, y1 = b
        steps = max(1, int(max(abs(x1-x0), abs(y1-y0))))
        for k in range(steps+1):
            t = k / steps
            self.disk(x0+(x1-x0)*t, y0+(y1-y0)*t, width/2, color)

    def poly(self, points, fill, outline=INK, width=4):
        # Scanline fill, then a softly irregular hand-inked outline.
        ymin = max(0, int(min(y for _, y in points)))
        ymax = min(self.h-1, int(max(y for _, y in points)))
        for y in range(ymin, ymax+1):
            xs = []
            for i, (x1, y1) in enumerate(points):
                x2, y2 = points[(i+1) % len(points)]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y-y1)*(x2-x1)/(y2-y1))
            xs.sort()
            for j in range(0, len(xs)-1, 2):
                for x in range(max(0, int(xs[j])), min(self.w, int(xs[j+1])+1)):
                    self.dot(x, y, fill)
        for i, point in enumerate(points):
            self.line(point, points[(i+1) % len(points)], outline, width)

    def ellipse(self, cx, cy, rx, ry, fill, outline=INK, width=4):
        for y in range(max(0, int(cy-ry)), min(self.h, int(cy+ry)+1)):
            for x in range(max(0, int(cx-rx)), min(self.w, int(cx+rx)+1)):
                if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1:
                    self.dot(x, y, fill)
        n = max(80, int(2*math.pi*max(rx, ry)))
        pts = [(cx+rx*math.cos(i*2*math.pi/n), cy+ry*math.sin(i*2*math.pi/n)) for i in range(n)]
        for i in range(0, n, 2):
            self.line(pts[i], pts[(i+1) % n], outline, width)

    def circle_outline(self, cx, cy, r, color=INK, width=4):
        n = max(32, int(2*math.pi*r))
        pts = [(cx+r*math.cos(i*2*math.pi/n), cy+r*math.sin(i*2*math.pi/n)) for i in range(n)]
        for i in range(0, n, 2): self.line(pts[i], pts[(i+1) % n], color, width)

    def text(self, x, y, value, scale, color=INK):
        # Tiny built-in 5x7 alphabet keeps rendering portable and deterministic.
        for ch in value.upper():
            glyph = FONT.get(ch, FONT[' '])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == '1':
                        self.disk(x + col*scale, y + row*scale, scale*0.53, color)
            x += 6*scale


FONT = {
    ' ': ['00000']*7,
    'A':['01110','10001','10001','11111','10001','10001','10001'], 'B':['11110','10001','10001','11110','10001','10001','11110'],
    'C':['01111','10000','10000','10000','10000','10000','01111'], 'D':['11110','10001','10001','10001','10001','10001','11110'],
    'E':['11111','10000','10000','11110','10000','10000','11111'], 'F':['11111','10000','10000','11110','10000','10000','10000'],
    'G':['01111','10000','10000','10111','10001','10001','01111'], 'H':['10001','10001','10001','11111','10001','10001','10001'],
    'I':['11111','00100','00100','00100','00100','00100','11111'], 'J':['00111','00010','00010','00010','10010','10010','01100'],
    'K':['10001','10010','10100','11000','10100','10010','10001'], 'L':['10000','10000','10000','10000','10000','10000','11111'],
    'M':['10001','11011','10101','10101','10001','10001','10001'], 'N':['10001','11001','10101','10011','10001','10001','10001'],
    'O':['01110','10001','10001','10001','10001','10001','01110'], 'P':['11110','10001','10001','11110','10000','10000','10000'],
    'Q':['01110','10001','10001','10001','10101','10010','01101'], 'R':['11110','10001','10001','11110','10100','10010','10001'],
    'S':['01111','10000','10000','01110','00001','00001','11110'], 'T':['11111','00100','00100','00100','00100','00100','00100'],
    'U':['10001','10001','10001','10001','10001','10001','01110'], 'V':['10001','10001','10001','10001','10001','01010','00100'],
    'W':['10001','10001','10001','10101','10101','10101','01010'], 'X':['10001','10001','01010','00100','01010','10001','10001'],
    'Y':['10001','10001','01010','00100','00100','00100','00100'], 'Z':['11111','00001','00010','00100','01000','10000','11111'],
    '!':['00100','00100','00100','00100','00100','00000','00100'], ',':['00000','00000','00000','00000','00110','00100','01000'],
    '.':['00000','00000','00000','00000','00000','00110','00110'], "'":['00100','00100','00000','00000','00000','00000','00000'],
}


def draw():
    c = Canvas(W, H, PAPER)
    # Warm paper grain and double scalloped frame.
    for y in range(0, H, 13):
        for x in range((y * 7) % 17, W, 17):
            tone = (245,234,210) if (x + 3*y) % 4 == 0 else (252,246,231)
            c.dot(x, y, tone)
    c.circle_outline(512, 505, 443, (190,137,96), 3)
    c.circle_outline(512, 505, 430, (190,137,96), 2)

    # Little confetti stars.
    for x, y, r in [(186,228,17),(834,223,14),(186,740,13),(833,739,16),(290,179,8),(735,178,9),(286,822,9),(738,821,8)]:
        pts=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5; rr=r if i%2==0 else r*.42
            pts.append((x+rr*math.cos(a),y+rr*math.sin(a)))
        c.poly(pts,(222,159,72),INK,2)

    # Heartfelt headline.
    c.text(332, 155, 'HAPPY BIRTHDAY', 5, (111,70,53))
    c.text(392, 222, 'DEAR JUDGE', 5, (159,101,70))
    # Tiny rosy cheeks and a smiling little cake character.
    c.ellipse(512, 568, 212, 48, (225,181,132), INK, 5)
    c.poly([(302,426),(322,597),(702,597),(722,426)], (245,206,157), INK, 6)
    c.ellipse(512, 426, 210, 42, (255,229,190), INK, 5)
    # Icing drips, each intentionally a slightly wobbly hand-shaped curve.
    c.poly([(309,426),(361,432),(367,470),(387,486),(405,467),(410,435),(456,439),(462,475),(482,490),(502,476),(510,438),(557,439),(564,472),(585,488),(607,473),(612,433),(660,430),(664,465),(684,479),(716,426),(716,443),(694,493),(672,497),(649,472),(644,444),(625,492),(584,505),(545,492),(536,449),(526,506),(478,510),(441,495),(433,450),(423,497),(382,508),(343,488),(338,445)], (255,246,220), INK, 3)
    # Candle and glowing flame.
    c.poly([(490,362),(534,362),(531,425),(493,425)], (209,111,92), INK, 4)
    c.line((505,376),(518,409),(250,190,148),3)
    c.ellipse(512,339,20,34,(238,164,69),INK,3)
    c.ellipse(512,344,8,19,(255,220,131),(255,220,131),1)
    # Friendly face on the cake.
    c.ellipse(445,548,12,16,INK,INK,1); c.ellipse(579,548,12,16,INK,INK,1)
    c.ellipse(414,570,21,10,(218,128,112),(218,128,112),1); c.ellipse(610,570,21,10,(218,128,112),(218,128,112),1)
    c.line((474,573),(489,584),INK,4); c.line((489,584),(510,588),INK,4); c.line((510,588),(533,588),INK,4); c.line((533,588),(550,582),INK,4)
    # Sprinkles across frosting.
    for x,y,col in [(366,426,(194,103,85)),(401,413,(116,147,111)),(454,425,(223,164,74)),(573,418,(116,147,111)),(628,425,(194,103,85)),(667,414,(223,164,74))]:
        c.line((x,y),(x+8,y-8),col,4)

    # A small gift beside the cake, tied with a ribbon.
    c.poly([(727,568),(858,568),(850,698),(736,698)],(198,126,91),INK,5)
    c.poly([(718,548),(865,548),(860,578),(724,578)],(222,160,109),INK,4)
    c.poly([(779,548),(801,548),(801,698),(780,698)],(247,216,169),INK,3)
    c.ellipse(777,539,24,12,(222,160,109),INK,3); c.ellipse(805,539,24,12,(222,160,109),INK,3)
    c.line((790,554),(772,581),INK,3); c.line((790,554),(811,581),INK,3)

    # Message card and gentle confetti dots.
    c.text(364, 712, 'THANK YOU FOR LOOKING', 2, (111,70,53))
    c.text(379, 752, 'AT ALL OUR LITTLE WORLDS.', 2, (111,70,53))
    c.text(423, 817, 'YOU DESERVE A LITTLE JOY!', 1, (159,101,70))
    c.circle_outline(235, 585, 25, (194,103,85), 4)
    c.line((218,585),(252,585),(194,103,85),4)
    c.line((235,568),(235,602),(194,103,85),4)
    # Grounding strokes under the illustration.
    for i in range(11):
        x=360+i*30
        wobble = (i % 3) - 1
        c.line((x,631+wobble),(x+18,631-wobble),(177,125,87),2)
    return c


def write_png(path, c):
    def chunk(kind, data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    raw=b''.join(b'\0'+bytes(c.p[y*c.w*3:(y+1)*c.w*3]) for y in range(c.h))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',c.w,c.h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    with open(path,'wb') as f: f.write(png)


if __name__ == '__main__':
    # The harness uses /output. On Windows, emulate that directory inside the
    # project so the renderer can be run locally without elevated permissions.
    target='/output/entry.png' if os.name != 'nt' else os.path.join(os.path.dirname(__file__), 'output', 'entry.png')
    os.makedirs(os.path.dirname(target),exist_ok=True)
    write_png(target,draw())
    print(target)


