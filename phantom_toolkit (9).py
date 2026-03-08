#!/usr/bin/env python3
# ================================================================
#   PHANTOM TOOLKIT  v4.0
#   made by extort
# ================================================================

import os, sys, platform, socket, hashlib, base64, secrets
import string, subprocess, json, time, threading, ipaddress
import struct, urllib.request, urllib.error, urllib.parse, re
from datetime import datetime

# ──────────────────────────────────────────────────────────────
#  COLORS
# ──────────────────────────────────────────────────────────────
class c:
    R  = "\033[0m";  B  = "\033[1m";  D  = "\033[2m";  IT = "\033[3m"
    R1 = "\033[91m"; G  = "\033[92m"; Y  = "\033[93m";  BL = "\033[94m"
    M  = "\033[95m"; C  = "\033[96m"; W  = "\033[97m"

# ──────────────────────────────────────────────────────────────
#  THEME ENGINE
# ──────────────────────────────────────────────────────────────
THEMES = {
    "phantom": {
        "name": "Phantom", "desc": "Cyan → Magenta (default)",
        "ghost": (0, 220, 255), "splash": "stars",
        "grad_stops": [(0,255,255),(80,200,255),(140,130,255),(200,80,255),(220,50,230)],
        "grad_a": (0,220,255), "grad_b": (200,80,255), "accent": c.C, "hi": c.M,
    },
    "blood": {
        "name": "Blood", "desc": "Deep red → orange fire",
        "ghost": (255, 40, 40), "splash": "city",
        "grad_stops": [(255,20,20),(255,60,10),(255,100,0),(255,140,0),(255,180,20)],
        "grad_a": (255,20,20), "grad_b": (255,160,0), "accent": c.R1, "hi": c.Y,
    },
    "matrix": {
        "name": "Matrix", "desc": "Classic green rain",
        "ghost": (0, 220, 80), "splash": "matrix",
        "grad_stops": [(0,255,80),(0,240,60),(0,210,40),(0,180,30),(0,150,20)],
        "grad_a": (0,255,80), "grad_b": (0,140,20), "accent": c.G, "hi": c.G,
    },
    "gold": {
        "name": "Gold", "desc": "Royal gold → amber",
        "ghost": (255, 200, 0), "splash": "stars",
        "grad_stops": [(255,220,0),(255,200,20),(255,170,30),(240,140,20),(220,110,0)],
        "grad_a": (255,220,0), "grad_b": (200,100,0), "accent": c.Y, "hi": c.Y,
    },
    "ice": {
        "name": "Ice", "desc": "Arctic white → ice blue",
        "ghost": (180, 240, 255), "splash": "stars",
        "grad_stops": [(255,255,255),(220,245,255),(180,230,255),(140,210,255),(100,190,255)],
        "grad_a": (255,255,255), "grad_b": (100,190,255), "accent": c.C, "hi": c.W,
    },
    "venom": {
        "name": "Venom", "desc": "Toxic green → acid yellow",
        "ghost": (100, 255, 50), "splash": "matrix",
        "grad_stops": [(60,255,20),(120,255,40),(180,255,10),(220,240,0),(255,220,0)],
        "grad_a": (60,255,20), "grad_b": (255,220,0), "accent": c.G, "hi": c.Y,
    },
    "sunset": {
        "name": "Sunset", "desc": "Pink → orange → warm yellow",
        "ghost": (255, 100, 180), "splash": "city",
        "grad_stops": [(255,60,160),(255,100,80),(255,150,40),(255,190,30),(255,220,60)],
        "grad_a": (255,60,160), "grad_b": (255,200,40), "accent": c.M, "hi": c.Y,
    },
    "ocean": {
        "name": "Ocean", "desc": "Deep navy → teal",
        "ghost": (0, 140, 255), "splash": "stars",
        "grad_stops": [(0,40,200),(0,80,230),(0,130,220),(0,190,200),(0,220,180)],
        "grad_a": (0,40,200), "grad_b": (0,220,200), "accent": c.BL, "hi": c.C,
    },
    "aurora": {
        "name": "Aurora", "desc": "Northern lights — green, blue, violet",
        "ghost": (80, 255, 180), "splash": "stars",
        "grad_stops": [(0,255,160),(40,200,255),(100,120,255),(160,60,255),(200,40,220)],
        "grad_a": (0,255,160), "grad_b": (200,40,220), "accent": c.G, "hi": c.M,
    },
    "neon": {
        "name": "Neon", "desc": "Hot pink → electric blue",
        "ghost": (255, 0, 180), "splash": "city",
        "grad_stops": [(255,0,180),(220,0,220),(160,0,255),(80,80,255),(0,180,255)],
        "grad_a": (255,0,180), "grad_b": (0,180,255), "accent": c.M, "hi": c.C,
    },
    "lava": {
        "name": "Lava", "desc": "Deep black-red → molten orange",
        "ghost": (200, 30, 0), "splash": "city",
        "grad_stops": [(120,0,0),(180,20,0),(220,60,0),(255,100,0),(255,160,20)],
        "grad_a": (120,0,0), "grad_b": (255,160,20), "accent": c.R1, "hi": c.Y,
    },
    "void": {
        "name": "Void", "desc": "Deep purple → dark violet",
        "ghost": (140, 0, 255), "splash": "stars",
        "grad_stops": [(60,0,120),(90,0,180),(120,0,220),(150,20,255),(180,60,255)],
        "grad_a": (60,0,120), "grad_b": (180,60,255), "accent": c.M, "hi": c.M,
    },
}

# Active theme (mutable dict so functions can read it)
ACTIVE_THEME = dict(THEMES["phantom"])

# Global animation offset (increments each frame for shimmer)
_ANIM_OFFSET = [0]

def _lerp(a, b, t):
    return (int(a[0]+(b[0]-a[0])*t), int(a[1]+(b[1]-a[1])*t), int(a[2]+(b[2]-a[2])*t))

def _rgb(r, g, b):
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"\033[38;2;{r};{g};{b}m"

def _bgrgb(r, g, b):
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"\033[48;2;{r};{g};{b}m"

def gradient_line(text, row_idx, total_rows=5, bold=True, shimmer=False):
    """Render one line with per-character gradient + optional shimmer wave."""
    stops = ACTIVE_THEME["grad_stops"]
    n   = len(stops)
    t   = row_idx / max(1, total_rows - 1)
    seg = t * (n - 1)
    lo  = int(seg); hi = min(lo+1, n-1)
    row_color = _lerp(stops[lo], stops[hi], seg - lo)
    out = []; L = max(1, len(text))
    offset = _ANIM_OFFSET[0] if shimmer else 0
    for ci, ch in enumerate(text):
        # base position gradient (left to right brightens slightly)
        lt = ci / L
        r  = row_color[0] + int(lt * 18)
        g  = row_color[1] - int(lt * 25)
        b  = row_color[2] + int(lt * 18)
        # shimmer: sine wave brightness pulse
        if shimmer:
            import math
            wave = math.sin((ci + offset) * 0.35) * 0.25 + 0.85
            r = int(r * wave); g = int(g * wave); b = int(b * wave)
        prefix = "\033[1m" if bold else ""
        out.append(f"{prefix}{_rgb(r,g,b)}{ch}\033[0m")
    return "".join(out)

def gradient_text(lines, bold=True, shimmer=False):
    n = len(lines)
    return [gradient_line(l, i, n, bold, shimmer) for i, l in enumerate(lines)]

def gradient_single(text, start_rgb=None, end_rgb=None, bold=True, shimmer=False):
    """Full per-character gradient across a single line."""
    sa = start_rgb or ACTIVE_THEME["grad_a"]
    ea = end_rgb   or ACTIVE_THEME["grad_b"]
    L  = max(1, len(text)); out = []
    offset = _ANIM_OFFSET[0] if shimmer else 0
    for ci, ch in enumerate(text):
        t   = ci / L
        rgb = _lerp(sa, ea, t)
        if shimmer:
            import math
            wave = math.sin((ci + offset) * 0.35) * 0.22 + 0.88
            rgb = (int(rgb[0]*wave), int(rgb[1]*wave), int(rgb[2]*wave))
        prefix = "\033[1m" if bold else ""
        out.append(f"{prefix}{_rgb(*rgb)}{ch}\033[0m")
    return "".join(out)

def rainbow_line(text, bold=True):
    """Full RGB rainbow across a line."""
    import math
    L = max(1, len(text)); out = []
    for ci, ch in enumerate(text):
        t = ci / L
        r = int((math.sin(t * math.pi * 2 + 0) * 0.5 + 0.5) * 255)
        g = int((math.sin(t * math.pi * 2 + 2.09) * 0.5 + 0.5) * 255)
        b = int((math.sin(t * math.pi * 2 + 4.19) * 0.5 + 0.5) * 255)
        prefix = "\033[1m" if bold else ""
        out.append(f"{prefix}{_rgb(r,g,b)}{ch}\033[0m")
    return "".join(out)

def th_accent(): return ACTIVE_THEME["accent"]
def th_hi():     return ACTIVE_THEME["hi"]
def th_ghost():  return _rgb(*ACTIVE_THEME["ghost"])

def fix_win():
    if platform.system() == "Windows":
        os.system("color")
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except: pass

TW = 72

def clr(): os.system("cls" if platform.system() == "Windows" else "clear")

def row(label, val, lc=None, vc=c.W):
    lc = lc or th_accent()
    print(f"  {lc}{c.B}{label:<24}{c.R}  {vc}{val}{c.R}")

def ok(msg):   print(f"\n  {c.G}{c.B}[+]{c.R}  {c.W}{msg}{c.R}")
def err(msg):  print(f"\n  {c.R1}{c.B}[-]{c.R}  {c.R1}{msg}{c.R}")
def warn(msg): print(f"\n  {c.Y}{c.B}[!]{c.R}  {c.Y}{msg}{c.R}")
def inf(msg):  print(f"\n  {c.BL}{c.B}[*]{c.R}  {c.W}{msg}{c.R}")
def inp(msg):  return input(f"\n  {c.M}{c.B}[>]{c.R}  {c.Y}{msg}{c.R}  ").strip()

def sep(ch="─", w=None): print(f"  {c.D}{ch * ((w or TW) - 4)}{c.R}")

def pause(): input(f"\n  {c.D}[ENTER] back to menu...{c.R}")

def section(title, col=None):
    col = col or th_accent()
    bar = "─" * max(0, TW - 8 - len(title))
    print(f"\n  {col}{c.B}──── {title} {bar}{c.R}\n")


# ──────────────────────────────────────────────────────────────
#  BRAILLE ART ASSETS
# ──────────────────────────────────────────────────────────────

# Same ghost used in both splash and banner
GHOST = [
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣠⣤⣤⣤⡴⣶⣶⠆⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣷⣿⣶⣿⣧⣤⣤⣤⣄⣀⣀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⠿⠿⠛⠛⠛⠋⠉⠉⠛⠛⠛⠿⠟⠛⠛⠛⠛⠛⣻⣿⣿⠋⠀",
    "⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⠟⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣟⡁⠀⠀",
    "⠀⠀⠀⠀⣠⣾⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠴⠿⠿⣿⣿⣷⣦⡀⠀",
    "⠀⠀⠀⢰⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣶⣄",
    "⠀⠀⠀⢸⣿⣿⣿⣦⣤⣤⣀⣀⣀⣀⣠⣤⠴⠖⠋⢉⣽⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙",
    "⠀⠀⢠⣿⠟⠉⠁⠈⠉⠙⠛⠛⠿⠿⣿⣿⣿⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⢠⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠽⠟⠛⠉⠀⢀⣀⣤⣴⣶⣶⣶⣶⣶⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⣿⣿⣿⣷⣶⣦⣤⣤⣤⠄⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠈⠉⠛⠿⣿⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀",
    "⢸⣿⠘⢿⣿⣿⠿⠛⠉⠀⠀⠀⢀⣀⣤⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀",
    "⠈⣿⣴⣿⣿⣄⠀⠀⠀⣀⣠⣴⠶⣿⣿⠋⠉⠉⠙⢻⣿⡆⠀⠀⠀⠀⠀⣀⣴⣶⣿⣿⣿⣿⣿⣷⡄⠀⠀",
    "⠀⢹⣿⡍⠛⠻⢷⣶⣶⠟⢿⣿⠗⠀⡀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢀⣴⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠂⠀",
    "⠀⠀⢻⡇⠀⠀⠀⢻⣿⣿⠈⠛⠀⢹⠇⠀⠀⠀⢶⣿⠇⠀⢀⣴⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠁⠀⠀⠀⠀⠹⡇⠀⠀⠀⣀⡾⠀⠀⠀⢸⡿⠀⣠⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⣦⠀⢠⣿⢳⠀⠙⣿⣿⢰⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣿⣷⡾⠿⠃⢸⣷⣀⢀⣾⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⠻⠷⢾⣿⣿⣷⡿⢸⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⢿⣷⣄⠀⠉⠛⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣦⣄⡀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣿⣾⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠿⠧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
]

TITLE_ART = [
    "    ____  __  _____    _   ________  __  ___  ",
    "   / __ \\/ / / /   |  / | / /_  __/ / / / _ | ",
    "  / /_/ / /_/ / /| | /  |/ / / /   / /_/ /| | ",
    " / .___/\\____/_/ | |/ /|  / / /   / __  / _  | ",
    "/_/         /_/ |_/_/ |_/ /_/   /_/ /_/ |_|  v4.0",
]

TAGLINE = "Multi-Purpose Hacking & Utility Toolkit"
CREDIT  = "made by extort"

GHOST_SMALL = [
    "  ⠀⠀⠀⣀⣤⣶⣿⣿⣶⣤⣀⠀⠀⠀",
    "  ⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀",
    "  ⠀⣾⣿⡟⠛⠉⠉⠉⠉⠛⢻⣿⣷⠀",
    "  ⠀⣿⣿⣇⠀⣠⡀⢀⣠⠀⣸⣿⣿⠀",
    "  ⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀",
    "  ⠀⣿⡿⠿⡿⠿⠿⠿⠿⢿⠿⢿⣿⠀",
    "  ⠀⢸⣿⠀⠙⠛⠛⠛⠛⠋⠀⣿⡇⠀",
    "  ⠀⠈⢿⣷⣤⣀⣀⣀⣀⣤⣾⡿⠁⠀",
    "  ⠀⠀⠀⠉⠛⠿⣿⣿⠿⠛⠉⠀⠀⠀",
]

# ──────────────────────────────────────────────────────────────
#  ANIMATED BACKGROUNDS
# ──────────────────────────────────────────────────────────────
import math, random as _rnd

def _stars_frame(width=78, height=22, seed=0):
    """Render one frame of a starfield."""
    _rnd.seed(seed)
    stars = [(int(_rnd.random()*width), int(_rnd.random()*height),
              _rnd.choice("·✦✧⋆★☆*·")) for _ in range(55)]
    grid = [[' ']*width for _ in range(height)]
    for sx, sy, ch in stars:
        if 0 <= sy < height and 0 <= sx < width:
            grid[sy][sx] = ch
    a, b = ACTIVE_THEME["grad_a"], ACTIVE_THEME["grad_b"]
    lines = []
    for row_data in grid:
        line = ""
        for ci, ch in enumerate(row_data):
            if ch != ' ':
                t = ci / width
                rgb = _lerp(a, b, t)
                bri = _rnd.uniform(0.4, 1.0)
                rgb = (int(rgb[0]*bri), int(rgb[1]*bri), int(rgb[2]*bri))
                line += f"{_rgb(*rgb)}{c.B}{ch}\033[0m"
            else:
                line += ' '
        lines.append(line)
    return lines

def _city_frame(width=78, height=22, tick=0):
    """Render a cyberpunk cityscape with animated windows."""
    a, b2 = ACTIVE_THEME["grad_a"], ACTIVE_THEME["grad_b"]
    buildings = [
        (0, 16, 8, 22), (9, 12, 15, 22), (16, 14, 22, 22),
        (23, 10, 30, 22),(31, 15, 36, 22),(37, 8, 46, 22),
        (47, 13, 53, 22),(54, 11, 60, 22),(61, 14, 67, 22),
        (68, 9, 78, 22),
    ]
    grid = [[' ']*width for _ in range(height)]
    # Draw buildings
    for bx1, by1, bx2, by2 in buildings:
        for row_i in range(by1, min(by2, height)):
            for col_i in range(bx1, min(bx2, width)):
                grid[row_i][col_i] = '█'
        # Roof
        if by1 > 0 and by1-1 < height:
            for col_i in range(bx1, min(bx2, width)):
                grid[by1-1][col_i] = '▀'
        # Windows
        for wr in range(by1+1, by2-1, 3):
            for wc in range(bx1+1, bx2-1, 3):
                if wr < height and wc < width:
                    lit = (tick + wr*7 + wc*3) % 17 < 12
                    grid[wr][wc] = '▪' if lit else '▫'
    # Ground
    for col_i in range(width):
        if height-1 < height:
            grid[height-1][col_i] = '▬'
    lines = []
    for ri, row_data in enumerate(grid):
        line = ""
        for ci, ch in enumerate(row_data):
            t = ci / max(1, width)
            rgb = _lerp(a, b2, t)
            if ch in ('▪',):  # lit window
                wr2, wg2, wb2 = 255, 220, 80
                line += f"{_rgb(wr2,wg2,wb2)}{c.B}{ch}\033[0m"
            elif ch == '▫':  # dark window
                line += f"\033[2m{_rgb(*rgb)}{ch}\033[0m"
            elif ch in ('█','▀','▬'):
                bri = 0.5 + 0.5*(1 - ri/height)
                cr = (int(rgb[0]*bri), int(rgb[1]*bri), int(rgb[2]*bri))
                line += f"{_rgb(*cr)}{ch}\033[0m"
            else:
                line += ch
        lines.append(line)
    return lines

def _matrix_frame(width=78, height=22, tick=0):
    """Render a matrix-rain style background."""
    _rnd.seed(tick * 17)
    chars = "ｦｧｨｩｪｫｬ0123456789ABCDEF@#$%"
    a, b2 = ACTIVE_THEME["grad_a"], ACTIVE_THEME["grad_b"]
    lines = []
    for ri in range(height):
        line = ""
        for ci in range(width):
            if _rnd.random() < 0.08:
                ch = _rnd.choice(chars)
                bri = _rnd.uniform(0.3, 1.0)
                t = ci / max(1, width)
                rgb = _lerp(a, b2, t)
                rgb = (int(rgb[0]*bri), int(rgb[1]*bri), int(rgb[2]*bri))
                line += f"{_rgb(*rgb)}{c.B}{ch}\033[0m"
            else:
                line += " "
        lines.append(line)
    return lines

def _get_bg_frame(tick=0, width=78, height=22):
    style = ACTIVE_THEME.get("splash", "stars")
    if style == "city":    return _city_frame(width, height, tick)
    elif style == "matrix": return _matrix_frame(width, height, tick)
    else:                  return _stars_frame(width, height, tick % 999)

def _render_splash_frame(tick, ghost_lines, title_lines, width=78):
    """Composite: background + ghost + title + credit box."""
    HEIGHT = 26
    bg = _get_bg_frame(tick, width, HEIGHT)
    # Composite ghost + title side by side into bg
    gh = len(ghost_lines); th = len(title_lines); top = (gh - th) // 2
    for i, gl in enumerate(ghost_lines):
        ti = i - top
        tl = f"   {title_lines[ti]}" if 0 <= ti < th else ""
        row_str = f"  {th_ghost()}{gl}\033[0m{tl}"
        if i < HEIGHT:
            bg[i] = row_str
    return bg

# ──────────────────────────────────────────────────────────────
#  SPLASH  (animated — runs frames until ENTER)
# ──────────────────────────────────────────────────────────────
def splash():
    import threading as _thr, sys as _sys
    clr()
    grad_title = gradient_text(TITLE_ART, shimmer=True)

    # Non-blocking keypress detection
    entered = [False]
    def wait_enter():
        input()
        entered[0] = True
    wt = _thr.Thread(target=wait_enter, daemon=True); wt.start()

    tick = 0
    print(f"\033[?25l", end="", flush=True)  # hide cursor
    try:
        while not entered[0]:
            _ANIM_OFFSET[0] = tick
            grad_title = gradient_text(TITLE_ART, shimmer=True)
            bg = _render_splash_frame(tick, GHOST, grad_title)
            print("\033[H", end="")  # move cursor home
            WIDTH = 78
            for line in bg:
                print(line[:WIDTH] if len(line) > WIDTH else line)

            # Credit box with pulsing border
            wave = math.sin(tick * 0.2) * 0.5 + 0.5
            a, b2 = ACTIVE_THEME["grad_a"], ACTIVE_THEME["grad_b"]
            pulse_a = (int(a[0]*wave + b2[0]*(1-wave)),
                       int(a[1]*wave + b2[1]*(1-wave)),
                       int(a[2]*wave + b2[2]*(1-wave)))
            box_top = gradient_single(f"╔{'═'*24}╗", pulse_a, b2)
            box_mid = gradient_single(f"║   {CREDIT}{'':7}║",  a, pulse_a)
            box_bot = gradient_single(f"╚{'═'*24}╝", b2, pulse_a)
            print(f"\n  \033[1m{box_top}")
            print(f"  \033[1m{box_mid}")
            print(f"  \033[1m{box_bot}\033[0m")
            tl = gradient_single(f"── {TAGLINE} ──", shimmer=True)
            print(f"\n  \033[1m{tl}\033[0m")
            print(f"\n  \033[2m[ press ENTER to enter the phantom... ]\033[0m  ", end="", flush=True)
            time.sleep(0.08); tick += 1
    finally:
        print("\033[?25h", end="", flush=True)  # restore cursor
    clr()

# ──────────────────────────────────────────────────────────────
#  BANNER  (shown on every menu refresh — subtle animated bg)
# ──────────────────────────────────────────────────────────────
def banner():
    clr()
    _ANIM_OFFSET[0] = (_ANIM_OFFSET[0] + 8) % 200
    grad_title = gradient_text(TITLE_ART, shimmer=True)
    gh = len(GHOST_SMALL); th = len(grad_title); top = (gh - th) // 2

    # Subtle background strip (5 rows)
    bg_strip = _get_bg_frame(_ANIM_OFFSET[0], 78, 5)
    bg_idx = 0
    for i, gl in enumerate(GHOST_SMALL):
        ti = i - top
        tl = f"   {grad_title[ti]}" if 0 <= ti < th else ""
        # blend ghost over bg strip
        bg_row = bg_strip[bg_idx % 5] if bg_strip else ""
        bg_idx += 1
        print(f"{th_ghost()}{gl}\033[0m{tl}")

    print()
    # Shimmer credit line
    credit_line = gradient_single(
        f"{'═'*4}  {CREDIT}  ·  {ACTIVE_THEME['name']} theme  {'═'*4}",
        shimmer=True)
    print(f"  \033[1m{credit_line}\033[0m")
    sep("═"); print()

# ──────────────────────────────────────────────────────────────
#  MENU
# ──────────────────────────────────────────────────────────────
CATEGORIES = [
    ("INFORMATION GATHERING", c.C, [
        ("01", "System Information",        "system_info"),
        ("02", "Network Info & Public IP",  "net_info"),
        ("03", "Whois Lookup",              "whois_lookup"),
        ("04", "DNS Lookup",                "dns_lookup"),
        ("05", "IP Geolocation",            "ip_geo"),
    ]),
    ("NETWORK TOOLS", c.G, [
        ("06", "Ping a Host",               "ping_host"),
        ("07", "IP Range Pinger",           "ip_range_ping"),
        ("08", "Port Scanner",              "port_scanner"),
        ("09", "Traceroute",                "traceroute"),
        ("10", "Subnet Calculator",         "subnet_calc"),
        ("11", "WiFi Manager",              "wifi_offliner"),
        ("12", "Network Speed Test",        "speed_test"),
        ("13", "Open Connections",          "open_connections"),
        ("14", "ARP Table Viewer",          "arp_table"),
        ("15", "Firewall Rule Viewer",      "firewall_view"),
        ("16", "Bandwidth Monitor",         "bandwidth_mon"),
        ("17", "Latency & Jitter Monitor",  "latency_monitor"),
        ("18", "Packet Loss Analyzer",      "packet_loss"),
        ("19", "Connection Stability Log",  "stability_log"),
        ("20", "Localhost Throughput Test", "localhost_stress"),
    ]),
    ("ENCRYPTION & ENCODING", c.Y, [
        ("21", "Hash Generator",            "hash_gen"),
        ("22", "Base64 Encode / Decode",    "b64_tool"),
        ("23", "ROT13 Cipher",              "rot13_tool"),
        ("24", "Caesar Cipher",             "caesar_tool"),
        ("25", "Password Generator",        "pass_gen"),
    ]),
    ("FILE & SYSTEM TOOLS", c.M, [
        ("26", "File Manager",              "file_manager"),
        ("27", "File Hash Checker",         "file_hash"),
        ("28", "System Resource Monitor",   "sys_monitor"),
        ("29", "Environment Variables",     "env_vars"),
        ("30", "Running Processes",         "proc_list"),
    ]),
    ("WEB & OTHER", c.BL, [
        ("31", "Weather Lookup",            "weather"),
        ("32", "HTTP Header Grabber",       "http_headers"),
        ("33", "URL Encoder / Decoder",     "url_tool"),
        ("34", "MAC Address Lookup",        "mac_lookup"),
        ("35", "ASCII Art Generator",       "ascii_art"),
    ]),
    ("MESSAGING", c.BL, [
        ("36", "Discord Tools",             "discord_tools"),
        ("37", "Telegram Tools",            "telegram_tools"),
    ]),
    ("OSINT & RECON", c.R1, [
        ("38", "Oathnet Domain Search",       "oathnet_tools"),
        ("39", "Anonymity & Privacy Check",   "anon_tools"),
        ("40", "Social Media Finder",         "social_finder"),
        ("41", "Forensic File Analysis",      "forensic_tools"),
        ("42", "Steganography Tools",         "stego_tools"),
        ("43", "OSINT Framework",             "osint_framework"),
        ("47", "Network Deep Lookup",         "network_lookup"),
        ("48", "Discord User Lookup",         "discord_lookup"),
    ]),
    ("PHANTOM AI & SETUP", c.M, [
        ("44", "Phantom AI Assistant",        "ai_assistant"),
        ("45", "Themes",                      "themes_menu"),
        ("46", "Install All Dependencies",    "install_deps"),
    ]),
]

def main_menu():
    banner()
    for cat_name, col, items in CATEGORIES:
        print(f"  {col}{c.B}  ── {cat_name} ──{c.R}")
        for num, label, _ in items:
            print(f"    {c.D}[{c.R}{c.B}{col}{num}{c.R}{c.D}]{c.R}  {c.W}{label}{c.R}")
        print()
    sep()
    print(f"    {c.D}[{c.R}{c.B}{c.R1}00{c.R}{c.D}]{c.R}  {c.D}Exit{c.R}   "
          f"{c.D}[{c.R}{c.C}home{c.R}{c.D}]{c.R}  {c.D}Return to splash{c.R}\n")
    return inp("Select module")

def get_func(num):
    key = num.zfill(2)
    for _, _, items in CATEGORIES:
        for n, _, fn in items:
            if n == key:
                return fn
    return None

# ──────────────────────────────────────────────────────────────
#  01  SYSTEM INFO
# ──────────────────────────────────────────────────────────────
def system_info():
    section("SYSTEM INFORMATION")
    row("OS",          f"{platform.system()} {platform.release()}")
    row("OS Version",  platform.version()[:52])
    row("Architecture",platform.machine())
    row("Processor",   (platform.processor() or "N/A")[:52])
    row("Hostname",    socket.gethostname())
    try:    row("Local IP", socket.gethostbyname(socket.gethostname()))
    except: row("Local IP", "unavailable")
    row("Python",      sys.version.split()[0])
    row("Date/Time",   datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
    row("CWD",         os.getcwd()[:52])
    try:
        import psutil
        row("CPU Cores",   str(psutil.cpu_count(logical=True)))
        row("CPU Usage",   f"{psutil.cpu_percent(interval=0.5)}%")
        m = psutil.virtual_memory()
        row("RAM Total",   f"{m.total//(1024**3)} GB")
        row("RAM Used",    f"{m.percent}%")
        d = psutil.disk_usage("/")
        row("Disk Total",  f"{d.total//(1024**3)} GB")
        row("Disk Used",   f"{d.percent}%")
    except ImportError:
        warn("pip install psutil  for extended stats")
    pause()

# ──────────────────────────────────────────────────────────────
#  02  NETWORK INFO
# ──────────────────────────────────────────────────────────────
def net_info():
    section("NETWORK INFORMATION")
    row("Hostname", socket.gethostname())
    try:    row("Local IP", socket.gethostbyname(socket.gethostname()))
    except: pass
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=6) as r:
            row("Public IP", json.loads(r.read())["ip"])
    except Exception as e:
        row("Public IP", f"unavailable ({e})")
    try:
        import psutil
        for name, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET:
                    row(f"  [{name}]", a.address)
    except ImportError: pass
    pause()

# ──────────────────────────────────────────────────────────────
#  03  WHOIS
# ──────────────────────────────────────────────────────────────
def whois_lookup():
    section("WHOIS LOOKUP")
    target = inp("Domain or IP")
    if not target: return
    inf(f"Querying whois for {target} ...")
    if platform.system() == "Windows":
        warn("whois not built-in on Windows. Install Sysinternals whois.")
        pause(); return
    result = subprocess.run(["whois", target], capture_output=True, text=True, timeout=15)
    lines = [l for l in result.stdout.splitlines() if l.strip() and not l.startswith("%")]
    for line in lines[:45]:
        print(f"  {c.W}{line}{c.R}")
    if len(lines) > 45:
        inf(f"...{len(lines)-45} lines truncated")
    pause()

# ──────────────────────────────────────────────────────────────
#  04  DNS LOOKUP
# ──────────────────────────────────────────────────────────────
def dns_lookup():
    section("DNS LOOKUP")
    host = inp("Hostname or IP")
    if not host: return
    try:
        ip = socket.gethostbyname(host)
        ok(f"Resolved: {ip}")
        full = socket.gethostbyname_ex(host)
        if full[1]: row("Aliases",  ", ".join(full[1]))
        if len(full[2]) > 1: row("All IPs", ", ".join(full[2]))
    except socket.gaierror as e:
        err(f"Forward lookup failed: {e}")
    try:
        rev = socket.gethostbyaddr(socket.gethostbyname(host))[0]
        row("Reverse DNS", rev)
    except: pass
    pause()

# ──────────────────────────────────────────────────────────────
#  05  IP GEOLOCATION
# ──────────────────────────────────────────────────────────────
def ip_geo():
    section("IP GEOLOCATION")
    ip = inp("IP address (blank = your IP)")
    url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            d = json.loads(r.read())
        if d.get("status") == "fail":
            err(d.get("message","Lookup failed")); pause(); return
        for k in ["query","country","regionName","city","zip","isp","org","timezone","lat","lon"]:
            if d.get(k): row(k.capitalize(), str(d[k]))
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  06  PING HOST
# ──────────────────────────────────────────────────────────────
def ping_host():
    section("PING HOST")
    host = inp("Host / IP")
    if not host: return
    try: count = int(inp("Count (default 4)") or "4")
    except: count = 4
    param = ["-n", str(count)] if platform.system() == "Windows" else ["-c", str(count)]
    inf(f"Pinging {host} × {count}...")
    try:
        result = subprocess.run(["ping"] + param + [host], capture_output=True, text=True, timeout=30)
        print(f"\n{c.W}{result.stdout}{c.R}")
        if result.returncode != 0 and result.stderr:
            err(result.stderr.strip())
    except subprocess.TimeoutExpired:
        err("Ping timed out.")
    except FileNotFoundError:
        err("ping command not found.")
    pause()

# ──────────────────────────────────────────────────────────────
#  07  IP RANGE PINGER
# ──────────────────────────────────────────────────────────────
def _ping_one(ip_str, results, lock):
    if platform.system() == "Windows":
        param = ["-n","1","-w","800"]
    else:
        param = ["-c","1","-W","1"]
    try:
        r = subprocess.run(["ping"] + param + [ip_str],
                           capture_output=True, text=True, timeout=3)
        alive = r.returncode == 0
    except Exception:
        alive = False
    with lock:
        results.append((ip_str, alive))

def ip_range_ping():
    section("IP RANGE PINGER")
    print(f"  {c.D}Examples:  192.168.1.0/24   10.0.0.1-10.0.0.50   192.168.1.5{c.R}\n")
    target = inp("CIDR / range / single IP")
    if not target: return

    ips = []
    try:
        if "/" in target:
            net = ipaddress.ip_network(target, strict=False)
            ips = [str(h) for h in net.hosts()]
            if len(ips) > 512:
                warn(f"{len(ips)} hosts — capping at 512.")
                ips = ips[:512]
        elif "-" in target:
            parts = [p.strip() for p in target.split("-")]
            start = ipaddress.ip_address(parts[0])
            end   = ipaddress.ip_address(parts[1])
            cur = start
            while cur <= end and len(ips) < 512:
                ips.append(str(cur)); cur += 1
        else:
            ips = [str(ipaddress.ip_address(target))]
    except ValueError as e:
        err(str(e)); pause(); return

    inf(f"Scanning {len(ips)} host(s) — multithreaded...\n")
    results = []; lock = threading.Lock()
    threads = [threading.Thread(target=_ping_one, args=(ip, results, lock), daemon=True) for ip in ips]

    for i in range(0, len(threads), 64):
        batch = threads[i:i+64]
        for t in batch: t.start()
        for t in batch: t.join()
        print(f"  {c.D}Progress: {min(i+64,len(threads))}/{len(threads)}{c.R}", end="\r")

    print()
    results.sort(key=lambda x: [int(p) for p in x[0].split(".")])
    alive = [r for r in results if r[1]]
    dead  = [r for r in results if not r[1]]

    sep()
    if alive:
        print(f"\n  {c.G}{c.B}ALIVE ({len(alive)}){c.R}")
        for ip, _ in alive:
            try:    hn = f"  {c.D}({socket.gethostbyaddr(ip)[0]}){c.R}"
            except: hn = ""
            print(f"    {c.G}●  {ip:<18}{c.R}{hn}")
    else:
        warn("No hosts responded.")
    print(f"\n  {c.D}No response: {len(dead)}{c.R}")
    sep()
    ok(f"Done. {len(alive)}/{len(ips)} alive.")
    pause()

# ──────────────────────────────────────────────────────────────
#  08  PORT SCANNER
# ──────────────────────────────────────────────────────────────
COMMON_PORTS = {
    21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 53:"DNS",
    80:"HTTP", 110:"POP3", 143:"IMAP", 443:"HTTPS", 445:"SMB",
    3306:"MySQL", 3389:"RDP", 5432:"PostgreSQL", 6379:"Redis",
    8080:"HTTP-Alt", 8443:"HTTPS-Alt", 27017:"MongoDB",
    5000:"Flask/Dev", 9200:"Elasticsearch", 11211:"Memcached",
}

def _scan_port(host, port, results, lock):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        if s.connect_ex((host, port)) == 0:
            with lock: results.append(port)
        s.close()
    except: pass

def port_scanner():
    section("PORT SCANNER")
    host = inp("Target host / IP")
    if not host: return
    print(f"\n  {c.D}[1] Common ports ({len(COMMON_PORTS)})   [2] Custom range   [3] Single port{c.R}")
    mode = inp("Mode") or "1"

    if mode == "1":
        ports = list(COMMON_PORTS.keys())
    elif mode == "3":
        try: ports = [int(inp("Port number"))]
        except: err("Invalid port."); pause(); return
    else:
        try:
            s = int(inp("Start port") or "1")
            e = int(inp("End port")   or "1024")
            ports = list(range(s, min(e+1, s+10001)))
        except: ports = list(range(1,1025))

    inf(f"Scanning {host}  [{len(ports)} ports] ...")
    results = []; lock = threading.Lock()
    threads = [threading.Thread(target=_scan_port, args=(host,p,results,lock), daemon=True) for p in ports]
    for i in range(0, len(threads), 128):
        batch = threads[i:i+128]
        for t in batch: t.start()
        for t in batch: t.join()

    results.sort()
    sep()
    if results:
        print(f"\n  {c.G}{c.B}OPEN PORTS  ({len(results)} found){c.R}")
        for p in results:
            svc = COMMON_PORTS.get(p, "")
            if not svc:
                try: svc = socket.getservbyport(p)
                except: svc = "unknown"
            print(f"    {c.G}●  {c.W}{c.B}{p:<7}{c.R}  {c.C}{svc}{c.R}")
        ok(f"{len(results)} open port(s).")
    else:
        warn("No open ports found in range.")
    pause()

# ──────────────────────────────────────────────────────────────
#  09  TRACEROUTE
# ──────────────────────────────────────────────────────────────
def traceroute():
    section("TRACEROUTE")
    host = inp("Target host / IP")
    if not host: return
    if platform.system() == "Windows":
        cmd = ["tracert", host]
    else:
        # prefer traceroute, fall back to tracepath
        if subprocess.run(["which","traceroute"], capture_output=True).returncode == 0:
            cmd = ["traceroute", host]
        elif subprocess.run(["which","tracepath"], capture_output=True).returncode == 0:
            cmd = ["tracepath", host]
        else:
            err("Neither traceroute nor tracepath found.\n  sudo apt install traceroute")
            pause(); return
    inf(f"Tracing route to {host}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        print(f"\n{c.W}{result.stdout}{c.R}")
        if result.returncode != 0 and result.stderr:
            warn(result.stderr.strip())
    except subprocess.TimeoutExpired:
        warn("Traceroute timed out after 90s.")
    pause()

# ──────────────────────────────────────────────────────────────
#  10  SUBNET CALCULATOR
# ──────────────────────────────────────────────────────────────
def subnet_calc():
    section("SUBNET CALCULATOR")
    cidr = inp("CIDR  (e.g. 192.168.1.0/24  or  10.0.0.5/16)")
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        row("Network Address", str(net.network_address))
        row("Broadcast",       str(net.broadcast_address))
        row("Netmask",         str(net.netmask))
        row("Wildcard Mask",   str(net.hostmask))
        row("Prefix Length",   f"/{net.prefixlen}")
        row("Total Addresses", f"{net.num_addresses:,}")
        row("Usable Hosts",    f"{max(0, net.num_addresses - 2):,}")
        row("IP Class",        f"IPv{net.version}")
        row("Is Private",      str(net.is_private))
        if net.num_addresses <= 1024:
            hosts = list(net.hosts())
            if hosts:
                row("First Host", str(hosts[0]))
                row("Last Host",  str(hosts[-1]))
        # Split into 2 subnets
        if net.prefixlen < 31:
            subs = list(net.subnets())
            row("Subnet A",  str(subs[0]))
            row("Subnet B",  str(subs[1]))
    except ValueError as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  11  WIFI MANAGER
# ──────────────────────────────────────────────────────────────
def wifi_offliner():
    section("WiFi MANAGER", c.R1)
    warn("Only use on networks/interfaces you own or have permission to test.")
    os_name = platform.system()

    if os_name == "Linux":
        # detect wireless interfaces
        ifaces = []
        try:
            r = subprocess.run(["iwconfig"], capture_output=True, text=True)
            out = r.stdout + r.stderr
            for line in out.splitlines():
                if line and not line.startswith(" ") and "no wireless" not in line:
                    iface = line.split()[0]
                    if iface: ifaces.append(iface)
        except FileNotFoundError: pass
        if not ifaces:
            try:
                r2 = subprocess.run(["ls","/sys/class/net"], capture_output=True, text=True)
                ifaces = r2.stdout.split()
            except: ifaces = ["wlan0"]

        print(f"\n  {c.C}{c.B}Detected interfaces:{c.R}")
        for i, f in enumerate(ifaces):
            print(f"    {c.Y}[{i}]  {f}{c.R}")

        print(f"\n  {c.D}[1] Take interface DOWN (disconnect)")
        print(f"  [2] Bring interface UP (reconnect)")
        print(f"  [3] Toggle WiFi via nmcli")
        print(f"  [4] Disconnect named network (nmcli)")
        print(f"  [5] List saved WiFi networks{c.R}")
        mode = inp("Mode")

        iface = inp("Interface (e.g. wlan0)") if mode in ("1","2") else ""

        if mode == "1" and iface:
            r = subprocess.run(["sudo","ip","link","set",iface,"down"], capture_output=True, text=True)
            ok(f"{iface} DOWN") if r.returncode == 0 else err(r.stderr.strip() or "Need root.")
        elif mode == "2" and iface:
            r = subprocess.run(["sudo","ip","link","set",iface,"up"], capture_output=True, text=True)
            ok(f"{iface} UP") if r.returncode == 0 else err(r.stderr.strip() or "Need root.")
        elif mode == "3":
            r = subprocess.run(["nmcli","radio","wifi"], capture_output=True, text=True)
            state = r.stdout.strip()
            inf(f"Current WiFi state: {state}")
            if "enabled" in state.lower():
                if inp("Turn OFF? (yes/no)").lower() == "yes":
                    r2 = subprocess.run(["sudo","nmcli","radio","wifi","off"], capture_output=True, text=True)
                    ok("WiFi OFF") if r2.returncode == 0 else err(r2.stderr.strip())
            else:
                if inp("Turn ON? (yes/no)").lower() == "yes":
                    r2 = subprocess.run(["sudo","nmcli","radio","wifi","on"], capture_output=True, text=True)
                    ok("WiFi ON") if r2.returncode == 0 else err(r2.stderr.strip())
        elif mode == "4":
            r = subprocess.run(["nmcli","-t","-f","NAME,TYPE,STATE","con","show","--active"],
                                capture_output=True, text=True)
            conns = [l.split(":")[0] for l in r.stdout.splitlines() if "wireless" in l.lower()]
            if conns:
                for i, con in enumerate(conns): print(f"    {c.Y}[{i}]  {con}{c.R}")
                name = inp("Connection name")
                r2 = subprocess.run(["sudo","nmcli","con","down",name], capture_output=True, text=True)
                ok(f"Disconnected '{name}'") if r2.returncode==0 else err(r2.stderr.strip())
            else:
                warn("No active wireless connections found.")
        elif mode == "5":
            r = subprocess.run(["nmcli","-f","NAME,TYPE","con","show"], capture_output=True, text=True)
            for line in r.stdout.splitlines():
                if "wifi" in line.lower() or "wireless" in line.lower() or "NAME" in line:
                    print(f"  {c.W}{line}{c.R}")

    elif os_name == "Windows":
        print(f"\n  {c.D}[1] Disable WiFi adapter")
        print(f"  [2] Enable WiFi adapter")
        print(f"  [3] List saved WiFi profiles")
        print(f"  [4] Show WiFi password for profile")
        print(f"  [5] Delete saved WiFi profile{c.R}")
        mode = inp("Mode")
        if mode in ("1","2"):
            iface = inp("Adapter name (default: Wi-Fi)") or "Wi-Fi"
            action = "disable" if mode == "1" else "enable"
            r = subprocess.run(["netsh","interface","set","interface",iface,action],
                                capture_output=True, text=True)
            ok(f"Adapter '{iface}' {action}d") if r.returncode==0 else err(r.stdout.strip())
        elif mode == "3":
            r = subprocess.run(["netsh","wlan","show","profiles"], capture_output=True, text=True)
            print(f"\n{c.W}{r.stdout}{c.R}")
        elif mode == "4":
            profile = inp("Profile name")
            r = subprocess.run(["netsh","wlan","show","profile",f"name={profile}","key=clear"],
                                capture_output=True, text=True)
            for line in r.stdout.splitlines():
                if "Key Content" in line or "SSID" in line or "Authentication" in line:
                    print(f"  {c.W}{line.strip()}{c.R}")
        elif mode == "5":
            profile = inp("Profile name to delete")
            r = subprocess.run(["netsh","wlan","delete","profile",f"name={profile}"],
                                capture_output=True, text=True)
            ok(r.stdout.strip()) if r.returncode==0 else err(r.stdout.strip())

    elif os_name == "Darwin":
        print(f"\n  {c.D}[1] Turn WiFi off")
        print(f"  [2] Turn WiFi on")
        print(f"  [3] List preferred networks{c.R}")
        mode = inp("Mode"); iface = "en0"
        if mode == "1":
            r = subprocess.run(["networksetup","-setairportpower",iface,"off"], capture_output=True, text=True)
            ok("WiFi OFF") if r.returncode==0 else err(r.stderr.strip())
        elif mode == "2":
            r = subprocess.run(["networksetup","-setairportpower",iface,"on"], capture_output=True, text=True)
            ok("WiFi ON") if r.returncode==0 else err(r.stderr.strip())
        elif mode == "3":
            r = subprocess.run(["networksetup","-listpreferredwirelessnetworks",iface],
                                capture_output=True, text=True)
            print(f"\n{c.W}{r.stdout}{c.R}")
    else:
        err(f"Unsupported OS: {os_name}")
    pause()

# ──────────────────────────────────────────────────────────────
#  12  NETWORK SPEED TEST
# ──────────────────────────────────────────────────────────────
def speed_test():
    section("NETWORK SPEED TEST")
    inf("Testing download speed via HTTP (no external lib needed)...")
    test_urls = [
        ("Cloudflare 10MB", "https://speed.cloudflare.com/__down?bytes=10000000"),
        ("GitHub (fallback)", "https://github.com/git/git/archive/refs/heads/master.zip"),
    ]
    for name, url in test_urls:
        try:
            inf(f"Connecting to {name}...")
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            start = time.time()
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read(10_000_000)   # read up to 10 MB
            elapsed = time.time() - start
            size_mb = len(data) / (1024*1024)
            speed   = size_mb / elapsed
            row("Downloaded",  f"{size_mb:.2f} MB")
            row("Time",        f"{elapsed:.2f} s")
            row("Speed",       f"{speed:.2f} MB/s  ({speed*8:.1f} Mbps)")
            break
        except Exception as e:
            warn(f"{name} failed: {e}")
    pause()

# ──────────────────────────────────────────────────────────────
#  13  OPEN CONNECTIONS
# ──────────────────────────────────────────────────────────────
def open_connections():
    section("OPEN NETWORK CONNECTIONS")
    try:
        import psutil
        conns = psutil.net_connections(kind="inet")
        print(f"  {c.C}{c.B}{'PROTO':<7}{'LOCAL':<26}{'REMOTE':<26}{'STATUS':<14}PID{c.R}")
        sep()
        for con in sorted(conns, key=lambda x: x.status):
            proto  = "TCP" if con.type == socket.SOCK_STREAM else "UDP"
            laddr  = f"{con.laddr.ip}:{con.laddr.port}" if con.laddr else "-"
            raddr  = f"{con.raddr.ip}:{con.raddr.port}" if con.raddr else "-"
            status = con.status or "-"
            pid    = str(con.pid) if con.pid else "-"
            col    = c.G if status == "ESTABLISHED" else c.Y if status == "LISTEN" else c.D
            print(f"  {col}{proto:<7}{laddr:<26}{raddr:<26}{status:<14}{pid}{c.R}")
    except ImportError:
        # fallback: netstat
        if platform.system() == "Windows":
            cmd = ["netstat","-ano"]
        else:
            cmd = ["ss","-tunp"] if subprocess.run(["which","ss"],capture_output=True).returncode==0 else ["netstat","-tunp"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines()[:50]:
                print(f"  {c.W}{line}{c.R}")
        except Exception as e:
            err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  14  ARP TABLE
# ──────────────────────────────────────────────────────────────
def arp_table():
    section("ARP TABLE")
    try:
        import psutil
        # net_if_stats for interface list
        pass
    except ImportError: pass

    if platform.system() == "Windows":
        cmd = ["arp","-a"]
    else:
        cmd = ["arp","-n"] if subprocess.run(["which","arp"],capture_output=True).returncode==0 else ["ip","neigh"]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            print(f"\n  {c.C}{c.B}{'IP ADDRESS':<20}{'MAC ADDRESS':<22}TYPE{c.R}")
            sep()
            for line in r.stdout.splitlines():
                if line.strip() and not line.startswith("Address") and not line.startswith("Interface"):
                    print(f"  {c.W}{line}{c.R}")
        else:
            err(r.stderr.strip())
    except FileNotFoundError:
        # Try /proc/net/arp on Linux
        try:
            with open("/proc/net/arp") as f:
                print(f"\n  {c.C}{c.B}{f.readline().strip()}{c.R}")
                sep()
                for line in f:
                    print(f"  {c.W}{line.strip()}{c.R}")
        except Exception as e2:
            err(str(e2))
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  15  FIREWALL RULE VIEWER
# ──────────────────────────────────────────────────────────────
def firewall_view():
    section("FIREWALL RULE VIEWER")
    os_name = platform.system()

    if os_name == "Linux":
        print(f"  {c.D}[1] iptables rules   [2] ufw status   [3] nftables{c.R}")
        mode = inp("Mode") or "1"
        if mode == "1":
            r = subprocess.run(["sudo","iptables","-L","-n","--line-numbers"],
                                capture_output=True, text=True, timeout=10)
            print(f"\n{c.W}{r.stdout or r.stderr}{c.R}")
        elif mode == "2":
            r = subprocess.run(["sudo","ufw","status","verbose"], capture_output=True, text=True, timeout=10)
            print(f"\n{c.W}{r.stdout or r.stderr}{c.R}")
        elif mode == "3":
            r = subprocess.run(["sudo","nft","list","ruleset"], capture_output=True, text=True, timeout=10)
            print(f"\n{c.W}{r.stdout or r.stderr}{c.R}")

    elif os_name == "Windows":
        print(f"  {c.D}[1] All rules (brief)   [2] Inbound   [3] Outbound{c.R}")
        mode = inp("Mode") or "1"
        if mode == "2":
            dir_flag = "dir=in"
        elif mode == "3":
            dir_flag = "dir=out"
        else:
            dir_flag = None
        if dir_flag:
            cmd = ["netsh","advfirewall","firewall","show","rule","name=all", dir_flag]
        else:
            cmd = ["netsh","advfirewall","show","currentprofile"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        lines = r.stdout.splitlines()[:80]
        for line in lines:
            print(f"  {c.W}{line}{c.R}")

    elif os_name == "Darwin":
        r = subprocess.run(["sudo","pfctl","-sr"], capture_output=True, text=True, timeout=10)
        print(f"\n{c.W}{r.stdout or r.stderr}{c.R}")
    else:
        err(f"Unsupported OS: {os_name}")
    pause()

# ──────────────────────────────────────────────────────────────
#  16  BANDWIDTH MONITOR
# ──────────────────────────────────────────────────────────────
def bandwidth_mon():
    section("BANDWIDTH MONITOR")
    try:
        import psutil
        inf("Sampling bandwidth over 5 seconds (press Ctrl+C to stop early)...\n")
        try:
            for tick in range(1, 8):
                stats1 = psutil.net_io_counters(pernic=True)
                time.sleep(1)
                stats2 = psutil.net_io_counters(pernic=True)
                print(f"  {c.C}{c.B}{'INTERFACE':<16}{'↓ RECV/s':>14}{'↑ SENT/s':>14}{c.R}")
                sep(w=50)
                for nic in stats2:
                    if nic in stats1:
                        recv = (stats2[nic].bytes_recv - stats1[nic].bytes_recv)
                        sent = (stats2[nic].bytes_sent - stats1[nic].bytes_sent)
                        if recv > 100 or sent > 100:  # filter idle
                            def fmt(b):
                                if b > 1048576: return f"{b/1048576:.2f} MB/s"
                                if b > 1024:    return f"{b/1024:.1f} KB/s"
                                return f"{b} B/s"
                            rc = c.G if recv > 0 else c.D
                            sc = c.Y if sent > 0 else c.D
                            print(f"  {c.W}{nic:<16}{c.R}{rc}{fmt(recv):>14}{c.R}{sc}{fmt(sent):>14}{c.R}")
                if tick < 7:
                    print(f"\n  {c.D}── tick {tick}/7 ──{c.R}\n")
        except KeyboardInterrupt:
            pass
    except ImportError:
        warn("pip install psutil  for this module")
        # fallback: /proc/net/dev
        if platform.system() == "Linux":
            try:
                with open("/proc/net/dev") as f:
                    print(f"\n{c.W}{f.read()}{c.R}")
            except: pass
    pause()

# ──────────────────────────────────────────────────────────────
#  17  HASH GENERATOR
# ──────────────────────────────────────────────────────────────
def hash_gen():
    section("HASH GENERATOR")
    text = inp("Text to hash")
    if not text: return
    enc = text.encode()
    for name, fn in [("MD5",    hashlib.md5),
                     ("SHA-1",  hashlib.sha1),
                     ("SHA-224",hashlib.sha224),
                     ("SHA-256",hashlib.sha256),
                     ("SHA-384",hashlib.sha384),
                     ("SHA-512",hashlib.sha512)]:
        row(name, fn(enc).hexdigest(), lc=c.Y)
    pause()

# ──────────────────────────────────────────────────────────────
#  18  BASE64
# ──────────────────────────────────────────────────────────────
def b64_tool():
    section("BASE64 ENCODE / DECODE")
    print(f"  {c.D}[1] Encode   [2] Decode{c.R}")
    mode = inp("Mode"); text = inp("Input text")
    if not text: return
    try:
        if mode == "1":
            ok(f"Encoded:\n\n  {c.W}{c.B}{base64.b64encode(text.encode()).decode()}{c.R}")
        else:
            ok(f"Decoded:\n\n  {c.W}{c.B}{base64.b64decode(text.encode()).decode()}{c.R}")
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  19  ROT13
# ──────────────────────────────────────────────────────────────
def rot13_tool():
    section("ROT13 CIPHER")
    text = inp("Text")
    if not text: return
    result = text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))
    ok(f"Result:  {c.W}{c.B}{result}{c.R}")
    pause()

# ──────────────────────────────────────────────────────────────
#  20  CAESAR CIPHER
# ──────────────────────────────────────────────────────────────
def caesar_tool():
    section("CAESAR CIPHER")
    print(f"  {c.D}[1] Encode   [2] Decode   [3] Bruteforce all 25 shifts{c.R}")
    mode = inp("Mode"); text = inp("Text")
    if not text: return

    def shift(t, n):
        out = []
        for ch in t:
            if ch.isalpha():
                b = ord('A') if ch.isupper() else ord('a')
                out.append(chr((ord(ch)-b+n)%26+b))
            else: out.append(ch)
        return "".join(out)

    if mode == "1":
        try: n = int(inp("Shift (1-25)") or "3")
        except: n = 3
        ok(f"Encoded:  {c.W}{c.B}{shift(text, n)}{c.R}")
    elif mode == "2":
        try: n = int(inp("Shift (1-25)") or "3")
        except: n = 3
        ok(f"Decoded:  {c.W}{c.B}{shift(text, -n)}{c.R}")
    else:
        print()
        for i in range(1, 26):
            print(f"  {c.C}[{i:>2}]{c.R}  {c.W}{shift(text, i)}{c.R}")
    pause()

# ──────────────────────────────────────────────────────────────
#  21  PASSWORD GENERATOR
# ──────────────────────────────────────────────────────────────
def pass_gen():
    section("PASSWORD GENERATOR")
    try:    length = int(inp("Length (default 20)") or "20")
    except: length = 20
    use_u = inp("Uppercase? (y/n)").lower() != "n"
    use_l = inp("Lowercase? (y/n)").lower() != "n"
    use_d = inp("Digits? (y/n)").lower() != "n"
    use_s = inp("Symbols? (y/n)").lower() != "n"
    try:    count = int(inp("How many? (default 8)") or "8")
    except: count = 8

    charset = ""
    if use_u: charset += string.ascii_uppercase
    if use_l: charset += string.ascii_lowercase
    if use_d: charset += string.digits
    if use_s: charset += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not charset: err("No charset selected."); pause(); return

    sep()
    for i in range(count):
        pw  = "".join(secrets.choice(charset) for _ in range(length))
        col = c.R1 if length < 8 else c.Y if length < 14 else c.G
        lvl = "WEAK" if length < 8 else "MEDIUM" if length < 14 else "STRONG"
        print(f"  {c.D}{i+1:>2}.{c.R}  {c.W}{c.B}{pw}{c.R}  {col}[{lvl}]{c.R}")
    pause()

# ──────────────────────────────────────────────────────────────
#  22  FILE MANAGER
# ──────────────────────────────────────────────────────────────
def file_manager():
    cwd = os.getcwd()
    while True:
        section(f"FILE MANAGER  {cwd[:50]}")
        print(f"  {c.D}Commands: ls  cd <path>  cat <file>  del <file>  new <file>  q (back){c.R}\n")
        cmd = inp("Command")
        if not cmd or cmd.lower() == "q": break
        parts = cmd.split(None, 1)
        op = parts[0].lower(); arg = parts[1] if len(parts) > 1 else ""

        if op == "ls":
            try:
                entries = sorted(os.listdir(cwd))
                if not entries: inf("Empty directory.")
                for e in entries:
                    fp = os.path.join(cwd, e)
                    if os.path.isdir(fp):
                        print(f"  {c.C}{c.B}  d  {e}/{c.R}")
                    else:
                        sz = os.path.getsize(fp)
                        mt = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
                        print(f"  {c.W}  -  {e:<42}{c.D}{sz:>10,} B  {mt}{c.R}")
            except PermissionError: err("Permission denied")

        elif op == "cd":
            if not arg: arg = inp("Path")
            t = os.path.abspath(os.path.join(cwd, arg))
            if os.path.isdir(t): cwd = t; ok(f"→ {cwd}")
            else: err("Not a directory.")

        elif op == "cat":
            if not arg: arg = inp("Filename")
            fp = os.path.join(cwd, arg)
            if os.path.isfile(fp):
                try:
                    with open(fp,"r",errors="replace") as fh:
                        lines = fh.readlines()
                    for i, l in enumerate(lines[:200], 1):
                        print(f"  {c.D}{i:>4}{c.R}  {c.W}{l}", end="")
                    if len(lines) > 200: inf(f"...{len(lines)-200} more lines")
                except Exception as e: err(str(e))
            else: err("File not found.")

        elif op == "del":
            if not arg: arg = inp("Filename")
            fp = os.path.join(cwd, arg)
            if os.path.isfile(fp):
                if inp(f"Delete '{arg}'? (yes/no)").lower() == "yes":
                    try: os.remove(fp); ok("Deleted.")
                    except Exception as e: err(str(e))
            else: err("File not found.")

        elif op == "new":
            if not arg: arg = inp("Filename")
            content = inp("Content (single line)")
            try:
                with open(os.path.join(cwd, arg),"w") as fh: fh.write(content+"\n")
                ok(f"Created '{arg}'")
            except Exception as e: err(str(e))
        else:
            warn(f"Unknown command: {op}")

# ──────────────────────────────────────────────────────────────
#  23  FILE HASH
# ──────────────────────────────────────────────────────────────
def file_hash():
    section("FILE HASH CHECKER")
    path = inp("File path")
    if not path: return
    if not os.path.isfile(path): err("File not found."); pause(); return
    try:
        with open(path,"rb") as f: data = f.read()
        row("File",    path)
        row("Size",    f"{len(data):,} bytes")
        row("MD5",     hashlib.md5(data).hexdigest(),    lc=c.Y)
        row("SHA-1",   hashlib.sha1(data).hexdigest(),   lc=c.Y)
        row("SHA-256", hashlib.sha256(data).hexdigest(), lc=c.Y)
        row("SHA-512", hashlib.sha512(data).hexdigest(), lc=c.Y)
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  24  SYSTEM MONITOR
# ──────────────────────────────────────────────────────────────
def sys_monitor():
    section("SYSTEM RESOURCE MONITOR")
    try:
        import psutil
        def bar(pct, w=28):
            f = int(w*pct/100)
            col = c.G if pct<60 else c.Y if pct<85 else c.R1
            return f"{col}{'█'*f}{c.D}{'░'*(w-f)}{c.R}  {pct:.1f}%"

        inf("Live monitor — press Ctrl+C to stop.\n")
        try:
            while True:
                cpu = psutil.cpu_percent(interval=0.5)
                mem = psutil.virtual_memory()
                dsk = psutil.disk_usage("/")
                print(f"\r  {c.C}CPU{c.R}  {bar(cpu)}   {c.C}RAM{c.R}  {bar(mem.percent)}   "
                      f"{c.C}DISK{c.R}  {bar(dsk.percent)}   ", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            ok("Monitor stopped.")
    except ImportError:
        warn("pip install psutil  for live monitoring.")
        # fallback: read /proc/loadavg
        if platform.system() == "Linux":
            try:
                with open("/proc/loadavg") as f:
                    row("Load average", f.read().strip())
            except: pass
    pause()

# ──────────────────────────────────────────────────────────────
#  25  ENVIRONMENT VARIABLES
# ──────────────────────────────────────────────────────────────
def env_vars():
    section("ENVIRONMENT VARIABLES")
    search = inp("Filter (blank = show all)").lower()
    count = 0
    for k, v in sorted(os.environ.items()):
        if not search or search in k.lower() or search in v.lower():
            row(k[:24], v[:56]); count += 1
    inf(f"{count} variable(s) shown.")
    pause()

# ──────────────────────────────────────────────────────────────
#  26  PROCESSES
# ──────────────────────────────────────────────────────────────
def proc_list():
    section("RUNNING PROCESSES")
    try:
        import psutil
        procs = []
        for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent","status"]):
            try: procs.append(p.info)
            except: pass
        procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
        print(f"  {c.C}{c.B}{'PID':<8}{'CPU%':<8}{'MEM%':<8}{'STATUS':<12}NAME{c.R}"); sep()
        for p in procs[:30]:
            cpu = p.get("cpu_percent") or 0
            mem = p.get("memory_percent") or 0
            col = c.R1 if cpu>50 else c.Y if cpu>15 else c.G
            print(f"  {c.D}{p['pid']:<8}{c.R}{col}{cpu:<8.1f}{c.R}{c.W}{mem:<8.1f}"
                  f"{(p.get('status') or ''):<12}{(p.get('name') or '')[:35]}{c.R}")
    except ImportError:
        cmd = ["tasklist"] if platform.system()=="Windows" else ["ps","aux","--sort=-pcpu"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines()[:35]:
                print(f"  {c.W}{line}{c.R}")
        except Exception as e: err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  27  WEATHER
# ──────────────────────────────────────────────────────────────
def weather():
    section("WEATHER LOOKUP")
    city = inp("City name")
    if not city: return
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent":"curl/7.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        cur  = d["current_condition"][0]
        area = d["nearest_area"][0]
        loc  = f"{area['areaName'][0]['value']}, {area['country'][0]['value']}"
        row("Location",   loc)
        row("Condition",  cur["weatherDesc"][0]["value"])
        row("Temp",       f"{cur['temp_C']}°C  /  {cur['temp_F']}°F")
        row("Feels Like", f"{cur['FeelsLikeC']}°C  /  {cur['FeelsLikeF']}°F")
        row("Humidity",   f"{cur['humidity']}%")
        row("Wind",       f"{cur['windspeedKmph']} km/h  {cur['winddir16Point']}")
        row("Visibility", f"{cur['visibility']} km")
        row("UV Index",   cur.get("uvIndex","N/A"))
        row("Cloud Cover",f"{cur.get('cloudcover','N/A')}%")
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  28  HTTP HEADERS
# ──────────────────────────────────────────────────────────────
def http_headers():
    section("HTTP HEADER GRABBER")
    url = inp("URL  (e.g. https://example.com)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Phantom-Toolkit)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            row("Status Code",  str(r.status))
            row("URL",          r.url[:60])
            sep()
            for k, v in r.headers.items():
                row(k[:28], v[:52])
    except urllib.error.HTTPError as e:
        row("HTTP Error", str(e.code))
        for k, v in e.headers.items():
            row(k[:28], v[:52])
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  29  URL TOOL
# ──────────────────────────────────────────────────────────────
def url_tool():
    section("URL ENCODER / DECODER")
    print(f"  {c.D}[1] Encode   [2] Decode   [3] Parse URL components{c.R}")
    mode = inp("Mode"); text = inp("Input")
    if not text: return
    if mode == "1":
        ok(f"Encoded:\n\n  {c.W}{c.B}{urllib.parse.quote(text)}{c.R}")
    elif mode == "3":
        p = urllib.parse.urlparse(text)
        for k, v in [("Scheme",p.scheme),("Netloc",p.netloc),("Path",p.path),
                     ("Params",p.params),("Query",p.query),("Fragment",p.fragment)]:
            if v: row(k, v)
    else:
        ok(f"Decoded:\n\n  {c.W}{c.B}{urllib.parse.unquote(text)}{c.R}")
    pause()

# ──────────────────────────────────────────────────────────────
#  30  MAC LOOKUP
# ──────────────────────────────────────────────────────────────
def mac_lookup():
    section("MAC ADDRESS LOOKUP")
    mac = inp("MAC address  (e.g. 00:1A:2B:3C:4D:5E)")
    if not mac: return
    prefix = mac.replace(":","").replace("-","").replace(".","")[:6].upper()
    try:
        url = f"https://api.maclookup.app/v2/macs/{prefix}"
        req = urllib.request.Request(url, headers={"User-Agent":"Phantom-Toolkit"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        row("MAC Prefix", prefix)
        row("Company",    d.get("company","Unknown"))
        row("Country",    d.get("country","N/A"))
        row("Type",       d.get("type","N/A"))
        row("Is Valid",   str(d.get("isValid", "N/A")))
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  31  ASCII ART
# ──────────────────────────────────────────────────────────────
def ascii_art():
    section("ASCII ART GENERATOR")
    text = inp("Text to convert")
    if not text: return
    try:
        import pyfiglet
        fonts = ["slant","banner3","doom","cyberlarge","blocks","big"]
        font  = inp(f"Font ({'/'.join(fonts)}, default=slant)") or "slant"
        try:
            art = pyfiglet.figlet_format(text, font=font)
        except pyfiglet.FontNotFound:
            art = pyfiglet.figlet_format(text, font="slant")
        print(f"\n{c.C}{c.B}{art}{c.R}")
    except ImportError:
        # simple manual bigtext using block chars
        print(f"\n  {c.C}{c.B}{'  '.join(f'[{ch}]' for ch in text.upper())}{c.R}")
        warn("For full ASCII art:  pip install pyfiglet")
    pause()

# ──────────────────────────────────────────────────────────────
#  17  LATENCY & JITTER MONITOR
# ──────────────────────────────────────────────────────────────
def latency_monitor():
    section("LATENCY & JITTER MONITOR", c.G)
    host  = inp("Target host (default: 8.8.8.8)") or "8.8.8.8"
    try:    count = int(inp("Number of pings (default 20)") or "20")
    except: count = 20

    inf(f"Pinging {host} × {count}  — measuring latency & jitter...\n")

    param = ["-n","1","-w","2000"] if platform.system()=="Windows" else ["-c","1","-W","2"]
    times = []

    print(f"  {c.C}{c.B}{'#':<5}{'RTT':>10}{'STATUS':>12}{c.R}")
    sep(w=40)

    for i in range(1, count+1):
        t0 = time.time()
        try:
            r = subprocess.run(["ping"]+param+[host], capture_output=True, text=True, timeout=4)
            elapsed = (time.time()-t0)*1000
            if r.returncode == 0:
                # try to parse actual RTT from ping output
                rtt = None
                for line in r.stdout.splitlines():
                    for kw in ["time=","time<","Zeit="]:
                        if kw in line:
                            try:
                                part = line.split(kw)[1].split()[0].replace("ms","").strip()
                                rtt = float(part)
                            except: pass
                rtt = rtt or elapsed
                times.append(rtt)
                col = c.G if rtt < 50 else c.Y if rtt < 150 else c.R1
                print(f"  {c.D}{i:<5}{c.R}{col}{rtt:>8.1f} ms{c.R}{c.G}{'  ALIVE':>10}{c.R}")
            else:
                print(f"  {c.D}{i:<5}{c.R}{'':>10}{c.R1}{'  TIMEOUT':>12}{c.R}")
        except Exception:
            print(f"  {c.D}{i:<5}{c.R}{'':>10}{c.R1}{'  ERROR':>12}{c.R}")
        time.sleep(0.3)

    if times:
        sep(w=40)
        avg    = sum(times)/len(times)
        mn     = min(times)
        mx     = max(times)
        jitter = sum(abs(times[i]-times[i-1]) for i in range(1,len(times))) / max(1,len(times)-1)
        loss   = ((count - len(times)) / count) * 100

        print(f"\n  {c.C}{c.B}── RESULTS ──────────────────{c.R}")
        row("Host",         host)
        row("Sent",         str(count))
        row("Received",     str(len(times)))
        row("Packet Loss",  f"{loss:.1f}%", vc=c.R1 if loss>5 else c.G)
        row("Min RTT",      f"{mn:.1f} ms")
        row("Max RTT",      f"{mx:.1f} ms")
        row("Avg RTT",      f"{avg:.1f} ms", vc=c.G if avg<50 else c.Y if avg<150 else c.R1)
        row("Jitter",       f"{jitter:.1f} ms", vc=c.G if jitter<10 else c.Y if jitter<30 else c.R1)

        # Mini sparkline
        if len(times) > 1:
            bars = " ▁▂▃▄▅▆▇█"
            lo, hi = min(times), max(times)
            rng = hi - lo or 1
            spark = "".join(bars[min(8, int((t-lo)/rng*8))] for t in times)
            print(f"\n  {c.D}Sparkline:{c.R}  {c.C}{spark}{c.R}")
    else:
        err("No responses received.")
    pause()

# ──────────────────────────────────────────────────────────────
#  18  PACKET LOSS ANALYZER
# ──────────────────────────────────────────────────────────────
def packet_loss():
    section("PACKET LOSS ANALYZER", c.G)
    host  = inp("Target host (default: 8.8.8.8)") or "8.8.8.8"
    try:    count = int(inp("Packets to send (default 50)") or "50")
    except: count = 50

    if platform.system() == "Windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), "-i", "0.2", host]

    inf(f"Sending {count} packets to {host}...\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=count*2+10)
        output = result.stdout

        # Print raw summary lines
        summary_lines = []
        for line in output.splitlines():
            ll = line.lower()
            if any(kw in ll for kw in ["packet","loss","transmitted","received",
                                        "statistics","rtt","round-trip","avg","min","max"]):
                summary_lines.append(line)

        if summary_lines:
            print(f"  {c.C}{c.B}── Raw Summary ──────────────────{c.R}")
            for l in summary_lines:
                print(f"  {c.W}{l.strip()}{c.R}")
        else:
            # Print last 10 lines of output
            for l in output.splitlines()[-12:]:
                print(f"  {c.W}{l}{c.R}")

        # Parse loss %
        loss_pct = None
        for line in output.splitlines():
            if "loss" in line.lower() or "%" in line:
                import re
                m = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
                if m:
                    loss_pct = float(m.group(1))
                    break

        print()
        sep(w=50)
        if loss_pct is not None:
            col = c.G if loss_pct == 0 else c.Y if loss_pct < 10 else c.R1
            quality = "Excellent" if loss_pct==0 else "Good" if loss_pct<5 else "Fair" if loss_pct<15 else "Poor"
            row("Packet Loss",   f"{loss_pct:.1f}%", vc=col)
            row("Link Quality",  quality,            vc=col)
        if result.returncode != 0 and not output.strip():
            err("Could not reach host or ping failed.")

    except subprocess.TimeoutExpired:
        err("Test timed out.")
    except Exception as e:
        err(str(e))
    pause()

# ──────────────────────────────────────────────────────────────
#  19  CONNECTION STABILITY LOGGER
# ──────────────────────────────────────────────────────────────
def stability_log():
    section("CONNECTION STABILITY LOGGER", c.G)
    host     = inp("Host to monitor (default: 8.8.8.8)") or "8.8.8.8"
    try:    interval = float(inp("Ping interval seconds (default 2)") or "2")
    except: interval = 2.0
    try:    duration = int(inp("Duration in seconds (default 60, 0=forever)") or "60")
    except: duration = 60

    param = ["-n","1","-w","1500"] if platform.system()=="Windows" else ["-c","1","-W","2"]

    inf(f"Monitoring {host}  every {interval}s" + (f"  for {duration}s" if duration else "  until Ctrl+C") + "\n")
    print(f"  {c.C}{c.B}{'TIME':<12}{'STATUS':<12}{'RTT':>10}{'STREAK'}{c.R}")
    sep(w=52)

    sent = 0; received = 0; streak_up = 0; streak_dn = 0
    log = []
    start = time.time()

    try:
        while True:
            if duration and (time.time()-start) >= duration:
                break

            ts  = datetime.now().strftime("%H:%M:%S")
            t0  = time.time()
            try:
                r   = subprocess.run(["ping"]+param+[host], capture_output=True, text=True, timeout=3)
                rtt = (time.time()-t0)*1000
                alive = r.returncode == 0

                # parse real RTT
                for line in r.stdout.splitlines():
                    for kw in ["time=","time<","Zeit="]:
                        if kw in line:
                            try:
                                rtt = float(line.split(kw)[1].split()[0].replace("ms",""))
                            except: pass
            except Exception:
                alive = False; rtt = 0

            sent += 1
            if alive:
                received += 1; streak_up += 1; streak_dn = 0
                status_str = f"{c.G}  UP      {c.R}"
                rtt_str    = f"{c.G}{rtt:>8.1f} ms{c.R}"
                streak_str = f"{c.G}  ↑ {streak_up} up{c.R}"
            else:
                streak_dn += 1; streak_up = 0
                status_str = f"{c.R1}  DOWN    {c.R}"
                rtt_str    = f"{c.R1}{'timeout':>10}{c.R}"
                streak_str = f"{c.R1}  ↓ {streak_dn} dn{c.R}"

            log.append((ts, alive, rtt if alive else None))
            print(f"  {c.D}{ts:<12}{c.R}{status_str}{rtt_str}{streak_str}")
            time.sleep(interval)

    except KeyboardInterrupt:
        pass

    # Summary
    print()
    sep(w=52)
    loss = ((sent-received)/sent*100) if sent else 0
    rtts = [r for _,a,r in log if a and r]
    print(f"\n  {c.C}{c.B}── SESSION SUMMARY ──────────────{c.R}")
    row("Host",        host)
    row("Duration",    f"{time.time()-start:.0f}s")
    row("Pings Sent",  str(sent))
    row("Successful",  str(received))
    row("Packet Loss", f"{loss:.1f}%", vc=c.G if loss==0 else c.Y if loss<10 else c.R1)
    if rtts:
        row("Min RTT",  f"{min(rtts):.1f} ms")
        row("Max RTT",  f"{max(rtts):.1f} ms")
        row("Avg RTT",  f"{sum(rtts)/len(rtts):.1f} ms")

    # Downtime events
    downs = [(i, ts) for i,(ts,a,_) in enumerate(log) if not a]
    if downs:
        warn(f"{len(downs)} timeout event(s) recorded.")
    else:
        ok("No downtime detected during session.")
    pause()

# ──────────────────────────────────────────────────────────────
#  20  LOCALHOST THROUGHPUT TEST
# ──────────────────────────────────────────────────────────────
def localhost_stress():
    section("LOCALHOST THROUGHPUT TEST", c.G)
    print(f"  {c.W}Tests your local network stack throughput using loopback (127.0.0.1).{c.R}")
    print(f"  {c.D}This only tests your own machine — no traffic leaves your computer.{c.R}\n")

    try:    size_mb = int(inp("Data size MB to transfer (default 100)") or "100")
    except: size_mb = 100
    try:    chunk_kb = int(inp("Chunk size KB (default 64)") or "64")
    except: chunk_kb = 64

    CHUNK = chunk_kb * 1024
    TOTAL = size_mb * 1024 * 1024
    PORT  = 19876
    results = {"sent": 0, "recv": 0, "time": 0, "error": None}

    def server_thread():
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", PORT))
            srv.listen(1)
            srv.settimeout(10)
            conn, _ = srv.accept()
            received = 0
            while received < TOTAL:
                data = conn.recv(CHUNK)
                if not data: break
                received += len(data)
            results["recv"] = received
            conn.close(); srv.close()
        except Exception as e:
            results["error"] = str(e)

    srv_t = threading.Thread(target=server_thread, daemon=True)
    srv_t.start()
    time.sleep(0.2)   # let server start

    inf(f"Transferring {size_mb} MB over loopback...")
    payload = b"X" * CHUNK
    try:
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.connect(("127.0.0.1", PORT))
        sent = 0
        t_start = time.time()
        while sent < TOTAL:
            remaining = TOTAL - sent
            chunk = payload if remaining >= CHUNK else b"X" * remaining
            cli.sendall(chunk)
            sent += len(chunk)
            pct = sent / TOTAL * 100
            bar_w = 30
            filled = int(bar_w * sent / TOTAL)
            bar = f"{c.G}{'█'*filled}{c.D}{'░'*(bar_w-filled)}{c.R}"
            print(f"\r  {bar}  {pct:5.1f}%  {sent//(1024*1024)} MB", end="", flush=True)
        elapsed = time.time() - t_start
        results["sent"] = sent
        results["time"] = elapsed
        cli.close()
    except Exception as e:
        results["error"] = str(e)

    srv_t.join(timeout=5)
    print()

    if results["error"]:
        err(f"Test failed: {results['error']}")
    else:
        sent_mb  = results["sent"] / (1024*1024)
        elapsed  = results["time"]
        speed_mb = sent_mb / elapsed if elapsed > 0 else 0
        speed_gb = speed_mb / 1024

        sep(w=50)
        print(f"\n  {c.C}{c.B}── THROUGHPUT RESULTS ───────────{c.R}")
        row("Data Transferred", f"{sent_mb:.1f} MB")
        row("Time",             f"{elapsed:.3f} s")
        row("Throughput",       f"{speed_mb:.0f} MB/s  ({speed_mb*8:.0f} Mbps)",
            vc=c.G if speed_mb > 500 else c.Y if speed_mb > 100 else c.R1)
        if speed_gb >= 1:
            row("",             f"≈ {speed_gb:.2f} GB/s")
        row("Chunk Size",       f"{chunk_kb} KB")
        ok("Loopback test complete.")
    pause()


# ──────────────────────────────────────────────────────────────
#  32  PHANTOM AI ASSISTANT
# ──────────────────────────────────────────────────────────────
PHANTOM_AI_SYSTEM = (
    "You are Phantom, an AI assistant built into the Phantom Toolkit by extort. "
    "You are knowledgeable, direct, and slightly mysterious. You help with cybersecurity "
    "concepts, networking, coding, system administration, and general questions. "
    "Keep responses concise and useful. You speak with confidence but never help with "
    "illegal activities or harming others."
)

def ai_assistant():
    section("PHANTOM AI ASSISTANT", c.M)
    print(f"  {c.M}{c.B}👻  Phantom AI  —  powered by Claude{c.R}")
    print(f"  {c.D}Type your message. 'exit' or 'quit' to return. 'clear' to reset chat.{c.R}\n")

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        warn("ANTHROPIC_API_KEY not set in environment.")
        print(f"\n  {c.D}Set it with:{c.R}")
        if platform.system() == "Windows":
            print(f"  {c.Y}  set ANTHROPIC_API_KEY=your_key_here{c.R}")
        else:
            print(f"  {c.Y}  export ANTHROPIC_API_KEY=your_key_here{c.R}")
        print(f"\n  {c.D}Get a free key at: https://console.anthropic.com{c.R}")
        pause()
        return

    history = []

    def call_claude(messages):
        payload = json.dumps({
            "model":      "claude-haiku-4-5-20251001",
            "max_tokens": 1024,
            "system":     PHANTOM_AI_SYSTEM,
            "messages":   messages,
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data    = payload,
            method  = "POST",
            headers = {
                "Content-Type":      "application/json",
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    while True:
        try:
            user_input = input(f"\n  {c.C}{c.B}You{c.R}  {c.D}»{c.R}  ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "back", "q"):
            break
        if user_input.lower() == "clear":
            history = []
            ok("Chat history cleared.")
            continue

        history.append({"role": "user", "content": user_input})

        inf("Thinking...")
        try:
            response = call_claude(history)
            reply = response["content"][0]["text"]
            history.append({"role": "assistant", "content": reply})

            # Pretty-print the reply
            print(f"\n  {c.M}{c.B}Phantom{c.R}  {c.D}»{c.R}")
            sep(w=60)
            # Word-wrap at ~66 chars
            words = reply.split()
            line = "  "
            for word in words:
                if len(line) + len(word) + 1 > 68:
                    print(f"{c.W}{line}{c.R}")
                    line = "  " + word
                else:
                    line += (" " if line != "  " else "") + word
            if line.strip():
                print(f"{c.W}{line}{c.R}")
            sep(w=60)

            # Trim history to last 10 exchanges to avoid token overflow
            if len(history) > 20:
                history = history[-20:]

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                msg = json.loads(body).get("error",{}).get("message", body)
            except: msg = body
            err(f"API error {e.code}: {msg}")
        except Exception as e:
            err(f"Connection error: {e}")


# ──────────────────────────────────────────────────────────────
#  33  INSTALL ALL DEPENDENCIES
# ──────────────────────────────────────────────────────────────
REQUIRED_PACKAGES = [
    ("psutil",   "psutil",   "System/process/network monitoring"),
    ("pyfiglet", "pyfiglet", "ASCII art generation"),
    ("requests", "requests", "HTTP requests (optional fallback)"),
]

def install_deps():
    section("INSTALL ALL DEPENDENCIES", c.G)
    print(f"  {c.W}This will install all optional packages to unlock full toolkit features.{c.R}\n")

    print(f"  {c.C}{c.B}Packages to install:{c.R}")
    for pkg, _, desc in REQUIRED_PACKAGES:
        print(f"    {c.G}●  {c.W}{pkg:<16}{c.D}  {desc}{c.R}")

    print()
    confirm = inp("Proceed with installation? (yes/no)")
    if confirm.lower() != "yes":
        warn("Installation cancelled.")
        pause()
        return

    # Detect pip command
    pip_cmd = None
    for candidate in ["pip3", "pip", sys.executable + " -m pip"]:
        parts = candidate.split()
        try:
            r = subprocess.run(parts + ["--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                pip_cmd = parts
                break
        except: continue

    if not pip_cmd:
        err("pip not found. Install Python pip first.")
        pause()
        return

    inf(f"Using: {' '.join(pip_cmd)}")
    print()

    results = []
    for pkg, install_name, desc in REQUIRED_PACKAGES:
        print(f"  {c.BL}{c.B}[*]{c.R}  Installing {c.W}{pkg}{c.R}...", end=" ", flush=True)
        try:
            r = subprocess.run(
                pip_cmd + ["install", "--upgrade", install_name],
                capture_output=True, text=True, timeout=120
            )
            if r.returncode == 0:
                # Check if already up to date
                if "already satisfied" in r.stdout.lower():
                    print(f"{c.D}already up to date{c.R}")
                    results.append((pkg, "up-to-date"))
                else:
                    print(f"{c.G}✔ installed{c.R}")
                    results.append((pkg, "installed"))
            else:
                print(f"{c.R1}✘ failed{c.R}")
                results.append((pkg, "failed"))
                if r.stderr:
                    print(f"  {c.D}{r.stderr.strip()[:100]}{c.R}")
        except subprocess.TimeoutExpired:
            print(f"{c.Y}✘ timeout{c.R}")
            results.append((pkg, "timeout"))
        except Exception as e:
            print(f"{c.R1}✘ error: {e}{c.R}")
            results.append((pkg, "error"))

    sep()
    ok_count  = sum(1 for _, s in results if s in ("installed","up-to-date"))
    fail_count= sum(1 for _, s in results if s not in ("installed","up-to-date"))

    print(f"\n  {c.G}{c.B}[+] {ok_count}/{len(REQUIRED_PACKAGES)} packages OK{c.R}")
    if fail_count:
        warn(f"{fail_count} package(s) failed — try running as administrator/root.")

    # Check API key for AI
    print()
    sep()
    print(f"\n  {c.M}{c.B}Phantom AI Setup{c.R}")
    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if api_key:
        ok("ANTHROPIC_API_KEY is already set. AI Assistant ready.")
    else:
        warn("ANTHROPIC_API_KEY not set.")
        print(f"  {c.D}To enable Phantom AI, set your key:{c.R}")
        if platform.system() == "Windows":
            print(f"  {c.Y}  set ANTHROPIC_API_KEY=sk-ant-...{c.R}")
            print(f"  {c.D}  (add to System Environment Variables for persistence){c.R}")
        else:
            print(f"  {c.Y}  export ANTHROPIC_API_KEY=sk-ant-...{c.R}")
            print(f"  {c.D}  (add to ~/.bashrc or ~/.zshrc for persistence){c.R}")
        print(f"  {c.D}  Get a key: https://console.anthropic.com{c.R}")
    pause()


# ──────────────────────────────────────────────────────────────
#  THEMES
# ──────────────────────────────────────────────────────────────
def themes_menu():
    global ACTIVE_THEME
    while True:
        clr()
        section("THEMES", c.M)
        print(f"  {gradient_single('Choose your visual style — each theme changes gradients + background animation', bold=False)}\n")
        keys = list(THEMES.keys())

        BG_ICONS = {"stars": "✦ Stars", "city": "🏙 City", "matrix": "⬛ Matrix"}

        for i, key in enumerate(keys, 1):
            t   = THEMES[key]
            cur = ACTIVE_THEME["name"] == t["name"]

            # Full gradient swatch — 12 smooth steps
            a_rgb = t["grad_a"]; b_rgb = t["grad_b"]
            swatch = ""
            steps = 14
            for si in range(steps):
                frac = si / max(1, steps - 1)
                rgb  = _lerp(a_rgb, b_rgb, frac)
                swatch += f"{_rgb(*rgb)}█\033[0m"

            # Ghost color dot
            gr, gg, gb = t["ghost"]
            ghost_dot = f"{_rgb(gr,gg,gb)}◆\033[0m"

            # Background style badge
            bg_label = BG_ICONS.get(t.get("splash","stars"), "✦ Stars")

            # Active marker with shimmer
            if cur:
                marker = f"  {gradient_single('◀ ACTIVE', t['grad_a'], t['grad_b'])}"
            else:
                marker = ""

            num_col = gradient_single(str(i), a_rgb, b_rgb)
            name_col = f"{_rgb(*a_rgb)}{c.B}{t['name']:<10}\033[0m"
            print(f"  {c.D}[{c.R}{num_col}{c.D}]{c.R}  {swatch}  {ghost_dot}  "
                  f"{name_col}  {c.D}{t['desc']:<34}{c.R}  {c.D}{bg_label}{c.R}{marker}")

        print(f"\n  {c.D}[{c.R}{c.B}P{c.R}{c.D}]{c.R}  {c.W}Preview animation{c.R}   "
              f"{c.D}[{c.R}{c.B}R{c.R}{c.D}]{c.R}  {c.W}Random theme{c.R}   "
              f"{c.D}[{c.R}{c.R1}0{c.R}{c.D}]{c.R}  {c.D}Back{c.R}\n")

        choice = inp("Select theme")
        if not choice or choice == "0": break

        if choice.upper() == "R":
            import random as _r
            rkey = _r.choice(keys)
            ACTIVE_THEME = dict(THEMES[rkey])
            clr(); banner()
            ok(f"Random theme: {ACTIVE_THEME['name']}")
            time.sleep(1.0)
            continue

        if choice.upper() == "P":
            # Live preview — cycle through all themes
            inf("Previewing all themes (2s each)... press Ctrl+C to stop")
            try:
                for key in keys:
                    ACTIVE_THEME = dict(THEMES[key])
                    clr(); banner()
                    tname = ACTIVE_THEME["name"]
                    tdesc = ACTIVE_THEME["desc"]
                    print(f"\n  {gradient_single(f'  PREVIEW: {tname}  —  {tdesc}')}\n")
                    # Mini background preview strip
                    bg = _get_bg_frame(42, 78, 6)
                    for line in bg: print(line)
                    time.sleep(2.0)
            except KeyboardInterrupt:
                pass
            continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                ACTIVE_THEME = dict(THEMES[keys[idx]])
                clr()
                # Animated theme-set confirmation
                for frame in range(20):
                    _ANIM_OFFSET[0] = frame * 6
                    clr()
                    banner()
                    pulse = gradient_single(
                        f"  ✔  Theme set to:  {ACTIVE_THEME['name']}  —  {ACTIVE_THEME['desc']}",
                        shimmer=True)
                    print(f"\n  {c.B}{pulse}\033[0m\n")
                    bg = _get_bg_frame(frame, 78, 5)
                    for line in bg: print(line)
                    time.sleep(0.06)
                time.sleep(0.3)
            else:
                warn("Invalid selection.")
        except ValueError:
            warn("Enter a number.")

# ──────────────────────────────────────────────────────────────
#  DISCORD TOOLS
# ──────────────────────────────────────────────────────────────
def discord_tools():
    while True:
        section("DISCORD TOOLS", c.BL)
        print(f"  {c.D}[1]{c.R}  {c.W}Webhook Sender{c.R}       {c.D}— send messages to a webhook{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}Webhook Info{c.R}          {c.D}— inspect a webhook URL{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}Embed Builder{c.R}         {c.D}— send rich embed card{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}Nitro Gift Checker{c.R}    {c.D}— check if a gift code is valid{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Server Invite Lookup{c.R}  {c.D}— get info from invite code{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")

        if mode == "0" or not mode: break

        elif mode == "1":
            section("WEBHOOK SENDER")
            url     = inp("Webhook URL")
            if not url: continue
            username = inp("Bot name (default: Phantom)") or "Phantom"
            content  = inp("Message content")
            if not content: continue
            payload  = json.dumps({"username": username, "content": content}).encode()
            try:
                req = urllib.request.Request(url, data=payload, method="POST",
                                             headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    code = r.status
                if code in (200, 204):
                    ok(f"Message sent! (HTTP {code})")
                else:
                    warn(f"Unexpected status: {code}")
            except urllib.error.HTTPError as e:
                err(f"HTTP {e.code}: {e.read().decode()[:120]}")
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "2":
            section("WEBHOOK INFO")
            url = inp("Webhook URL")
            if not url: continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Phantom-Toolkit"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    d = json.loads(r.read())
                for k in ["id","name","channel_id","guild_id","type","token"]:
                    if k in d: row(k.replace("_"," ").title(), str(d[k]))
                if "avatar" in d and d["avatar"]:
                    row("Avatar URL", f"https://cdn.discordapp.com/avatars/{d['id']}/{d['avatar']}.png")
            except urllib.error.HTTPError as e:
                err(f"HTTP {e.code} — invalid webhook?")
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "3":
            section("EMBED BUILDER")
            url     = inp("Webhook URL")
            if not url: continue
            title   = inp("Embed title")
            desc    = inp("Embed description")
            color_s = inp("Color hex (default 5865F2 = Discord blurple)") or "5865F2"
            footer  = inp("Footer text (optional)")
            try: color_int = int(color_s.lstrip("#"), 16)
            except: color_int = 0x5865F2
            embed = {"title": title, "description": desc, "color": color_int}
            if footer: embed["footer"] = {"text": footer}
            payload = json.dumps({
                "username": "Phantom",
                "embeds":   [embed],
            }).encode()
            try:
                req = urllib.request.Request(url, data=payload, method="POST",
                                             headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    ok(f"Embed sent! (HTTP {r.status})")
            except urllib.error.HTTPError as e:
                err(f"HTTP {e.code}: {e.read().decode()[:120]}")
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "4":
            section("NITRO GIFT CHECKER")
            code = inp("Gift code (or full URL)")
            if not code: continue
            code = code.split("/")[-1].strip()
            url  = f"https://discord.com/api/v10/entitlements/gift-codes/{code}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    d = json.loads(r.read())
                if d.get("uses") is not None:
                    ok(f"Code is VALID")
                    row("Code",       code)
                    row("Uses",       str(d.get("uses","?")))
                    row("Max Uses",   str(d.get("max_uses","?")))
                    if d.get("subscription_plan"):
                        row("Plan", d["subscription_plan"].get("name","?"))
                else:
                    warn("Code response unclear.")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    err("Code is INVALID or already redeemed.")
                elif e.code == 429:
                    warn("Rate limited by Discord. Wait and try again.")
                else:
                    err(f"HTTP {e.code}")
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "5":
            section("SERVER INVITE LOOKUP")
            invite = inp("Invite code or URL (e.g. discord.gg/abc123)")
            if not invite: continue
            code = invite.split("/")[-1].strip()
            url  = f"https://discord.com/api/v10/invites/{code}?with_counts=true"
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    d = json.loads(r.read())
                guild = d.get("guild", {})
                ch    = d.get("channel", {})
                row("Server Name",    guild.get("name","?"))
                row("Server ID",      guild.get("id","?"))
                row("Description",    (guild.get("description") or "None")[:60])
                row("Channel",        f"#{ch.get('name','?')}")
                row("Online Members", str(d.get("approximate_presence_count","?")))
                row("Total Members",  str(d.get("approximate_member_count","?")))
                row("Invite Code",    code)
                if guild.get("icon"):
                    row("Icon URL", f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png")
            except urllib.error.HTTPError as e:
                err(f"HTTP {e.code} — invalid invite?" if e.code == 404 else f"HTTP {e.code}")
            except Exception as e:
                err(str(e))
            pause()

# ──────────────────────────────────────────────────────────────
#  TELEGRAM TOOLS
# ──────────────────────────────────────────────────────────────
def telegram_tools():
    while True:
        section("TELEGRAM TOOLS", c.BL)
        print(f"  {c.D}[1]{c.R}  {c.W}Send Message{c.R}         {c.D}— send via bot token{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}Bot Info{c.R}             {c.D}— inspect a bot token{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}Get Chat ID{c.R}          {c.D}— find your chat/group ID{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}Send Photo URL{c.R}       {c.D}— send an image via URL{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Username Lookup{c.R}      {c.D}— get info on a public channel{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if mode == "0" or not mode: break

        def tg_request(token, method, data=None):
            url = f"https://api.telegram.org/bot{token}/{method}"
            if data:
                payload = json.dumps(data).encode()
                req = urllib.request.Request(url, data=payload, method="POST",
                                             headers={"Content-Type":"application/json"})
            else:
                req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read())

        if mode == "1":
            section("SEND MESSAGE")
            token   = inp("Bot token")
            chat_id = inp("Chat ID (user, group, or channel)")
            text    = inp("Message text")
            if not all([token, chat_id, text]): pause(); continue
            try:
                r = tg_request(token, "sendMessage", {"chat_id": chat_id, "text": text, "parse_mode":"HTML"})
                if r.get("ok"):
                    ok(f"Message sent! (msg_id: {r['result']['message_id']})")
                else:
                    err(r.get("description","Unknown error"))
            except Exception as e: err(str(e))
            pause()

        elif mode == "2":
            section("BOT INFO")
            token = inp("Bot token")
            if not token: pause(); continue
            try:
                r = tg_request(token, "getMe")
                if r.get("ok"):
                    b = r["result"]
                    row("Name",        b.get("first_name","?"))
                    row("Username",    f"@{b.get('username','?')}")
                    row("Bot ID",      str(b.get("id","?")))
                    row("Can Join Groups", str(b.get("can_join_groups","?")))
                    row("Can Read Messages", str(b.get("can_read_all_group_messages","?")))
                else:
                    err(r.get("description","Invalid token"))
            except Exception as e: err(str(e))
            pause()

        elif mode == "3":
            section("GET CHAT ID")
            token = inp("Bot token")
            if not token: pause(); continue
            inf("Fetching recent updates...")
            try:
                r = tg_request(token, "getUpdates")
                if r.get("ok"):
                    updates = r.get("result", [])
                    if not updates:
                        warn("No updates. Send a message to the bot first, then retry.")
                    else:
                        seen = set()
                        for u in updates[-10:]:
                            msg = u.get("message") or u.get("channel_post") or {}
                            chat = msg.get("chat", {})
                            cid  = chat.get("id")
                            if cid and cid not in seen:
                                seen.add(cid)
                                row("Chat ID",   str(cid))
                                row("Type",      chat.get("type","?"))
                                row("Name",      chat.get("title") or chat.get("username") or
                                                 f"{chat.get('first_name','')} {chat.get('last_name','')}".strip())
                                sep(w=40)
                else:
                    err(r.get("description","Error"))
            except Exception as e: err(str(e))
            pause()

        elif mode == "4":
            section("SEND PHOTO URL")
            token   = inp("Bot token")
            chat_id = inp("Chat ID")
            photo   = inp("Photo URL")
            caption = inp("Caption (optional)")
            if not all([token, chat_id, photo]): pause(); continue
            try:
                data = {"chat_id": chat_id, "photo": photo}
                if caption: data["caption"] = caption
                r = tg_request(token, "sendPhoto", data)
                ok("Photo sent!") if r.get("ok") else err(r.get("description","Error"))
            except Exception as e: err(str(e))
            pause()

        elif mode == "5":
            section("USERNAME LOOKUP")
            username = inp("Username or channel (e.g. @phantom or t.me/phantom)")
            if not username: pause(); continue
            username = username.lstrip("@").replace("https://t.me/","").strip()
            url = f"https://t.me/{username}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    html = r.read().decode(errors="replace")
                import re
                title   = re.search(r'<meta property="og:title" content="([^"]+)"',   html)
                desc    = re.search(r'<meta property="og:description" content="([^"]+)"', html)
                image   = re.search(r'<meta property="og:image" content="([^"]+)"',   html)
                members = re.search(r'(\d[\d\s]*)\s*members?',  html, re.IGNORECASE)
                row("Username",    username)
                row("Title",       title.group(1)   if title   else "?")
                row("Description", (desc.group(1)   if desc    else "?")[:60])
                row("Members",     members.group(1).strip() if members else "?")
                row("Profile URL", url)
                if image: row("Image", image.group(1)[:70])
            except urllib.error.HTTPError as e:
                err(f"HTTP {e.code} — account may be private or not exist.")
            except Exception as e:
                err(str(e))
            pause()


# ──────────────────────────────────────────────────────────────
#  OATHNET TOOLS
# ──────────────────────────────────────────────────────────────
def oathnet_tools():
    while True:
        section("OATHNET DOMAIN / OSINT TOOLS", c.R1)
        print(f"  {c.D}Powered by oathnet.org — 15+ OSINT sources{c.R}\n")
        print(f"  {c.D}[1]{c.R}  {c.W}Domain Search{c.R}          {c.D}— open oathnet search for a domain{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}Automated Recon{c.R}         {c.D}— launch automated mode on target{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}Bulk Domain Search{c.R}      {c.D}— queue multiple domains at once{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}Secure Search{c.R}           {c.D}— privacy-focused oathnet search{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Manual Mode{c.R}             {c.D}— open oathnet in manual mode{c.R}")
        print(f"  {c.D}[6]{c.R}  {c.W}Build Search URL{c.R}        {c.D}— generate oathnet query link{c.R}")
        print(f"  {c.D}[7]{c.R}  {c.W}Quick OSINT Bundle{c.R}      {c.D}— run whois + DNS + geo + oathnet{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if mode == "0" or not mode:
            break

        # ── Helper: open oathnet URL in browser ──────────────────
        def open_url(url):
            inf(f"Opening: {url}")
            try:
                if platform.system() == "Windows":
                    os.startfile(url)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", url])
                else:
                    subprocess.Popen(["xdg-open", url])
                ok("Launched in your default browser.")
            except Exception as e:
                err(f"Could not open browser: {e}")
                print(f"\n  {c.C}Manual URL:{c.R}  {c.W}{url}{c.R}")

        # ── Helper: fetch oathnet page text ──────────────────────
        def oathnet_fetch(path, params=None):
            base = "https://oathnet.org"
            if params:
                base += path + "?" + urllib.parse.urlencode(params)
            else:
                base += path
            req = urllib.request.Request(
                base,
                headers={"User-Agent": "Mozilla/5.0 (Phantom-Toolkit OSINT)"}
            )
            with urllib.request.urlopen(req, timeout=12) as r:
                return r.read().decode(errors="replace"), base

        # ────────────────────────────────────────────────────────
        if mode == "1":
            section("DOMAIN SEARCH")
            domain = inp("Target domain  (e.g. example.com)")
            if not domain:
                continue
            domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            row("Target", domain)
            url = f"https://oathnet.org/?q={urllib.parse.quote(domain)}"
            row("Oathnet URL", url)
            print(f"\n  {c.D}[1] Open in browser   [2] Fetch text preview{c.R}")
            sub = inp("Action") or "1"
            if sub == "2":
                inf("Fetching oathnet results...")
                try:
                    content, full_url = oathnet_fetch("/", {"q": domain})
                    # Extract meaningful lines
                    lines = [l.strip() for l in content.splitlines() if len(l.strip()) > 20]
                    sep()
                    for line in lines[:40]:
                        # Skip script/style noise
                        if any(skip in line.lower() for skip in ["<script", "<style", "function(", "var ", "const ", "{", "}"]):
                            continue
                        # Strip HTML tags for display
                        clean = re.sub(r'<[^>]+>', '', line).strip()
                        if clean and len(clean) > 5:
                            print(f"  {c.W}{clean[:90]}{c.R}")
                    inf("For full results, open in browser.")
                except Exception as e:
                    err(f"Fetch failed: {e}")
                    inf("Try opening in browser instead.")
                    open_url(url)
            else:
                open_url(url)
            pause()

        elif mode == "2":
            section("AUTOMATED RECON")
            domain = inp("Target domain")
            if not domain:
                continue
            domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            row("Target",  domain)
            row("Mode",    "Automated")
            url = f"https://oathnet.org/?q={urllib.parse.quote(domain)}&mode=automated"
            row("URL", url)
            inf("Launching automated recon on oathnet...")
            open_url(url)
            pause()

        elif mode == "3":
            section("BULK DOMAIN SEARCH")
            print(f"  {c.D}Enter domains one per line. Blank line to finish.{c.R}\n")
            domains = []
            while True:
                d = input(f"  {c.D}>{c.R} ").strip().lower()
                if not d:
                    break
                d = d.replace("https://", "").replace("http://", "").split("/")[0]
                if d:
                    domains.append(d)
            if not domains:
                warn("No domains entered.")
                continue
            inf(f"Opening {len(domains)} oathnet search(es)...")
            sep()
            for i, domain in enumerate(domains[:10], 1):
                url = f"https://oathnet.org/?q={urllib.parse.quote(domain)}&mode=bulk"
                print(f"  {c.D}{i:>2}.{c.R}  {c.W}{domain:<40}{c.R}  {c.D}{url}{c.R}")
                open_url(url)
                if i < len(domains):
                    time.sleep(0.8)  # slight delay between tabs
            if len(domains) > 10:
                warn(f"Only opened first 10 of {len(domains)} domains to avoid tab flood.")
            pause()

        elif mode == "4":
            section("SECURE SEARCH")
            domain = inp("Target domain")
            if not domain:
                continue
            domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            row("Target", domain)
            row("Mode",   "Secure (privacy-focused)")
            url = f"https://oathnet.org/?q={urllib.parse.quote(domain)}&secure=1"
            open_url(url)
            pause()

        elif mode == "5":
            section("MANUAL MODE")
            domain = inp("Target domain")
            if not domain:
                continue
            domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            url = f"https://oathnet.org/?q={urllib.parse.quote(domain)}&mode=manual"
            row("Target", domain)
            row("Mode",   "Manual")
            open_url(url)
            pause()

        elif mode == "6":
            section("BUILD SEARCH URL")
            domain  = inp("Target domain")
            if not domain:
                continue
            domain  = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            print(f"\n  {c.D}[1] Automated  [2] Manual  [3] Secure  [4] Bulk  [5] Default{c.R}")
            mtype   = inp("Mode type") or "5"
            mode_map = {"1": "automated", "2": "manual", "3": "", "4": "bulk", "5": ""}
            params  = {"q": domain}
            if mtype in ("1","2","4") and mode_map.get(mtype):
                params["mode"] = mode_map[mtype]
            if mtype == "3":
                params["secure"] = "1"
            url = "https://oathnet.org/?" + urllib.parse.urlencode(params)
            sep()
            row("Target",  domain)
            row("URL",     url)
            print(f"\n  {c.Y}{url}{c.R}")
            open_q = inp("Open in browser? (y/n)") or "y"
            if open_q.lower() == "y":
                open_url(url)
            pause()

        elif mode == "7":
            section("QUICK OSINT BUNDLE")
            domain = inp("Target domain or IP")
            if not domain:
                continue
            domain = domain.strip().replace("https://", "").replace("http://", "").split("/")[0]
            sep()
            inf(f"Running full OSINT bundle on: {domain}\n")

            # 1. Local DNS
            print(f"  {th_accent()}{c.B}[ DNS Lookup ]{c.R}")
            try:
                ip = socket.gethostbyname(domain)
                row("  Resolved IP", ip)
                try:
                    rev = socket.gethostbyaddr(ip)[0]
                    row("  Reverse DNS", rev)
                except: pass
            except Exception as e:
                row("  DNS", f"Failed: {e}")

            # 2. IP Geolocation
            print(f"\n  {th_accent()}{c.B}[ IP Geolocation ]{c.R}")
            try:
                url_geo = f"http://ip-api.com/json/{domain}"
                req = urllib.request.Request(url_geo, headers={"User-Agent": "Phantom-Toolkit"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    d = json.loads(r.read())
                if d.get("status") == "success":
                    for k in ["query","country","regionName","city","isp","org","timezone"]:
                        if d.get(k): row(f"  {k.capitalize()}", str(d[k]))
                else:
                    row("  Geo", d.get("message", "Lookup failed"))
            except Exception as e:
                row("  Geo", f"Failed: {e}")

            # 3. HTTP Headers peek
            print(f"\n  {th_accent()}{c.B}[ HTTP Headers Peek ]{c.R}")
            try:
                req = urllib.request.Request(
                    f"https://{domain}",
                    headers={"User-Agent": "Mozilla/5.0 (Phantom-Toolkit)"}
                )
                with urllib.request.urlopen(req, timeout=8) as r:
                    for hdr in ["Server", "X-Powered-By", "Content-Type", "X-Frame-Options",
                                "Strict-Transport-Security", "Content-Security-Policy"]:
                        val = r.headers.get(hdr)
                        if val: row(f"  {hdr}", val[:60])
            except urllib.error.HTTPError as e:
                row("  HTTP", f"Status {e.code}")
            except Exception as e:
                row("  HTTPS", f"Failed: {e}")

            # 4. SSL cert quick check
            print(f"\n  {th_accent()}{c.B}[ SSL Certificate ]{c.R}")
            try:
                import ssl
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(
                    socket.create_connection((domain, 443), timeout=6),
                    server_hostname=domain
                ) as s:
                    cert = s.getpeercert()
                    subj = dict(x[0] for x in cert.get("subject", []))
                    row("  Common Name", subj.get("commonName", "?"))
                    na = cert.get("notAfter", "")
                    if na:
                        try:
                            exp = datetime.strptime(na, "%b %d %H:%M:%S %Y %Z")
                            days = (exp - datetime.utcnow()).days
                            col = c.G if days > 30 else c.Y if days > 7 else c.R1
                            row("  Expires", na, vc=col)
                            row("  Days Left", str(days), vc=col)
                        except: row("  Expires", na)
            except Exception as e:
                row("  SSL", f"Failed: {e}")

            # 5. Open on Oathnet
            print(f"\n  {th_accent()}{c.B}[ Oathnet Deep Search ]{c.R}")
            oathnet_url = f"https://oathnet.org/?q={urllib.parse.quote(domain)}&mode=automated"
            row("  Oathnet URL", oathnet_url)
            open_q = inp("\nOpen full Oathnet recon in browser? (y/n)") or "y"
            if open_q.lower() == "y":
                open_url(oathnet_url)

            # Extra: common OSINT links
            print(f"\n  {th_accent()}{c.B}[ Quick OSINT Links ]{c.R}")
            osint_links = [
                ("Shodan",        f"https://www.shodan.io/search?query={urllib.parse.quote(domain)}"),
                ("VirusTotal",    f"https://www.virustotal.com/gui/domain/{domain}"),
                ("SecurityTrails",f"https://securitytrails.com/domain/{domain}/dns"),
                ("crt.sh (SSL)",  f"https://crt.sh/?q={urllib.parse.quote(domain)}"),
                ("DomainTools",   f"https://whois.domaintools.com/{domain}"),
                ("URLScan",       f"https://urlscan.io/search/#domain:{domain}"),
            ]
            for name, link in osint_links:
                row(f"  {name}", link[:80])

            ok("OSINT bundle complete.")
            pause()



# ──────────────────────────────────────────────────────────────
#  39  ANONYMITY & PRIVACY CHECK
# ──────────────────────────────────────────────────────────────
def anon_tools():
    while True:
        section("ANONYMITY & PRIVACY TOOLS", c.R1)
        print(f"  {c.D}[1]{c.R}  {c.W}Tor Exit Node Check{c.R}         {c.D}— is your IP a Tor exit?{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}VPN / Proxy Detector{c.R}        {c.D}— check IP for proxy flags{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}DNS Leak Test{c.R}               {c.D}— check which DNS server you use{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}IP Anonymity Report{c.R}         {c.D}— full anonymity score for an IP{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Browser Fingerprint Info{c.R}    {c.D}— what sites can see about you{c.R}")
        print(f"  {c.D}[6]{c.R}  {c.W}Proxy List Fetcher{c.R}          {c.D}— fetch free public proxy list{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if not mode or mode == "0": break

        if mode == "1":
            section("TOR EXIT NODE CHECK")
            ip = inp("IP to check (blank = your IP)")
            try:
                if not ip:
                    req = urllib.request.Request("https://api.ipify.org?format=json",
                                                 headers={"User-Agent":"Phantom"})
                    with urllib.request.urlopen(req, timeout=6) as r:
                        ip = json.loads(r.read())["ip"]
                row("Checking IP", ip)
                # Query Tor exit list
                url = f"https://check.torproject.org/torbulkexitlist"
                req = urllib.request.Request(url, headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    exit_list = r.read().decode()
                if ip in exit_list.splitlines():
                    warn(f"{ip} IS a known Tor exit node!")
                    row("Tor Exit", "YES", vc=c.R1)
                else:
                    ok(f"{ip} is NOT in the Tor exit list.")
                    row("Tor Exit", "NO", vc=c.G)
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "2":
            section("VPN / PROXY DETECTOR")
            ip = inp("IP address (blank = your IP)")
            try:
                url = f"http://ip-api.com/json/{ip}?fields=query,proxy,hosting,vpn,mobile,isp,org,country,city" if ip else \
                      "http://ip-api.com/json/?fields=query,proxy,hosting,vpn,mobile,isp,org,country,city"
                req = urllib.request.Request(url, headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    d = json.loads(r.read())
                row("IP",       d.get("query","?"))
                row("Country",  d.get("country","?"))
                row("City",     d.get("city","?"))
                row("ISP",      d.get("isp","?")[:50])
                row("Org",      d.get("org","?")[:50])
                for flag in ["proxy","hosting","mobile"]:
                    val = d.get(flag, False)
                    col = c.R1 if val else c.G
                    row(flag.capitalize(), "YES" if val else "NO", vc=col)
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "3":
            section("DNS LEAK TEST")
            inf("Checking your DNS resolver...")
            try:
                # Resolve a unique hostname to see which DNS is used
                for hostname in ["one.one.one.one", "dns.google", "resolver1.opendns.com"]:
                    try:
                        ip_resolved = socket.gethostbyname(hostname)
                        row(f"Resolved {hostname}", ip_resolved)
                    except: pass
                # Use external API for DNS check
                req = urllib.request.Request(
                    "https://api.ipify.org?format=json",
                    headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    my_ip = json.loads(r.read())["ip"]
                row("Your Public IP", my_ip)
                # Check system DNS servers
                if platform.system() in ("Linux", "Darwin"):
                    try:
                        with open("/etc/resolv.conf") as f:
                            for line in f:
                                if line.startswith("nameserver"):
                                    row("System DNS", line.split()[1])
                    except: pass
                elif platform.system() == "Windows":
                    r2 = subprocess.run(["ipconfig","/all"],capture_output=True,text=True)
                    for line in r2.stdout.splitlines():
                        if "DNS Servers" in line:
                            row("DNS Server", line.split(":")[-1].strip())
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "4":
            section("IP ANONYMITY REPORT")
            ip = inp("IP address (blank = your IP)")
            try:
                base = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
                req = urllib.request.Request(
                    base + "?fields=query,country,city,isp,org,proxy,hosting,mobile,timezone",
                    headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    d = json.loads(r.read())
                score = 100
                flags = []
                if d.get("proxy"):   score -= 40; flags.append("Proxy/VPN detected (-40)")
                if d.get("hosting"): score -= 30; flags.append("Hosting/datacenter IP (-30)")
                if d.get("mobile"):  score -= 10; flags.append("Mobile carrier (-10)")
                row("IP", d.get("query","?")); row("Location", f"{d.get('city','?')}, {d.get('country','?')}")
                row("ISP", d.get("isp","?")[:50]); row("Timezone", d.get("timezone","?"))
                sep()
                col = c.G if score >= 80 else c.Y if score >= 50 else c.R1
                row("Anonymity Score", f"{score}/100", vc=col)
                lvl = "HIGH" if score >= 80 else "MEDIUM" if score >= 50 else "LOW"
                row("Anonymity Level", lvl, vc=col)
                if flags:
                    print(f"\n  {c.R1}{c.B}Risk Factors:{c.R}")
                    for f2 in flags: print(f"    {c.R1}• {f2}{c.R}")
                else:
                    ok("No anonymity flags detected.")
            except Exception as e:
                err(str(e))
            pause()

        elif mode == "5":
            section("BROWSER FINGERPRINT INFO")
            print(f"\n  {th_accent()}{c.B}What websites can detect about you:{c.R}\n")
            row("Operating System",  platform.system() + " " + platform.release())
            row("Architecture",      platform.machine())
            row("Python Version",    sys.version.split()[0])
            row("Hostname",          socket.gethostname())
            try:
                ip = socket.gethostbyname(socket.gethostname())
                row("Local IP",  ip)
            except: pass
            try:
                req = urllib.request.Request("https://api.ipify.org?format=json",
                                             headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    row("Public IP", json.loads(r.read())["ip"])
            except: pass
            row("Terminal Size",     f"{os.get_terminal_size().columns}x{os.get_terminal_size().lines}" if hasattr(os,"get_terminal_size") else "Unknown")
            row("TERM env",          os.environ.get("TERM","?"))
            row("LANG env",          os.environ.get("LANG","?"))
            row("Shell",             os.environ.get("SHELL","?"))
            row("Timezone",          str(datetime.now().astimezone().tzinfo))
            pause()

        elif mode == "6":
            section("PUBLIC PROXY LIST")
            inf("Fetching proxy list from public API...")
            try:
                url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite"
                req = urllib.request.Request(url, headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=12) as r:
                    data = r.read().decode()
                proxies = [p.strip() for p in data.splitlines() if p.strip()]
                ok(f"Fetched {len(proxies)} proxies")
                print(f"\n  {c.C}{c.B}Sample (first 20):{c.R}")
                for p in proxies[:20]:
                    print(f"  {c.W}{p}{c.R}")
                if len(proxies) > 20:
                    inf(f"...and {len(proxies)-20} more")
                # Save option
                save = inp("Save to proxies.txt? (y/n)") or "n"
                if save.lower() == "y":
                    with open("proxies.txt","w") as f2:
                        f2.write("\n".join(proxies))
                    ok(f"Saved {len(proxies)} proxies to proxies.txt")
            except Exception as e:
                err(str(e))
            pause()

# ──────────────────────────────────────────────────────────────
#  40  SOCIAL MEDIA FINDER
# ──────────────────────────────────────────────────────────────
def social_finder():
    section("SOCIAL MEDIA FINDER", c.R1)
    username = inp("Target username")
    if not username: return
    PLATFORMS = [
        ("GitHub",       f"https://github.com/{username}"),
        ("Reddit",       f"https://reddit.com/user/{username}"),
        ("Twitter/X",    f"https://twitter.com/{username}"),
        ("Instagram",    f"https://instagram.com/{username}"),
        ("TikTok",       f"https://tiktok.com/@{username}"),
        ("YouTube",      f"https://youtube.com/@{username}"),
        ("Twitch",       f"https://twitch.tv/{username}"),
        ("Pinterest",    f"https://pinterest.com/{username}"),
        ("LinkedIn",     f"https://linkedin.com/in/{username}"),
        ("Steam",        f"https://steamcommunity.com/id/{username}"),
        ("Roblox",       f"https://roblox.com/user.aspx?username={username}"),
        ("Spotify",      f"https://open.spotify.com/user/{username}"),
        ("SoundCloud",   f"https://soundcloud.com/{username}"),
        ("Medium",       f"https://medium.com/@{username}"),
        ("Dev.to",       f"https://dev.to/{username}"),
        ("GitLab",       f"https://gitlab.com/{username}"),
        ("Replit",       f"https://replit.com/@{username}"),
        ("Pastebin",     f"https://pastebin.com/u/{username}"),
        ("Keybase",      f"https://keybase.io/{username}"),
        ("Telegram",     f"https://t.me/{username}"),
        ("Mastodon",     f"https://mastodon.social/@{username}"),
        ("Tumblr",       f"https://tumblr.com/{username}"),
        ("Flickr",       f"https://flickr.com/people/{username}"),
        ("VK",           f"https://vk.com/{username}"),
        ("Snapchat",     f"https://snapchat.com/add/{username}"),
    ]
    inf(f"Searching {len(PLATFORMS)} platforms for '{username}'...\n")
    found = []; not_found = []
    lock = threading.Lock()

    def check(name, url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                if r.status == 200:
                    with lock: found.append((name, url))
                else:
                    with lock: not_found.append(name)
        except:
            with lock: not_found.append(name)

    threads = [threading.Thread(target=check, args=(n,u), daemon=True) for n,u in PLATFORMS]
    for t in threads: t.start()

    # Progress while waiting
    done = [0]
    for t in threads:
        t.join(timeout=8)
        done[0] += 1
        pct = done[0]/len(threads)*100
        print(f"\r  {gradient_single(f'Scanning... {done[0]}/{len(threads)}  ({pct:.0f}%)')}  ", end="", flush=True)
    print()
    sep()
    if found:
        print(f"\n  {c.G}{c.B}FOUND on {len(found)} platform(s):{c.R}")
        for name, url in sorted(found, key=lambda x:x[0]):
            print(f"    {c.G}●  {c.W}{c.B}{name:<16}{c.R}  {c.D}{url}{c.R}")
    else:
        warn("No profiles found.")
    print(f"\n  {c.D}Not found: {len(not_found)} platforms{c.R}")
    ok(f"Done. {len(found)}/{len(PLATFORMS)} profiles found.")
    pause()

# ──────────────────────────────────────────────────────────────
#  41  FORENSIC FILE ANALYSIS
# ──────────────────────────────────────────────────────────────
MAGIC_SIG = {
    b'\x89PNG\r\n\x1a\n': "PNG Image",
    b'\xff\xd8\xff':       "JPEG Image",
    b'GIF87a':             "GIF87 Image",
    b'GIF89a':             "GIF89 Image",
    b'%PDF':               "PDF Document",
    b'PK\x03\x04':        "ZIP / Office / JAR",
    b'\x1f\x8b':          "Gzip Archive",
    b'BZh':               "Bzip2 Archive",
    b'7z\xbc\xaf':        "7-Zip Archive",
    b'\xfd7zXZ':          "XZ Archive",
    b'\x7fELF':           "ELF Executable (Linux/Unix)",
    b'MZ':                "Windows PE Executable",
    b'\xca\xfe\xba\xbe':  "Java Class / Mach-O Universal",
    b'\xce\xfa\xed\xfe':  "Mach-O 32-bit Binary",
    b'\xcf\xfa\xed\xfe':  "Mach-O 64-bit Binary",
    b'#!':                "Script (shebang)",
    b'<!DOCTYPE':         "HTML Document",
    b'<html':             "HTML Document",
    b'<?xml':             "XML Document",
    b'<?php':             "PHP Script",
    b'RIFF':              "WAV / AVI (RIFF container)",
    b'\x00\x00\x00\x18ftypmp4': "MP4 Video",
    b'\x00\x00\x00 ftyp': "MP4/M4V Video",
    b'OggS':              "Ogg Media",
    b'fLaC':              "FLAC Audio",
    b'ID3':               "MP3 Audio (ID3 tag)",
    b'\xff\xfb':          "MP3 Audio",
    b'WAVE':              "WAV Audio",
    b'SQLite format 3':   "SQLite Database",
    b'\x4d\x5a':         "Windows PE Executable",
}

def forensic_tools():
    while True:
        section("FORENSIC FILE ANALYSIS", c.Y)
        print(f"  {c.D}[1]{c.R}  {c.W}File Signature Analyzer{c.R}   {c.D}— identify file type by bytes{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}Strings Extractor{c.R}         {c.D}— extract printable strings{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}Hex Dump{c.R}                  {c.D}— view raw bytes in hex{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}Metadata Viewer{c.R}           {c.D}— show file metadata & EXIF hints{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Entropy Calculator{c.R}        {c.D}— detect encryption/compression{c.R}")
        print(f"  {c.D}[6]{c.R}  {c.W}Hash Compare{c.R}              {c.D}— compare two file hashes{c.R}")
        print(f"  {c.D}[7]{c.R}  {c.W}Find URLs in File{c.R}         {c.D}— extract embedded URLs{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if not mode or mode == "0": break

        if mode == "1":
            section("FILE SIGNATURE ANALYZER")
            path = inp("File path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try:
                with open(path,"rb") as f: header = f.read(32)
                detected = "Unknown / Custom"
                for sig, ftype in MAGIC_SIG.items():
                    if header[:len(sig)] == sig:
                        detected = ftype; break
                sz = os.path.getsize(path)
                row("File",       path)
                row("Size",       f"{sz:,} bytes  ({sz/1024:.1f} KB)")
                row("Extension",  os.path.splitext(path)[1] or "(none)")
                row("Detected",   detected, vc=c.G)
                row("Header Hex", header[:16].hex(' '))
                row("Header ASCII","".join(chr(b) if 32<=b<127 else '.' for b in header[:16]))
                ext = os.path.splitext(path)[1].lower()
                if detected != "Unknown / Custom":
                    if ext and not any(detected.lower().startswith(e) for e in [ext.lstrip(".")]):
                        warn(f"Extension '{ext}' may not match detected type '{detected}'")
            except Exception as e: err(str(e))
            pause()

        elif mode == "2":
            section("STRINGS EXTRACTOR")
            path = inp("File path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try: min_len = int(inp("Minimum string length (default 5)") or "5")
            except: min_len = 5
            try:
                with open(path,"rb") as f: data = f.read()
                strings = []; current = []
                for byte in data:
                    if 32 <= byte < 127:
                        current.append(chr(byte))
                    else:
                        if len(current) >= min_len:
                            strings.append("".join(current))
                        current = []
                if len(current) >= min_len: strings.append("".join(current))
                ok(f"Found {len(strings)} strings (min length {min_len})")
                # Highlight interesting ones
                interesting = [s for s in strings if any(kw in s.lower() for kw in
                    ["http","https","password","pass","key","token","secret","api","email","@","flag","admin"])]
                if interesting:
                    print(f"\n  {c.Y}{c.B}Interesting strings:{c.R}")
                    for s in interesting[:20]: print(f"  {c.Y}▶  {s[:80]}{c.R}")
                print(f"\n  {c.C}{c.B}All strings (first 50):{c.R}")
                for s in strings[:50]: print(f"  {c.W}{s[:80]}{c.R}")
                if len(strings) > 50: inf(f"...and {len(strings)-50} more")
                # Save option
                if strings and inp("Save to strings.txt? (y/n)").lower() == "y":
                    with open("strings.txt","w") as f2: f2.write("\n".join(strings))
                    ok(f"Saved {len(strings)} strings.")
            except Exception as e: err(str(e))
            pause()

        elif mode == "3":
            section("HEX DUMP")
            path = inp("File path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try: limit = int(inp("Bytes to show (default 256)") or "256")
            except: limit = 256
            try:
                with open(path,"rb") as f: data = f.read(limit)
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    hex_part = " ".join(f"{b:02x}" for b in chunk)
                    asc_part = "".join(chr(b) if 32<=b<127 else "." for b in chunk)
                    offset_col = gradient_single(f"{i:08x}", bold=False)
                    print(f"  {offset_col}  {c.W}{hex_part:<47}{c.R}  {c.C}|{asc_part}|{c.R}")
            except Exception as e: err(str(e))
            pause()

        elif mode == "4":
            section("METADATA VIEWER")
            path = inp("File path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try:
                st = os.stat(path)
                row("File",     path)
                row("Size",     f"{st.st_size:,} bytes")
                row("Created",  datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"))
                row("Modified", datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
                row("Accessed", datetime.fromtimestamp(st.st_atime).strftime("%Y-%m-%d %H:%M:%S"))
                row("Mode",     oct(st.st_mode))
                row("UID/GID",  f"{st.st_uid} / {st.st_gid}")
                row("Inode",    str(st.st_ino))
                # Try exiftool if available
                try:
                    r2 = subprocess.run(["exiftool", path], capture_output=True, text=True, timeout=8)
                    if r2.returncode == 0:
                        print(f"\n  {th_accent()}{c.B}EXIF Data:{c.R}")
                        for line in r2.stdout.splitlines()[:30]:
                            print(f"  {c.W}{line}{c.R}")
                except FileNotFoundError:
                    inf("Install exiftool for EXIF data.")
            except Exception as e: err(str(e))
            pause()

        elif mode == "5":
            section("ENTROPY CALCULATOR")
            path = inp("File path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try:
                with open(path,"rb") as f: data = f.read()
                if not data: err("Empty file."); pause(); continue
                freq = [0]*256
                for b in data: freq[b] += 1
                entropy = 0.0
                for count in freq:
                    if count:
                        p = count / len(data)
                        entropy -= p * math.log2(p)
                row("File Size", f"{len(data):,} bytes")
                row("Entropy",   f"{entropy:.4f} bits/byte")
                col = c.R1 if entropy > 7.5 else c.Y if entropy > 6.5 else c.G
                if entropy > 7.5:
                    interpretation = "VERY HIGH — likely encrypted or compressed"
                elif entropy > 6.5:
                    interpretation = "HIGH — compressed or packed"
                elif entropy > 5.0:
                    interpretation = "MEDIUM — mixed data"
                else:
                    interpretation = "LOW — mostly text or structured data"
                row("Interpretation", interpretation, vc=col)
                # Bar chart
                print(f"\n  {c.D}Byte frequency distribution:{c.R}")
                groups = [0]*16
                for i, count in enumerate(freq): groups[i//16] += count
                max_g = max(groups) or 1
                for i, g in enumerate(groups):
                    bar_w = int(g/max_g * 30)
                    start_byte = i*16
                    bar = gradient_single("█"*bar_w + "░"*(30-bar_w))
                    print(f"  {c.D}0x{start_byte:02x}-0x{start_byte+15:02x}{c.R}  {bar}  {c.D}{g:,}{c.R}")
            except Exception as e: err(str(e))
            pause()

        elif mode == "6":
            section("HASH COMPARE")
            p1 = inp("First file path"); p2 = inp("Second file path")
            if not os.path.isfile(p1): err(f"Not found: {p1}"); pause(); continue
            if not os.path.isfile(p2): err(f"Not found: {p2}"); pause(); continue
            try:
                def file_hashes(path):
                    with open(path,"rb") as f: data = f.read()
                    return {
                        "MD5":    hashlib.md5(data).hexdigest(),
                        "SHA-1":  hashlib.sha1(data).hexdigest(),
                        "SHA-256":hashlib.sha256(data).hexdigest(),
                    }
                h1 = file_hashes(p1); h2 = file_hashes(p2)
                print(f"\n  {c.C}{c.B}{'HASH':<10}  {'FILE 1':>42}  {'FILE 2':>42}  MATCH{c.R}")
                sep()
                for algo in ["MD5","SHA-1","SHA-256"]:
                    match = h1[algo] == h2[algo]
                    col = c.G if match else c.R1
                    print(f"  {c.W}{algo:<10}{c.R}  {c.D}{h1[algo][:20]}...{c.R}  {c.D}{h2[algo][:20]}...{c.R}  {col}{'✔' if match else '✘'}{c.R}")
                if all(h1[a]==h2[a] for a in h1):
                    ok("Files are IDENTICAL (all hashes match)")
                else:
                    warn("Files are DIFFERENT (hash mismatch)")
            except Exception as e: err(str(e))
            pause()

        elif mode == "7":
            section("FIND URLs IN FILE")
            path = inp("File path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try:
                with open(path,"rb") as f: raw = f.read()
                try: text = raw.decode("utf-8", errors="replace")
                except: text = raw.decode("latin-1", errors="replace")
                urls = list(set(re.findall(r'https?://[^\s\'"<>]+', text)))
                emails = list(set(re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)))
                ips_found = list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)))
                ok(f"Found {len(urls)} URLs, {len(emails)} emails, {len(ips_found)} IPs")
                if urls:
                    print(f"\n  {c.C}{c.B}URLs ({len(urls)}):{c.R}")
                    for u in urls[:30]: print(f"  {c.W}• {u[:80]}{c.R}")
                if emails:
                    print(f"\n  {c.Y}{c.B}Emails ({len(emails)}):{c.R}")
                    for e2 in emails[:20]: print(f"  {c.Y}• {e2}{c.R}")
                if ips_found:
                    print(f"\n  {c.M}{c.B}IPs ({len(ips_found)}):{c.R}")
                    for ip2 in ips_found[:20]: print(f"  {c.M}• {ip2}{c.R}")
            except Exception as e: err(str(e))
            pause()

# ──────────────────────────────────────────────────────────────
#  42  STEGANOGRAPHY TOOLS
# ──────────────────────────────────────────────────────────────
def stego_tools():
    while True:
        section("STEGANOGRAPHY TOOLS", c.M)
        print(f"  {c.D}[1]{c.R}  {c.W}Hide Text in File (EOF append){c.R}  {c.D}— append hidden data after EOF{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}Extract Hidden Text{c.R}             {c.D}— read appended hidden data{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}LSB Text Encoder (BMP/raw){c.R}      {c.D}— encode text into LSB of bytes{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}LSB Text Decoder{c.R}                {c.D}— decode text from LSB{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Zero-Width Unicode Encoder{c.R}      {c.D}— hide in invisible unicode chars{c.R}")
        print(f"  {c.D}[6]{c.R}  {c.W}Zero-Width Decoder{c.R}              {c.D}— extract from zero-width text{c.R}")
        print(f"  {c.D}[7]{c.R}  {c.W}Whitespace Steganography{c.R}        {c.D}— hide in trailing spaces{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if not mode or mode == "0": break

        if mode == "1":
            section("HIDE TEXT IN FILE (EOF)")
            src = inp("Source file path"); secret = inp("Secret message")
            if not src or not os.path.isfile(src): err("File not found."); pause(); continue
            dst = inp(f"Output file path (default: {src}.stego)") or src + ".stego"
            try:
                with open(src,"rb") as f: data = f.read()
                marker = b"\n\n==PHANTOM_STEGO==\n"
                payload = marker + secret.encode("utf-8") + b"\n==END_STEGO=="
                with open(dst,"wb") as f2: f2.write(data + payload)
                ok(f"Hidden message embedded in: {dst}")
                row("Original size", f"{len(data):,} bytes")
                row("New size",      f"{len(data)+len(payload):,} bytes")
            except Exception as e: err(str(e))
            pause()

        elif mode == "2":
            section("EXTRACT HIDDEN TEXT (EOF)")
            path = inp("File path to inspect")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try:
                with open(path,"rb") as f: data = f.read()
                marker = b"==PHANTOM_STEGO=="
                end_marker = b"==END_STEGO=="
                if marker in data:
                    start = data.index(marker) + len(marker)
                    end   = data.index(end_marker) if end_marker in data else len(data)
                    secret = data[start:end].decode("utf-8","replace").strip()
                    ok("Hidden message found!")
                    sep()
                    print(f"\n  {c.Y}{c.B}{secret}{c.R}\n")
                else:
                    warn("No Phantom stego marker found in this file.")
            except Exception as e: err(str(e))
            pause()

        elif mode == "3":
            section("LSB TEXT ENCODER")
            path = inp("Binary/data file path"); secret = inp("Secret text to hide")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            dst = inp("Output file (default: lsb_out.bin)") or "lsb_out.bin"
            try:
                with open(path,"rb") as f: data = bytearray(f.read())
                bits = ''.join(f"{b:08b}" for b in secret.encode("utf-8")) + "00000000"  # null term
                if len(bits) > len(data):
                    err(f"File too small to hold {len(secret)} chars. Need {len(bits)} bytes."); pause(); continue
                for i, bit in enumerate(bits):
                    data[i] = (data[i] & 0xFE) | int(bit)
                with open(dst,"wb") as f2: f2.write(bytes(data))
                ok(f"LSB encoded to: {dst}")
                row("Hidden chars", str(len(secret)))
                row("Bits used",    str(len(bits)))
            except Exception as e: err(str(e))
            pause()

        elif mode == "4":
            section("LSB TEXT DECODER")
            path = inp("LSB-encoded file path")
            if not path or not os.path.isfile(path): err("File not found."); pause(); continue
            try: max_chars = int(inp("Max chars to read (default 200)") or "200")
            except: max_chars = 200
            try:
                with open(path,"rb") as f: data = f.read()
                bits = "".join(str(b & 1) for b in data[:max_chars*8+8])
                chars = []
                for i in range(0, len(bits)-7, 8):
                    byte_val = int(bits[i:i+8], 2)
                    if byte_val == 0: break
                    if 32 <= byte_val < 127: chars.append(chr(byte_val))
                result = "".join(chars)
                if result:
                    ok("LSB Decoded text:")
                    sep()
                    print(f"\n  {c.Y}{c.B}{result}{c.R}\n")
                else:
                    warn("No readable LSB text found.")
            except Exception as e: err(str(e))
            pause()

        elif mode == "5":
            section("ZERO-WIDTH UNICODE ENCODER")
            cover = inp("Cover text (public message)")
            secret = inp("Secret text to hide")
            if not cover or not secret: pause(); continue
            # Encode secret as binary, map to ZW chars
            ZW_ZERO = "\u200b"  # zero-width space = 0
            ZW_ONE  = "\u200c"  # zero-width non-joiner = 1
            ZW_SEP  = "\u200d"  # zero-width joiner = separator
            bits = "".join(f"{b:08b}" for b in secret.encode("utf-8"))
            zw_payload = ZW_SEP + "".join(ZW_ZERO if bit=="0" else ZW_ONE for bit in bits) + ZW_SEP
            result = cover + zw_payload
            ok("Zero-width encoded text:")
            print(f"\n  {c.W}(copy everything below — it looks like just the cover text){c.R}")
            sep()
            print(f"\n{result}\n")
            sep()
            row("Cover text length", str(len(cover)))
            row("ZW chars added",    str(len(zw_payload)))
            row("Total chars",       str(len(result)))
            pause()

        elif mode == "6":
            section("ZERO-WIDTH DECODER")
            print(f"  {c.D}Paste text containing zero-width chars. Blank line to finish.{c.R}\n")
            lines = []
            while True:
                line = input(f"  {c.D}>{c.R} ")
                if not line: break
                lines.append(line)
            text = "\n".join(lines)
            ZW_ZERO = "\u200b"; ZW_ONE = "\u200c"; ZW_SEP = "\u200d"
            if ZW_SEP not in text:
                warn("No zero-width stego markers found."); pause(); continue
            try:
                start = text.index(ZW_SEP) + 1
                end   = text.index(ZW_SEP, start)
                zw_bits = text[start:end]
                bits = "".join("0" if ch==ZW_ZERO else "1" for ch in zw_bits if ch in (ZW_ZERO, ZW_ONE))
                chars = []
                for i in range(0, len(bits)-7, 8):
                    byte_val = int(bits[i:i+8], 2)
                    if byte_val == 0: break
                    chars.append(chr(byte_val))
                result = "".join(chars)
                ok("Decoded hidden message:")
                sep()
                print(f"\n  {c.Y}{c.B}{result}{c.R}\n")
            except Exception as e: err(f"Decode failed: {e}")
            pause()

        elif mode == "7":
            section("WHITESPACE STEGANOGRAPHY")
            print(f"  {c.D}[1] Encode  [2] Decode{c.R}")
            sub = inp("Mode")
            if sub == "1":
                cover_text = inp("Cover text (multi-word sentence)")
                secret = inp("Secret bits message (letters only)")
                if not cover_text or not secret: pause(); continue
                # Encode each char of secret as trailing spaces count (a=1, b=2 etc)
                words = cover_text.split()
                result_lines = []
                for i, word in enumerate(words):
                    if i < len(secret):
                        count = ord(secret[i].lower()) - ord('a') + 1
                        result_lines.append(word + " " * count)
                    else:
                        result_lines.append(word)
                encoded = " ".join(result_lines)
                ok("Whitespace encoded. Copy the line below exactly:")
                print(f"\n{encoded}\n")
            else:
                text = inp("Paste encoded text")
                if not text: pause(); continue
                words = text.split(" ")
                secret_chars = []
                for word in words:
                    trail = len(word) - len(word.rstrip(" "))
                    if trail > 0:
                        ch = chr(ord('a') + trail - 1)
                        secret_chars.append(ch)
                if secret_chars:
                    ok("Decoded: " + "".join(secret_chars))
                else:
                    warn("No whitespace encoding detected.")
            pause()

# ──────────────────────────────────────────────────────────────
#  43  OSINT FRAMEWORK TREE
# ──────────────────────────────────────────────────────────────
OSINT_TREE = {
    "👤 Username": {
        "Social Media": ["Sherlock (CLI)", "Maigret", "Social Analyzer"],
        "Gaming": ["Steam", "Xbox", "PSN", "Discord"],
        "Dev Platforms": ["GitHub","GitLab","Replit","HackerNews"],
    },
    "📧 Email": {
        "Breach Check": ["HaveIBeenPwned","DeHashed","LeakCheck"],
        "Validation": ["Hunter.io","Email-Checker.net","Verify-Email"],
        "Provider Info": ["MXToolbox","ViewDNS"],
    },
    "🌐 Domain / IP": {
        "Whois": ["ARIN","RIPE","APNIC","whois.domaintools.com"],
        "DNS": ["MXToolbox","DNSdumpster","SecurityTrails","DNSDB"],
        "Certificates": ["crt.sh","Censys","Certificate Transparency"],
        "Reputation": ["VirusTotal","Shodan","Censys","AlienVault OTX"],
        "OSINT Tools": ["Oathnet","Maltego","SpiderFoot","recon-ng"],
    },
    "📱 Phone Number": {
        "Carrier Info": ["NumLookup","AnyWho","Truecaller"],
        "Breach": ["HaveIBeenPwned phone","DeHashed"],
    },
    "🖼 Image": {
        "Reverse Search": ["Google Images","TinEye","Yandex Images"],
        "Metadata (EXIF)": ["exiftool","Jeffrey's Exif Viewer"],
    },
    "👥 Social Networks": {
        "Twitter/X":   ["Social Bearing","Foller.me","TweetDeck"],
        "Instagram":   ["Picuki","InstaDP","Imginn"],
        "LinkedIn":    ["CrossLinked","LinkedIn OSINT Guide"],
        "Facebook":    ["Who Posted What","StalkFace","Facebook Graph"],
        "Reddit":      ["Reddit Investigator","Pushshift","SnoopSnoo"],
    },
    "🗺 Physical Location": {
        "Maps": ["Google Maps","OpenStreetMap","Bing Maps","Waze"],
        "Satellite": ["Google Earth","Sentinel Hub","Copernicus"],
        "Geotag Analysis": ["GeoSpy.ai","GeoGuessr (training)","pic2map"],
    },
    "📄 Documents": {
        "Search": ["Google Dork filetype:","FOCA","Metagoofil"],
        "Metadata": ["exiftool","PDF Examiner","MAT2"],
    },
    "🔑 Credentials": {
        "Breach DBs": ["HaveIBeenPwned","LeakCheck","DeHashed","Snusbase"],
        "Paste Sites": ["Pastebin","Ghostbin","Hastebin","Rentry"],
    },
}

def osint_framework():
    section("OSINT FRAMEWORK TREE", c.R1)
    print(f"  {gradient_single('Interactive OSINT resource directory')}\n")
    categories = list(OSINT_TREE.keys())
    for i, cat in enumerate(categories, 1):
        print(f"  {c.D}[{c.R}{c.B}{th_accent()}{i:>2}{c.R}{c.D}]{c.R}  {c.W}{c.B}{cat}{c.R}")
    print(f"  {c.D}[{c.R}{c.B}{c.G} A{c.R}{c.D}]{c.R}  {c.W}Show all{c.R}")
    print(f"  {c.D}[{c.R}{c.R1} 0{c.R}{c.D}]{c.R}  {c.D}Back{c.R}\n")

    choice = inp("Select category")
    if choice == "0" or not choice: return
    if choice.upper() == "A":
        selected = list(OSINT_TREE.items())
    else:
        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(categories):
                warn("Invalid."); pause(); return
            selected = [(categories[idx], OSINT_TREE[categories[idx]])]
        except: warn("Invalid."); pause(); return

    for cat_name, subcats in selected:
        print(f"\n  {gradient_single(cat_name)}")
        sep()
        for subcat, tools in subcats.items():
            print(f"\n  {th_accent()}{c.B}  {subcat}{c.R}")
            for tool in tools:
                print(f"      {c.D}└─{c.R}  {c.W}{tool}{c.R}")

    print()
    pause()


# ──────────────────────────────────────────────────────────────
#  47  NETWORK DEEP LOOKUP
# ──────────────────────────────────────────────────────────────
def network_lookup():
    while True:
        section("NETWORK DEEP LOOKUP", c.G)
        print(f"  {c.D}[1]{c.R}  {c.W}Full IP / Domain Report{c.R}      {c.D}— geo, ASN, PTR, ports, abuse{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}ASN Lookup{c.R}                   {c.D}— get ASN info for IP or org{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}CIDR / BGP Prefix Lookup{c.R}     {c.D}— find IP block owner{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}Reverse DNS (PTR) Bulk{c.R}       {c.D}— reverse-resolve a list of IPs{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Open Port Scanner (fast){c.R}     {c.D}— scan common ports quickly{c.R}")
        print(f"  {c.D}[6]{c.R}  {c.W}Banner Grabber{c.R}               {c.D}— grab service banners on ports{c.R}")
        print(f"  {c.D}[7]{c.R}  {c.W}IP Reputation Check{c.R}          {c.D}— abuse/spam/blacklist check{c.R}")
        print(f"  {c.D}[8]{c.R}  {c.W}Network Route Map{c.R}            {c.D}— trace hops with geo per hop{c.R}")
        print(f"  {c.D}[9]{c.R}  {c.W}SSL / TLS Deep Inspect{c.R}       {c.D}— full cert chain + cipher info{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if not mode or mode == "0": break

        # ── shared helper ──────────────────────────────────────
        def ip_api(target, fields="query,country,countryCode,regionName,city,zip,lat,lon,isp,org,as,proxy,hosting,mobile,timezone,status,message"):
            url = f"http://ip-api.com/json/{target}?fields={fields}"
            req = urllib.request.Request(url, headers={"User-Agent": "Phantom-Toolkit"})
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.loads(r.read())

        def resolve(target):
            try:    return socket.gethostbyname(target)
            except: return target

        # ── 1. Full IP/Domain Report ───────────────────────────
        if mode == "1":
            section("FULL IP / DOMAIN REPORT")
            target = inp("IP address or domain")
            if not target: continue
            target = target.strip().replace("https://","").replace("http://","").split("/")[0]

            ip = resolve(target)
            row("Target",     target)
            row("Resolved IP", ip)

            # Reverse DNS
            try:
                ptr = socket.gethostbyaddr(ip)[0]
                row("Reverse DNS (PTR)", ptr)
            except: row("Reverse DNS (PTR)", "none")

            # Geo + ISP
            print(f"\n  {th_accent()}{c.B}[ Geolocation & Network ]{c.R}")
            try:
                d = ip_api(ip)
                if d.get("status") == "success":
                    for k,label in [("country","Country"),("regionName","Region"),
                                    ("city","City"),("zip","ZIP"),("lat","Lat"),
                                    ("lon","Lon"),("timezone","Timezone"),
                                    ("isp","ISP"),("org","Org"),("as","ASN")]:
                        if d.get(k): row(f"  {label}", str(d[k]))
                    for flag in ["proxy","hosting","mobile"]:
                        val = d.get(flag,False)
                        row(f"  {flag.capitalize()}", "YES" if val else "NO",
                            vc=c.R1 if val else c.G)
            except Exception as e: err(f"Geo lookup failed: {e}")

            # WHOIS quick
            print(f"\n  {th_accent()}{c.B}[ WHOIS (quick) ]{c.R}")
            try:
                req = urllib.request.Request(
                    f"https://rdap.arin.net/registry/ip/{ip}",
                    headers={"User-Agent":"Phantom","Accept":"application/json"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    rd = json.loads(r.read())
                name = rd.get("name","?")
                handle = rd.get("handle","?")
                kind = rd.get("type","?")
                row("  ARIN Name",   name)
                row("  Handle",      handle)
                row("  Type",        kind)
                for event in rd.get("events",[]):
                    if event.get("eventAction") == "last changed":
                        row("  Last Changed", event.get("eventDate","?")[:10])
            except Exception as e:
                row("  RDAP", f"Failed ({type(e).__name__})")

            # SSL cert if domain
            if target != ip:
                print(f"\n  {th_accent()}{c.B}[ SSL Certificate ]{c.R}")
                try:
                    import ssl
                    ctx = ssl.create_default_context()
                    with ctx.wrap_socket(
                        socket.create_connection((target,443),timeout=6),
                        server_hostname=target) as s:
                        cert = s.getpeercert()
                        subj = dict(x[0] for x in cert.get("subject",[]))
                        row("  CN",      subj.get("commonName","?"))
                        na = cert.get("notAfter","")
                        if na:
                            exp = datetime.strptime(na,"%b %d %H:%M:%S %Y %Z")
                            days = (exp - datetime.utcnow()).days
                            col = c.G if days>30 else c.Y if days>7 else c.R1
                            row("  Expires", na, vc=col)
                            row("  Days Left", str(days), vc=col)
                        sans = [v for _,v in cert.get("subjectAltName",[])]
                        row("  SANs", ", ".join(sans[:4]))
                except Exception as e:
                    row("  SSL", f"Failed: {e}")

            # Common ports quick check
            print(f"\n  {th_accent()}{c.B}[ Common Ports ]{c.R}")
            COMMON = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",
                      80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",
                      3306:"MySQL",3389:"RDP",8080:"HTTP-Alt",8443:"HTTPS-Alt"}
            open_ports = []
            for port, svc in COMMON.items():
                try:
                    s2 = socket.socket()
                    s2.settimeout(0.5)
                    if s2.connect_ex((ip, port)) == 0:
                        open_ports.append((port, svc))
                    s2.close()
                except: pass
            if open_ports:
                for port, svc in open_ports:
                    row(f"  Port {port}", f"OPEN  ({svc})", vc=c.G)
            else:
                row("  Open Ports", "None found (common ports)", vc=c.D)

            pause()

        # ── 2. ASN Lookup ──────────────────────────────────────
        elif mode == "2":
            section("ASN LOOKUP")
            target = inp("IP address, ASN number (e.g. AS15169), or org name")
            if not target: continue
            target = target.strip()
            try:
                if target.upper().startswith("AS") and target[2:].isdigit():
                    url = f"https://api.hackertarget.com/aslookup/?q={target}"
                else:
                    ip = resolve(target)
                    url = f"https://api.hackertarget.com/aslookup/?q={ip}"
                req = urllib.request.Request(url, headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = r.read().decode()
                for line in data.strip().splitlines():
                    print(f"  {c.W}{line}{c.R}")
                # Also try ipinfo
                ip2 = resolve(target) if not target.upper().startswith("AS") else target
                req2 = urllib.request.Request(
                    f"https://ipinfo.io/{ip2}/json",
                    headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req2, timeout=8) as r2:
                    d2 = json.loads(r2.read())
                sep()
                for k in ["ip","hostname","city","region","country","org","timezone"]:
                    if d2.get(k): row(f"  {k.capitalize()}", str(d2[k]))
            except Exception as e: err(str(e))
            pause()

        # ── 3. CIDR / BGP Prefix ──────────────────────────────
        elif mode == "3":
            section("CIDR / BGP PREFIX LOOKUP")
            target = inp("IP address or CIDR (e.g. 8.8.8.0/24)")
            if not target: continue
            try:
                ip = resolve(target.split("/")[0])
                req = urllib.request.Request(
                    f"https://api.hackertarget.com/aslookup/?q={ip}",
                    headers={"User-Agent":"Phantom"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    print(f"\n  {c.W}{r.read().decode().strip()}{c.R}")
                # RDAP for network block
                req2 = urllib.request.Request(
                    f"https://rdap.arin.net/registry/ip/{ip}",
                    headers={"User-Agent":"Phantom","Accept":"application/json"})
                with urllib.request.urlopen(req2, timeout=8) as r2:
                    rd = json.loads(r2.read())
                row("Network Name",   rd.get("name","?"))
                row("Handle",         rd.get("handle","?"))
                row("Start Address",  rd.get("startAddress","?"))
                row("End Address",    rd.get("endAddress","?"))
                row("IP Version",     rd.get("ipVersion","?"))
                row("Type",           rd.get("type","?"))
                # CIDR notation
                try:
                    start = rd.get("startAddress","")
                    end   = rd.get("endAddress","")
                    if start and end:
                        nets = list(ipaddress.summarize_address_range(
                            ipaddress.ip_address(start),
                            ipaddress.ip_address(end)))
                        row("CIDR Blocks", ", ".join(str(n) for n in nets[:4]))
                except: pass
            except Exception as e: err(str(e))
            pause()

        # ── 4. Bulk Reverse DNS ────────────────────────────────
        elif mode == "4":
            section("REVERSE DNS BULK LOOKUP")
            print(f"  {c.D}Enter IPs one per line. Blank to start.{c.R}\n")
            ips = []
            while True:
                ip_in = input(f"  {c.D}>{c.R} ").strip()
                if not ip_in: break
                ips.append(ip_in)
            if not ips: continue
            inf(f"Resolving {len(ips)} IPs...")
            results = {}
            lock = threading.Lock()
            def ptr_lookup(ip_addr):
                try:
                    host = socket.gethostbyaddr(ip_addr)[0]
                except Exception as e:
                    host = f"(no PTR: {e})"
                with lock: results[ip_addr] = host
            threads = [threading.Thread(target=ptr_lookup, args=(ip,), daemon=True) for ip in ips]
            for t in threads: t.start()
            for t in threads: t.join(timeout=6)
            sep()
            for ip_addr in ips:
                host = results.get(ip_addr, "(timeout)")
                col = c.G if not host.startswith("(") else c.D
                row(ip_addr, host, vc=col)
            pause()

        # ── 5. Fast Port Scanner ───────────────────────────────
        elif mode == "5":
            section("FAST PORT SCANNER")
            target = inp("Target IP or hostname")
            if not target: continue
            try:
                ports_in = inp("Port range (e.g. 1-1024) or list (80,443,8080)")
                port_list = []
                if "," in ports_in:
                    port_list = [int(p.strip()) for p in ports_in.split(",") if p.strip().isdigit()]
                elif "-" in ports_in:
                    a2, b2 = ports_in.split("-",1)
                    port_list = list(range(int(a2), int(b2)+1))
                else:
                    port_list = [int(ports_in)] if ports_in.strip().isdigit() else list(range(1,1025))
                ip = resolve(target)
                row("Target", f"{target}  ({ip})")
                row("Ports",  f"{min(port_list)}–{max(port_list)}  ({len(port_list)} ports)")
                inf("Scanning...")
                open_p = []; lock2 = threading.Lock()
                def scan_port(port):
                    try:
                        s3 = socket.socket(); s3.settimeout(0.4)
                        if s3.connect_ex((ip, port)) == 0:
                            try:
                                svc = socket.getservbyport(port)
                            except: svc = "unknown"
                            with lock2: open_p.append((port, svc))
                        s3.close()
                    except: pass
                ts = [threading.Thread(target=scan_port, args=(p,), daemon=True) for p in port_list]
                batch = 200
                for i in range(0, len(ts), batch):
                    chunk = ts[i:i+batch]
                    for t in chunk: t.start()
                    for t in chunk: t.join(timeout=3)
                    done = min(i+batch, len(ts))
                    pct = done/len(ts)*100
                    print(f"\r  {gradient_single(f'Progress: {done}/{len(ts)} ({pct:.0f}%)', bold=False)}  ", end="", flush=True)
                print()
                sep()
                if open_p:
                    open_p.sort()
                    ok(f"{len(open_p)} open port(s) found")
                    for port, svc in open_p:
                        row(f"  Port {port}", f"OPEN  —  {svc}", vc=c.G)
                else:
                    warn("No open ports found in range.")
            except Exception as e: err(str(e))
            pause()

        # ── 6. Banner Grabber ─────────────────────────────────
        elif mode == "6":
            section("BANNER GRABBER")
            target = inp("Target IP or hostname")
            if not target: continue
            ports_raw = inp("Ports to probe (comma-separated, e.g. 21,22,25,80,443)")
            try:
                ports_bg = [int(p.strip()) for p in ports_raw.split(",") if p.strip().isdigit()] or [21,22,25,80,443,8080]
                ip = resolve(target)
                row("Target", f"{target} ({ip})")
                sep()
                for port in ports_bg:
                    try:
                        s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s4.settimeout(2)
                        if s4.connect_ex((ip, port)) != 0:
                            row(f"  Port {port}", "CLOSED", vc=c.D)
                            s4.close(); continue
                        # Send basic probe
                        probe_map = {80:b"HEAD / HTTP/1.0\r\n\r\n",
                                     443:b"HEAD / HTTP/1.0\r\n\r\n",
                                     21:b"", 22:b"", 25:b"EHLO phantom\r\n"}
                        probe = probe_map.get(port, b"")
                        if probe: s4.send(probe)
                        banner_raw = b""
                        s4.settimeout(1.5)
                        try:
                            while True:
                                chunk = s4.recv(512)
                                if not chunk: break
                                banner_raw += chunk
                                if len(banner_raw) > 1024: break
                        except: pass
                        s4.close()
                        banner_txt = banner_raw.decode("utf-8","replace").strip()[:80].replace("\n"," ").replace("\r","")
                        if banner_txt:
                            row(f"  Port {port}", banner_txt, vc=c.G)
                        else:
                            row(f"  Port {port}", "OPEN (no banner)", vc=c.Y)
                    except Exception as ex:
                        row(f"  Port {port}", f"Error: {ex}", vc=c.R1)
            except Exception as e: err(str(e))
            pause()

        # ── 7. IP Reputation ──────────────────────────────────
        elif mode == "7":
            section("IP REPUTATION CHECK")
            target = inp("IP address to check")
            if not target: continue
            ip = resolve(target)
            row("Checking", ip)

            # AbuseIPDB public check (no key needed for basic)
            print(f"\n  {th_accent()}{c.B}[ DNS Blacklist (DNSBL) Checks ]{c.R}")
            DNSBL_LIST = [
                "zen.spamhaus.org", "bl.spamcop.net",
                "dnsbl.sorbs.net",  "b.barracudacentral.org",
                "dnsbl-1.uceprotect.net", "psbl.surriel.com",
                "ix.dnsbl.manitu.net", "all.spamrats.com",
            ]
            rev_ip = ".".join(reversed(ip.split(".")))
            listed = []
            for bl in DNSBL_LIST:
                query = f"{rev_ip}.{bl}"
                try:
                    socket.gethostbyname(query)
                    listed.append(bl)
                    row(f"  {bl}", "LISTED", vc=c.R1)
                except socket.gaierror:
                    row(f"  {bl}", "clean", vc=c.G)

            sep()
            if listed:
                warn(f"IP is listed on {len(listed)} blacklist(s)!")
            else:
                ok("IP is clean on all checked blacklists.")

            # Geo / proxy flags
            print(f"\n  {th_accent()}{c.B}[ IP API Flags ]{c.R}")
            try:
                d = ip_api(ip)
                if d.get("status") == "success":
                    row("  ISP",     d.get("isp","?"))
                    row("  Org",     d.get("org","?"))
                    for flag in ["proxy","hosting","mobile"]:
                        val = d.get(flag,False)
                        row(f"  {flag.capitalize()}", "YES" if val else "NO",
                            vc=c.R1 if val else c.G)
            except Exception as e: err(f"ip-api: {e}")
            pause()

        # ── 8. Network Route Map ──────────────────────────────
        elif mode == "8":
            section("NETWORK ROUTE MAP (GEO TRACEROUTE)")
            target = inp("Target IP or hostname")
            if not target: continue
            ip = resolve(target)
            row("Target", f"{target} ({ip})")
            inf("Tracing route (may take 30s)...")
            sep()

            cmd = (["tracert","-h","20",target] if platform.system()=="Windows"
                   else ["traceroute","-m","20","-w","2",target])
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                hop_ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', proc.stdout)
                hop_ips = list(dict.fromkeys(hop_ips))  # deduplicate, keep order

                for i, hop_ip in enumerate(hop_ips[:20], 1):
                    try:
                        d2 = ip_api(hop_ip,"query,country,city,isp,status")
                        if d2.get("status") == "success":
                            loc = f"{d2.get('city','?')}, {d2.get('country','?')}"
                            isp = d2.get("isp","?")[:30]
                        else:
                            loc = "private/unknown"; isp = ""
                    except: loc = "lookup failed"; isp = ""
                    hop_grad = gradient_single(f"Hop {i:>2}", bold=False)
                    print(f"  {hop_grad}  {c.W}{hop_ip:<18}{c.R}  {c.C}{loc:<28}{c.R}  {c.D}{isp}{c.R}")
            except FileNotFoundError:
                err("traceroute not found. Install traceroute (Linux) or use Windows.")
            except Exception as e: err(str(e))
            pause()

        # ── 9. SSL / TLS Deep Inspect ─────────────────────────
        elif mode == "9":
            section("SSL / TLS DEEP INSPECT")
            domain = inp("Domain (e.g. example.com)")
            if not domain: continue
            domain = domain.strip().replace("https://","").replace("http://","").split("/")[0]
            try: port_ssl = int(inp("Port (default 443)") or "443")
            except: port_ssl = 443
            try:
                import ssl
                ctx = ssl.create_default_context()
                conn = socket.create_connection((domain, port_ssl), timeout=8)
                ssl_sock = ctx.wrap_socket(conn, server_hostname=domain)
                cert = ssl_sock.getpeercert()
                cipher = ssl_sock.cipher()
                proto  = ssl_sock.version()
                ssl_sock.close()

                row("Domain",      domain)
                row("Protocol",    proto or "?")
                row("Cipher",      cipher[0] if cipher else "?")
                row("Key Bits",    str(cipher[2]) if cipher and len(cipher)>2 else "?")
                sep()
                subj = dict(x[0] for x in cert.get("subject",[]))
                row("Common Name", subj.get("commonName","?"))
                issuer = dict(x[0] for x in cert.get("issuer",[]))
                row("Issued By",   issuer.get("organizationName","?"))
                row("Serial",      str(cert.get("serialNumber","?"))[:24])
                nb = cert.get("notBefore",""); na = cert.get("notAfter","")
                row("Valid From",  nb)
                if na:
                    try:
                        exp = datetime.strptime(na,"%b %d %H:%M:%S %Y %Z")
                        days = (exp - datetime.utcnow()).days
                        col = c.G if days>30 else c.Y if days>7 else c.R1
                        row("Expires",   na, vc=col)
                        row("Days Left", str(days), vc=col)
                    except: row("Expires", na)
                sans = [v for _,v in cert.get("subjectAltName",[])]
                if sans:
                    print(f"\n  {th_accent()}{c.B}Subject Alt Names ({len(sans)}):{c.R}")
                    for san in sans[:10]: print(f"    {c.W}• {san}{c.R}")
                # Security grade hint
                sec_issues = []
                if proto in ("SSLv2","SSLv3","TLSv1","TLSv1.1"):
                    sec_issues.append(f"Outdated protocol: {proto}")
                if cipher and any(w in cipher[0] for w in ("RC4","DES","MD5","NULL","EXPORT","anon")):
                    sec_issues.append(f"Weak cipher: {cipher[0]}")
                sep()
                if sec_issues:
                    for issue in sec_issues: warn(issue)
                else:
                    ok("No obvious TLS weaknesses detected.")
            except Exception as e: err(str(e))
            pause()

# ──────────────────────────────────────────────────────────────
#  48  DISCORD USER / SERVER LOOKUP
# ──────────────────────────────────────────────────────────────
def discord_lookup():
    while True:
        section("DISCORD LOOKUP", c.BL)
        print(f"  {c.D}[1]{c.R}  {c.W}User ID Lookup{c.R}           {c.D}— decode snowflake + fetch profile{c.R}")
        print(f"  {c.D}[2]{c.R}  {c.W}Server Invite Lookup{c.R}     {c.D}— get server info from invite code{c.R}")
        print(f"  {c.D}[3]{c.R}  {c.W}Webhook Info Lookup{c.R}      {c.D}— inspect webhook URL details{c.R}")
        print(f"  {c.D}[4]{c.R}  {c.W}Snowflake Decoder{c.R}        {c.D}— decode any Discord snowflake ID{c.R}")
        print(f"  {c.D}[5]{c.R}  {c.W}Bot Token Inspector{c.R}      {c.D}— decode token payload (no auth){c.R}")
        print(f"  {c.D}[6]{c.R}  {c.W}CDN Asset Lookup{c.R}         {c.D}— fetch user avatar / banner URL{c.R}")
        print(f"  {c.D}[7]{c.R}  {c.W}Username → ID Search{c.R}     {c.D}— search known APIs for user ID{c.R}")
        print(f"  {c.D}[8]{c.R}  {c.W}Guild / Server ID Lookup{c.R} {c.D}— decode server snowflake{c.R}")
        print(f"  {c.D}[0]{c.R}  {c.D}Back{c.R}\n")
        mode = inp("Select")
        if not mode or mode == "0": break

        DISCORD_EPOCH = 1420070400000

        def decode_snowflake(sid):
            try:
                sid_int = int(sid)
                timestamp_ms = (sid_int >> 22) + DISCORD_EPOCH
                worker_id    = (sid_int & 0x3E0000) >> 17
                process_id   = (sid_int & 0x1F000) >> 12
                increment    = sid_int & 0xFFF
                created_at   = datetime.utcfromtimestamp(timestamp_ms / 1000)
                return {
                    "id":          sid_int,
                    "timestamp_ms":timestamp_ms,
                    "created_at":  created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "worker_id":   worker_id,
                    "process_id":  process_id,
                    "increment":   increment,
                    "age_days":    (datetime.utcnow() - created_at).days,
                }
            except Exception as e:
                return {"error": str(e)}

        def discord_api_get(path, token=None):
            url = "https://discord.com/api/v10" + path
            headers = {"User-Agent": "Mozilla/5.0"}
            if token: headers["Authorization"] = token
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.loads(r.read()), r.status

        # ── 1. User ID Lookup ─────────────────────────────────
        if mode == "1":
            section("DISCORD USER ID LOOKUP")
            uid = inp("Discord User ID (snowflake)")
            if not uid: continue
            uid = uid.strip()

            # Snowflake decode
            snow = decode_snowflake(uid)
            if "error" in snow:
                err(f"Invalid snowflake: {snow['error']}"); pause(); continue
            row("User ID",        uid)
            row("Account Created",snow["created_at"])
            row("Account Age",    f"{snow['age_days']} days")
            row("Worker ID",      str(snow["worker_id"]))
            row("Process ID",     str(snow["process_id"]))
            row("Increment",      str(snow["increment"]))

            # Public profile via Discord API (no auth needed for basic)
            print(f"\n  {th_accent()}{c.B}[ Public Profile ]{c.R}")
            try:
                data, status = discord_api_get(f"/users/{uid}")
                username  = data.get("username","?")
                discrim   = data.get("discriminator","0")
                global_name = data.get("global_name") or username
                bot       = data.get("bot", False)
                avatar    = data.get("avatar")
                banner    = data.get("banner")
                flags_val = data.get("public_flags", 0)
                row("Username",     username + (f"#{discrim}" if discrim != "0" else ""))
                row("Display Name", global_name)
                row("Bot",          "YES" if bot else "NO", vc=c.R1 if bot else c.G)
                if avatar:
                    ext = "gif" if avatar.startswith("a_") else "png"
                    row("Avatar URL",  f"https://cdn.discordapp.com/avatars/{uid}/{avatar}.{ext}?size=1024")
                if banner:
                    ext2 = "gif" if banner.startswith("a_") else "png"
                    row("Banner URL",  f"https://cdn.discordapp.com/banners/{uid}/{banner}.{ext2}?size=1024")

                # Decode public flags
                FLAG_MAP = {
                    1: "Discord Staff",          2: "Partner",
                    4: "HypeSquad Events",        8: "Bug Hunter Lv1",
                    64: "HypeSquad Bravery",      128: "HypeSquad Brilliance",
                    256: "HypeSquad Balance",     512: "Early Supporter",
                    16384: "Bug Hunter Lv2",      131072: "Verified Bot Dev",
                    4194304: "Active Developer",
                }
                badges = [label for bit, label in FLAG_MAP.items() if flags_val & bit]
                if badges:
                    row("Badges", ", ".join(badges), vc=c.Y)
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    inf("Public lookup requires no auth — but Discord returned 401.")
                    inf("Try using a bot token in option [5] for full lookup.")
                elif e.code == 404:
                    warn("User not found or account deleted.")
                else:
                    err(f"Discord API: HTTP {e.code}")
            except Exception as e:
                err(f"Lookup failed: {e}")
            pause()

        # ── 2. Server Invite Lookup ───────────────────────────
        elif mode == "2":
            section("SERVER INVITE LOOKUP")
            invite = inp("Invite code or full URL (e.g. discord.gg/abc123)")
            if not invite: continue
            invite = invite.strip()
            # Extract code from URL
            invite = re.sub(r'https?://(www\.)?(discord\.gg|discord\.com/invite)/?', '', invite)
            invite = invite.strip("/")
            try:
                data, _ = discord_api_get(
                    f"/invites/{invite}?with_counts=true&with_expiration=true")
                guild = data.get("guild", {})
                channel = data.get("channel", {})
                inviter = data.get("inviter", {})
                approx_members = data.get("approximate_member_count", "?")
                approx_online  = data.get("approximate_presence_count", "?")

                row("Server Name",      guild.get("name","?"))
                row("Server ID",        guild.get("id","?"))
                row("Description",      (guild.get("description") or "none")[:60])
                row("Verification Lvl", str(guild.get("verification_level","?")))
                row("Boost Level",      str(guild.get("premium_tier","?")))
                row("Total Members",    str(approx_members))
                row("Online Members",   str(approx_online))
                row("Channel",         f"#{channel.get('name','?')} (ID: {channel.get('id','?')})")
                if inviter:
                    inv_name = inviter.get("username","?")
                    inv_id   = inviter.get("id","?")
                    row("Invited By",   f"{inv_name} ({inv_id})")
                    snow2 = decode_snowflake(inv_id)
                    if "error" not in snow2:
                        row("Inviter Created", snow2["created_at"])

                # Guild icon
                icon = guild.get("icon")
                if icon:
                    ext = "gif" if icon.startswith("a_") else "png"
                    row("Icon URL", f"https://cdn.discordapp.com/icons/{guild.get('id')}/{icon}.{ext}?size=512")

                # Snowflake decode server ID
                gid = guild.get("id","")
                if gid:
                    sep()
                    snow3 = decode_snowflake(gid)
                    if "error" not in snow3:
                        row("Server Created", snow3["created_at"])
                        row("Server Age",     f"{snow3['age_days']} days")

                expires = data.get("expires_at")
                if expires:
                    row("Invite Expires",  expires[:10])
                else:
                    row("Invite Expires",  "Never (permanent)")

                # Features
                feats = guild.get("features", [])
                if feats:
                    print(f"\n  {th_accent()}{c.B}Server Features:{c.R}")
                    for feat in feats:
                        print(f"    {c.D}✦  {c.W}{feat.replace('_',' ').title()}{c.R}")

            except urllib.error.HTTPError as e:
                if e.code == 404: warn("Invite not found or expired.")
                else: err(f"Discord API: HTTP {e.code}")
            except Exception as e: err(str(e))
            pause()

        # ── 3. Webhook Info Lookup ────────────────────────────
        elif mode == "3":
            section("WEBHOOK INFO LOOKUP")
            wh_url = inp("Webhook URL")
            if not wh_url: continue
            try:
                req = urllib.request.Request(
                    wh_url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    data = json.loads(r.read())
                row("Webhook ID",      data.get("id","?"))
                row("Webhook Name",    data.get("name","?"))
                row("Channel ID",      data.get("channel_id","?"))
                row("Guild ID",        data.get("guild_id","?"))
                row("Token",           data.get("token","?")[:20] + "...")
                row("Type",            str(data.get("type","?")))
                # Decode IDs
                for field, label in [("id","Webhook Created"),("channel_id","Channel Created"),("guild_id","Server Created")]:
                    fid = data.get(field,"")
                    if fid:
                        snow = decode_snowflake(fid)
                        if "error" not in snow:
                            row(f"  {label}", snow["created_at"])
                # Avatar
                av = data.get("avatar")
                if av:
                    row("Avatar", f"https://cdn.discordapp.com/avatars/{data['id']}/{av}.png")
            except urllib.error.HTTPError as e:
                if e.code == 401: warn("Webhook token invalid or deleted.")
                elif e.code == 404: warn("Webhook not found.")
                else: err(f"HTTP {e.code}")
            except Exception as e: err(str(e))
            pause()

        # ── 4. Snowflake Decoder ──────────────────────────────
        elif mode == "4":
            section("SNOWFLAKE DECODER")
            while True:
                sid = inp("Snowflake ID (or 0 to stop)")
                if not sid or sid == "0": break
                snow = decode_snowflake(sid)
                if "error" in snow:
                    err(f"Invalid: {snow['error']}")
                else:
                    row("ID",           str(snow["id"]))
                    row("Created At",   snow["created_at"])
                    row("Age (days)",   str(snow["age_days"]))
                    row("Timestamp ms", str(snow["timestamp_ms"]))
                    row("Worker ID",    str(snow["worker_id"]))
                    row("Process ID",   str(snow["process_id"]))
                    row("Increment",    str(snow["increment"]))
                    sep()

        # ── 5. Bot Token Inspector ────────────────────────────
        elif mode == "5":
            section("BOT TOKEN INSPECTOR")
            warn("This only decodes the token — it does NOT authenticate.")
            token = inp("Bot token (format: xxxxxxxx.xxxxxx.xxxxxxxxxxxxx)")
            if not token: continue
            parts = token.strip().split(".")
            if len(parts) < 2:
                err("Invalid token format."); pause(); continue
            try:
                # Part 1: base64-encoded user ID
                id_part = parts[0]
                # Add padding
                pad = 4 - len(id_part) % 4
                if pad != 4: id_part += "=" * pad
                decoded_id = base64.b64decode(id_part).decode("utf-8","replace")
                row("Encoded User ID",  parts[0])
                row("Decoded User ID",  decoded_id)

                snow = decode_snowflake(decoded_id)
                if "error" not in snow:
                    row("Account Created", snow["created_at"])
                    row("Account Age",     f"{snow['age_days']} days")

                # Part 2: timestamp
                try:
                    ts_part = parts[1]
                    pad2 = 4 - len(ts_part) % 4
                    if pad2 != 4: ts_part += "=" * pad2
                    ts_bytes = base64.b64decode(ts_part)
                    ts_int = int.from_bytes(ts_bytes, "big") + 1293840000
                    ts_dt  = datetime.utcfromtimestamp(ts_int)
                    row("Token Issued",    ts_dt.strftime("%Y-%m-%d %H:%M:%S UTC"))
                except: row("Token Timestamp", "Could not decode")

                row("Token Length",    str(len(token)))
                ok("Token decoded (structural only — no auth attempted).")
            except Exception as e: err(str(e))
            pause()

        # ── 6. CDN Asset Lookup ───────────────────────────────
        elif mode == "6":
            section("DISCORD CDN ASSET LOOKUP")
            uid = inp("User or Guild ID")
            if not uid: continue
            asset = inp("Asset hash (from API response, e.g. a_abc123)")
            if not asset: continue
            atype = inp("Type: [1] Avatar  [2] Banner  [3] Guild Icon  [4] Guild Banner") or "1"
            atype_map = {"1":"avatars","2":"banners","3":"icons","4":"guilds"}
            folder = atype_map.get(atype, "avatars")
            ext = "gif" if asset.startswith("a_") else "png"

            if folder in ("avatars","banners"):
                url = f"https://cdn.discordapp.com/{folder}/{uid}/{asset}.{ext}?size=4096"
            elif folder == "icons":
                url = f"https://cdn.discordapp.com/icons/{uid}/{asset}.{ext}?size=4096"
            else:
                url = f"https://cdn.discordapp.com/guilds/{uid}/splash/{asset}.{ext}?size=4096"

            row("Asset URL", url)
            row("Animated",  "YES (GIF)" if asset.startswith("a_") else "NO (static)")

            # Check if URL is live
            try:
                req = urllib.request.Request(url, method="HEAD",
                                              headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    ok(f"Asset is live (HTTP {r.status})")
                    row("Content-Type",  r.headers.get("Content-Type","?"))
                    cl = r.headers.get("Content-Length","?")
                    if cl != "?": row("File Size", f"{int(cl):,} bytes")
            except urllib.error.HTTPError as e:
                warn(f"Asset returned HTTP {e.code} (may be deleted)")
            except Exception as e:
                warn(f"Could not verify: {e}")

            # Open in browser
            if inp("Open in browser? (y/n)").lower() == "y":
                try:
                    if platform.system()=="Windows":   os.startfile(url)
                    elif platform.system()=="Darwin":  subprocess.Popen(["open", url])
                    else:                               subprocess.Popen(["xdg-open", url])
                except: pass
            pause()

        # ── 7. Username → ID Search ───────────────────────────
        elif mode == "7":
            section("USERNAME → DISCORD ID SEARCH")
            username = inp("Discord username")
            if not username: continue
            inf(f"Searching for '{username}' across OSINT sources...")
            # Check disboard, discord.me, top.gg and similar profile pages
            SOURCES = [
                ("Discord.me",   f"https://discord.me/{username}"),
                ("Disboard",     f"https://disboard.org/user/{username}"),
                ("Discord.io",   f"https://discord.io/{username}"),
            ]
            for name2, url2 in SOURCES:
                try:
                    req = urllib.request.Request(
                        url2, headers={"User-Agent":"Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=5) as r:
                        content = r.read().decode("utf-8","replace")
                        # Try to find Discord ID in page
                        ids_found = re.findall(r'\b\d{17,19}\b', content)
                        ids_found = list(dict.fromkeys(ids_found))[:3]
                        if ids_found:
                            row(name2, f"Found IDs: {', '.join(ids_found)}", vc=c.G)
                        else:
                            row(name2, "Profile may exist (no ID extracted)", vc=c.Y)
                except urllib.error.HTTPError as e:
                    row(name2, f"HTTP {e.code}", vc=c.D)
                except Exception:
                    row(name2, "Not found / timeout", vc=c.D)
            inf("For definitive lookup, use the user's snowflake ID with option [1].")
            pause()

        # ── 8. Guild / Server ID Lookup ───────────────────────
        elif mode == "8":
            section("GUILD / SERVER ID LOOKUP")
            gid = inp("Server (Guild) ID")
            if not gid: continue
            snow = decode_snowflake(gid)
            if "error" in snow:
                err(f"Invalid snowflake: {snow['error']}"); pause(); continue
            row("Guild ID",      gid)
            row("Created At",    snow["created_at"])
            row("Server Age",    f"{snow['age_days']} days")
            row("Timestamp ms",  str(snow["timestamp_ms"]))
            row("Worker ID",     str(snow["worker_id"]))
            row("Process ID",    str(snow["process_id"]))
            row("Increment",     str(snow["increment"]))
            inf("For full server info, use an invite code with option [2].")
            pause()


# ──────────────────────────────────────────────────────────────
#  DISPATCH TABLE
# ──────────────────────────────────────────────────────────────
DISPATCH = {
    "system_info":      system_info,
    "net_info":         net_info,
    "whois_lookup":     whois_lookup,
    "dns_lookup":       dns_lookup,
    "ip_geo":           ip_geo,
    "ping_host":        ping_host,
    "ip_range_ping":    ip_range_ping,
    "port_scanner":     port_scanner,
    "traceroute":       traceroute,
    "subnet_calc":      subnet_calc,
    "wifi_offliner":    wifi_offliner,
    "speed_test":       speed_test,
    "open_connections": open_connections,
    "arp_table":        arp_table,
    "firewall_view":    firewall_view,
    "bandwidth_mon":    bandwidth_mon,
    "latency_monitor":  latency_monitor,
    "packet_loss":      packet_loss,
    "stability_log":    stability_log,
    "localhost_stress": localhost_stress,
    "hash_gen":         hash_gen,
    "b64_tool":         b64_tool,
    "rot13_tool":       rot13_tool,
    "caesar_tool":      caesar_tool,
    "pass_gen":         pass_gen,
    "file_manager":     file_manager,
    "file_hash":        file_hash,
    "sys_monitor":      sys_monitor,
    "env_vars":         env_vars,
    "proc_list":        proc_list,
    "weather":          weather,
    "http_headers":     http_headers,
    "url_tool":         url_tool,
    "mac_lookup":       mac_lookup,
    "ascii_art":        ascii_art,
    "discord_tools":    discord_tools,
    "telegram_tools":   telegram_tools,
    "oathnet_tools":    oathnet_tools,
    "anon_tools":       anon_tools,
    "social_finder":    social_finder,
    "forensic_tools":   forensic_tools,
    "stego_tools":      stego_tools,
    "osint_framework":  osint_framework,
    "network_lookup":   network_lookup,
    "discord_lookup":   discord_lookup,
    "ai_assistant":     ai_assistant,
    "themes_menu":      themes_menu,
    "install_deps":     install_deps,
}

# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────
def main():
    fix_win()
    splash()
    while True:
        choice = main_menu()
        cl = choice.lower()

        if cl in ("00", "0", "exit", "quit", "q"):
            clr()
            print(f"\n  {gradient_single('PHANTOM TOOLKIT  —  Session ended.', bold=True)}")
            print(f"  {c.D}{CREDIT}{c.R}\n")
            break

        elif cl in ("home", "h", "splash", "back"):
            splash()
            continue

        fn = get_func(choice)
        if fn and fn in DISPATCH:
            clr(); banner(); DISPATCH[fn]()
        else:
            warn(f"'{choice}' is not a valid module."); time.sleep(0.7)

if __name__ == "__main__":
    main()
