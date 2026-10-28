#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tic Tac Chaos - a party-style tic-tac-toe game (Python + Pygame).

Run it:
    pip install pygame
    python tic_tac_chaos.py

Everything (graphics, confetti, sounds) is generated in code - no image or
audio files. Settings and stats are saved next to this file in
tic_tac_chaos_save.json.

Controls: mouse/touch everywhere, number keys 1-9 place a mark
(1 = top-left, 9 = bottom-right). In replay: Space = play/pause,
Left/Right = step.
"""
import array
import io
import json
import math
import os
import random
import sys
from functools import lru_cache

try:
    import pygame
except ImportError:
    print("Pygame is not installed. Run:  pip install pygame")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tic_tac_chaos_save.json")

# Midway theme fonts: put Bungee-Regular.ttf and Fredoka.ttf in a "fonts" folder next to this file.
# If they're missing the game falls back to Impact / Trebuchet MS (same fallbacks as the HTML design).
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
BUNGEE = os.path.join(FONT_DIR, "Bungee-Regular.ttf")
FREDOKA = os.path.join(FONT_DIR, "Fredoka.ttf")
DISPLAY_FONT = BUNGEE if os.path.isfile(BUNGEE) else "impact,arialblack,arial"
TEXT_FONT = FREDOKA if os.path.isfile(FREDOKA) else "trebuchetms,arial"

# Midway palette (from the HTML design)
RED, BLUE, SKY, NIGHT, BULB, CANVAS = (239, 51, 64), (47, 107, 255), (76, 195, 255), (10, 18, 64), (255, 210, 63), (244, 246, 255)
CURTAIN_RED = (214, 31, 44)

# Carnival / arcade stickers (same SVG artwork as the HTML design, rendered by pygame)
STICKERS = {
    "pretzel": '<g fill="none" stroke="#C9822B" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 40C6 30 6 14 18 12C26 11 28 20 24 26C21 31 30 36 34 40"/><path d="M34 40C42 30 42 14 30 12C22 11 20 20 24 26C27 31 18 36 14 40"/><path d="M14 40Q24 47 34 40"/></g><g fill="#fff"><circle cx="8.5" cy="23" r="1.4"/><circle cx="39.5" cy="23" r="1.4"/><circle cx="25.5" cy="16.4" r="1.4"/></g>',
    "pin": '<path d="M24 3C19.5 3 18 8 20 12.5C21.4 15.7 17 19 16 27C15.2 34 17.6 45 24 45C30.4 45 32.8 34 32 27C31 19 26.6 15.7 28 12.5C30 8 28.5 3 24 3Z" fill="#fff"/><path d="M20.2 14.5Q24 17 27.8 14.5L27.2 18Q24 20.4 20.8 18Z" fill="#EF3340"/><path d="M16.2 29Q24 32 31.8 29L32 33Q24 36.4 16 33Z" fill="#EF3340"/>',
    "ball": '<circle cx="24" cy="24" r="20" fill="#0A1240"/><path d="M11.5 15a14 14 0 0 1 8-7" stroke="#fff" stroke-opacity=".4" stroke-width="3" stroke-linecap="round" fill="none"/><circle cx="20" cy="18" r="2.6" fill="#fff"/><circle cx="28" cy="16" r="2.6" fill="#fff"/><circle cx="26" cy="24" r="2.6" fill="#fff"/>',
    "stick": '<rect x="6" y="32" width="36" height="12" rx="4" fill="#0A1240"/><rect x="22" y="16" width="4" height="18" fill="#E8EDFF"/><circle cx="24" cy="12" r="9" fill="#FFD23F"/><circle cx="21" cy="9" r="2.6" fill="#fff" fill-opacity=".7"/><circle cx="13" cy="38" r="2" fill="#EF3340"/><circle cx="35" cy="38" r="2" fill="#4CC3FF"/>',
    "pad": '<rect x="3" y="12" width="42" height="26" rx="13" fill="#0A1240"/><rect x="11" y="23" width="12" height="4" fill="#fff"/><rect x="15" y="19" width="4" height="12" fill="#fff"/><circle cx="32" cy="22" r="2.8" fill="#FFD23F"/><circle cx="38" cy="28" r="2.8" fill="#EF3340"/>',
    "balloon": '<path d="M24 3C14 3 9 11 11 20C13 29 20 33 24 34C28 33 35 29 37 20C39 11 34 3 24 3Z" fill="#FFD23F"/><path d="M24 34l-3 4h6Z" fill="#E8A800"/><path d="M24 38c-3 3 3 5 0 9" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/><ellipse cx="17" cy="14" rx="3" ry="5" fill="#fff" fill-opacity=".5" transform="rotate(20 17 14)"/>',
    "corn": '<g fill="#FFF3B0"><circle cx="15" cy="14" r="6"/><circle cx="25" cy="10" r="7"/><circle cx="34" cy="15" r="6"/><circle cx="21" cy="19" r="6"/><circle cx="30" cy="21" r="5.5"/></g><path d="M10 22h28l-3.5 22h-21Z" fill="#fff"/><path d="M16 22L17.4 44M24 22V44M32 22L30.6 44" stroke="#EF3340" stroke-width="4.5"/>',
    "floss": '<rect x="22" y="26" width="4" height="20" rx="2" fill="#fff"/><g fill="#FF9AD1"><circle cx="16" cy="18" r="8"/><circle cx="24" cy="12" r="9"/><circle cx="32" cy="18" r="8"/><circle cx="24" cy="24" r="8"/></g><path d="M17 17q3-4 7-2M26 22q4 0 5-4" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-linecap="round" fill="none"/>',
    "wheel": '<g stroke="#0A1240" stroke-width="2.5" stroke-linecap="round" fill="none"><circle cx="24" cy="21" r="16"/><path d="M24 5V37M8 21H40M12.7 9.7L35.3 32.3M35.3 9.7L12.7 32.3"/><path d="M24 21L14 46M24 21L34 46"/></g><g fill="#FFD23F"><circle cx="24" cy="5" r="3"/><circle cx="40" cy="21" r="3"/><circle cx="24" cy="37" r="3"/><circle cx="8" cy="21" r="3"/></g><g fill="#fff"><circle cx="35.3" cy="9.7" r="3"/><circle cx="35.3" cy="32.3" r="3"/><circle cx="12.7" cy="9.7" r="3"/><circle cx="12.7" cy="32.3" r="3"/></g><circle cx="24" cy="21" r="2.4" fill="#0A1240"/>',
    "ticket": '<path d="M4 12h40v8a4 4 0 0 0 0 8v8H4v-8a4 4 0 0 0 0-8Z" fill="#FFD23F"/><path d="M16 14v20" stroke="#B87D00" stroke-width="2" stroke-dasharray="3 3"/><path d="M24 24h14" stroke="#B87D00" stroke-width="3" stroke-linecap="round"/>',
    "dice": '<rect x="6" y="6" width="36" height="36" rx="8" fill="#fff"/><g fill="#0A1240"><circle cx="16" cy="16" r="3.2"/><circle cx="32" cy="16" r="3.2"/><circle cx="24" cy="24" r="3.2"/><circle cx="16" cy="32" r="3.2"/><circle cx="32" cy="32" r="3.2"/></g>',
    "cup": '<path d="M14 6h20v12c0 7-4.5 11-10 11s-10-4-10-11Z" fill="#FFD23F"/><path d="M14 10H7c0 8 3 12 8 13M34 10h7c0 8-3 12-8 13" stroke="#FFD23F" stroke-width="3" fill="none" stroke-linecap="round"/><rect x="21.5" y="29" width="5" height="8" fill="#E8A800"/><rect x="14" y="37" width="20" height="6" rx="2" fill="#FFD23F"/><path d="M18 10v8" stroke="#fff" stroke-opacity=".6" stroke-width="2.5" stroke-linecap="round"/>',
}

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
CELL_NAMES = ["top-left", "top-middle", "top-right", "middle-left", "center",
              "middle-right", "bottom-left", "bottom-middle", "bottom-right"]

# (emoji, short label used if the computer has no emoji font)
PIECES = [("❌", "X"), ("⭕", "O"), ("🍕", "Pz"), ("🍔", "Bg"), ("🐱", "Ct"), ("🐶", "Dg"),
          ("🔥", "Fi"), ("💧", "Dr"), ("🦄", "Un"), ("🐉", "Dn"), ("😎", "Co"), ("🤖", "Rb"),
          ("🌮", "Ta"), ("🍩", "Do"), ("⚡", "Zp"), ("🌙", "Mn"), ("👻", "Gh"), ("🐸", "Fr"),
          ("🍉", "Wm"), ("⭐", "St")]
FALLBACK = dict(PIECES)
FALLBACK.update({"🧐": "SG", "😰": "NN", "👴": "DU", "🧱": "Bk", "🔄": "Sw", "✌": "x2",
                 "⚔": "VS", "🌋": "EQ", "🏆": "Cup", "🎨": "Art"})
PIECE_EMOJIS = [e for e, _ in PIECES]

DEFAULT_DARES = [
    "Do your best villain laugh.",
    "Do 10 squats right now.",
    "Narrate the next round like a cricket commentator.",
    "Compliment the winner dramatically for 30 seconds.",
    "Speak in an accent until the next game ends.",
    "Play the next round with your non-dominant hand.",
    "Sing the first song that comes to your mind.",
    "Do your best slow-motion replay of your losing move.",
    "Let the winner pick your nickname for the rest of the game.",
    'Bow to the winner and say "You are the GOAT".',
]

AI_PERSONAS = {
    "smug": dict(
        name="Smug Genius", emoji="🧐", best=1.0,
        desc="Unbeatable minimax. Will not let you forget it.",
        lines=[
            "I calculated that 3 moves ago.",
            "Cute move. Statistically irrelevant, but cute.",
            "I've already seen how this ends. Spoiler: you lose.",
            "Take your time. Losing shouldn't be rushed.",
            "My circuits are barely warm.",
            "That box you're eyeing? Trap. You're welcome.",
            "I'd explain my strategy, but you'd need a whiteboard.",
            "Another flawless move. I'm almost bored.",
            "Fun fact: a draw is the best you'll ever get from me.",
            "Did you plan that move, or did it just happen?",
        ]),
    "newbie": dict(
        name="Nervous Newbie", emoji="😰", best=0.4,
        desc="Random moves 60% of the time. Panics 100% of the time.",
        lines=[
            "Is this the right box?? Please don't win.",
            "Oh no oh no I clicked it. Is that allowed?",
            "I read a tutorial once. It didn't help.",
            "My hands are sweating. Do robots sweat?",
            "Okay okay okay, that was on purpose. Probably.",
            "Please be gentle, it's my first day.",
            "Wait, which one am I again?",
            "I think I'm winning? No? Cool cool cool.",
            "Sorry! Sorry. Was that rude? Sorry.",
        ]),
    "uncle": dict(
        name="Desi Uncle", emoji="👴", best=0.7,
        desc="Best move 70% of the time. Life advice 100% free.",
        lines=[
            "Beta, focus on the corners, same as engineering seat.",
            "Arre, centre lo beta. Centre is like government job. Stable.",
            "In my time we played this on the back of ration card.",
            "Sharma ji ka beta never loses tic-tac-toe, just saying.",
            "Itna time kyun laga? Life mein bhi itna sochoge?",
            "Beta, first make good moves, then think about marriage.",
            "Corner pakdo, settle ho jao. Simple funda.",
            "Ye game bhi investment hai beta, FD jaisa socho.",
            "Thodi chai pi lo, dimaag fresh ho jayega.",
            "Phone side mein rakho beta, focus karo.",
        ]),
}

POWERS = [("block", "🧱", "Block"), ("swap", "🔄", "Swap"), ("double", "✌", "Double")]

THEMES = {
    "Midway": dict(bg=NIGHT, panel=(24, 38, 112), board=(17, 28, 88),
                   grid=BULB, grid2=BULB, text=(255, 255, 255), sub=(176, 190, 240),
                   accent=SKY, accent2=RED, hover=(38, 56, 142),
                   line=(58, 78, 170), shadow=(0, 0, 0, 110),
                   font=TEXT_FONT, display=DISPLAY_FONT, style="midway"),
    "Classic": dict(bg=(244, 244, 240), panel=(255, 255, 255), board=(255, 255, 255),
                    grid=(38, 40, 52), grid2=(38, 40, 52), text=(28, 30, 40), sub=(105, 108, 120),
                    accent=(66, 133, 244), accent2=(234, 67, 53), hover=(230, 236, 248),
                    line=(218, 220, 228), shadow=(0, 0, 0, 40),
                    font="arial,helvetica,dejavusans", style="plain"),
    "Neon": dict(bg=(6, 6, 14), panel=(18, 18, 34), board=(10, 10, 22),
                 grid=(0, 240, 255), grid2=(255, 45, 200), text=(232, 240, 255), sub=(150, 160, 205),
                 accent=(0, 220, 255), accent2=(255, 45, 200), hover=(28, 28, 62),
                 line=(60, 60, 110), shadow=(0, 0, 0, 90),
                 font="consolas,couriernew,dejavusansmono", style="neon"),
    "Pastel": dict(bg=(255, 230, 238), panel=(240, 232, 255), board=(255, 246, 250),
                   grid=(186, 160, 220), grid2=(150, 215, 190), text=(92, 70, 112), sub=(146, 124, 166),
                   accent=(124, 196, 166), accent2=(244, 143, 177), hover=(228, 244, 236),
                   line=(222, 206, 236), shadow=(120, 80, 140, 40),
                   font="comicsansms,chalkboardse,trebuchetms,arial", style="soft"),
    "Chalkboard": dict(bg=(32, 70, 50), panel=(42, 86, 62), board=(36, 78, 56),
                       grid=(236, 240, 228), grid2=(236, 240, 228), text=(246, 246, 236), sub=(190, 212, 192),
                       accent=(255, 226, 120), accent2=(255, 150, 150), hover=(54, 102, 76),
                       line=(84, 128, 100), shadow=(0, 0, 0, 70),
                       font="segoeprint,chalkduster,comicsansms,arial", style="chalk"),
}

CONFETTI_COLORS = [(255, 71, 87), (255, 165, 2), (46, 213, 115), (30, 144, 255),
                   (255, 107, 129), (236, 204, 104), (162, 155, 254), (0, 210, 211)]
WHEEL_COLORS = [(255, 99, 132), (255, 159, 64), (255, 205, 86), (75, 192, 192), (54, 162, 235),
                (153, 102, 255), (46, 213, 115), (255, 120, 200), (0, 200, 220), (240, 110, 70)]

EMOJI_FONT_PATHS = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/google-noto-emoji/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
    "C:/Windows/Fonts/seguisym.ttf",
]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def lighten(c, t):
    return mix(c, (255, 255, 255), t)


def darken(c, t):
    return mix(c, (0, 0, 0), t)


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def on_color(c):
    return (25, 25, 35) if lum(c) > 150 else (250, 250, 255)


def ease_out_back(p):
    c1 = 1.70158
    return 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2


def ease_io(p):
    return p * p * (3 - 2 * p)


def cubic_bezier(x1, y1, x2, y2, x):
    """Same curve as CSS cubic-bezier(x1, y1, x2, y2), evaluated at progress x (0..1)."""
    x = clamp(x, 0.0, 1.0)
    lo, hi = 0.0, 1.0
    for _ in range(30):
        t = (lo + hi) / 2
        bx = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3
        if bx < x:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3


def ease_in(p):
    return cubic_bezier(0.42, 0, 1, 1, p)


_sticker_cache = {}


def sticker(name, px):
    """Render one of the SVG stickers at px x px (cached)."""
    px = max(8, int(px))
    key = (name, px)
    if key not in _sticker_cache:
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="%d" height="%d">%s</svg>'
               % (px, px, STICKERS[name])).encode()
        try:
            img = pygame.image.load(io.BytesIO(svg), "sticker.svg").convert_alpha()
        except Exception:  # very old pygame without SVG support: plain bulb dot
            img = pygame.Surface((px, px), pygame.SRCALPHA)
            pygame.draw.circle(img, BULB, (px // 2, px // 2), px // 2)
        _sticker_cache[key] = img
    return _sticker_cache[key]


def lines_for(board, p):
    return [ln for ln in LINES if all(board[i] == p for i in ln)]


@lru_cache(maxsize=None)
def negamax(b, p):
    """Score of position b for player p (who is about to move)."""
    if lines_for(b, 1 - p):
        return -(1 + b.count(None))      # lose, but prefer losing later
    if None not in b:
        return 0
    best = -99
    for i in range(9):
        if b[i] is None:
            best = max(best, -negamax(b[:i] + (p,) + b[i + 1:], 1 - p))
    return best


def best_moves(board, p, legal):
    b = tuple(board)
    best, out = None, []
    for i in legal:
        v = -negamax(b[:i] + (p,) + b[i + 1:], 1 - p)
        if best is None or v > best:
            best, out = v, [i]
        elif v == best:
            out.append(i)
    return out


def load_save():
    settings = dict(p1_name="Player 1", p2_name="Player 2", p1_emoji="❌", p2_emoji="⭕",
                    theme="Midway", sound=True, powerups=False, custom_dares=[],
                    tourney_names=["", "", "", ""], midway_v1=False)
    stats = dict(games=0, draws=0, dares=0, quakes=0, champions=0)
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.get("settings", {}).items():
            if k in settings and type(v) == type(settings[k]):
                settings[k] = v
        for k, v in data.get("stats", {}).items():
            if k in stats and isinstance(v, int):
                stats[k] = v
    except Exception:
        pass
    if not settings["midway_v1"]:  # one-time switch to the new Midway look for older save files
        settings["theme"] = "Midway"
        settings["midway_v1"] = True
    if settings["theme"] not in THEMES:
        settings["theme"] = "Midway"
    if settings["p1_emoji"] not in PIECE_EMOJIS:
        settings["p1_emoji"] = "❌"
    if settings["p2_emoji"] not in PIECE_EMOJIS or settings["p2_emoji"] == settings["p1_emoji"]:
        settings["p2_emoji"] = "⭕" if settings["p1_emoji"] != "⭕" else "❌"
    settings["custom_dares"] = [str(d) for d in settings["custom_dares"]][:30]
    names = [str(n) for n in settings["tourney_names"]][:8]
    settings["tourney_names"] = names + [""] * (2 - len(names)) if len(names) < 2 else names
    return settings, stats


# ---------------------------------------------------------------------------
# Sound (all generated with math, no audio files)
# ---------------------------------------------------------------------------
class Sounds:
    def __init__(self, app):
        self.app = app
        self.bank = {}
        self.ok = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1, 512)
            info = pygame.mixer.get_init()
            if not info:
                return
            self.rate, size, self.ch = info
            if abs(size) != 16:
                return
            self.build()
            self.ok = True
        except Exception:
            self.ok = False

    def _make(self, samples):
        arr = array.array("h")
        for s in samples:
            v = int(clamp(s, -1.0, 1.0) * 32767 * 0.7)
            for _ in range(self.ch):
                arr.append(v)
        return pygame.mixer.Sound(buffer=arr.tobytes())

    def build(self):
        r = self.rate
        two_pi = 2 * math.pi

        def tone(f0, f1, dur, vol=0.5, wave="sine", decay=1.5):
            n = int(r * dur)
            out = [0.0] * n
            ph = 0.0
            for i in range(n):
                t = i / n
                ph += two_pi * (f0 + (f1 - f0) * t) / r
                if wave == "sine":
                    v = math.sin(ph)
                elif wave == "square":
                    v = 1.0 if math.sin(ph) >= 0 else -1.0
                elif wave == "tri":
                    v = 2 * abs(2 * ((ph / two_pi) % 1) - 1) - 1
                else:
                    v = 2 * ((ph / two_pi) % 1) - 1
                attack = min(1.0, i / (r * 0.004))
                out[i] = v * vol * attack * (1 - t) ** decay
            return out

        def seq(parts):
            n = max(int(st * r) + len(sm) for st, sm in parts)
            buf = [0.0] * n
            for st, sm in parts:
                o = int(st * r)
                for j, v in enumerate(sm):
                    buf[o + j] += v
            return buf

        self.bank["place"] = self._make(tone(520, 900, 0.09, 0.45, "tri"))
        self.bank["click"] = self._make(tone(880, 660, 0.035, 0.22, "square", 2))
        self.bank["tick"] = self._make(tone(2400, 1900, 0.014, 0.28, "square", 1))
        notes = [523, 659, 784, 1047]
        parts = [(i * 0.11, tone(f, f, 0.18 if i < 3 else 0.55, 0.36, "tri", 1.2)) for i, f in enumerate(notes)]
        parts += [(0.33, tone(1319, 1319, 0.5, 0.16, "sine", 1.4)), (0.33, tone(784, 784, 0.5, 0.14, "sine", 1.4))]
        self.bank["victory"] = self._make(seq(parts))
        self.bank["draw"] = self._make(seq([(0, tone(440, 415, 0.16, 0.35, "tri")),
                                            (0.17, tone(349, 330, 0.3, 0.35, "tri"))]))
        self.bank["error"] = self._make(tone(170, 130, 0.18, 0.28, "square", 1))
        self.bank["power"] = self._make(seq([(0, tone(300, 1300, 0.28, 0.3, "saw", 1)),
                                             (0.05, tone(600, 1800, 0.25, 0.15, "sine", 1))]))
        self.bank["whoosh"] = self._make(tone(900, 180, 0.4, 0.35, "sine", 0.8))
        self.bank["coin"] = self._make(seq([(0, tone(988, 988, 0.08, 0.25, "square", 0.3)),
                                            (0.08, tone(1319, 1319, 0.4, 0.25, "square", 1.3))]))
        self.bank["chime"] = self._make(seq([(0, tone(1047, 1047, 0.6, 0.3, "sine", 1.6)),
                                             (0.08, tone(1568, 1568, 0.6, 0.22, "sine", 1.6)),
                                             (0.16, tone(2093, 2093, 0.5, 0.15, "sine", 1.8))]))
        n = int(r * 1.0)
        out = [0.0] * n
        y = 0.0
        ph = 0.0
        for i in range(n):
            y += (random.uniform(-1, 1) - y) * 0.06
            ph += two_pi * 42 / r
            t = i / n
            out[i] = (y * 2.4 + 0.45 * math.sin(ph)) * min(1, t * 8) * (1 - t) ** 0.8 * 0.85
        self.bank["rumble"] = self._make(out)

    def play(self, name):
        if self.ok and self.app.settings["sound"] and name in self.bank:
            try:
                self.bank[name].play()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Text / emoji rendering with caching and graceful fallback
# ---------------------------------------------------------------------------
class Gfx:
    def __init__(self):
        self.fonts, self.texts, self.efonts, self.emojis = {}, {}, {}, {}
        self.epaths = [p for p in EMOJI_FONT_PATHS if os.path.exists(p)]
        try:
            m = pygame.font.match_font("segoeuiemoji,applecoloremoji,notocoloremoji,notoemoji,symbola,segoeuisymbol")
            if m and m not in self.epaths:
                self.epaths.append(m)
        except Exception:
            pass

    def font(self, size, bold=False, family="arial"):
        key = (size, bold, family)
        f = self.fonts.get(key)
        if f is None:
            try:
                if os.path.isfile(family):  # bundled .ttf (Bungee / Fredoka)
                    f = pygame.font.Font(family, size)
                    f.set_bold(bold)
                else:
                    f = pygame.font.SysFont(family, size, bold=bold)
            except Exception:
                f = pygame.font.Font(None, size)
            self.fonts[key] = f
        return f

    def _efont(self, path, size):
        key = (path, size)
        if key not in self.efonts:
            res = None
            for s in (size, 109, 64, 32):
                try:
                    res = pygame.font.Font(path, s)
                    break
                except Exception:
                    continue
            self.efonts[key] = res
        return self.efonts[key]

    def emoji(self, ch, size, color=(40, 40, 40)):
        ch = ch.replace("\ufe0f", "").replace("\u200d", "")
        size = max(8, int(size))
        key = (ch, size, tuple(color))
        if key in self.emojis:
            return self.emojis[key]
        surf = None
        for path in self.epaths:
            f = self._efont(path, max(12, min(size, 160)))
            if not f:
                continue
            try:
                if ord(ch[0]) <= 0xFFFF:  # metrics() can't report glyphs above U+FFFF
                    m = f.metrics(ch)
                    if not m or any(x is None for x in m):
                        continue
                s = f.render(ch, True, color)
                if s.get_width() < 3:
                    continue
                surf = s
                break
            except Exception:
                continue
        if surf is not None:
            w, h = surf.get_size()
            k = size / max(w, h)
            nw, nh = max(1, int(w * k)), max(1, int(h * k))
            try:
                surf = pygame.transform.smoothscale(surf.convert_alpha(), (nw, nh))
            except Exception:
                surf = pygame.transform.scale(surf, (nw, nh))
        else:  # no emoji font on this computer: draw a coloured badge instead
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2)
            pygame.draw.circle(surf, lighten(color, 0.4), (size // 2, size // 2), size // 2, max(2, size // 14))
            lab = FALLBACK.get(ch, ch[:1] if ch.isascii() else "?")
            txt = self.font(max(8, int(size * 0.42)), True).render(lab, True, on_color(color))
            surf.blit(txt, txt.get_rect(center=(size // 2, size // 2)))
        if len(self.emojis) > 1500:
            self.emojis.clear()
        self.emojis[key] = surf
        return surf

    def text(self, s, size, color, bold=False, family="arial"):
        key = (s, size, tuple(color), bold, family)
        if key in self.texts:
            return self.texts[key]
        f = self.font(size, bold, family)
        parts, buf = [], ""
        for ch in s:
            if ch in "\ufe0f\u200d":
                continue
            if ord(ch) >= 0x2300:
                if buf:
                    parts.append(f.render(buf, True, color))
                    buf = ""
                parts.append(self.emoji(ch, int(size * 1.05), color))
            else:
                buf += ch
        if buf or not parts:
            parts.append(f.render(buf or " ", True, color))
        w = sum(p.get_width() for p in parts)
        h = max(p.get_height() for p in parts)
        out = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
        x = 0
        for p in parts:
            out.blit(p, (x, (h - p.get_height()) // 2))
            x += p.get_width()
        if len(self.texts) > 3000:
            self.texts.clear()
        self.texts[key] = out
        return out

    def wrap(self, text, size, maxw, bold=False, family="arial"):
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.text(trial, size, (0, 0, 0), bold, family).get_width() <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines or [""]


# ---------------------------------------------------------------------------
# Drawing helpers for the board and decorations
# ---------------------------------------------------------------------------
def board_cells(x, y, size):
    c = size / 3
    return [pygame.Rect(int(x + (i % 3) * c), int(y + (i // 3) * c), int(c), int(c)) for i in range(9)]


def draw_grid(a, surf, x, y, size):
    t = a.theme
    c = size / 3
    style = t["style"]
    m = size * 0.03
    segs = []
    for k in (1, 2):
        segs.append(((x + k * c, y + m), (x + k * c, y + size - m), "v"))
        segs.append(((x + m, y + k * c), (x + size - m, y + k * c), "h"))
    w = max(3, int(size * 0.018))
    if style in ("neon", "chalk"):
        g = pygame.Surface((int(size) + 40, int(size) + 40), pygame.SRCALPHA)
        sh = lambda p: (p[0] - x + 20, p[1] - y + 20)
        if style == "neon":
            for p1, p2, d in segs:
                col = t["grid"] if d == "v" else t["grid2"]
                for width, alpha in ((w * 5, 30), (w * 3, 65), (int(w * 1.6), 150)):
                    pygame.draw.line(g, (*col, alpha), sh(p1), sh(p2), max(1, int(width)))
                pygame.draw.line(g, (255, 255, 255, 230), sh(p1), sh(p2), max(1, w // 2))
        else:
            rng = random.Random(7)
            for p1, p2, d in segs:
                for _ in range(4):
                    j = lambda: rng.uniform(-2.5, 2.5)
                    q1 = (sh(p1)[0] + j(), sh(p1)[1] + j())
                    q2 = (sh(p2)[0] + j(), sh(p2)[1] + j())
                    pygame.draw.line(g, (*t["grid"], rng.randint(110, 190)), q1, q2, max(2, w // 2))
                for _ in range(14):
                    k = rng.random()
                    px = sh(p1)[0] + (sh(p2)[0] - sh(p1)[0]) * k + rng.uniform(-5, 5)
                    py = sh(p1)[1] + (sh(p2)[1] - sh(p1)[1]) * k + rng.uniform(-5, 5)
                    pygame.draw.circle(g, (*t["grid"], 90), (int(px), int(py)), 1)
        surf.blit(g, (x - 20, y - 20))
    else:
        if style == "soft":
            w = int(w * 1.5)
        for p1, p2, d in segs:
            col = t["grid"] if d == "v" else t["grid2"]
            pygame.draw.line(surf, col, p1, p2, w)
            pygame.draw.circle(surf, col, (int(p1[0]), int(p1[1])), w // 2)
            pygame.draw.circle(surf, col, (int(p2[0]), int(p2[1])), w // 2)
        if style == "midway":  # marquee bulbs twinkling along the grid lines
            for n, (p1, p2, d) in enumerate(segs):
                for k in range(9):
                    f = (k + 0.5) / 9
                    on = (k + n + int(a.now * 3)) % 2 == 0
                    pygame.draw.circle(surf, (255, 244, 190) if on else (232, 168, 0),
                                       (int(p1[0] + (p2[0] - p1[0]) * f), int(p1[1] + (p2[1] - p1[1]) * f)),
                                       max(2, int(w * 0.75)))


def draw_bricks(surf, rect):
    pygame.draw.rect(surf, (168, 72, 50), rect, border_radius=6)
    rows = 3
    rh = rect.h / rows
    for r in range(rows):
        yy = rect.y + r * rh
        if r:
            pygame.draw.line(surf, (236, 214, 190), (rect.x, yy), (rect.right - 1, yy), 3)
        off = 0 if r % 2 == 0 else rect.w / 4
        for k in range(3):
            xx = rect.x + off + k * rect.w / 2
            if rect.x < xx < rect.right - 2:
                pygame.draw.line(surf, (236, 214, 190), (xx, yy), (xx, yy + rh), 3)
    pygame.draw.rect(surf, (110, 44, 30), rect, 3, border_radius=6)


def draw_piece(a, surf, emoji, pl, center, size, scale=1.0, alpha=255):
    img = a.gfx.emoji(emoji, int(size), a.pcol(pl))
    if abs(scale - 1.0) > 0.01:
        w, h = img.get_size()
        ns = (max(1, int(w * scale)), max(1, int(h * scale)))
        try:
            img = pygame.transform.smoothscale(img, ns)
        except Exception:
            img = pygame.transform.scale(img, ns)
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surf.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))


def draw_win_lines(a, surf, cells, lines, t0):
    area = cells[0].union(cells[8])
    c = cells[0].w
    area = area.inflate(c, c)
    g = pygame.Surface(area.size, pygame.SRCALPHA)
    p = ease_io(clamp((a.now - t0) / 0.45, 0, 1))
    pulse = 0.5 + 0.5 * math.sin(a.now * 7)
    for ln in lines:
        sx, sy = cells[ln[0]].center
        ex, ey = cells[ln[2]].center
        dx, dy = ex - sx, ey - sy
        d = math.hypot(dx, dy) or 1
        sx, sy = sx - dx / d * c * 0.35, sy - dy / d * c * 0.35
        ex, ey = ex + dx / d * c * 0.35, ey + dy / d * c * 0.35
        ex, ey = sx + (ex - sx) * p, sy + (ey - sy) * p
        s = (sx - area.x, sy - area.y)
        e = (ex - area.x, ey - area.y)
        for width, alpha in ((c * 0.24, int(45 + 40 * pulse)), (c * 0.14, 120), (c * 0.065, 255)):
            pygame.draw.line(g, (255, 210, 30, alpha), s, e, max(2, int(width)))
            pygame.draw.circle(g, (255, 210, 30, alpha), (int(e[0]), int(e[1])), max(1, int(width / 2)))
            pygame.draw.circle(g, (255, 210, 30, alpha), (int(s[0]), int(s[1])), max(1, int(width / 2)))
        pygame.draw.line(g, (255, 255, 230, 255), s, e, max(1, int(c * 0.02)))
    surf.blit(g, area.topleft)


def draw_board(a, surf, x, y, size, board, emojis, **o):
    t = a.theme
    ox, oy = o.get("offset", (0, 0))
    x, y = x + ox, y + oy
    cells = board_cells(x, y, size)
    c = size / 3
    pad = int(size * 0.04)
    pygame.draw.rect(surf, t["board"], (x - pad, y - pad, size + 2 * pad, size + 2 * pad),
                     border_radius=int(size * 0.06))
    hover = o.get("hover")
    for i, r in enumerate(cells):
        inner = r.inflate(-int(c * 0.14), -int(c * 0.14))
        if i == hover:
            pygame.draw.rect(surf, o.get("hover_color") or t["hover"], inner, border_radius=int(c * 0.15))
        if i in o.get("highlight", ()):
            pulse = 0.5 + 0.5 * math.sin(a.now * 6)
            pygame.draw.rect(surf, o.get("hl_color") or t["accent"], inner.inflate(int(8 * pulse), int(8 * pulse)),
                             width=max(3, int(c * 0.04)), border_radius=int(c * 0.15))
    draw_grid(a, surf, x, y, size)
    b = o.get("blocked")
    if b is not None and board[b] is None:
        draw_bricks(surf, cells[b].inflate(-int(c * 0.34), -int(c * 0.34)))
    pop = o.get("pop") or {}
    hidden = o.get("hidden", ())
    wl = o.get("win_lines") or []
    wcells = {i for ln in wl for i in ln}
    for i in range(9):
        v = board[i]
        if v is None or i in hidden:
            continue
        sc = 1.0
        if i in pop:
            sc = max(0.02, ease_out_back(clamp((a.now - pop[i]) / 0.28, 0, 1)))
        if i in wcells:
            sc *= 1 + 0.08 * math.sin(a.now * 8 + i)
        draw_piece(a, surf, emojis[v], v, cells[i].center, c * 0.62, sc)
    g = o.get("ghost")
    if g is not None:
        draw_piece(a, surf, emojis[g[1]], g[1], cells[g[0]].center, c * 0.62, 0.9, alpha=80)
    if wl:
        draw_win_lines(a, surf, cells, wl, o.get("win_t", 0))
    return cells


def draw_crown(surf, cx, by, w):
    if w < 4:
        return
    h = w * 0.7
    x0 = cx - w / 2
    pts = [(x0, by), (x0, by - h * 0.6), (x0 + w * 0.25, by - h * 0.3), (cx, by - h),
           (x0 + w * 0.75, by - h * 0.3), (x0 + w, by - h * 0.6), (x0 + w, by)]
    pygame.draw.polygon(surf, (255, 200, 40), pts)
    pygame.draw.polygon(surf, (175, 115, 10), pts, 2)
    for px, py in (pts[1], pts[3], pts[5]):
        pygame.draw.circle(surf, (255, 235, 120), (int(px), int(py)), max(2, int(w * 0.07)))
    for jx, col in ((x0 + w * 0.22, (230, 50, 80)), (cx, (60, 140, 255)), (x0 + w * 0.78, (40, 190, 110))):
        pygame.draw.circle(surf, col, (int(jx), int(by - h * 0.14)), max(2, int(w * 0.07)))


def draw_trophy(surf, cx, cy, h):
    gold, dark, light = (255, 200, 40), (185, 125, 15), (255, 236, 140)
    w = h * 0.72
    top = cy - h * 0.45
    body = [(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.28, cy), (cx - w * 0.28, cy)]
    lw = max(4, int(h * 0.05))
    pygame.draw.arc(surf, dark, (cx - w / 2 - w * 0.2, top + h * 0.03, w * 0.42, h * 0.32), math.pi / 2, 3 * math.pi / 2, lw)
    pygame.draw.arc(surf, dark, (cx + w / 2 - w * 0.22, top + h * 0.03, w * 0.42, h * 0.32), -math.pi / 2, math.pi / 2, lw)
    pygame.draw.polygon(surf, gold, body)
    pygame.draw.ellipse(surf, gold, (cx - w * 0.28, cy - h * 0.06, w * 0.56, h * 0.12))
    pygame.draw.ellipse(surf, dark, (cx - w / 2, top - h * 0.06, w, h * 0.12))
    pygame.draw.ellipse(surf, light, (cx - w / 2 + 4, top - h * 0.06 + 3, w - 8, h * 0.12 - 6), 2)
    pygame.draw.rect(surf, gold, (cx - w * 0.07, cy, w * 0.14, h * 0.2))
    pygame.draw.rect(surf, gold, (cx - w * 0.3, cy + h * 0.18, w * 0.6, h * 0.1), border_radius=6)
    pygame.draw.rect(surf, dark, (cx - w * 0.38, cy + h * 0.27, w * 0.76, h * 0.12), border_radius=6)
    pygame.draw.line(surf, light, (cx - w * 0.3, top + h * 0.08), (cx - w * 0.18, cy - h * 0.08), max(3, int(h * 0.03)))
    star = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = h * 0.11 if k % 2 == 0 else h * 0.045
        star.append((cx + rr * math.cos(ang), top + h * 0.2 + rr * math.sin(ang)))
    pygame.draw.polygon(surf, (255, 250, 220), star)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
class Screen:
    def __init__(self, app):
        self.app = app

    def on_enter(self):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass

    def on_key(self, key):
        pass


# (tag, name, hint, mode, colour, [(sticker, x%, y%, tilt deg, scale)]) - layout from the Midway design:
# two wide tiles on top, three below; tilted carnival stickers on each tile.
TILES = [("1P", "Vs AI", "Pick an opponent with a personality.", "ai", RED,
          [("stick", .54, .20, 14, 1.25), ("pretzel", .76, .58, -18, 1.1), ("ball", .36, .66, -10, .9)]),
         ("2P", "Classic Duel", "2 players on one device.", "classic", BLUE,
          [("pad", .58, .22, -12, 1.25), ("balloon", .80, .56, 16, 1.1), ("corn", .38, .64, 8, 1)]),
         ("5X", "Earthquake Mode", "The board shakes and cells swap every 5 moves.", "quake", SKY,
          [("wheel", .08, .62, -8, 1.1), ("floss", .42, .58, 14, 1), ("ticket", .72, .68, -16, .9)]),
         ("8P", "Party Tournament", "Bracket for up to 8 friends.", "tourney", RED,
          [("cup", .08, .64, 12, 1.1), ("pin", .40, .56, -14, 1.15), ("corn", .72, .66, 10, 1)]),
         ("DIY", "Customize", "Choose your pieces and board theme.", "custom", SKY,
          [("dice", .08, .60, -10, 1.15), ("ball", .42, .66, 12, .95), ("balloon", .72, .56, -14, 1.05)])]


def spaced_text(a, text, size, color, family, spacing=0.08):
    """Text with letter-spacing (like CSS letter-spacing: .08em)."""
    imgs = [a.gfx.text(ch, size, color, False, family) for ch in text]
    gap = int(size * spacing)
    w = sum(i.get_width() for i in imgs) + gap * max(0, len(imgs) - 1)
    h = max(i.get_height() for i in imgs)
    out = pygame.Surface((max(1, w), h), pygame.SRCALPHA)
    x = 0
    for i in imgs:
        out.blit(i, (x, 0))
        x += i.get_width() + gap
    return out


class HomeScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.hov = [0.0] * len(TILES)

    def open(self, key):
        a = self.app
        if key in ("classic", "quake"):
            a.start_game(key)
        elif key == "ai":
            a.go(AISelectScreen(a))
        elif key == "tourney":
            if a.tourney and not a.tourney.champion():
                a.go(BracketScreen(a))
            else:
                a.go(TourneySetupScreen(a))
        else:
            a.go(CustomizeScreen(a))

    def tile_rects(self, top):
        a = self.app
        W, H, s = a.W, a.H, a.s
        pad = gap = int(16 * s)
        if W >= 820:  # 6-column grid: two wide tiles on top, three below
            u = (W - 2 * pad - 5 * gap) / 6
            rh = (H - top - pad - gap) / 2
            spans = [(0, 0, 3), (0, 3, 3), (1, 0, 2), (1, 2, 2), (1, 4, 2)]
            return [pygame.Rect(int(pad + c * (u + gap)), int(top + r * (rh + gap)),
                                int(n * u + (n - 1) * gap), int(rh)) for r, c, n in spans]
        u = (W - 2 * pad - gap) / 2  # narrow: one wide tile, then pairs
        rh = (H - top - pad - 2 * gap) / 3
        spans = [(0, 0, 2), (1, 0, 1), (1, 1, 1), (2, 0, 1), (2, 1, 1)]
        return [pygame.Rect(int(pad + c * (u + gap)), int(top + r * (rh + gap)),
                            int(n * u + (n - 1) * gap), int(rh)) for r, c, n in spans]

    def update(self, dt):
        for i in range(len(self.hov)):
            target = 1.0 if getattr(self, "_hover", None) == i else 0.0
            self.hov[i] += (target - self.hov[i]) * min(1, dt * 14)

    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        dfont = t.get("display", t["font"])
        top = int(70 * s)
        # marquee title row
        title = spaced_text(a, "Tic Tac Chaos", a.fs(34), BULB, dfont, 0.04)
        surf.blit(title, title.get_rect(midleft=(int(16 * s), top // 2 + int(2 * s))))
        st = a.stats
        a.label(f"Games {st['games']}  ·  Dares {st['dares']}  ·  Quakes {st['quakes']}  ·  Champions {st['champions']}",
                a.fs(14), t["sub"], (W - int(80 * s), top // 2), anchor="midright",
                maxw=max(60, W - title.get_width() - int(130 * s)))
        pill = spaced_text(a, "Replay intro", a.fs(12), BULB, dfont, 0.0)
        pr = pill.get_rect().inflate(int(28 * s), int(16 * s))
        pr.bottomleft = (int(16 * s), H - int(16 * s))
        if a.hit(pr):  # checked before the tiles because the pill sits on top of one
            a.go(IntroScreen(a))
            return
        self._hover = None
        vw = W / 100
        for i, ((tag, name, hint, key, col, stickers), rect) in enumerate(zip(TILES, self.tile_rects(top))):
            if a.interactive and rect.collidepoint(a.mouse):
                self._hover = i
            h = self.hov[i]
            r = rect.move(0, -int(4 * s * h))
            fg = NIGHT if col == SKY else (255, 255, 255)
            pygame.draw.rect(surf, col, r, border_radius=int(24 * s))
            pad = int(clamp(2.4 * vw, 18, 30))
            y = r.y + pad
            tg = spaced_text(a, tag, 14, mix(fg, col, 0.2), dfont)
            surf.blit(tg, (r.x + pad, y))
            y += tg.get_height() + int(6 * s)
            nsz = int(clamp(3.4 * vw, 26, 44))
            for ln in a.gfx.wrap(name, nsz, r.w - 2 * pad, False, dfont):
                img = a.gfx.text(ln, nsz, fg, False, dfont)
                surf.blit(img, (r.x + pad, y))
                y += int(nsz * 1.05)
            y += int(8 * s)
            for ln in a.gfx.wrap(hint, 17, r.w - 2 * pad, True, t["font"])[:2]:
                img = a.gfx.text(ln, 17, fg, True, t["font"])
                surf.blit(img, (r.x + pad, y))
                y += int(17 * 1.3)
            # tilted stickers, clipped to the tile like overflow: hidden
            surf.set_clip(r)
            base = clamp(6.4 * vw, 48, 88)
            for name_, xp, yp, rot, sc in stickers:
                size = base * sc
                img = sticker(name_, size * 1.1)  # render a bit larger so the hover zoom stays crisp
                k = (1 + 0.1 * h) / 1.1
                img = pygame.transform.rotozoom(img, -(rot + 10 * h), k)
                cx, cy = r.x + r.w * xp + size / 2, r.y + r.h * yp + size / 2
                shadow = pygame.mask.from_surface(img).to_surface(setcolor=(10, 18, 64, 72), unsetcolor=(0, 0, 0, 0))
                surf.blit(shadow, shadow.get_rect(center=(cx, cy + 3)))
                surf.blit(img, img.get_rect(center=(cx, cy)))
            surf.set_clip(None)
            if a.hit(rect):
                self.open(key)
                return
        # "Replay intro" pill (bottom-left, like the design) - drawn on top of the tiles
        ps = pygame.Surface(pr.size, pygame.SRCALPHA)
        pygame.draw.rect(ps, (10, 18, 64, 217), ps.get_rect(), border_radius=pr.h // 2)
        surf.blit(ps, pr.topleft)
        surf.blit(pill, pill.get_rect(center=pr.center))


class IntroScreen(Screen):
    """Insert coin -> Credit 01 -> sign fades -> striped curtains open onto the home screen (3.7 s)."""

    def __init__(self, app):
        super().__init__(app)
        self.home = HomeScreen(app)
        self.t0 = app.now
        self.coin_played = self.whoosh_played = False
        self.curtain_key = None
        self.curtains = None

    def done(self):
        self.app.go(self.home)

    def on_key(self, key):
        self.done()

    def update(self, dt):
        t = self.app.now - self.t0
        if t >= 1.15 and not self.coin_played:
            self.coin_played = True
            self.app.sfx.play("coin")
        if t >= 2.5 and not self.whoosh_played:
            self.whoosh_played = True
            self.app.sfx.play("whoosh")
        if t >= 3.7:
            self.done()

    def build_curtains(self, W, H):
        if self.curtain_key == (W, H):
            return self.curtains
        pat = pygame.Surface((120, H))
        for x in range(120):  # 60px red / 60px canvas stripes with soft fold shading
            base = CURTAIN_RED if x < 60 else CANVAS
            f = (x % 60) / 60
            shade = 0.22 * (1 - f / 0.4) if f < 0.4 else 0.12 * (f - 0.4) / 0.6
            pygame.draw.line(pat, darken(base, shade), (x, 0), (x, H - 1))
        full = pygame.Surface((W, H))
        x = W // 2 - 120 * (W // 240 + 2)
        while x < W:
            full.blit(pat, (x, 0))
            x += 120
        half = W // 2
        self.curtains = (full.subsurface((0, 0, half, H)).copy(), full.subsurface((half, 0, W - half, H)).copy())
        self.curtain_key = (W, H)
        return self.curtains

    def coin_state(self, t):
        """CSS coin-drop keyframes (.9s ease-in, .35s delay, fill both): returns (y, scaleX, opacity)."""
        p = clamp((t - 0.35) / 0.9, 0, 1)
        keys = [(0.0, -60, 1.0), (0.35, -10, 0.15), (0.60, 26, 1.0), (1.0, 84, 0.2)]
        for (p0, y0, s0), (p1, y1, s1) in zip(keys, keys[1:]):
            if p <= p1:
                e = ease_in((p - p0) / (p1 - p0))
                y, sx = y0 + (y1 - y0) * e, s0 + (s1 - s0) * e
                break
        op = ease_in(p / 0.15) if p < 0.15 else 1.0
        return y, sx, op

    def draw_slot(self, t):
        slot = pygame.Surface((120, 110), pygame.SRCALPHA)
        y, sx, op = self.coin_state(t)
        coin = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(coin, (184, 125, 0), (25, 25), 25)
        pygame.draw.circle(coin, BULB, (25, 25), 22)
        pygame.draw.circle(coin, (233, 164, 0), (25, 25), 19)
        pygame.draw.circle(coin, BULB, (25, 25), 17)
        coin = pygame.transform.smoothscale(coin, (max(1, int(50 * sx)), 50))
        coin.set_alpha(int(255 * op))
        slot.blit(coin, coin.get_rect(center=(60, 22 + y)))
        pygame.draw.rect(slot, CURTAIN_RED, (0, 76, 120, 34), border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.rect(slot, (0, 0, 0), (25, 88, 70, 8))
        return slot

    def draw(self, surf):
        a = self.app
        W, H = a.W, a.H
        t = a.now - self.t0
        if a.clicked:  # click anywhere to skip
            a.clicked = None
            self.done()
            return
        a.interactive = False
        self.home.draw(surf)  # the home screen waits behind the curtains
        a.interactive = True
        # curtains: cubic-bezier(.7, 0, .25, 1), 1.1s, starting at 2.5s
        left, right = self.build_curtains(W, H)
        p = cubic_bezier(0.7, 0, 0.25, 1, (t - 2.5) / 1.1)
        surf.blit(left, (int(-1.01 * left.get_width() * p), 0))
        surf.blit(right, (W // 2 + int(1.01 * right.get_width() * p), 0))
        # the sign
        if t >= 2.55:
            return
        dfont = DISPLAY_FONT
        tsz = int(clamp(0.044 * W, 22, 34))
        if t < 1.35:
            txt = a.gfx.text("Insert coin", tsz, BULB, False, dfont)
            ph_op = 1.0 if t < 1.3 else 1 - (t - 1.3) / 0.1
            if (t % 0.6) >= 0.3:
                ph_op *= 0.15  # blink (step-end)
        else:
            txt = a.gfx.text("Credit 01", tsz, (255, 255, 255), False, dfont)
            ph_op = clamp((t - 1.35) / 0.1, 0, 1)
        sub = spaced_text(a, "Ready player 1", 14, BULB, dfont)
        one_h = txt.get_height() + 18 + 110
        cw = max(min(280, int(W * 0.7)), txt.get_width(), sub.get_width())
        padx = 40 if W > 420 else 18
        sw, sh = cw + 2 * padx + 12, one_h + 28 + 26 + 12
        m = 30  # room for the ring and drop shadow
        sign = pygame.Surface((sw + 2 * m, sh + 2 * m), pygame.SRCALPHA)
        r = pygame.Rect(m, m, sw, sh)
        pygame.draw.rect(sign, (0, 0, 0, 102), r.inflate(16, 16).move(12, 14), border_radius=28)
        pygame.draw.rect(sign, NIGHT, r.inflate(16, 16), border_radius=28)
        pygame.draw.rect(sign, NIGHT, r, border_radius=20)
        pygame.draw.rect(sign, BULB, r, 6, border_radius=20)
        content = pygame.Surface((cw, one_h), pygame.SRCALPHA)
        content.blit(txt, txt.get_rect(midtop=(cw // 2, 0)))
        if t < 1.35:
            content.blit(self.draw_slot(t), (cw // 2 - 60, txt.get_height() + 18))
        else:
            content.blit(sub, sub.get_rect(midtop=(cw // 2, txt.get_height() + 10)))
        content.set_alpha(int(255 * clamp(ph_op, 0, 1)))
        sign.blit(content, (r.x + 6 + padx, r.y + 6 + 28))
        if t >= 2.3:  # sign-out: .25s ease-in, fade + scale to .92
            e = ease_in((t - 2.3) / 0.25)
            sign = pygame.transform.rotozoom(sign, 0, 1 - 0.08 * e)
            sign.set_alpha(int(255 * (1 - e)))
        surf.blit(sign, sign.get_rect(center=(W // 2, H // 2)))


class AISelectScreen(Screen):
    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        tb = a.top_bar("Choose your opponent")
        gap = int(20 * s)
        cw = min(int(320 * s), (W - 4 * gap) // 3)
        ch = min(int(440 * s), H - tb - int(60 * s))
        x0 = (W - (3 * cw + 2 * gap)) // 2
        y0 = tb + int(30 * s)
        for i, key in enumerate(["smug", "newbie", "uncle"]):
            P = AI_PERSONAS[key]
            rect = pygame.Rect(x0 + i * (cw + gap), y0, cw, ch)
            hover = a.interactive and rect.collidepoint(a.mouse)
            a.panel(rect, hover=hover, border=t["accent"] if hover else None)
            esz = int(min(cw * 0.36, 110 * s))
            bob = math.sin(a.now * 3 + i) * 4 * s
            img = a.gfx.emoji(P["emoji"], esz, t["accent2"])
            surf.blit(img, img.get_rect(center=(rect.centerx, rect.y + int(24 * s) + esz // 2 + bob)))
            yy = rect.y + int(36 * s) + esz
            a.label(P["name"], a.fs(24), t["text"], (rect.centerx, yy), bold=True, maxw=cw - 20)
            yy += a.fs(24)
            for ln in a.wrap(P["desc"], a.fs(15), cw - int(30 * s)):
                a.label(ln, a.fs(15), t["sub"], (rect.centerx, yy))
                yy += int(a.fs(15) * 1.3)
            yy += int(10 * s)
            quote = '"' + P["lines"][int(a.now / 3 + i) % len(P["lines"])] + '"'
            qlines = a.wrap(quote, a.fs(15), cw - int(44 * s))[:4]
            qh = len(qlines) * int(a.fs(15) * 1.3) + int(16 * s)
            qr = pygame.Rect(rect.x + int(14 * s), yy, cw - int(28 * s), qh)
            if qr.bottom < rect.bottom - int(70 * s):
                pygame.draw.rect(surf, t["hover"], qr, border_radius=int(12 * s))
                qy = qr.y + int(8 * s) + a.fs(15) // 2
                for ln in qlines:
                    a.label(ln, a.fs(15), t["text"], (qr.centerx, qy))
                    qy += int(a.fs(15) * 1.3)
            br = pygame.Rect(rect.x + int(20 * s), rect.bottom - int(64 * s), cw - int(40 * s), int(46 * s))
            if a.button(br, "Challenge") or a.hit(rect):
                a.start_game("ai", persona=key)


class GameScreen(Screen):
    TITLES = {"classic": "Classic Duel", "quake": "Earthquake Mode", "tourney": "Party Tournament"}

    def __init__(self, app, mode, persona=None, tmatch=None):
        super().__init__(app)
        st = app.settings
        self.mode, self.persona, self.tmatch = mode, persona, tmatch
        if mode == "tourney":
            names = [tmatch["p1"], tmatch["p2"]]
        else:
            names = [st["p1_name"].strip() or "Player 1", st["p2_name"].strip() or "Player 2"]
        self.players = [dict(name=names[0], emoji=st["p1_emoji"], ai=None),
                        dict(name=names[1], emoji=st["p2_emoji"], ai=None)]
        if mode == "ai":
            P = AI_PERSONAS[persona]
            self.players[1] = dict(name=P["name"], emoji=P["emoji"], ai=persona)
        self.key = "ai-" + persona if mode == "ai" else mode
        self.match_score = [0, 0]
        self.match_done = False
        self.starter = 0
        self.speech = None
        self.card_flash = None
        self.new_round(alternate=False)

    @property
    def emojis(self):
        return [p["emoji"] for p in self.players]

    # ----- game flow -------------------------------------------------------
    def new_round(self, alternate=True):
        if alternate:
            self.starter = 1 - self.starter
        self.board = [None] * 9
        self.turn = self.starter
        self.move_count = 0
        self.power_on = self.app.settings["powerups"] and self.mode in ("classic", "quake")
        self.powers = [{k: True for k, _, _ in POWERS} for _ in range(2)]
        self.pending = None
        self.double_left = 0
        self.blocked = None
        self.phase = "play"
        self.result = None
        self.pop = {}
        self.anim_t = 0.0
        self.swap_cells = None
        self.ai_timer = 0.0
        first = self.players[self.turn]
        self.actions = []
        self.record(f"Game start: {first['emoji']} {first['name']} goes first", [])
        self.maybe_ai()

    def record(self, caption, cells, win=None):
        self.actions.append(dict(board=list(self.board), caption=caption, cells=list(cells),
                                 blocked=self.blocked[0] if self.blocked else None, win=win))

    def maybe_ai(self):
        if self.phase == "play" and self.players[self.turn]["ai"]:
            self.phase = "ai_wait"
            self.ai_timer = 0.6
            self.speech = ("", self.app.now, True)

    def legal_cells(self):
        empties = [i for i in range(9) if self.board[i] is None]
        if self.blocked and self.blocked[1] == self.turn:
            others = [i for i in empties if i != self.blocked[0]]
            if others:
                return others
        return empties

    def ai_choose(self):
        legal = self.legal_cells()
        if random.random() < AI_PERSONAS[self.persona]["best"]:
            return random.choice(best_moves(self.board, self.turn, legal))
        return random.choice(legal)

    def cell_clicked(self, c):
        a = self.app
        if self.phase != "play" or self.players[self.turn]["ai"]:
            return
        p, opp = self.turn, 1 - self.turn
        me = self.players[p]
        if self.pending == "block":
            if self.board[c] is None:
                self.blocked = (c, opp)
                self.powers[p]["block"] = False
                self.pending = None
                self.power_fx(p, "block", "BLOCK")
                self.record(f"BLOCK: {me['emoji']} bricks the {CELL_NAMES[c]}", [c])
            else:
                a.sfx.play("error")
                a.toast("Pick an EMPTY cell to brick.")
            return
        if self.pending == "swap":
            if self.board[c] == opp:
                self.board[c] = p
                self.pop[c] = a.now
                self.powers[p]["swap"] = False
                self.pending = None
                self.power_fx(p, "swap", "SWAP", sound="whoosh")
                self.record(f"SWAP: {me['emoji']} steals the {CELL_NAMES[c]} from {self.players[opp]['emoji']}", [c])
                self.after_action(counted=False)
            else:
                a.sfx.play("error")
                a.toast(f"Pick one of {self.players[opp]['name']}'s marks.")
            return
        if c in self.legal_cells():
            self.place(c)
        else:
            a.sfx.play("error")
            if self.blocked and self.blocked[0] == c and self.board[c] is None:
                a.toast("That cell is bricked this turn!")

    def place(self, c):
        a = self.app
        p = self.turn
        self.board[c] = p
        self.pop[c] = a.now
        a.sfx.play("place")
        self.move_count += 1
        self.record(f"Move {self.move_count}: {self.players[p]['emoji']} takes the {CELL_NAMES[c]}", [c])
        if self.double_left > 0:
            self.double_left -= 1
        self.after_action(counted=True)

    def after_action(self, counted):
        p = self.turn
        ln = lines_for(self.board, p)
        if ln:
            self.finish(p, ln, "")
        elif None not in self.board:
            self.finish(None, [], "It's a draw")
        elif counted and self.mode == "quake" and self.move_count % 5 == 0:
            self.phase = "shake"
            self.anim_t = 0.0
            self.app.sfx.play("rumble")
            self.app.toast("EARTHQUAKE!")
        else:
            self.advance_turn()

    def advance_turn(self):
        if self.double_left > 0:
            return  # same player places their second DOUBLE mark
        if self.blocked and self.blocked[1] == self.turn:
            self.blocked = None
        self.turn = 1 - self.turn
        self.maybe_ai()

    def finish_quake(self):
        a = self.app
        c1, c2 = self.swap_cells
        self.swap_cells = None
        self.board[c1], self.board[c2] = self.board[c2], self.board[c1]
        for c in (c1, c2):
            if self.board[c] is not None:
                self.pop[c] = a.now
        a.stats["quakes"] += 1
        self.record(f"EARTHQUAKE: {CELL_NAMES[c1]} swapped with {CELL_NAMES[c2]}", [c1, c2])
        w0, w1 = lines_for(self.board, 0), lines_for(self.board, 1)
        if w0 and w1:
            self.finish(None, w0 + w1, "The earth has chosen chaos")
        elif w0:
            self.finish(0, w0, "Won by earthquake!")
        elif w1:
            self.finish(1, w1, "Won by earthquake!")
        elif None not in self.board:
            self.finish(None, [], "It's a draw")
        else:
            self.phase = "play"
            self.advance_turn()

    def finish(self, winner, lines, msg):
        a = self.app
        self.phase = "over"
        self.pending = None
        self.double_left = 0
        self.blocked = None
        self.result = dict(winner=winner, lines=lines, msg=msg, t=a.now)
        if winner is None:
            a.sfx.play("draw")
            cap = msg or "It's a draw"
            a.stats["draws"] += 1
        else:
            pl = self.players[winner]
            a.sfx.play("victory")
            a.confetti(3.0)
            cap = f"{pl['emoji']} {pl['name']} wins!" + (f" {msg}" if msg else "")
        self.record(cap, sorted({i for ln in lines for i in ln}), win=lines or None)
        a.stats["games"] += 1
        if self.mode == "tourney":
            if winner is not None:
                self.match_score[winner] += 1
                if self.match_score[winner] >= 3:
                    self.match_done = True
                    self.tmatch["winner"] = self.players[winner]["name"]
                    self.tmatch["score"] = list(self.match_score)
                    a.tourney.propagate()
        else:
            sc = a.session_scores.setdefault(self.key, [0, 0, 0])
            sc[2 if winner is None else winner] += 1
        a.save()

    def power_fx(self, p, key, word, sound="power"):
        a = self.app
        a.sfx.play(sound)
        a.toast(f"{self.players[p]['name']} used {word}!")
        self.card_flash = (p, key, a.now)

    def use_power(self, p, key):
        a = self.app
        if key == "double":
            if self.move_count == 0:
                a.sfx.play("error")
                a.toast("DOUBLE can't be used on the very first move!")
                return
            self.powers[p]["double"] = False
            self.double_left = 2
            self.pending = None
            self.power_fx(p, "double", "DOUBLE")
            self.record(f"DOUBLE: {self.players[p]['emoji']} will place two marks", [])
            return
        if self.pending == key:
            self.pending = None
            return
        if key == "swap" and (1 - p) not in self.board:
            a.sfx.play("error")
            a.toast("Nothing to swap yet!")
            return
        self.pending = key

    def update(self, dt):
        a = self.app
        if self.phase == "ai_wait":
            self.ai_timer -= dt
            if self.ai_timer <= 0:
                self.phase = "play"
                self.place(self.ai_choose())
                self.speech = (random.choice(AI_PERSONAS[self.persona]["lines"]), a.now, False)
        elif self.phase == "shake":
            self.anim_t += dt
            if self.anim_t >= 1.0:
                self.swap_cells = tuple(random.sample(range(9), 2))
                self.phase = "swap"
                self.anim_t = 0.0
                a.sfx.play("whoosh")
        elif self.phase == "swap":
            self.anim_t += dt
            if self.anim_t >= 0.75:
                self.finish_quake()

    def overlay_visible(self):
        return self.result is not None and self.app.now - self.result["t"] >= 0.9

    def on_key(self, key):
        idx = None
        if pygame.K_1 <= key <= pygame.K_9:
            idx = key - pygame.K_1
        elif pygame.K_KP1 <= key <= pygame.K_KP9:
            idx = key - pygame.K_KP1
        if idx is not None and not self.overlay_visible():
            self.cell_clicked(idx)

    # ----- drawing -----------------------------------------------------------
    def layout(self):
        a = self.app
        s, W, H = a.s, a.W, a.H
        tb = int(64 * s)
        info_h = int(92 * s)
        bottom_h = int(72 * s)
        side_min = clamp(W * 0.2, 150 * s, 300 * s)
        bs = int(min(H - tb - info_h - bottom_h - 20 * s, W - 2 * side_min - 60 * s, 600 * s))
        pw = int(min(280 * s, (W - bs) / 2 - 24 * s))
        bx = (W - bs) // 2
        by = tb + info_h
        return tb, bx, by, bs, pw

    def status_text(self):
        pl = self.players[self.turn]
        if self.phase in ("shake", "swap"):
            return "EARTHQUAKE!!!"
        if self.phase == "over":
            res = self.result
            if res["winner"] is None:
                return res["msg"] or "It's a draw"
            w = self.players[res["winner"]]
            return f"{w['emoji']} {w['name']} wins!"
        if self.phase == "ai_wait":
            return f"{pl['emoji']} {pl['name']} is thinking" + "." * (int(self.app.now * 3) % 4)
        txt = f"{pl['emoji']} {pl['name']}'s turn"
        if self.pending == "block":
            txt += "  -  tap an empty cell to BRICK it"
        elif self.pending == "swap":
            txt += "  -  tap an enemy mark to SWAP it"
        elif self.double_left:
            txt += f"  -  DOUBLE: {self.double_left} mark{'s' if self.double_left > 1 else ''} left"
        return txt

    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        overlay = self.overlay_visible()
        if overlay:
            a.interactive = False
        title = "Vs " + self.players[1]["name"] if self.mode == "ai" else self.TITLES[self.mode]
        if self.mode == "tourney" and a.tourney:
            title = a.tourney.round_name(self.tmatch.get("round", 0))
        tb, bx, by, bs, pw = self.layout()
        a.top_bar(title)

        # status line + second info line
        a.label(self.status_text(), a.fs(28), a.pcol(self.turn) if self.phase in ("play", "ai_wait") else t["text"],
                (W // 2, tb + int(20 * s)), bold=True, maxw=W - 40)
        if self.mode == "quake":
            n = 5 - self.move_count % 5
            if self.phase in ("shake", "swap"):
                txt, col = "The ground is moving...", t["accent2"]
            else:
                txt, col = f"Next quake in: {n} move{'s' if n != 1 else ''}", t["accent2"] if n == 1 else t["sub"]
            jx = math.sin(a.now * 40) * 3 * s if n == 1 and self.phase == "play" else 0
            a.label(txt, a.fs(18), col, (W // 2 + jx, tb + int(52 * s)), bold=True)
        elif self.mode == "tourney":
            p1, p2 = self.players
            a.label(f"Best of 5 (first to 3, draws don't count):  {p1['name']} {self.match_score[0]} - "
                    f"{self.match_score[1]} {p2['name']}", a.fs(18), t["accent2"], (W // 2, tb + int(52 * s)),
                    bold=True, maxw=W - 40)
        else:
            a.label("Keys 1-9 also work (1 = top-left)", a.fs(14), t["sub"], (W // 2, tb + int(52 * s)))

        # side panels
        lx = (bx - pw) // 2
        rx = bx + bs + ((W - bx - bs) - pw) // 2
        self.draw_player(surf, pygame.Rect(lx, by, pw, bs), 0)
        self.draw_player(surf, pygame.Rect(rx, by, pw, bs), 1)

        # board
        human_turn = self.phase == "play" and not self.players[self.turn]["ai"]
        cells0 = board_cells(bx, by, bs)
        hover = ghost = None
        hover_col = None
        if human_turn and a.interactive:
            for i, r in enumerate(cells0):
                if r.collidepoint(a.mouse):
                    if self.pending == "swap":
                        if self.board[i] == 1 - self.turn:
                            hover, hover_col = i, mix(t["accent2"], t["board"], 0.6)
                    elif self.pending == "block":
                        if self.board[i] is None:
                            hover, hover_col = i, mix((168, 72, 50), t["board"], 0.6)
                    elif i in self.legal_cells():
                        hover, ghost = i, (i, self.turn)
        offset = (0, 0)
        if self.phase == "shake":
            k = 1 - self.anim_t
            offset = (math.sin(a.now * 70) * 16 * s * k, math.cos(a.now * 53) * 8 * s * k)
        hidden = self.swap_cells or ()
        hl = []
        if self.blocked and self.board[self.blocked[0]] is None:
            hl = []
        res = self.result
        cells = draw_board(a, surf, bx, by, bs, self.board, self.emojis, hover=hover, hover_color=hover_col,
                           ghost=ghost, pop=self.pop, hidden=hidden, highlight=hl,
                           blocked=self.blocked[0] if self.blocked else None, offset=offset,
                           win_lines=res["lines"] if res else None, win_t=res["t"] if res else 0)
        if self.swap_cells:
            p = ease_io(clamp(self.anim_t / 0.75, 0, 1))
            for src, dst in ((self.swap_cells[0], self.swap_cells[1]), (self.swap_cells[1], self.swap_cells[0])):
                v = self.board[src]
                if v is None:
                    continue
                (sx, sy), (ex, ey) = cells[src].center, cells[dst].center
                cx = sx + (ex - sx) * p
                cy = sy + (ey - sy) * p - math.sin(math.pi * p) * bs / 3 * 0.7
                draw_piece(a, surf, self.emojis[v], v, (cx, cy), bs / 3 * 0.62, 1 + 0.35 * math.sin(math.pi * p))
        if human_turn and a.interactive and a.clicked:
            for i, r in enumerate(cells0):
                if r.collidepoint(a.clicked):
                    a.clicked = None
                    self.cell_clicked(i)
                    break

        # bottom: scoreboard and power-up toggle
        yb = by + bs + int(36 * s)
        if self.mode != "tourney":
            sc = a.session_scores.get(self.key, [0, 0, 0])
            p1, p2 = self.players
            a.label(f"{p1['emoji']} {p1['name']}: {sc[0]}     Draws: {sc[2]}     {p2['emoji']} {p2['name']}: {sc[1]}",
                    a.fs(18), t["text"], (W // 2, yb), bold=True, maxw=W - 40)
        if self.mode in ("classic", "quake"):
            on = a.settings["powerups"]
            br = pygame.Rect(W - int(220 * s), H - int(58 * s), int(200 * s), int(42 * s))
            if a.button(br, f"Power-ups: {'ON' if on else 'OFF'}", kind="secondary", selected=on):
                a.settings["powerups"] = not on
                a.save()
                self.new_round(alternate=False)
                a.toast(f"Power-ups {'ON' if not on else 'OFF'} - fresh round!")
        a.interactive = True
        if overlay:
            self.draw_result(surf)

    def draw_player(self, surf, rect, p):
        a = self.app
        t, s = a.theme, a.s
        pl = self.players[p]
        active = self.phase in ("play", "ai_wait") and self.turn == p
        a.panel(rect, border=a.pcol(p) if active else None, glow=active)
        cx = rect.centerx
        esz = int(min(rect.w * 0.4, 84 * s))
        y = rect.y + int(46 * s)
        bob = math.sin(a.now * 4) * 3 * s if active else 0
        img = a.gfx.emoji(pl["emoji"], esz, a.pcol(p))
        surf.blit(img, img.get_rect(midtop=(cx, y + bob)))
        res = self.result
        if res and res["winner"] == p:
            k = ease_out_back(clamp((a.now - res["t"]) / 0.5, 0, 1))
            draw_crown(surf, cx, y - int(4 * s) + math.sin(a.now * 3) * 3 * s, esz * 0.6 * k)
        y += esz + int(12 * s)
        a.label(pl["name"], a.fs(22), a.pcol(p), (cx, y), bold=True, maxw=rect.w - 20)
        y += a.fs(22)
        status = ""
        if res:
            status = "WINNER!" if res["winner"] == p else ""
        elif active:
            status = "Thinking..." if pl["ai"] else "Your turn!"
        elif pl["ai"]:
            status = "AI opponent"
        if status:
            a.label(status, a.fs(16), t["sub"], (cx, y), bold=True)
        y += int(26 * s)
        if self.power_on:
            ch = int(min(44 * s, (rect.bottom - y - 12 * s) / 3 - 8 * s))
            for key, icon, name in POWERS:
                used = not self.powers[p][key]
                can = (not used and self.phase == "play" and self.turn == p and self.double_left == 0
                       and not pl["ai"])
                r = pygame.Rect(rect.x + int(12 * s), y, rect.w - int(24 * s), max(24, ch))
                label = f"{icon} {name}" + ("  (used)" if used else "")
                if a.button(r, label, enabled=can, kind="secondary", selected=(self.pending == key and self.turn == p)):
                    self.use_power(p, key)
                cf = self.card_flash
                if cf and cf[0] == p and cf[1] == key and a.now - cf[2] < 0.6:
                    k = (a.now - cf[2]) / 0.6
                    g = r.inflate(int(30 * k * s), int(30 * k * s))
                    gs = pygame.Surface(g.size, pygame.SRCALPHA)
                    pygame.draw.rect(gs, (*a.pcol(p), int(220 * (1 - k))), gs.get_rect(), 4, border_radius=14)
                    surf.blit(gs, g.topleft)
                y += max(24, ch) + int(8 * s)
        if pl["ai"] and self.speech:
            text, t0, thinking = self.speech
            if thinking:
                text = "thinking" + "." * (int(a.now * 3) % 4 + 1)
            fsz = a.fs(15)
            lines = a.wrap(text, fsz, rect.w - int(40 * s))[:5]
            bh = len(lines) * int(fsz * 1.3) + int(20 * s)
            br = pygame.Rect(rect.x + int(12 * s), y + int(10 * s), rect.w - int(24 * s), bh)
            k = ease_out_back(clamp((a.now - t0) / 0.3, 0, 1))
            if k > 0.05 and br.bottom < rect.bottom + int(60 * s):
                bub = br.inflate(-int(br.w * (1 - k)), -int(br.h * (1 - k)))
                pygame.draw.polygon(surf, t["hover"], [(cx - 10, bub.y + 2), (cx + 10, bub.y + 2), (cx, bub.y - 12)])
                pygame.draw.rect(surf, t["hover"], bub, border_radius=int(14 * s))
                pygame.draw.rect(surf, t["line"], bub, 2, border_radius=int(14 * s))
                if k > 0.9:
                    ly = br.y + int(10 * s) + fsz // 2
                    for ln in lines:
                        a.label(ln, fsz, t["text"], (br.centerx, ly))
                        ly += int(fsz * 1.3)

    def draw_result(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        res = self.result
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 120))
        surf.blit(dim, (0, 0))
        w = res["winner"]
        p1, p2 = self.players
        btns = []
        if w is not None:
            win, lose = self.players[w], self.players[1 - w]
        if self.mode == "tourney":
            if w is None:
                title, sub = "It's a draw", "Draws don't count in the match. Play on!"
                btns = [("Next Game", lambda: self.new_round()), ("Watch Replay", self.open_replay)]
            elif self.match_done:
                title = f"{win['emoji']} {win['name']} wins the match!"
                sub = f"Final score {max(self.match_score)}-{min(self.match_score)}"
                champ = a.tourney.champion()
                btns = [(f"Spin the Dare Wheel for {lose['name']}", lambda: self.open_wheel(lose["name"])),
                        ("See the Champion!" if champ else "Back to Bracket",
                         (lambda: a.go(ChampionScreen(a))) if champ else (lambda: a.go(BracketScreen(a)))),
                        ("Watch Replay", self.open_replay)]
            else:
                title = f"{win['emoji']} {win['name']} wins this game!"
                sub = f"Match: {p1['name']} {self.match_score[0]} - {self.match_score[1]} {p2['name']}"
                btns = [("Next Game", lambda: self.new_round()), ("Watch Replay", self.open_replay)]
        else:
            if w is None:
                title = res["msg"] or "It's a draw"
                sub = "It's a draw!" if res["msg"] == "The earth has chosen chaos" else "Nobody wins. Nobody gets a dare."
                btns = [("Rematch", lambda: self.new_round()), ("Watch Replay", self.open_replay),
                        ("Home", a.go_home)]
            else:
                title = f"{win['emoji']} {win['name']} wins!"
                sub = res["msg"] or "Flawless. Absolutely flawless."
                btns = [(f"Spin the Dare Wheel for {lose['name']}", lambda: self.open_wheel(lose["name"])),
                        ("Rematch", lambda: self.new_round()), ("Watch Replay", self.open_replay),
                        ("Home", a.go_home)]
        pw = min(int(540 * s), W - 40)
        tsz = a.fs(36)
        tlines = a.wrap(title, tsz, pw - 40, bold=True)
        bh = int(52 * s)
        ph = int(40 * s) + len(tlines) * int(tsz * 1.2) + int(50 * s) + len(btns) * (bh + int(12 * s)) + int(16 * s)
        k = ease_out_back(clamp((a.now - res["t"] - 0.9) / 0.35, 0, 1))
        rect = pygame.Rect(0, 0, pw, ph)
        rect.center = (W // 2, H // 2 + int((1 - k) * 60 * s))
        a.panel(rect, border=t["accent"])
        y = rect.y + int(32 * s)
        for ln in tlines:
            a.label(ln, tsz, t["text"], (rect.centerx, y + tsz // 2), bold="display" not in t, family=t.get("display"),
                    maxw=pw - 30)
            y += int(tsz * 1.2)
        a.label(sub, a.fs(18), t["sub"], (rect.centerx, y + int(14 * s)), maxw=pw - 30)
        y += int(46 * s)
        for i, (label, fn) in enumerate(btns):
            r = pygame.Rect(rect.x + int(30 * s), y, pw - int(60 * s), bh)
            if a.button(r, label, kind="danger" if label.startswith("Spin") else ("primary" if i < 2 else "secondary")):
                fn()
                return
            y += bh + int(12 * s)

    def open_wheel(self, loser):
        self.app.go(WheelScreen(self.app, loser, self))

    def open_replay(self):
        self.app.go(ReplayScreen(self.app, self))


class WheelScreen(Screen):
    def __init__(self, app, loser, back):
        super().__init__(app)
        self.loser, self.back = loser, back
        self.rot = random.uniform(0, 360)
        self.spinning = False
        self.result = None
        self.result_t = 0
        self.new_dare = ""
        self.cache_key = None
        self.cache = None
        self.last_idx = None

    def dares(self):
        return DEFAULT_DARES + self.app.settings["custom_dares"]

    def index(self):
        n = len(self.dares())
        return int(((-self.rot) % 360) / (360 / n)) % n

    def spin(self):
        n = len(self.dares())
        seg = 360 / n
        k = random.randrange(n)
        theta = k * seg + random.uniform(0.15, 0.85) * seg
        self.start = self.rot
        self.target = self.rot + 360 * random.randint(4, 6) + ((-theta - self.rot) % 360)
        self.t, self.dur = 0.0, random.uniform(4.2, 4.9)
        self.spinning = True
        self.result = None
        self.last_idx = self.index()

    def update(self, dt):
        if not self.spinning:
            return
        a = self.app
        self.t += dt
        p = clamp(self.t / self.dur, 0, 1)
        self.rot = self.start + (self.target - self.start) * (1 - (1 - p) ** 4)
        idx = self.index()
        if idx != self.last_idx:
            self.last_idx = idx
            a.sfx.play("tick")
        if p >= 1:
            self.spinning = False
            self.result = self.dares()[idx]
            self.result_t = a.now
            a.sfx.play("chime")
            a.stats["dares"] += 1
            a.save()

    def build(self, R):
        a = self.app
        dares = self.dares()
        key = (tuple(dares), R)
        if key == self.cache_key:
            return self.cache
        n = len(dares)
        seg = 360 / n
        S = pygame.Surface((2 * R + 8, 2 * R + 8), pygame.SRCALPHA)
        cx = cy = R + 4
        for i in range(n):
            a0, a1 = i * seg, (i + 1) * seg
            pts = [(cx, cy)]
            steps = max(2, int(seg / 3))
            for k in range(steps + 1):
                ang = math.radians(a0 + (a1 - a0) * k / steps)
                pts.append((cx + R * math.sin(ang), cy - R * math.cos(ang)))
            col = WHEEL_COLORS[i % len(WHEEL_COLORS)]
            if i == n - 1 and n % len(WHEEL_COLORS) == 1:
                col = WHEEL_COLORS[3]
            pygame.draw.polygon(S, col, pts)
            pygame.draw.polygon(S, (255, 255, 255), pts, 2)
            label = dares[i] if len(dares[i]) <= 20 else dares[i][:19].rstrip() + "..."
            txt = a.gfx.text(label, max(10, int(R * 0.066)), on_color(col), True, "arial")
            mid = a0 + seg / 2
            rt = pygame.transform.rotate(txt, 90 - mid)
            rr = R * 0.58
            S.blit(rt, rt.get_rect(center=(cx + rr * math.sin(math.radians(mid)), cy - rr * math.cos(math.radians(mid)))))
        pygame.draw.circle(S, (255, 255, 255), (cx, cy), R, 6)
        self.cache_key, self.cache = key, S
        return S

    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        show_card = self.result is not None and not self.spinning
        if show_card:
            a.interactive = False
        tb = a.top_bar(f"Dare Wheel for {self.loser}")
        narrow = W < 860
        right_w = int(min(340 * s, W * 0.36))
        cx = int((W - right_w) / 2) if not narrow else int(W * 0.34)
        R = int(min((W - right_w) / 2 - 40 * s, (H - tb) / 2 - 80 * s))
        R = max(80, R)
        cy = tb + int(30 * s) + R
        wheel = self.build(R)
        img = pygame.transform.rotozoom(wheel, -self.rot, 1)
        surf.blit(img, img.get_rect(center=(cx, cy)))
        pygame.draw.circle(surf, t["panel"], (cx, cy), int(R * 0.14))
        pygame.draw.circle(surf, t["accent2"], (cx, cy), int(R * 0.14), 4)
        for k in range(24):
            ang = math.radians(k * 15)
            on = (int(a.now * 6) + k) % 2 == 0
            pygame.draw.circle(surf, (255, 240, 160) if on else (200, 170, 80),
                               (int(cx + (R + 9) * math.sin(ang)), int(cy - (R + 9) * math.cos(ang))), max(3, int(4 * s)))
        wob = math.sin(a.now * 40) * 3 if self.spinning else 0
        pts = [(cx - 20 * s + wob, cy - R - 26 * s), (cx + 20 * s + wob, cy - R - 26 * s), (cx, cy - R + 14 * s)]
        pygame.draw.polygon(surf, t["accent2"], pts)
        pygame.draw.polygon(surf, darken(t["accent2"], 0.4), pts, 3)
        br = pygame.Rect(0, 0, int(200 * s), int(56 * s))
        br.center = (cx, cy + R + int(46 * s))
        if a.button(br, "SPINNING..." if self.spinning else "SPIN", enabled=not self.spinning, kind="danger", size=a.fs(26)):
            self.spin()

        # right side: custom dares
        px = W - right_w - int(20 * s)
        prect = pygame.Rect(px, tb + int(16 * s), right_w, H - tb - int(36 * s))
        a.panel(prect)
        y = prect.y + int(18 * s)
        a.label("Add your own dare", a.fs(20), t["text"], (prect.x + int(16 * s), y), anchor="topleft", bold=True)
        y += int(34 * s)
        iw = prect.w - int(32 * s)
        self.new_dare, sub = a.text_input((prect.x + int(16 * s), y, iw, int(44 * s)), "dare", self.new_dare,
                                          "Type a dare...", 60)
        y += int(52 * s)
        if (a.button((prect.x + int(16 * s), y, iw, int(42 * s)), "+ Add to wheel", enabled=not self.spinning) or sub) \
                and self.new_dare.strip() and not self.spinning:
            a.settings["custom_dares"].append(self.new_dare.strip())
            a.save()
            a.toast("Dare added to the wheel!")
            self.new_dare = ""
        y += int(58 * s)
        cd = a.settings["custom_dares"]
        a.label(f"Custom dares ({len(cd)})", a.fs(16), t["sub"], (prect.x + int(16 * s), y), anchor="topleft", bold=True)
        y += int(28 * s)
        rh = int(36 * s)
        maxrows = max(0, int((prect.bottom - y - 70 * s) // (rh + 6)))
        for i, d in enumerate(cd[:maxrows]):
            r = pygame.Rect(prect.x + int(16 * s), y, iw, rh)
            pygame.draw.rect(surf, t["hover"], r, border_radius=int(10 * s))
            a.label(d, a.fs(14), t["text"], (r.x + int(10 * s), r.centery), anchor="midleft", maxw=iw - int(56 * s))
            xr = pygame.Rect(r.right - rh, r.y, rh, rh)
            if a.button(xr.inflate(-6, -6), "x", enabled=not self.spinning, kind="danger", size=a.fs(16)):
                cd.pop(i)
                a.save()
                break
            y += rh + 6
        if len(cd) > maxrows:
            a.label(f"+{len(cd) - maxrows} more on the wheel", a.fs(14), t["sub"], (prect.x + int(16 * s), y), anchor="topleft")
        if not cd:
            a.label("None yet. Get creative!", a.fs(14), t["sub"], (prect.x + int(16 * s), y), anchor="topleft")
        if a.button((prect.x + int(16 * s), prect.bottom - int(58 * s), iw, int(44 * s)), "Back", kind="secondary"):
            a.go(self.back)
        a.interactive = True
        if show_card:
            self.draw_card(surf)

    def draw_card(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        surf.blit(dim, (0, 0))
        k = ease_out_back(clamp((a.now - self.result_t) / 0.4, 0, 1))
        cw = min(int(620 * s), W - 40)
        dsz = a.fs(34)
        lines = a.wrap(self.result, dsz, cw - int(60 * s), bold=True)
        ch = int(150 * s) + len(lines) * int(dsz * 1.25) + int(80 * s)
        rect = pygame.Rect(0, 0, cw, ch)
        rect.center = (W // 2, H // 2 + int((1 - k) * 80 * s))
        a.panel(rect, border=t["accent2"])
        y = rect.y + int(36 * s)
        a.label(f"{self.loser}, your dare is:", a.fs(22), t["sub"], (rect.centerx, y), bold=True, maxw=cw - 30)
        y += int(46 * s)
        for ln in lines:
            a.label(ln, dsz, t["accent2"], (rect.centerx, y + dsz // 2), bold=True)
            y += int(dsz * 1.25)
        bw = (cw - int(80 * s)) // 2
        by = rect.bottom - int(76 * s)
        if a.button((rect.x + int(30 * s), by, bw, int(50 * s)), "Spin Again"):
            self.spin()
        if a.button((rect.right - int(30 * s) - bw, by, bw, int(50 * s)), "Back", kind="secondary"):
            a.go(self.back)


class ReplayScreen(Screen):
    SPEEDS = [0.5, 1.0, 2.0]

    def __init__(self, app, game):
        super().__init__(app)
        self.game = game
        self.acts = game.actions
        self.emojis = game.emojis
        self.step = 0
        self.playing = True
        self.si = 1
        self.acc = 0.0
        self.drag = False
        self.pop = {}
        self.step_t = app.now

    def set_step(self, i):
        i = int(clamp(i, 0, len(self.acts) - 1))
        if i == self.step:
            return
        self.step = i
        self.step_t = self.app.now
        act = self.acts[i]
        self.pop = {c: self.app.now for c in act["cells"] if act["board"][c] is not None}
        self.app.sfx.play("place")

    def toggle(self):
        if not self.playing and self.step == len(self.acts) - 1:
            self.step = 0
            self.pop = {}
            self.acc = 0.0
        self.playing = not self.playing

    def update(self, dt):
        if self.playing:
            self.acc += dt * self.SPEEDS[self.si]
            if self.acc >= 0.8:
                self.acc -= 0.8
                if self.step < len(self.acts) - 1:
                    self.set_step(self.step + 1)
                else:
                    self.playing = False

    def on_key(self, key):
        if key == pygame.K_SPACE:
            self.toggle()
        elif key == pygame.K_RIGHT:
            self.set_step(self.step + 1)
        elif key == pygame.K_LEFT:
            self.set_step(self.step - 1)

    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        tb = a.top_bar("Instant Replay")
        bs = int(min(H - tb - 230 * s, W - 80 * s, 520 * s))
        bx, by = (W - bs) // 2, tb + int(24 * s)
        act = self.acts[self.step]
        hl_col = t["accent2"] if act["caption"].startswith(("EARTHQUAKE", "SWAP", "BLOCK")) else t["accent"]
        draw_board(a, surf, bx, by, bs, act["board"], self.emojis, highlight=act["cells"], hl_color=hl_col,
                   blocked=act["blocked"], pop=self.pop, win_lines=act.get("win"), win_t=self.step_t)
        a.label(act["caption"], a.fs(24), t["text"], (W // 2, by + bs + int(32 * s)), bold=True, maxw=W - 40)
        a.label(f"Step {self.step + 1} / {len(self.acts)}", a.fs(15), t["sub"], (W // 2, by + bs + int(62 * s)))
        bw = int(150 * s)
        bh = int(46 * s)
        row_y = H - int(124 * s)
        x0 = W // 2 - (3 * bw + 2 * int(14 * s)) // 2
        if a.button((x0, row_y, bw, bh), "Pause" if self.playing else "Play"):
            self.toggle()
        if a.button((x0 + bw + int(14 * s), row_y, bw, bh), f"Speed: {self.SPEEDS[self.si]:g}x", kind="secondary"):
            self.si = (self.si + 1) % len(self.SPEEDS)
        if a.button((x0 + 2 * (bw + int(14 * s)), row_y, bw, bh), "Back to game", kind="secondary"):
            a.go(self.game)
            return
        track = pygame.Rect(int(60 * s), H - int(48 * s), W - int(120 * s), int(8 * s))
        n = len(self.acts)
        if a.interactive and a.clicked and track.inflate(0, int(36 * s)).collidepoint(a.clicked):
            a.clicked = None
            self.drag = True
        if self.drag:
            if a.mouse_down:
                self.set_step(round((a.mouse[0] - track.x) / max(1, track.w) * (n - 1)))
                self.acc = 0.0
            else:
                self.drag = False
        pygame.draw.rect(surf, t["line"], track, border_radius=4)
        frac = self.step / max(1, n - 1)
        pygame.draw.rect(surf, t["accent"], (track.x, track.y, int(track.w * frac), track.h), border_radius=4)
        for i in range(n):
            tx = track.x + track.w * i / max(1, n - 1)
            pygame.draw.circle(surf, t["sub"], (int(tx), track.centery), max(2, int(3 * s)))
        kx = track.x + track.w * frac
        pygame.draw.circle(surf, t["accent2"], (int(kx), track.centery), int(13 * s))
        pygame.draw.circle(surf, t["panel"], (int(kx), track.centery), int(6 * s))


class CustomizeScreen(Screen):
    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        st = a.settings
        tb = a.top_bar("Customize")
        gap = int(28 * s)
        colw = min(int(420 * s), (W - 2 * int(24 * s) - gap) // 2)
        startx = (W - (2 * colw + gap)) // 2
        y0 = tb + int(10 * s)
        cols = 5
        g8 = int(8 * s)
        bsz = min(int(60 * s), (colw - (cols - 1) * g8) // cols)
        for p in (0, 1):
            x = startx + p * (colw + gap)
            a.label(f"Player {p + 1}", a.fs(22), a.pcol(p), (x, y0), anchor="topleft", bold=True)
            nk = "p1_name" if p == 0 else "p2_name"
            val, _ = a.text_input((x, y0 + int(32 * s), colw, int(42 * s)), f"name{p}", st[nk], "Enter a name", 14)
            if val != st[nk]:
                st[nk] = val
                a.save()
            mine = st["p1_emoji"] if p == 0 else st["p2_emoji"]
            other = st["p2_emoji"] if p == 0 else st["p1_emoji"]
            gy = y0 + int(84 * s)
            for i, (e, _) in enumerate(PIECES):
                r = pygame.Rect(x + (i % cols) * (bsz + g8), gy + (i // cols) * (bsz + g8), bsz, bsz)
                taken, sel = e == other, e == mine
                hover = a.interactive and not taken and r.collidepoint(a.mouse)
                bg = t["hover"] if hover else t["panel"]
                pygame.draw.rect(surf, bg, r, border_radius=int(12 * s))
                pygame.draw.rect(surf, a.pcol(p) if sel else t["line"], r, max(2, int((5 if sel else 2) * s)),
                                 border_radius=int(12 * s))
                img = a.gfx.emoji(e, int(bsz * (0.66 if hover or sel else 0.6)), a.pcol(p))
                if taken:
                    img = img.copy()
                    img.set_alpha(55)
                surf.blit(img, img.get_rect(center=r.center))
                if taken:
                    a.label(f"P{2 - p}", a.fs(12), t["sub"], (r.right - int(12 * s), r.bottom - int(10 * s)), bold=True)
                elif a.hit(r):
                    st["p1_emoji" if p == 0 else "p2_emoji"] = e
                    a.sfx.play("place")
                    a.save()
        ty = y0 + int(84 * s) + 4 * (bsz + g8) + int(14 * s)
        a.label("Board theme", a.fs(22), t["text"], (startx, ty), anchor="topleft", bold=True)
        ty += int(34 * s)
        tw = min(int(190 * s), (colw - g8) // 2 + colw // 4)
        th = int(50 * s)
        for i, name in enumerate(THEMES):
            r = pygame.Rect(startx + (i % 2) * (tw + g8 * 2), ty + (i // 2) * (th + g8 * 2), tw, th)
            if a.button(r, "      " + name, kind="secondary", selected=(st["theme"] == name)):
                st["theme"] = name
                a.save()
            th_ = THEMES[name]
            sw = pygame.Rect(r.x + int(10 * s), r.centery - int(14 * s), int(28 * s), int(28 * s))
            pygame.draw.rect(surf, th_["bg"], sw, border_radius=6)
            pygame.draw.line(surf, th_["grid"], (sw.centerx, sw.y + 4), (sw.centerx, sw.bottom - 4), 3)
            pygame.draw.line(surf, th_["grid2"], (sw.x + 4, sw.centery), (sw.right - 4, sw.centery), 3)
            pygame.draw.rect(surf, th_["line"], sw, 1, border_radius=6)
        px = startx + 2 * tw + int(60 * s)
        psz = int(min(H - ty - 40 * s, W - px - 40 * s, 210 * s))
        if psz > 60:
            a.label("Live preview", a.fs(16), t["sub"], (px + psz // 2, ty - int(18 * s)), bold=True)
            demo = [0, None, 1, None, 0, None, 1, None, None]
            draw_board(a, surf, px, ty + int(6 * s), psz, demo, [st["p1_emoji"], st["p2_emoji"]],
                       win_lines=None)


class TourneySetupScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        names = list(app.settings.get("tourney_names") or [])
        while len(names) < 2:
            names.append("")
        self.names = names[:8]

    def start(self):
        a = self.app
        clean = []
        for i, n in enumerate(self.names):
            n = n.strip() or f"Player {i + 1}"
            base, k = n, 2
            while n in clean:
                n = f"{base} {k}"
                k += 1
            clean.append(n)
        a.settings["tourney_names"] = list(self.names)
        a.save()
        a.tourney = Tournament(clean)
        a.go(BracketScreen(a))

    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        tb = a.top_bar("Party Tournament")
        a.label("2 to 8 players. Random bracket - byes go to lucky players if the count isn't 2, 4 or 8.",
                a.fs(16), t["sub"], (W // 2, tb + int(16 * s)), maxw=W - 40)
        rh = int(min(46 * s, (H - tb - 180 * s) / 8 - 8 * s))
        iw = int(min(380 * s, W - 200 * s))
        x = (W - iw) // 2
        y = tb + int(44 * s)
        for i in range(len(self.names)):
            a.label(f"{i + 1}.", a.fs(20), t["sub"], (x - int(14 * s), y + rh // 2), anchor="midright", bold=True)
            self.names[i], sub = a.text_input((x, y, iw, rh), f"t{i}", self.names[i], f"Player {i + 1}", 16)
            if sub:
                a.focus = f"t{i + 1}" if i + 1 < len(self.names) else None
            if len(self.names) > 2:
                if a.button((x + iw + int(10 * s), y, rh, rh), "x", kind="danger", size=a.fs(18)):
                    self.names.pop(i)
                    a.focus = None
                    break
            y += rh + int(8 * s)
        y += int(8 * s)
        bw = int(200 * s)
        if len(self.names) < 8:
            if a.button((W // 2 - bw - int(8 * s), y, bw, int(48 * s)), "+ Add player", kind="secondary"):
                self.names.append("")
                a.focus = f"t{len(self.names) - 1}"
                a.focus_claimed = True
        if a.button((W // 2 + int(8 * s), y, bw, int(48 * s)), "Shuffle & Start"):
            self.start()


class Tournament:
    def __init__(self, names):
        names = list(names)
        random.shuffle(names)
        size = 1
        while size < len(names):
            size *= 2
        byes = size - len(names)
        first = [dict(p1=n, p2=None, winner=n, bye=True, score=None) for n in names[:byes]]
        rest = names[byes:]
        for i in range(0, len(rest), 2):
            first.append(dict(p1=rest[i], p2=rest[i + 1], winner=None, bye=False, score=None))
        random.shuffle(first)
        self.rounds = [first]
        n = len(first)
        while n > 1:
            n //= 2
            self.rounds.append([dict(p1=None, p2=None, winner=None, bye=False, score=None) for _ in range(n)])
        for r, rnd in enumerate(self.rounds):
            for m in rnd:
                m["round"] = r
        self.propagate()

    def propagate(self):
        for r in range(len(self.rounds) - 1):
            for i, m in enumerate(self.rounds[r]):
                if m["winner"]:
                    self.rounds[r + 1][i // 2]["p1" if i % 2 == 0 else "p2"] = m["winner"]

    def next_match(self):
        for rnd in self.rounds:
            for m in rnd:
                if m["p1"] and m["p2"] and not m["winner"]:
                    return m
        return None

    def champion(self):
        return self.rounds[-1][0]["winner"]

    def round_name(self, r):
        left = len(self.rounds) - r
        return {1: "Final", 2: "Semifinals", 3: "Quarterfinals"}.get(left, f"Round {r + 1}")


class BracketScreen(Screen):
    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        T = a.tourney
        tb = a.top_bar("Party Tournament")
        R = len(T.rounds)
        m = int(24 * s)
        colw = (W - 2 * m) / R
        boxw = int(min(colw - 36 * s, 250 * s))
        boxh = int(64 * s)
        top, bottom = tb + int(44 * s), H - int(96 * s)
        nxt = T.next_match()
        rects = {}
        for r, rnd in enumerate(T.rounds):
            x = int(m + r * colw + (colw - boxw) / 2)
            a.label(T.round_name(r), a.fs(18), t["sub"], (x + boxw // 2, tb + int(18 * s)), bold=True)
            sp = (bottom - top) / len(rnd)
            for i in range(len(rnd)):
                cy = top + sp * (i + 0.5)
                rects[(r, i)] = pygame.Rect(x, int(cy - boxh / 2), boxw, boxh)
        for (r, i), rect in rects.items():
            if r < R - 1:
                nr = rects[(r + 1, i // 2)]
                midx = (rect.right + nr.x) // 2
                col = t["accent"] if T.rounds[r][i]["winner"] else t["line"]
                pygame.draw.lines(surf, col, False, [rect.midright, (midx, rect.centery), (midx, nr.centery), nr.midleft], 3)
        for (r, i), rect in rects.items():
            mt = T.rounds[r][i]
            is_next = mt is nxt
            a.panel(rect, border=t["accent2"] if is_next else None, glow=is_next, radius=int(10 * s))
            for k, key in enumerate(("p1", "p2")):
                name = mt[key]
                row = pygame.Rect(rect.x + 4, rect.y + 4 + k * (rect.h - 8) // 2, rect.w - 8, (rect.h - 8) // 2)
                won = mt["winner"] and name == mt["winner"] and not mt["bye"]
                if won:
                    pygame.draw.rect(surf, mix(t["accent"], t["panel"], 0.55), row, border_radius=int(8 * s))
                if name is None:
                    label, col = ("BYE" if mt["bye"] else "TBD"), t["sub"]
                else:
                    lost = mt["winner"] and name != mt["winner"]
                    label, col = name, (mix(t["sub"], t["panel"], 0.3) if lost else t["text"])
                a.label(label, a.fs(16), col, (row.x + int(8 * s), row.centery), anchor="midleft", bold=bool(won),
                        maxw=row.w - int(46 * s))
                if mt["score"]:
                    a.label(str(mt["score"][k]), a.fs(16), col, (row.right - int(10 * s), row.centery), anchor="midright", bold=True)
                elif mt["bye"] and k == 0:
                    a.label("advances", a.fs(12), t["sub"], (row.right - int(8 * s), row.centery), anchor="midright")
        champ = T.champion()
        bw = int(min(420 * s, W - 260 * s))
        br = pygame.Rect(W // 2 - bw // 2, H - int(74 * s), bw, int(52 * s))
        if champ:
            if a.button(br, f"Crown the champion: {champ}!", kind="danger"):
                a.go(ChampionScreen(a))
        elif nxt and a.button(br, f"Play next match: {nxt['p1']} vs {nxt['p2']}"):
            a.start_game("tourney", tmatch=nxt)
        if a.button((W - int(200 * s), H - int(68 * s), int(180 * s), int(42 * s)), "New Tournament", kind="secondary"):
            a.go(TourneySetupScreen(a))


class ChampionScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.t0 = app.now
        app.confetti(6.5, top=True)
        app.sfx.play("victory")
        app.stats["champions"] += 1
        app.save()

    def draw(self, surf):
        a = self.app
        t, s, W, H = a.theme, a.s, a.W, a.H
        tb = a.top_bar("Champion")
        champ = a.tourney.champion() if a.tourney else "?"
        k = ease_out_back(clamp((a.now - self.t0) / 0.7, 0, 1))
        th = int(min(260 * s, H * 0.36) * max(0.05, k))
        cy = tb + int(30 * s) + int(min(260 * s, H * 0.36)) // 2 + int(10 * s)
        draw_trophy(surf, W // 2, cy + math.sin(a.now * 2) * 5 * s, th)
        y = cy + int(min(260 * s, H * 0.36)) // 2 + int(36 * s)
        a.label("TOURNAMENT CHAMPION", a.fs(22), t["sub"], (W // 2, y), bold=True)
        a.label(champ, a.fs(64), t["accent2"], (W // 2, y + int(56 * s)), bold="display" not in t,
                family=t.get("display"), maxw=W - 40)
        bw = int(220 * s)
        by = y + int(110 * s)
        if a.button((W // 2 - bw - int(10 * s), by, bw, int(52 * s)), "New Tournament"):
            a.go(TourneySetupScreen(a))
        if a.button((W // 2 + int(10 * s), by, bw, int(52 * s)), "Home", kind="secondary"):
            a.go_home()


# ---------------------------------------------------------------------------
# App: window, immediate-mode UI helpers, effects, main loop
# ---------------------------------------------------------------------------
class App:
    def __init__(self, size=(1100, 760)):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Tic Tac Chaos")
        self.surf = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.gfx = Gfx()
        self.settings, self.stats = load_save()
        self.sfx = Sounds(self)
        self.now = 0.0
        self.W, self.H = self.surf.get_size()
        self.s = 1.0
        self.mouse = (0, 0)
        self.mouse_down = False
        self.clicked = None
        self.typed = []
        self.focus = None
        self.focus_claimed = False
        self.interactive = True
        self.session_scores = {}
        self.particles = []
        self.emitters = []
        self.toasts = []
        self.tourney = None
        self.screen = IntroScreen(self)

    @property
    def theme(self):
        return THEMES[self.settings["theme"]]

    # navigation
    def go(self, screen):
        self.screen = screen
        self.focus = None
        screen.on_enter()

    def go_home(self):
        self.go(HomeScreen(self))

    def start_game(self, mode, persona=None, tmatch=None):
        self.go(GameScreen(self, mode, persona, tmatch))

    def save(self):
        try:
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump({"settings": self.settings, "stats": self.stats}, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    # UI helpers
    def fs(self, n):
        return max(9, int(n * self.s))

    def pcol(self, p):
        return self.theme["accent"] if p == 0 else self.theme["accent2"]

    def label(self, text, size, color, pos, anchor="center", bold=False, family=None, maxw=None):
        img = self.gfx.text(str(text), size, color, bold, family or self.theme["font"])
        if maxw and img.get_width() > maxw > 10:
            k = maxw / img.get_width()
            try:
                img = pygame.transform.smoothscale(img, (int(maxw), max(1, int(img.get_height() * k))))
            except Exception:
                img = pygame.transform.scale(img, (int(maxw), max(1, int(img.get_height() * k))))
        r = img.get_rect()
        setattr(r, anchor, (int(pos[0]), int(pos[1])))
        self.surf.blit(img, r)
        return r

    def wrap(self, text, size, maxw, bold=False):
        return self.gfx.wrap(text, size, maxw, bold, self.theme["font"])

    def hit(self, rect):
        if self.interactive and self.clicked and pygame.Rect(rect).collidepoint(self.clicked):
            self.clicked = None
            self.sfx.play("click")
            return True
        return False

    def panel(self, rect, hover=False, border=None, glow=False, color=None, radius=None):
        t = self.theme
        r = pygame.Rect(rect)
        rad = radius or int(16 * self.s)
        sh = pygame.Surface((r.w + 12, r.h + 14), pygame.SRCALPHA)
        pygame.draw.rect(sh, t["shadow"], (6, 9, r.w, r.h), border_radius=rad)
        self.surf.blit(sh, (r.x - 6, r.y - 6))
        if glow and border:
            pulse = 0.5 + 0.5 * math.sin(self.now * 5)
            g = r.inflate(int(14 + 8 * pulse), int(14 + 8 * pulse))
            gs = pygame.Surface(g.size, pygame.SRCALPHA)
            pygame.draw.rect(gs, (*border, int(60 + 50 * pulse)), gs.get_rect(), border_radius=rad + 8)
            self.surf.blit(gs, g.topleft)
        col = color or t["panel"]
        if hover:
            col = lighten(col, 0.06) if lum(col) < 128 else darken(col, 0.03)
        pygame.draw.rect(self.surf, col, r, border_radius=rad)
        pygame.draw.rect(self.surf, border or t["line"], r, width=max(2, int((4 if border else 2) * self.s)),
                         border_radius=rad)

    def button(self, rect, label, enabled=True, kind="primary", selected=False, size=None):
        t = self.theme
        r = pygame.Rect(rect)
        live = enabled and self.interactive
        hover = live and r.collidepoint(self.mouse)
        bg = t["accent"] if kind == "primary" else t["accent2"] if kind == "danger" else t["panel"]
        if selected:
            bg = t["accent2"] if kind != "danger" else t["accent"]
        if not enabled:
            bg = mix(bg, t["bg"], 0.55)
        if hover:
            bg = lighten(bg, 0.12) if lum(bg) < 170 else darken(bg, 0.07)
        dr = r.copy()
        if hover and self.mouse_down:
            dr = dr.inflate(-4, -4)
        elif hover:
            dr.y -= 2
        rad = min(int(14 * self.s), dr.h // 2)
        pygame.draw.rect(self.surf, darken(bg, 0.25), dr.move(0, 3), border_radius=rad)
        pygame.draw.rect(self.surf, bg, dr, border_radius=rad)
        if kind == "secondary" and not selected:
            pygame.draw.rect(self.surf, t["line"], dr, width=2, border_radius=rad)
        fg = t["text"] if (kind == "secondary" and not selected) else on_color(bg)
        if not enabled:
            fg = mix(fg, bg, 0.45)
        self.label(label, size or max(10, int(r.h * 0.4)), fg, dr.center, bold=True, maxw=dr.w - 16)
        if live and self.clicked and r.collidepoint(self.clicked):
            self.clicked = None
            self.sfx.play("click")
            return True
        return False

    def text_input(self, rect, fid, value, placeholder="", maxlen=16):
        t = self.theme
        r = pygame.Rect(rect)
        if self.interactive and self.clicked and r.collidepoint(self.clicked):
            self.clicked = None
            self.focus = fid
            self.focus_claimed = True
        focused = self.focus == fid
        submitted = False
        if focused:
            self.focus_claimed = self.focus_claimed or not self.clicked
            for ch in self.typed:
                if ch == "\b":
                    value = value[:-1]
                elif ch == "\n":
                    submitted = True
                elif len(value) < maxlen and ch.isprintable():
                    value += ch
            self.typed = []
        pygame.draw.rect(self.surf, t["board"], r, border_radius=int(10 * self.s))
        pygame.draw.rect(self.surf, t["accent"] if focused else t["line"], r, max(2, int((3 if focused else 2) * self.s)),
                         border_radius=int(10 * self.s))
        fsz = max(10, int(r.h * 0.42))
        tx = r.x + int(12 * self.s)
        if value:
            lr = self.label(value, fsz, t["text"], (tx, r.centery), anchor="midleft", maxw=r.w - 30)
            cx = lr.right + 2
        else:
            self.label(placeholder, fsz, t["sub"], (tx, r.centery), anchor="midleft", maxw=r.w - 30)
            cx = tx
        if focused and int(self.now * 2) % 2 == 0:
            pygame.draw.line(self.surf, t["text"], (cx, r.y + r.h * 0.22), (cx, r.bottom - r.h * 0.22), 2)
        return value, submitted

    def top_bar(self, title, home=True):
        s = self.s
        if home and self.button((int(14 * s), int(12 * s), int(110 * s), int(42 * s)), "< Home", kind="secondary"):
            self.go_home()
        disp = self.theme.get("display")
        self.label(title, self.fs(28), BULB if disp else self.theme["text"], (self.W // 2, int(34 * s)),
                   bold=not disp, family=disp, maxw=self.W - int(300 * s))
        return int(64 * s)

    def sound_rect(self):
        sz = int(46 * self.s)
        return pygame.Rect(self.W - sz - int(14 * self.s), int(10 * self.s), sz, sz)

    def draw_sound_toggle(self):
        t = self.theme
        r = self.sound_rect()
        self.panel(r, hover=r.collidepoint(self.mouse), radius=r.w // 2)
        cx, cy = r.center
        u = r.w / 46
        col = t["text"]
        pygame.draw.polygon(self.surf, col, [(cx - 12 * u, cy - 5 * u), (cx - 6 * u, cy - 5 * u), (cx + 2 * u, cy - 12 * u),
                                             (cx + 2 * u, cy + 12 * u), (cx - 6 * u, cy + 5 * u), (cx - 12 * u, cy + 5 * u)])
        if self.settings["sound"]:
            for rr in (8, 14):
                pygame.draw.arc(self.surf, col, (cx - rr * u + 4 * u, cy - rr * u, 2 * rr * u, 2 * rr * u),
                                -math.pi / 3.2, math.pi / 3.2, max(2, int(2 * u)))
        else:
            pygame.draw.line(self.surf, t["accent2"], (cx + 6 * u, cy - 6 * u), (cx + 14 * u, cy + 6 * u), max(2, int(3 * u)))
            pygame.draw.line(self.surf, t["accent2"], (cx + 14 * u, cy - 6 * u), (cx + 6 * u, cy + 6 * u), max(2, int(3 * u)))

    # effects
    def toast(self, text):
        self.toasts.append([text, self.now])
        self.toasts = self.toasts[-3:]

    def confetti(self, seconds, top=False):
        self.emitters.append([self.now + seconds, top])

    def update_fx(self, dt):
        W, H, s = self.W, self.H, self.s
        self.emitters = [e for e in self.emitters if e[0] > self.now]
        for _, top in self.emitters:
            if len(self.particles) > 900:
                break
            for side in (0, 1):
                for _ in range(3):
                    d = 1 if side == 0 else -1
                    self.particles.append([-10 if side == 0 else W + 10, H * random.uniform(0.55, 0.9),
                                           random.uniform(250, 720) * d * s, random.uniform(-1100, -550) * s,
                                           random.choice(CONFETTI_COLORS), random.uniform(7, 13) * s,
                                           random.uniform(4, 7) * s, random.uniform(0, 360),
                                           random.uniform(-500, 500), random.random() < 0.2])
            if top:
                for _ in range(3):
                    self.particles.append([random.uniform(0, W), -10, random.uniform(-80, 80), random.uniform(60, 220),
                                           random.choice(CONFETTI_COLORS), random.uniform(7, 13) * s,
                                           random.uniform(4, 7) * s, random.uniform(0, 360),
                                           random.uniform(-500, 500), random.random() < 0.2])
        for p in self.particles:
            p[3] = min(p[3] + 1000 * s * dt, 240 * s)
            p[2] *= 0.985
            p[0] += (p[2] + math.sin(self.now * 4 + p[7]) * 40) * dt
            p[1] += p[3] * dt
            p[7] += p[8] * dt
        self.particles = [p for p in self.particles if p[1] < H + 30 and -80 < p[0] < W + 80]

    def draw_fx(self):
        for x, y, _, _, col, w, h, rot, _, circ in self.particles:
            if circ:
                pygame.draw.circle(self.surf, col, (int(x), int(y)), max(2, int(h * 0.6)))
                continue
            ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            hw, hh = w / 2, h / 2 * abs(math.cos(math.radians(rot * 1.7))) + 0.5
            pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            pygame.draw.polygon(self.surf, col, pts)

    def draw_toasts(self):
        t = self.theme
        y = int(78 * self.s)
        for text, t0 in list(self.toasts):
            age = self.now - t0
            if age > 1.9:
                self.toasts.remove([text, t0])
                continue
            k = ease_out_back(clamp(age / 0.25, 0, 1))
            alpha = int(255 * clamp((1.9 - age) / 0.4, 0, 1))
            img = self.gfx.text(text, self.fs(20), on_color(t["accent2"]), True, t["font"])
            r = img.get_rect()
            box = r.inflate(int(36 * self.s), int(18 * self.s))
            surf = pygame.Surface(box.size, pygame.SRCALPHA)
            pygame.draw.rect(surf, (*t["accent2"], 235), surf.get_rect(), border_radius=box.h // 2)
            surf.blit(img, img.get_rect(center=(box.w // 2, box.h // 2)))
            if abs(k - 1) > 0.01:
                surf = pygame.transform.smoothscale(surf, (max(1, int(box.w * k)), max(1, int(box.h * k))))
            surf.set_alpha(alpha)
            self.surf.blit(surf, surf.get_rect(center=(self.W // 2, y + box.h // 2)))
            y += box.h + int(8 * self.s)

    # main loop
    def step(self, dt, events):
        self.now += dt
        self.clicked = None
        self.typed = []
        keys = []
        for ev in events:
            if ev.type == pygame.QUIT:
                self.save()
                return False
            elif ev.type == pygame.VIDEORESIZE:
                try:
                    self.surf = pygame.display.set_mode((max(640, ev.w), max(520, ev.h)), pygame.RESIZABLE)
                except Exception:
                    pass
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.clicked = ev.pos
                self.mouse_down = True
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                self.mouse_down = False
            elif ev.type == pygame.TEXTINPUT:
                if self.focus:
                    self.typed.extend(ev.text)
            elif ev.type == pygame.KEYDOWN:
                if self.focus:
                    if ev.key == pygame.K_BACKSPACE:
                        self.typed.append("\b")
                    elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.typed.append("\n")
                    elif ev.key == pygame.K_ESCAPE:
                        self.focus = None
                else:
                    keys.append(ev.key)
        self.mouse = pygame.mouse.get_pos()
        self.W, self.H = self.surf.get_size()
        self.s = clamp(min(self.W / 1100, self.H / 760), 0.6, 1.6)
        click_frame = self.clicked is not None
        self.focus_claimed = False
        if self.clicked and self.sound_rect().collidepoint(self.clicked):
            self.clicked = None
            self.settings["sound"] = not self.settings["sound"]
            self.save()
            self.sfx.play("click")
        for k in keys:
            self.screen.on_key(k)
        self.screen.update(dt)
        self.update_fx(dt)
        self.surf.fill(self.theme["bg"])
        self.interactive = True
        self.screen.draw(self.surf)
        self.interactive = True
        self.draw_fx()
        self.draw_toasts()
        self.draw_sound_toggle()
        if click_frame and not self.focus_claimed:
            self.focus = None
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.step(min(dt, 0.05), pygame.event.get())
            pygame.display.flip()
        pygame.quit()


def main():
    App().run()


if __name__ == "__main__":
    main()
