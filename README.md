# Bubble Bobble Odyssey

A browser game inspired by Taito's 1986 arcade game Bubble Bobble: blow bubbles, trap enemies, bounce on your bubbles,
and clear 100 rounds of platforms, shafts, caves, labyrinths, waterfalls, forests, cities, space, fire and ice.

**Play:** open `index.html` in a browser (or the GitHub Pages site).

## Controls

One player: A/D move, Space (or W) jump, hold jump to bounce on bubbles, S+Space drop through a platform, E blow a bubble.
F toggles autofire, M mutes, P pauses. On the title screen A/D switches between 1 and 2 players and N lets you type a
three-letter name (some secret items only appear for certain names). Every new game starts at round 1; use the save to
come back to a later round.

Two players (co-op, both must be picked on the title screen):

| | Move | Jump | Bubble |
|---|---|---|---|
| Bub (green, 1UP) | A / D, S down | Space or W | E |
| Bob (blue, 2UP) | arrow keys | Up or Right Shift | Right Ctrl, `/` or `.` |

On a phone or tablet (iOS Safari included) on-screen controls appear automatically: a left / right / down pad on the
left, BUBBLE and JUMP on the right, an AUTO pill (top-left) that toggles autofire, and a pill in the top-right corner that
pauses (or switches 1P/2P on the title screen).
Tap JUMP on the title screen to start (left/right switch 1P/2P there). Press T on a keyboard to show or hide
the overlay. Adding the page to the iOS home screen runs it full screen.

Gamepads (standard mapping) also work: stick or d-pad moves, A jumps, X (or B/Y/bumper/trigger) blows a bubble, Start pauses.
With one player any pad plays. With two players the first pad is Bob and a second pad is Bub, so "joypad + WASD" is
the natural two-player setup.

## Saving

The game checkpoints itself at the start of every round, with one save for 1-player games and one for 2-player games.
On the title screen pick 1 or 2 players and press C (gamepad: the bubble button, touch: the CONTINUE pill) to carry on
from the saved round with scores, candies, shoes, rings and thunder bubbles intact. Escape during a game saves and returns
to the title; Delete on the title clears the save for the selected player count. A new game only overwrites the old
save once it reaches its second round, so a stray Enter costs nothing.

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

## Items

The full arcade item table is in. Popped monsters drop food that gets richer as the rounds go on (green pepper to gold
crowns); popping several at once hands out the chain bonuses (tangerine, peach, watermelon, pineapple, grapes and the
diamonds). Bosses drop crowns.

Special bubbles drift up from the floor on some rounds (each round has its own mix, and some have none): **water**
(pop it and a stream runs along the platforms and off the edges all the way to the floor, sweeping monsters away; touch
it and Bub rides it, jump to hop off), **fire** (flames spread along the platform), **thunder** (a lightning bolt shoots
off) and **EXTEND** letters (collect all six for a bonus). Take too long and HURRY UP! makes the monsters angry.
Candy powers wear off after six lost lives; the Cross of Thunder fires lightning across every row of the level.

All 53 special items appear under their arcade conditions, with their arcade effects: candies and shoes upgrade Bub,
the clock stops time, dynamite / crosses / lamps / book / tiara / fork / knife / cola clear the screen in different ways,
parasols skip rounds, holy waters and the crayon turn the level into a bonus stage, rings pay you for walking,
jumping and blowing, the necklaces give extend bubbles or an energy ball, the doors lead to a secret room or warp to
round 70, Takoppachi / the flamingo / chuhai / treasure boxes / magic canes turn leftover bubbles into items when the
round is won, and the treasure boxes and canes also summon a HUGE version of that item (about ten Bubs tall, worth up
to 80,000). The Drug of Thunder waits on round 100; the Special Bubble is a 1 in 4096 chance.

`tools/` holds the sprite-extraction and build scripts (see `tools/README.txt`). Character sprites are from the original game and
belong to Taito; this is a non-commercial fan prototype.
