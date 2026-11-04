MIDNIGHT DASH
============

Midnight Dash is a small three-lane runner made for the Python tutor skills test.
Move between lanes to avoid the Hopper and Night Bat, and survive for 45 seconds
to reach the finish.

HOW TO RUN
----------
1. Install Python 3.13 and Pygame Zero.
   If Pygame Zero is not installed, run: python -m pip install pgzero
2. Open a terminal in this project folder.
3. Run: pgzrun game.py

CONTROLS
--------
Left Arrow  - move one lane to the left
Right Arrow - move one lane to the right
Enter       - start or play again
Mouse       - click menu buttons

There are three health points. An enemy collision removes one point. Losing all
three ends the run. The main menu button toggles both music and sound effects.

LIBRARIES
---------
The game uses Pygame Zero and its built-in Actor, Rect, screen, keys, mouse,
music, and sounds objects. The source file has no imports of pygame or any other
library. The allowed math and random modules are not needed by this version.

PROJECT FILES
-------------
game.py                 Game logic
images/                 Player and enemy animation frames
sounds/                 Collision, menu, win, and loss effects
music/                  Looping background music
screenshots/            Menu, gameplay, and character previews
README.md               Project overview and setup guide
readme.txt              Run instructions and controls
