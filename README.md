# Atoms

Atoms is one of the ten puzzles bundled inside [Almanac](https://play.google.com/store/apps/details?id=com.voodoo.almanac&hl=en), and frankly, it's my least favorite one. I have a limited number of skips in the app, and I almost always end up spending them on this exact puzzle. At some point that got embarrassing enough that instead of just getting better at the puzzle, I decided it would be far more productive to build an engine that solves it for me, so I never have to burn another skip on it again. Conclusion: all programmers are lazy.

This project is a Pygame based recreation of the Atoms puzzle, paired with a Z3 powered solver that can take any board you design and tell you whether it's solvable, and if so, exactly how to connect the atoms.

## List of Contents

1. [Game Rules](#game-rules)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Installation and Running](#installation-and-running)
5. [File Structure](#file-structure)
6. [Project Description](#project-description)
   * [The Solver Engine (Z3)](#the-solver-engine-z3)
   * [Graphics and UI (Pygame)](#graphics-and-ui-pygame)
   * [Object Oriented Structure](#object-oriented-structure)
7. [Future Improvements](#future-improvements)

## Game Rules

Atoms is played on a grid where "atoms" are placed, each carrying a number from 1 to 8. The goal is to connect the atoms with horizontal or vertical lines so that the total number of lines touching each atom exactly matches its number.

A few constraints make the puzzle interesting:

* Lines can only run horizontally or vertically between atoms that share a row or column, and only if there is nothing blocking the direct path between them.
* Up to two lines can be drawn between the same pair of atoms.
* Lines are not allowed to cross one another.
* When the puzzle is fully solved, every atom must be part of a single connected structure. No atom, or group of atoms, can be left isolated from the rest.

## Tech Stack

* Python 3
* [Pygame](https://www.pygame.org/) for the windowing, rendering, and input handling
* [Z3](https://github.com/Z3Prover/z3) for the constraint solving

## Prerequisites

* Python 3 installed on your machine
* `pip` available on your PATH

## Installation and Running

```bash
pip install pygame z3-solver
python main.py
```

Enter a grid width and height between 4 and 15, click START, place your atoms on the design screen, and hit SOLVE.

## File Structure

```
.
├── main.py       # Entry point, event loop and screen state management
├── solver.py     # Z3 based solving logic, no Pygame dependency
├── atom.py       # Atom class, a single intersection point on the grid
├── button.py     # Reusable clickable Button class
├── input_box.py  # Digit only text input used on the menu screen
└── grid.py       # Grid construction and drawing helper functions
```
## Project Description

### The Solver Engine (Z3)

The heart of this project is `solver.py`, which formulates the puzzle as a constraint satisfaction problem and hands it off to [Z3](https://github.com/Z3Prover/z3), Microsoft's theorem prover, to solve.

Here's the general approach:

1. **Candidate Edges:** `_build_candidate_edges` scans every row and every column of the grid and records a potential edge between any two atoms that are next to each other in that row or column, with nothing in between. Each candidate edge is tagged as either horizontal ("H") or vertical ("V").

2. **Line Count Variables.** For every candidate edge, an integer variable is created representing how many lines (0, 1 or 2) will actually be drawn on that edge in the final solution.

3. **Degree Constraints:** For each atom, the sum of the line count variables on all of its incident edges must equal the atom's own number. This is what forces a "5" atom to end up with exactly five line segments touching it.

4. **No Crossing Lines:** `_edges_cross` checks every pair of one horizontal and one vertical candidate edge to see if they would physically intersect on the board. If they would, the solver adds a constraint saying that at least one of the two must have zero lines.

5. **Connectivity:** This is the trickiest part of the model. To guarantee the final answer forms a single connected network rather than several disconnected islands, the solver picks an arbitrary root atom and assigns every atom an "order" variable. Every non root atom is then constrained to have at least one neighbor whose order is exactly one less than its own, and which is connected to it by at least one line. This effectively forces a path back to the root for every atom in the solution, which rules out any disconnected sub group of atoms, even if their individual degree counts would otherwise be satisfied.

6. **Solve & Extract.** Once all constraints are in place, `solver.check()` is called. If the result is satisfiable, the model is read back out and turned into a list of solution edges, each carrying the two atoms it connects, its orientation, and how many lines (1 or 2) should be drawn.

The solver also handles a few edge cases gracefully before ever touching Z3: an empty board, a board with only a single atom, and a board where no atoms share a row or column all return early with a descriptive error message instead of being sent to the solver.

### Graphics and UI (Pygame)

The interface is built with Pygame and is split across three screens, all managed from `main.py` through a simple `ScreenState` enum (`MENU`, `DESIGN`, `SOLVE`).

* **`MENU` screen:** The user types in a grid width and height using two `InputBox` widgets, each restricted to digit input and a maximum character count. Pressing START validates the input against a minimum and maximum grid size and, if valid, builds the grid and moves to the design screen.

<img width="700" height="730" alt="image" src="https://github.com/user-attachments/assets/532b6605-dce3-4227-a2fd-ec71bb0631fa" />

* **`DESIGN` screen:** This is where the puzzle gets built. The grid is drawn using thin lines between intersection points, and each intersection is represented by an `Atom` object. Clicking an atom cycles its value from empty through 1 to 8 and back to empty, unless the eraser tool is active, in which case a click resets it straight to empty. An ERASER button toggles that mode, and a SOLVE button hands the current board off to `solve_atoms`.

<img width="698" height="726" alt="image" src="https://github.com/user-attachments/assets/4d402aec-1c46-4db5-8b0f-37c9d44557d2" />

* **`SOLVE` screen:** Once the solver has run, this screen re-draws the grid and overlays the solution as colored lines between atoms, using a small offset to render double lines when two connections exist between the same pair of atoms. A message tells the user whether the puzzle was solvable, along with the reason if it wasn't. A NEXT button returns to the menu to start over.

<img width="699" height="727" alt="image" src="https://github.com/user-attachments/assets/b38c6a49-87ed-449d-9654-253cc61cbf65" />

Hover states are used throughout the UI. Atoms glow faintly when hovered while empty, and darken with a colored border when hovered while filled, with the border color flipping to a warning red when the eraser is active. Buttons get a translucent highlight overlay on hover as well.

### Object Oriented Structure

The codebase leans on a handful of small, self contained classes rather than one large script, which keeps the Pygame boilerplate out of the way of the actual puzzle logic:

* **`Atom` (`atom.py`).** Represents a single intersection point on the grid. It owns its own position, radius, current value, and hover state, and knows how to handle its own mouse events and how to draw itself, including the empty hover glow and the filled state with its number.

* **`Button` (`button.py`).** A generic clickable rectangle with hover and border styling, reused for START, ERASER, SOLVE, and NEXT. Since it only needs a rect, a label, and a color, the same class covers every button in the app without any duplication.

* **`InputBox` (`input_box.py`).** A minimal text field limited to digits, used for capturing the width and height on the menu screen. It tracks its own active state and renders a label above itself along with a placeholder when empty.

* **`grid.py`.** Not a class, but a small module of free functions that build the grid of `Atom` objects (`create_grid`), draw the grid lines (`draw_grid_lines`), and draw the solved connections on top of it (`draw_solution_edges`). Keeping this separate from `Atom` itself avoids mixing "a single point" logic with "the whole grid" logic.

* **`main.py`.** Owns the Pygame event loop, the `ScreenState` transitions, and instantiates everything else. It deliberately contains no solving logic and no low level drawing logic of its own; it just wires the other pieces together.

* **`solver.py`.** Pure logic, with zero Pygame dependency. It takes the grid of `Atom` objects, rows, and cols, and returns a plain tuple of `(solved, error_message, solution_edges)`, which keeps the constraint solving code fully testable in isolation from the UI.

## Future Improvements

* **Screenshot Based Input:** Right now the grid size and every atom have to be entered by hand, which is basically doing half the puzzle yourself before the solver even starts. A more useful version of this tool would let you feed it a screenshot of the actual puzzle from [Almanac](https://play.google.com/store/apps/details?id=com.voodoo.almanac&hl=en), detect the grid dimensions and the position and value of each atom from the image, map that onto the board automatically, and hand it straight to the solver, cutting out the manual setup entirely.
* **Mobile Accessibility:** The app currently only runs as a local Pygame window, which means using it requires a full Python environment set up on a computer. Since the whole point of this project is to save time when you hit a wall in the puzzle, it would help a lot more if it were reachable from a phone directly, without needing to install Python, Pygame and Z3 first. That likely means rebuilding the solver as a backend service with a lightweight web or mobile frontend, rather than a desktop script.
