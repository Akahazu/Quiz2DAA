# Quiz2DAA

| NRP | Name | Class | GitHub |
| --- | ---- | ----- | ------ |
| 5025241107 | Muhammad Zahran Rizki Prinanda | G | [@Akahazu](https://github.com/Akahazu) |
| 5025241152 | Bintang Ilham Pabeta | E | [@ilhmpbta](https://github.com/ilhmpbta) |
| 5025241162 | Felix Aldorino | F | [@NewGenome](https://github.com/NewGenome) |

# Restaurant 67 🍔🍞

A 2D top-down, grid-based arcade game built with Python and Pygame. Navigate through a confined restaurant map, collect coins to increase your score, and survive dynamic enemies powered by BFS and Dijkstra pathfinding algorithms!

## Gameplay

![Gameplay Demo](https://i.imgur.com/gkyq7BS.gif)

### Unique Character Skills
| Burger Boy | Breadwinner |
| ---------- | ----------- |
| ![Burgerboy Projectile](https://i.imgur.com/7kSj5nR.gif) | ![Breadwinner Invincibility](https://i.imgur.com/ueY19jR.gif) |
| **Projectile Attack**: Spends score points to shoot a projectile that destroys enemies on contact. | **Invincibility**: Spends score points to become temporarily invincible, destroying enemies on collision for bonus points. |

### Dynamic Enemy AI & Power-ups
![Enemy Freeze Powerup](https://i.imgur.com/lBiDdPi.gif)  
Enemies actively hunt the player using two distinct graph traversal algorithms:

* **Enemy 1:** Utilizes **Dijkstra's Algorithm** (Priority Queue/Min-Heap).
* **Enemy 2:** Utilizes **Breadth-First Search (BFS)**.

Collecting the rare Blue Power-up temporarily freezes all enemies on the map.

---

## Features
* **Dual Pathfinding Architecture:** Custom pathfinding module evaluating grid matrices in real-time.
* **State Machine Pattern:** Clean transitions between Start Screen, Character Selection, Gameplay, and Game Over states.
* **Grid-Based Collision:** Strict matrix-level bounds checking and Pygame sprite hitboxes.
* **Map Parsing:** `.tmx` tilemap integration via `pytmx`.

## Installation & Setup

Ensure you have Python 3.x installed on your system.

1. **Clone the repository:**

      ```bash
      git clone https://github.com/Akahazu/Quiz2DAA
      cd Quiz2DAA
      ```

2. **Install Dependencies**

      ```bash
      pip install pygame pytmx
      ```

3. **Run the game**

      ```bash
      python game.py
      ```

## Controls

- **Movement:** `W`, `A`, `S`, `D` or `Arrow Keys`
- **Use Skill:** `SPACEBAR` (Requires 1000 score points)
- **Quit Game:** Close window or `ESC`

## Project Structure

- `game.py` - The main game loop and UI rendering.
- `core.py` - Player, Projectiles, and PowerUp entity classes.
- `enemies.py` - Enemy logic, pathfinding execution, and respawn timers.
- `algorithm.py` - Core algorithms (BFS & Dijkstra) utilizing `collections.deque` and `heapq`.
- `game_map.py` - Matrix layouts, wall generation, and coin management.
- `settings.py` - Global variables, constants, and configuration.

## Game Over

![Game Over](https://i.imgur.com/6dRQmnK.gif)

