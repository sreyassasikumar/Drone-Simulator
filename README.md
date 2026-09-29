# Drone-Simulator

A 3D browser-based tactical drone simulation built with Three.js. Take command of an aerial drone through dynamic weather, hostile airspace, payload delivery routes, and search-and-rescue operations.

---

## Features

- **Physics & Flight Dynamics:** Realistic inertia, wind drift, motor RPM spin-up, tilt stabilization, altitude damping, and collision damage.
- **Combat & Targeting:** Equipped with onboard cannons, target scanning, lock-on tracking, and gimbal elevation controls.
- **Dynamic Weather & Day/Night Cycle:** Experience changing daylight, coastal storms, heavy rain, wind vectors, and visibility shifts.
- **Interactive HUD:** Live telemetry tracking hull integrity, battery draw, signal strength, GPS status, speed, altitude, and objective markers[cite: 2].
- **Campaign & Upgrades:** Complete 8 distinct sorties to earn credits and upgrade battery capacity, motors, propellers, armor, sensors, camera vision, and weapons[cite: 2].
- **Dual Camera Views:** Switch seamlessly between third-person chase cam and first-person cockpit (FPV) view[cite: 2].

---

## Mission Sorties

1. **First Flight:** Master takeoff, flight stabilization, waypoint navigation, and autolanding[cite: 2].
2. **Delivery:** Pick up cargo from the depot and transport it safely across city airspace[cite: 2].
3. **Pursuit:** Intercept and shadow a moving high-speed target drone within close range[cite: 2].
4. **Search:** Deploy radar pulses over farmlands to locate and secure a hidden beacon[cite: 2].
5. **Airspace:** Engage and neutralize hostile scout drones and heavy gunships[cite: 2].
6. **Storm:** Navigate severe winds, lightning, and rain while dealing with signal degradation[cite: 2].
7. **Damaged:** Take off with pre-existing rotor damage and impaired controls to complete an emergency run[cite: 2].
8. **Extraction:** High-stakes night mission under severe battery constraints and active hostile patrols[cite: 2].

---

## Controls

### Keyboard

| Key | Action |
| :--- | :--- |
| **Enter** | Spin up motors / Take off[cite: 2] |
| **W / S** | Pitch Forward / Backward[cite: 2] |
| **A / D** | Roll / Strafe Left / Right[cite: 2] |
| **Q / E** | Yaw Left / Right[cite: 2] |
| **R / F** | Climb / Descend[cite: 2] |
| **Shift** | Afterburner / Boost thrust[cite: 2] |
| **Space** | Fire Cannons[cite: 2] |
| **Z** | Pulse Radar Scan[cite: 2] |
| **T** | Lock Target[cite: 2] |
| **G** | Reload Weapon[cite: 2] |
| **C** | Toggle Camera (Chase / FPV)[cite: 2] |
| **L** | Engage Autoland (near landing pad)[cite: 2] |
| **Up / Down Arrows** | Adjust Gimbal Pitch[cite: 2] |

### Mouse

- **Click inside canvas:** Capture pointer lock[cite: 2].
- **Mouse Movement:** Steer Yaw (horizontal) and Gimbal Pitch (vertical)[cite: 2].
- **Left Mouse Button (LMB):** Fire Cannons[cite: 2].
- **Right Mouse Button (RMB):** Lock Target[cite: 2].
- **Scroll Wheel:** Climb / Descend[cite: 2].

---

## Requirements & Prerequisites

- Python 3.8+
- Modern web browser (Chrome, Edge, Firefox, or Safari)
- Python packages (install via `pip install -r requirements.txt`):
  - **`urllib3`** (or URI handler utilities)
  - **`pywebview`** (for launching the app in a standalone native desktop GUI window)

---

## Installation & Setup

1. **Make sure thar PYTHON IDLE is installed**
   ```bash
   python -m pip install pywebview
   python -m pip install ursina

2. **Clone the repository:**
   ```bash
   git clone https://github.com/sreyassasikumar/Drone-Simulator.git
   cd Drone-Simulator
   python main.py

