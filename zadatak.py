import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet

# -----------------------------
# CONFIG
# -----------------------------
FS = 50                 # Hz for raw signals
DT = 1.0 / FS

MET_HZ = 10             # Hz for metrics stream
MET_DT = 1.0 / MET_HZ

HR_TARGET = 75.0        # bpm
BR_TARGET = 12.0        # breaths/min

# small slow modulation so numbers are NOT constant
HR_WOBBLE = 6.0         # bpm peak-to-peak/2
BR_WOBBLE = 2.0         # rpm peak-to-peak/2

# -----------------------------
# LSL OUTLETS
# -----------------------------
out_ekg = StreamOutlet(StreamInfo("EKG", "ECG", 1, FS, "float32", "ekg_nk"))
out_rsp = StreamOutlet(StreamInfo("RSP", "RESP", 1, FS, "float32", "rsp_nk"))

# 4-channel metrics: [HR, HRV, BR, BRV]
out_met = StreamOutlet(StreamInfo("metrike", "METRICS", 4, MET_HZ, "float32", "met_nk"))

print("LSL ON: metrike=[HR,HRV,BR,BRV], plus EKG/RSP")

# -----------------------------
# STATE
# -----------------------------
t0 = time.perf_counter()
next_met = t0

# phases for continuous signals (never reset)
phase_ecg = 0.0
phase_rsp = 0.0

# -----------------------------
# LOOP
# -----------------------------
try:
    while True:
        now = time.perf_counter()
        t = now - t0

        # ---- Make targets slowly change so vvvv clearly sees motion ----
        # HR and BR vary slowly over time
        hr_now = HR_TARGET + HR_WOBBLE * np.sin(2 * np.pi * 0.07 * t)  # very slow
        br_now = BR_TARGET + BR_WOBBLE * np.sin(2 * np.pi * 0.05 * t)  # very slow

        # ---- Raw signals (simple, stable) ----
        # ECG-ish: faster sinus + small noise
        ecg_freq = hr_now / 60.0  # Hz
        ecg = 0.8 * np.sin(2 * np.pi * ecg_freq * phase_ecg) + 0.05 * np.random.randn()

        # Resp: slow sinus + small noise
        rsp_freq = br_now / 60.0  # Hz
        rsp = 0.6 * np.sin(2 * np.pi * rsp_freq * phase_rsp) + 0.02 * np.random.randn()

        phase_ecg += DT
        phase_rsp += DT

        out_ekg.push_sample([float(ecg)])
        out_rsp.push_sample([float(rsp)])

        # ---- Metrics at 10 Hz ----
        if now >= next_met:
            next_met += MET_DT

            # fake variability values (so not zero)
            # HRV ~ 15..45 ms
            hrv = 30.0 + 15.0 * np.sin(2 * np.pi * 0.09 * t + 1.2)

            # BRV ~ 0.5..2.5
            brv = 1.5 + 1.0 * np.sin(2 * np.pi * 0.08 * t + 0.7)

            out_met.push_sample([float(hr_now), float(hrv), float(br_now), float(brv)])

        time.sleep(DT)

except KeyboardInterrupt:
    print("Stopped.")