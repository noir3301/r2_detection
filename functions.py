import time
import mouse
import win32gui, win32ui
import math
from numpy import *
from PIL import Image
from variables import *



def pixel_color_at(x, y):
    hdc = win32gui.GetWindowDC(win32gui.GetDesktopWindow())
    c = int(win32gui.GetPixel(hdc, x, y))
    col = (c & 0xff), ((c >> 8) & 0xff), ((c >> 16) & 0xff)
    return col

def pixels_colors_row(x : tuple, y):
    colors = ()
    hdc = win32gui.GetWindowDC(win32gui.GetDesktopWindow())
    for ix in x:
        c = int(win32gui.GetPixel(hdc, ix, y))
        colors += ((c & 0xff), ((c >> 8) & 0xff), ((c >> 16) & 0xff)),
    return colors

def get_cursor():
    hcursor = win32gui.GetCursorInfo()[1]
    if hcursor == 0:
        return None
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 36, 36)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), hcursor)
    bmpinfo = hbmp.GetInfo()
    bmpstr = hbmp.GetBitmapBits(True)
    cursor = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1).convert(
        "RGBA")
    win32gui.DeleteObject(hbmp.GetHandle())
    hdc.DeleteDC()
    return cursor

def is_cursor_attack():
    cursor = get_cursor()
    if cursor is None:
        return False
    if cursor.getpixel(CURSOR_CORDS[0]) == CURSOR_COLORS[0] and cursor.getpixel(CURSOR_CORDS[1]) == CURSOR_COLORS[1]:
        return True
    return False

def is_attacking():
    colors = pixels_colors_row(ATTACK_LABEL_X, ATTACK_LABEL_Y)
    for c, color in enumerate(colors):
        for r, rgb in enumerate(color):
            if ATTACK_LABEL_COLORS[c][r][0] > rgb or ATTACK_LABEL_COLORS[c][r][1] < rgb:
                return False
    return True

def mouse_click():
    mouse.press()
    time.sleep(0.08)
    mouse.press('right')
    time.sleep(0.08)
    mouse.release()
    time.sleep(0.08)
    mouse.release('right')

def is_full_hp():
    colors = pixels_colors_row(HP_X, HP_Y)
    for color in colors:
        if color == HP_COLOR_RED:
            return True
    return False


def get_distance(x, y):
    x_invert = SCREEN_WIDTH - x
    y_invert = SCREEN_HEIGHT - y
    if y <= SCREEN_HEIGHT*0.5:
        distance_y = int(abs(y_invert ** 2 - CHAR_Y ** 2)) // 100
    else:
        distance_y =  int(abs(y_invert ** 1.8 - CHAR_Y ** 1.8)) // 100
    distance_x = int(abs(x_invert ** 1.4 - CHAR_X ** 1.4) * math.sqrt(y_invert)) // 100
    return int(math.sqrt(distance_x**2 + distance_y ** 2))