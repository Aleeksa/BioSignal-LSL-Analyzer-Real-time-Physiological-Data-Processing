# BioSignal LSL Analyzer 🧠💓

This project is a comprehensive system for real-time acquisition, streaming, and analysis of physiological signals (ECG and Respiration) using **Python** and the **Lab Streaming Layer (LSL)** protocol.

## 🚀 Key Features
- **BLE Acquisition:** Direct connection to medical-grade sensors via the Bluetooth Low Energy protocol (using the `Bleak` library).
- **LSL Streaming:** Standardized data transmission over a local network, enabling seamless synchronization with other devices and research tools.
- **Digital Signal Processing (DSP):** Real-time R-peak detection and calculation of Heart Rate (HR) and Heart Rate Variability (HRV) metrics.
- **Signal Simulation:** Built-in synthetic ECG and RSP signal generator for system testing without the need for physical hardware.



## 🛠 Tech Stack
- **Python 3.x**
- **PyLSL:** For high-precision network data streaming.
- **Bleak:** For robust Bluetooth communication with wearable sensors.
- **NumPy & SciPy:** For advanced mathematical signal processing and peak detection algorithms.



## 📂 File Structure
- `srce.py`: Collects heart rate data from Polar sensors (or similar).
- `disanje.py`: Collects and normalizes respiration (RSP) data.
- `klk2_prvi_deo_lsl.py`: The main analyzer script that calculates metrics such as HRV, RMSSD, and Breathing Rate (BR).
- `zadatak.py`: A signal simulator that broadcasts synthetic data to LSL channels.
- `check_lsl.py`: A utility tool to discover and verify active LSL streams on the network.

## ⚙️ How to Run
1. **Install dependencies:**
   ```bash
   pip install bleak pylsl numpy scipy
   python zadatak.py
   python klk2_prvi_deo_lsl.py
