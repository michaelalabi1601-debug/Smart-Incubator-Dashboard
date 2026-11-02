# 🥚 Smart Incubator Dashboard & SIL Simulator

A Software-in-the-Loop (SIL) microclimate control and IoT telemetry dashboard designed for precision poultry incubation. This project demonstrates rigorous closed-loop control system design, first-order plant modeling, and biological stage-switching logic implemented in Python and Streamlit.

---

## 🚀 Key Engineering Features

1. **Dual Closed-Loop PID Control with Anti-Windup**
   * Implements independent discrete Proportional-Integral-Derivative (PID) controllers for both thermal and relative humidity regulation.
   * Features **integral anti-windup clamping** (`np.clip`) to prevent controller saturation and system instability during large environmental disturbances or startup phases.

2. **First-Order Plant Physics Simulation**
   * **Thermal Plant:** Models chamber temperature dynamics using Euler integration on a first-order differential equation, incorporating thermal capacitance ($C$) and Newton's Law of Cooling for ambient heat dissipation.
   * **Humidity Plant:** Balances active humidification against natural moisture decay and ventilation losses.

3. **Biological Stage Optimization (Poultry Standards)**
   * Automatically adjusts control setpoints to match embryonic development stages:
     * **Setting Phase (Days 1–17):** Maintains $37.5^\circ\text{C}$ and $52.5\%$ RH (midpoint of 50–55%) to ensure proper water weight loss through the eggshell.
     * **Lockdown Phase (Days 18–21):** Shifts humidity up to $67.5\%$ RH (midpoint of 65–70%) to prevent inner membranes from hardening right before hatching.

4. **Interactive HMI & Telemetry**
   * Built with **Streamlit** and **Plotly** for dynamic, real-time closed-loop response visualization and live ESP32 MQTT telemetry ingestion.

---

## 📐 Mathematical Formulation

### 1. Thermal Plant Physics
The rate of internal temperature change ($\frac{dT}{dt}$) is governed by the energy balance equation:

$$\frac{dT}{dt} = \frac{Q_{\text{gain}} - Q_{\text{loss}} + Q_{\text{disturbance}}}{C}$$

Where:
* $Q_{\text{gain}}$ is the scaled heater output power.
* $Q_{\text{loss}} = k(T_{\text{chamber}} - T_{\text{ambient}})$ represents heat dissipation.
* $C$ is the thermal capacitance (inertial resistance to temperature change).

### 2. Discrete PID Control Law
The control output $u(t)$ combines error feedback across three terms:

$$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

With active clamping enforced on the integral accumulator to eliminate windup overshoot.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** Streamlit
* **Data Processing & Math:** NumPy, Pandas
* **Visualization:** Plotly Express
* **Hardware Target (Optional):** ESP32 Microcontroller via MQTT

---

## 📦 Installation & Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/michaelalabi1601-debug/Smart-Incubator-Dashboard.git](https://github.com/michaelalabi1601-debug/Smart-Incubator-Dashboard.git)
   cd Smart-Incubator-Dashboard
   ```
2. Run the SIL Simulator Dashboard:
   ```Bash
    streamlit run app.py
    ```
    ## 📂 Repository Structure
Smart-Incubator-Dashboard/
│
├── ```app.py```                # Main Streamlit dashboard & SIL simulation loop
├── ```requirements.txt```      # Python package dependencies
├── ```README.md```             # Project documentation
└── ```scripts/```              # Modular simulation and controller classes
