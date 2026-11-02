import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time

# Configure page layout for a professional dashboard look
st.set_page_config(
    page_title="Smart Incubator Dashboard | SIL Simulator",
    page_icon="🥚",
    layout="wide"
)

# ==========================================
# 1. PLANT PHYSICS & CONTROL CLASSES
# ==========================================

class ThermalPlant:
    """
    Models the physical dynamics of the incubator heating chamber.
    Uses a first-order differential equation solved via Euler integration
    to simulate thermal inertia, heat input, and ambient heat dissipation.
    """
    def __init__(self, ambient_temp=25.0, thermal_mass=40.0, heat_loss_coeff=0.08):
        self.temperature = ambient_temp
        self.ambient = ambient_temp
        self.C = thermal_mass          # Thermal capacitance (resistance to rapid temperature changes)
        self.k = heat_loss_coeff       # Ambient heat loss coefficient (Newton's Law of Cooling)
        
    def step(self, heater_power_pct, dt=1.0, disturbance=0.0):
        """Calculates the next temperature state given current heater power and time step (dt)."""
        # Scale heater power percentage to thermal energy gain units
        heat_gain = (heater_power_pct / 100.0) * 2.5
        
        # Calculate natural heat loss to the external environment
        heat_loss = self.k * (self.temperature - self.ambient)
        
        # First-order differential equation: dT/dt = (Gain - Loss + Disturbance) / Capacitance
        dT_dt = (heat_gain - heat_loss + disturbance) / self.C
        self.temperature += dT_dt * dt
        
        return self.temperature


class HumidityPlant:
    """
    Models the physical dynamics of the incubator humidity chamber.
    Balances active humidification against natural moisture decay and ventilation losses.
    """
    def __init__(self, ambient_hum=40.0):
        self.humidity = ambient_hum
        
    def step(self, humidifier_power_pct, dt=1.0, ventilation_open=False):
        """Calculates the next humidity state given humidifier output."""
        target_boost = (humidifier_power_pct / 100.0) * 1.5
        decay = 0.05 * (self.humidity - 40.0)
        vent_loss = 0.8 if ventilation_open else 0.0
        
        # Rate of change of relative humidity (dH/dt)
        dh_dt = target_boost - decay - vent_loss
        self.humidity = np.clip(self.humidity + dh_dt * dt, 20.0, 95.0)
        
        return self.humidity


class PIDController:
    """
    Discrete PID Controller with Proportional, Integral, and Derivative terms,
    augmented with an Integral Anti-Windup clamp to prevent saturation.
    """
    def __init__(self, kp, ki, kd, setpoint=37.5):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.integral = 0.0
        self.previous_error = 0.0
        
    def update(self, current_value, dt=1.0):
        # 1. Compute error magnitude
        error = self.setpoint - current_value
        
        # 2. Proportional term (immediate response to error)
        p_term = self.kp * error
        
        # 3. Integral term with Anti-Windup Clamping (accumulates error over time safely)
        self.integral = np.clip(self.integral + (error * dt), -30.0, 30.0)
        i_term = self.ki * self.integral
        
        # 4. Derivative term (dampens overshoot based on rate of error change)
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        d_term = self.kd * derivative
        
        # Store error history for next cycle
        self.previous_error = error
        
        # 5. Constrain total controller output to actuator limits (0% to 100% duty cycle)
        output = p_term + i_term + d_term
        return np.clip(output, 0.0, 100.0)


# ==========================================
# 2. STREAMLIT USER INTERFACE & STATE SETUP
# ==========================================

st.sidebar.header("System Controls")
mode = st.sidebar.radio("Data Source:", ["Live ESP32 (MQTT)", "Simulation Mode"])

st.sidebar.markdown("---")
st.sidebar.subheader("Poultry Incubation Biology")

# Stage selector reflecting biological requirements of chicken eggs
incubation_stage = st.sidebar.selectbox(
    "Development Stage", 
    ["Days 1–17 (Setting Phase)", "Days 18–21 (Lockdown Phase)"]
)

# Automatically adjust optimal biological setpoints based on stage
if incubation_stage == "Days 1–17 (Setting Phase)":
    TARGET_TEMP = 37.5  # °C - Optimal embryo metabolic temperature
    TARGET_HUM = 52.5   # % - Midpoint of 50-55% RH for controlled water loss through shell
else:
    TARGET_TEMP = 37.5  # °C - Maintained constant
    TARGET_HUM = 67.5   # % - Increased to 65-70% RH to prevent membranes hardening during hatching

st.sidebar.info(f"Target Temp: **{TARGET_TEMP} °C**\n\nTarget Humidity: **{TARGET_HUM}%**")

# Initialize persistent session state variables for simulation continuity
if 'sim_initialized' not in st.session_state:
    st.session_state.plant_temp = ThermalPlant()
    st.session_state.plant_hum = HumidityPlant()
    st.session_state.pid_temp = PIDController(kp=15.0, ki=1.2, kd=2.5, setpoint=TARGET_TEMP)
    st.session_state.pid_hum = PIDController(kp=5.0, ki=0.5, kd=1.0, setpoint=TARGET_HUM)
    st.session_state.history = pd.DataFrame(columns=['Time', 'Temperature', 'Humidity'])
    st.session_state.counter = 0
    st.session_state.sim_initialized = True

# Update controller target setpoints dynamically if user changes the biological stage
st.session_state.pid_temp.setpoint = TARGET_TEMP
st.session_state.pid_hum.setpoint = TARGET_HUM

# Main Dashboard Layout
st.title("🥚 Smart Incubator SIL Control Dashboard")
st.markdown("Software-in-the-Loop (SIL) microclimate simulation demonstrating dual PID loops and biological stage optimization.")

col1, col2 = st.columns(2)

if mode == "Simulation Mode":
    # --- SIMULATION EXECUTION LOOP ---
    current_time = st.session_state.counter
    
    # Compute PID control outputs based on current plant states
    heater_output = st.session_state.pid_temp.update(st.session_state.plant_temp.temperature)
    humidifier_output = st.session_state.pid_hum.update(st.session_state.plant_hum.humidity)
    
    # Advance physical plant simulation steps
    temp = st.session_state.plant_temp.step(heater_output)
    hum = st.session_state.plant_hum.step(humidifier_output)
    
    st.session_state.counter += 1
    
    # Append recent metrics to rolling history dataframe
    new_row = pd.DataFrame({'Time': [current_time], 'Temperature': [temp], 'Humidity': [hum]})
    st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
    if len(st.session_state.history) > 60:
        st.session_state.history = st.session_state.history.iloc[1:]

    # Display real-time telemetry metrics
    with col1:
        st.metric(label="Chamber Temperature", value=f"{temp:.2f} °C", delta=f"Target: {TARGET_TEMP}°C")
    with col2:
        st.metric(label="Chamber Humidity", value=f"{hum:.1f}%", delta=f"Target: {TARGET_HUM}%")

    # Render interactive Plotly trend graph
    fig = px.line(
        st.session_state.history, 
        x='Time', 
        y=['Temperature', 'Humidity'], 
        title="Real-Time Microclimate Closed-Loop Response",
        labels={'value': 'Sensor Measurement', 'Time': 'Simulation Cycle'}
    )
    fig.update_layout(yaxis=dict(range=[20, 80]))
    st.plotly_chart(fig, use_container_width=True)

    # Refresh loop for live dashboard feel
    time.sleep(1.0)
    st.rerun()

else:
    st.warning("Waiting for live telemetry packets from ESP32 MQTT broker...")
    st.info("Ensure your hardware or local bridge is publishing JSON payloads to `/incubator/telemetry`.")