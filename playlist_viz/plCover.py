import matplotlib.cm as cm
from PIL import Image, ImageDraw
import numpy as np
#with a value between 0 and 1, generate an image
def genSolidCover(normVal, size=512,genRand=False):
    if genRand:
        artColor =(np.random.randint(0,255),np.random.randint(0,255),np.random.randint(0,255))
    else:
        colorNorm = cm.bwr(normVal)
#        colorUse = tuple([int(colorIdx*256) for colorIdx in colorNorm])
        artColor = tuple([int(colorIdx * 256) for colorIdx in colorNorm])

    return Image.new('RGB',(size,size),color=artColor)



def gen2ColorCover(normVal1,normVal2, size=512,genRand=False):
    if genRand:
        artColor1 =(np.random.randint(0,255),np.random.randint(0,255),np.random.randint(0,255))
        artColor2 =(np.random.randint(0,255),np.random.randint(0,255),np.random.randint(0,255))

    else:
        colorNorm1 = cm.bwr(normVal1)
        colorNorm2 = cm.viridis(normVal2)
#        colorUse = tuple([int(colorIdx*256) for colorIdx in colorNorm])
        artColor1 = tuple([int(colorIdx * 256) for colorIdx in colorNorm1[0:3]])
        artColor2 = tuple([int(colorIdx * 256) for colorIdx in colorNorm2[0:3]])

    imCanvas = Image.new('RGB',(size,size),(255,255,255))
    draw = ImageDraw.Draw(imCanvas)
    region=Rect(0,0,size,size)
    vertGradient(draw,region,gradientColor,[artColor1,artColor2])
    return imCanvas

# Draw functions cribbed from online
def gradientColor(minval, maxval, val, color_palette):
    """ Computes intermediate RGB color of a value in the range of minval
        to maxval (inclusive) based on a color_palette representing the range.
    """
    max_index = len(color_palette)-1
    delta = maxval - minval
    if delta == 0:
        delta = 1
    v = float(val-minval) / delta * max_index
    i1, i2 = int(v), min(int(v)+1, max_index)
    (r1, g1, b1), (r2, g2, b2) = color_palette[i1], color_palette[i2]
    f = v - i1
    return int(r1 + f*(r2-r1)), int(g1 + f*(g2-g1)), int(b1 + f*(b2-b1))

def horzGradient(draw, rect, color_func, color_palette):
    minval, maxval = 1, len(color_palette)
    delta = maxval - minval
    width = float(rect.width)  # Cache.
    for x in range(rect.min.x, rect.max.x+1):
        f = (x - rect.min.x) / width
        val = minval + f * delta
        color = color_func(minval, maxval, val, color_palette)
        draw.line([(x, rect.min.y), (x, rect.max.y)], fill=color)

def vertGradient(draw, rect, color_func, color_palette):
    minval, maxval = 1, len(color_palette)
    delta = maxval - minval
    height = float(rect.height)  # Cache.
    for y in range(rect.min.y, rect.max.y+1):
        f = (y - rect.min.y) / height
        val = minval + f * delta
        color = color_func(minval, maxval, val, color_palette)
    #    print(color)
        draw.line([(rect.min.x, y), (rect.max.x, y)], fill=color)

class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        minx, maxx = (x1,x2) if x1 < x2 else (x2,x1)
        miny, maxy = (y1,y2) if y1 < y2 else (y2,y1)
        self.min = Point(minx, miny)
        self.max = Point(maxx, maxy)

    width  = property(lambda self: self.max.x - self.min.x)
    height = property(lambda self: self.max.y - self.min.y)
    # colorNormEnergy = cm.bwr(energyMean)
    # colorNormVal = cm.BrBG(valenceMean)
