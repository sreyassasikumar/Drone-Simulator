# 🚁 Drone Simulator

<p align="center">
  **A 3D Browser-Based Tactical Drone Simulation**
  <br>
  Take command of an aerial drone and experience realistic flight dynamics, dynamic weather, hostile airspace, tactical missions, and search-and-rescue operations.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Web%20%7C%20Desktop-blue" alt="Platform">
  <img src="https://img.shields.io/badge/3D%20Engine-Three.js-black" alt="Three.js">
  <img src="https://img.shields.io/badge/Language-JavaScript-yellow" alt="JavaScript">
  <img src="https://img.shields.io/badge/Backend-Python-blue" alt="Python">
  <img src="https://img.shields.io/badge/Project-Team%20Project-purple" alt="Team Project">
</p>

---

## 📌 About the Project

**Drone Simulator** is an interactive 3D tactical drone simulation developed using Three.js. It allows players to pilot a drone through different environments while completing challenging missions involving navigation, cargo delivery, target tracking, combat, and emergency extraction.

The simulator combines flight physics, environmental effects, weapon systems, mission progression, and real-time telemetry to create an immersive aerial simulation experience.

---

## ✨ Features

### 🚁 Physics & Flight Dynamics
- Realistic flight inertia and movement.
- Wind drift and environmental effects.
- Motor RPM spin-up simulation.
- Tilt stabilization and altitude damping.
- Collision detection and damage effects.

### 🎯 Combat & Targeting
- Onboard cannon system.
- Target scanning and lock-on tracking.
- Gimbal elevation controls.
- Weapon firing and reloading mechanics.

### 🌦️ Dynamic Weather & Environment
- Changing daylight and night conditions.
- Coastal storms and heavy rainfall.
- Dynamic wind vectors.
- Visibility changes based on weather conditions.

### 📊 Interactive HUD
Live telemetry and flight information, including:
- Hull integrity.
- Battery consumption.
- Signal strength.
- GPS status.
- Flight speed and altitude.
- Mission objectives and target markers.

### 🏆 Campaign & Upgrade System
- Complete 8 different mission sorties.
- Earn credits by completing missions.
- Upgrade drone components, including:
  - Battery capacity.
  - Motors and propellers.
  - Armor.
  - Sensors.
  - Camera vision.
  - Weapons.

### 📷 Dual Camera Views
- **Third-Person Chase Camera:** Observe the drone from behind.
- **First-Person View (FPV):** Experience the simulation from the drone's cockpit perspective.

---

## 🎮 Mission Sorties

The simulator includes eight different missions, each introducing unique objectives and challenges.

| No. | Mission | Objective |
|---|---|---|
| 1 | First Flight | Learn takeoff, flight stabilization, waypoint navigation, and autolanding. |
| 2 | Delivery | Collect cargo from a depot and transport it safely across city airspace. |
| 3 | Pursuit | Intercept and follow a high-speed moving target drone. |
| 4 | Search | Use radar pulses to locate a hidden beacon over farmland. |
| 5 | Airspace | Engage hostile scout drones and heavy gunships. |
| 6 | Storm | Navigate severe winds, lightning, rain, and signal degradation. |
| 7 | Damaged | Complete an emergency mission with pre-existing rotor damage and impaired controls. |
| 8 | Extraction | Complete a high-risk night mission with limited battery capacity and hostile patrols. |

---

## 🕹️ Controls

### ⌨️ Keyboard Controls

| Key | Action |
|:---:|---|
| `Enter` | Spin up motors / Take off |
| `W / S` | Pitch forward / backward |
| `A / D` | Roll / Strafe left / right |
| `Q / E` | Yaw left / right |
| `R / F` | Climb / Descend |
| `Shift` | Afterburner / Boost thrust |
| `Space` | Fire cannons |
| `Z` | Pulse radar scan |
| `T` | Lock target |
| `G` | Reload weapon |
| `C` | Toggle camera (Chase / FPV) |
| `L` | Engage autoland near landing pad |
| `Up / Down Arrows` | Adjust gimbal pitch |

### 🖱️ Mouse Controls

| Mouse Action | Function |
|---|---|
| Click inside canvas | Capture pointer lock |
| Mouse Movement | Control yaw and gimbal pitch |
| Left Mouse Button | Fire cannons |
| Right Mouse Button | Lock target |
| Scroll Wheel | Climb / Descend |

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| HTML5 | Web page structure |
| CSS3 | Interface styling |
| JavaScript | Simulation logic and interactions |
| Three.js | 3D rendering and environment |
| Python | Desktop application launcher |
| pywebview | Native desktop window integration |
| Git & GitHub | Version control and source management |

---

## 💻 Requirements & Prerequisites

Before running the project, make sure you have:

- Python 3.8 or later.
- Git installed on your system.
- A modern browser such as Google Chrome, Microsoft Edge, Firefox, or Safari.
- A compatible graphics processor for smooth 3D rendering.

### Python Dependencies

Install the required packages using:

```bash
python -m pip install -r requirements.txt
```

The setup also mentions:
- `pywebview` – for launching the application in a standalone desktop window.
- `urllib3` – HTTP utility library, if required by the application.
- `ursina` – install only if the Python source code uses the Ursina engine.

---

## 🚀 Installation & Setup

### 1. Install Python

Download and install Python from:

https://www.python.org/downloads/

Verify the installation:

```bash
python --version
```

### 2. Install Git

On Windows, open Command Prompt or PowerShell and run:

```bash
winget install --id Git.Git -e --source winget
```

Verify Git:

```bash
git --version
```

### 3. Clone the Repository

```bash
git clone https://github.com/sreyassasikumar/Drone-Simulator.git
```

Navigate into the project directory:

```bash
cd Drone-Simulator
```

### 4. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

If `pywebview` is not included in `requirements.txt`, install it separately:

```bash
py -m pip install pywebview
```

### 5. Prepare the Application

If the project requires the Windows build script, execute it:

```bash
build.bat
```

Check the asset directory:

```bash
dir asset
```

If the generated HTML file is located at `asset/DRONE__OPS.html`, copy it to the project root:

```bash
copy asset\DRONE__OPS.html .
```

### 6. Run the Simulator

Start the application:

```bash
python main.py
```

Follow the on-screen instructions to begin your drone simulation.

> **Note:** The commands above assume a Windows environment. The build script and asset-copy step are project-specific; follow the repository's actual build process if those files or steps differ.

---

## 📂 Project Structure

```text
Drone-Simulator/
│
├── asset/
│   └── DRONE__OPS.html
│
├── main.py
├── requirements.txt
├── build.bat
│
└── README.md
```

*The structure above is a simplified overview based on the setup instructions. Update it if the repository contains additional source files, folders, or assets.*

---

## 🎯 Learning Outcomes

Working with this project provides practical exposure to:

- 3D graphics and browser-based simulation using Three.js.
- JavaScript-based interactive application development.
- Basic flight physics and movement simulation.
- Real-time input handling and HUD development.
- Environmental effects and dynamic weather systems.
- Mission-based gameplay and progression systems.
- Python-based desktop application integration.
- Project setup, dependency management, and Git version control.
- Team collaboration and software development practices.

---

## 🔮 Future Enhancements

- Multiplayer drone simulation.
- More realistic aerodynamic and flight physics.
- Additional maps and mission environments.
- Advanced AI-controlled enemy drones.
- Improved collision and damage simulation.
- Drone camera recording and replay functionality.
- VR-based first-person drone simulation.
- Expanded customization and upgrade options.

---

## 👥 Team Members

1. **A Sreeram**
2. **Sreyas Sasikumar**
3. **Neeraj J Krishna**

---

## 🎓 Academic Details

- **Institution:** Muthoot Institute of Technology and Science (MITS)
- **Department:** Artificial Intelligence and Data Science
- **Academic Batch:** 2025–2029
- **Semester:** 3
- **Project Type:** Competitive Team Project

---

<p align="center">
  **Explore. Navigate. Survive. Complete the Mission.** 🚁
  <br>
  <i>Built to bring tactical drone simulation to the browser.</i>
</p>
