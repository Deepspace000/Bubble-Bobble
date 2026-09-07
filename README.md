# Bubble Bobble prototype

A browser prototype inspired by Taito's 1986 arcade game Bubble Bobble: blow bubbles, trap enemies, bounce on your bubbles,
and clear 100 rounds of platforms, shafts, caves, labyrinths, waterfalls, forests, cities, space, fire and ice.

**Play:** open `index.html` in a browser (or the GitHub Pages site).

## Controls

One player: A/D move, Space (or W) jump, hold jump to bounce on bubbles, S+Space drop through a platform, E blow a bubble.
F toggles autofire, M mutes, P pauses. On the title screen W/S picks a starting level and A/D switches between 1 and 2 players.

Two players (co-op, both must be picked on the title screen):

| | Move | Jump | Bubble |
|---|---|---|---|
| Bub (green, 1UP) | A / D, S down | Space or W | E |
| Bob (blue, 2UP) | arrow keys | Up or Right Shift | Right Ctrl, `/` or `.` |

Gamepads (standard mapping) also work: stick or d-pad moves, A jumps, X (or B/Y/bumper/trigger) blows a bubble, Start pauses.
With one player any pad plays. With two players the first pad is Bob and a second pad is Bub, so "joypad + WASD" is
the natural two-player setup.

## Rounds

Rounds 1-72 are the original mix (with a dessert treasure room every sixth slot and a boss every fifth round).
Rounds 73-100 add five new worlds, and keep the narrow half-width shafts going as winding snake climbs:

- **Forest** - rolling stepped hills you can walk up, bushes, mushrooms and trees, leaves drifting down.
- **City** - skyscrapers with lit windows; zig-zag ledges climb the canyons between them, the exit is on the tallest roof.
  Wind gusts blow through, shoving you and your bubbles (watch for the WIND marker).
- **Space** - asteroids under low gravity (huge floaty jumps, some fields wrap top to bottom) or crushing heavy gravity.
- **Fire** - lava lakes and troughs, burning stepping stones (stand on one too long and you cook), fire geysers, embers.
  Monsters that touch lava leap out furious.
- **Ice** - slippery momentum: you slide when you stop and skid when you turn. Snow falls.

Round 100, THE FURNACE, is a narrow burning snake shaft with the final Super Drunk boss.

`tools/` holds the sprite-extraction and build scripts (see `tools/README.txt`). Character sprites are from the original game and
belong to Taito; this is a non-commercial fan prototype.
