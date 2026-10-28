# PixiPlay 🎪

**Tic-tac-toe, but with personality.**

PixiPlay is a party-style tic-tac-toe game built in Python with Pygame. It started from the same idea as my very first beginner tic-tac-toe project, then grew into something much bigger: AI opponents that trash-talk, a board that literally shakes, power-ups, a dare wheel for whoever loses, a full tournament bracket, and instant replays.

Everything you see and hear (graphics, carnival stickers, confetti, sound effects) is generated in code. There are no image or audio files.

> In-game, the window title still reads **Tic Tac Chaos**, which was the working name.

<!-- Add screenshots / a GIF here -->
<!-- ![Home screen](screenshots/home.png) -->

---

## Quick start

You need **Python 3** and **Pygame 2**.

```bash
pip install pygame
python tic_tac_chaos.py
```

That's it. Settings and stats are saved automatically to `tic_tac_chaos_save.json` next to the script.

---

## Game modes

| Mode | What it is |
|---|---|
| **Vs AI** | Play against one of three AI opponents, each with a personality (see below). |
| **Classic Duel** | Two players, one device. Good old tic-tac-toe. |
| **Earthquake Mode** | Every 5 moves the board shakes and two random cells swap places. You can win *by* earthquake, or both players can get a line at once, in which case the earth has chosen chaos. |
| **Party Tournament** | 2 to 8 players, randomly shuffled into a bracket (byes are handed out if the count isn't 2, 4 or 8). Every match is best of 5, first to 3 wins, and draws don't count. Ends with a trophy and a confetti storm for the champion. |
| **Customize** | Pick names, pieces and board themes, with a live preview. |

### Meet the AI opponents

| Opponent | Skill | Vibe |
|---|---|---|
| 🧐 **Smug Genius** | Plays the perfect move every time (minimax). A draw is the best you'll get. | Will not let you forget it. |
| 😰 **Nervous Newbie** | Plays the best move only 40% of the time, random otherwise. | Apologises constantly. Panics 100% of the time. |
| 👴 **Desi Uncle** | Plays the best move 70% of the time. | Free life advice in Hinglish. Brings up Sharma ji ka beta. |

Each opponent talks to you in a speech bubble after every move.

---

## The fun extras

- **Power-ups** (Classic and Earthquake modes, toggle on the game screen). Each player gets one of each per round:
  - 🧱 **Block**: brick an empty cell so your opponent can't use it on their next turn
  - 🔄 **Swap**: steal one of your opponent's marks and make it yours
  - ✌ **Double**: place two marks in one turn (not allowed on the very first move)
- **Dare Wheel**: the loser spins a wheel of dares ("Narrate the next round like a cricket commentator", "Do 10 squats right now"...). You can add your own dares and they're saved for next time.
- **Instant Replay**: rewatch any game step by step with play/pause, 0.5x / 1x / 2x speed and a scrubbable timeline. Earthquakes, swaps and blocks are all recorded.
- **Arcade intro**: insert a coin, get your credit, and the striped carnival curtains open onto the home screen (click or press any key to skip).
- **5 board themes**: Midway (default carnival look), Classic, Neon, Pastel and Chalkboard.
- **20 pieces** to choose from: ❌ ⭕ 🍕 🍔 🐱 🐶 🔥 💧 🦄 🐉 😎 🤖 🌮 🍩 ⚡ 🌙 👻 🐸 🍉 ⭐
- **Lifetime stats** on the home screen: games played, dares handed out, earthquakes survived and champions crowned.

---

## Controls

| Action | Input |
|---|---|
| Place a mark | Click a cell, or press **1-9** (1 = top-left, 9 = bottom-right) |
| Replay: play / pause | **Space** |
| Replay: step back / forward | **Left / Right** arrows |
| Sound on / off | Speaker button in the top-right corner |

The window is resizable and the layout scales to fit.

---

## How it's built

- **Single file**, no assets. All drawing uses Pygame primitives. The carnival stickers are small inline SVGs rendered by Pygame at runtime.
- **Sound effects are synthesised with math** (sine, square, triangle and saw waves plus a noise rumble for earthquakes), so there are no audio files to ship.
- **AI** uses negamax (a compact form of minimax) with memoisation via `functools.lru_cache`, so the perfect-play search is instant. The personality comes from how often each opponent actually *uses* the best move.
- **Screens** (home, game, wheel, replay, tournament, etc.) are simple classes that the main `App` switches between, with an immediate-mode style UI for buttons and text inputs.
- **Graceful fallbacks**: if your computer has no emoji font, pieces are drawn as coloured badges with short labels. If the optional fonts are missing, it falls back to system fonts.

### Optional fonts

For the full carnival look, download [Bungee](https://fonts.google.com/specimen/Bungee) and [Fredoka](https://fonts.google.com/specimen/Fredoka) from Google Fonts and place them here:

```
fonts/
├── Bungee-Regular.ttf
└── Fredoka.ttf
```

The game works fine without them.

---

## Project structure

```
pixiplay/
├── tic_tac_chaos.py          # the whole game
├── fonts/                    # optional (Bungee + Fredoka)
└── tic_tac_chaos_save.json   # created automatically: settings + stats
```

---

## Why this exists

My first tic-tac-toe was the classic beginner project: a 3x3 grid and a win check. This is the same game, revisited with everything I wanted to add once I knew more: real AI, animation, sound, game modes, and a lot of silliness. Mostly it's here as a record of how far a "simple" project can go when you keep asking *what if*.
