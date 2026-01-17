# Snake & Ladders: Truth or Dare Edition 

A classic board game reimagined with a **Dark Medieval Fantasy** theme. This project modernizes the traditional gameplay by integrating interactive "Truth or Dare" challenges, a dynamic physics engine, and a fully customizable content system.

## 📸 Screenshots
<img width="1905" height="1089" alt="image" src="https://github.com/user-attachments/assets/f7485cb6-fa49-427b-8ef7-035201de62e4" />



###  Visual & Audio
* **High-Fidelity Assets:** Custom marble tile rendering, parchment UI, and medieval-themed icons.
* **Dynamic Animations:** Smooth token interpolation, particle effects for victory screens, and "breathing" environmental animations.
* **Immersive Sound Design:** Context-aware audio for dice rolls, footsteps, and UI interactions.

###  Core Mechanics
* **Data-Driven Challenges:** All Truth & Dare questions are loaded from external JSON files. This allows the game content to be completely rewritten (e.g., for Education, Ice Breakers, or Party Modes) without modifying the source code.
* **Dare Countdown System:** To increase intensity, "Dare" challenges feature an **integrated countdown timer**. Players must complete the physical task before the time runs out!
* **Smart Sidebar:** A glass-morphism style sidebar that logs game history in real-time.

##  Gameplay Mechanics

1.  **Rolling:** Press `Space` to roll the physics-based dice.
2.  **Navigation:**
    * 🐍 **Snake:** Slid down to the tail (Bad luck!).
    * 🪜 **Ladder:** Climb up to the top (Shortcut!).
3.  **The Challenge System:**
    * Landing on a "Scroll Tile" triggers a popup.
    * 📜 **Truth:** Answer the question honestly. Take your time to reflect.
    * ⏳ **Dare (Timed):** A high-stakes challenge! **A countdown timer will start immediately.** Perform the action quickly.

## 🛠️ Installation

### Prerequisites
* Python 3.8 or higher
* pip (Python Package Installer)

### Steps
1.  Clone the repository:
    ```bash
    git clone [https://github.com/detectivecrewze/Snake-Ladders-Truth-or-Dare)
    ```
2.  Navigate to the project directory:
    ```bash
    cd REPO-NAME
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the game:
    ```bash
    python game.py
    ```

## ⚙️ Customization (How to Edit Questions)

This game is designed to be flexible. You can change the "Truth" questions or "Dare" tasks easily.

1.  Locate the file `challenges.json` in the main folder.
2.  Open it with any text editor (Notepad, VS Code, etc.).
3.  Modify the text inside the quotes.
    * *Example:* Change `"Dare: Sing a song!"` to `"Dare: Do 10 pushups!"`
4.  Save the file. The game will automatically load your new rules upon restart.

## 🎮 Controls

| Key | Action |
| :--- | :--- |
| **SPACE** | Roll Dice / Confirm / Next |
| **ESC** | Pause Menu / Back |
| **Mouse** | Navigate UI |
