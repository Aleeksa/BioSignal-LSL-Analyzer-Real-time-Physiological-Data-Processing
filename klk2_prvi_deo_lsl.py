import time
import math
import random
from collections import deque

import numpy as np
from pylsl import StreamInfo, StreamOutlet


FS = 100.0           
DT = 1.0 / FS

BASE_HR = 70.0       
BASE_BR = 12.0       

WINDOW_SEC = 20.0
WIN = int(WINDOW_SEC * FS)

METRICS_PERIOD = 1.0


def detect_peaks_simple(x: np.ndarray, fs: float, min_distance_sec: float, threshold: float) -> np.ndarray:
   
    if x.size < 3:
        return np.array([], dtype=int)

    min_dist = max(1, int(min_distance_sec * fs))
    peaks = []
    last = -10**9

    for i in range(1, x.size - 1):
        if x[i] > threshold and x[i - 1] < x[i] >= x[i + 1]:
            if i - last >= min_dist:
                peaks.append(i)
                last = i
            else:
                
                if peaks and x[i] > x[peaks[-1]]:
                    peaks[-1] = i
                    last = i
    return np.array(peaks, dtype=int)


def rmssd_ms(intervals_sec: np.ndarray) -> float:
    if intervals_sec.size < 3:
        return 0.0
    diff = np.diff(intervals_sec)
    return float(np.sqrt(np.mean(diff * diff)) * 1000.0)

def ecg_template(t: float) -> float:
   
    waves = [
        (0.12, 0.08, 0.015),   # P
        (-0.15, 0.16, 0.010),  # Q
        (1.00, 0.18, 0.012),   # R
        (-0.25, 0.20, 0.010),  # S
        (0.35, 0.32, 0.030),   # T
    ]
    y = 0.0
    for amp, mu, sig in waves:
        y += amp * math.exp(-0.5 * ((t - mu) / sig) ** 2)
    return y

def main():

    info_ecg = StreamInfo("EKG_raw", "physio", 1, FS, "float32", "ekg_raw_001")
    info_rsp = StreamInfo("RSP_raw", "physio", 1, FS, "float32", "rsp_raw_001")
    info_met = StreamInfo("physio_metrics", "metrics", 4, 0.0, "float32", "metrics_001")

    outlet_ecg = StreamOutlet(info_ecg)
    outlet_rsp = StreamOutlet(info_rsp)
    outlet_met = StreamOutlet(info_met)

    buf_ecg = deque(maxlen=WIN)
    buf_rsp = deque(maxlen=WIN)

    t0 = time.perf_counter()
    next_metrics_time = 0.0

    hr = BASE_HR
    br = BASE_BR
    phase_rsp = 0.0

    beat_times = deque()

    next_beat_time = 0.0

    wander_phase = 0.0

    print("LSL streams started: EKG_raw, RSP_raw, physio_metrics")
    print("Stop: Ctrl+C")

    while True:
        now = time.perf_counter() - t0

        hr += random.uniform(-0.15, 0.15)     
        hr = max(45.0, min(120.0, hr))
        hr += 0.15 * math.sin(2 * math.pi * 0.03 * now)  

        br += random.uniform(-0.03, 0.03)
        br = max(6.0, min(25.0, br))
        br += 0.03 * math.sin(2 * math.pi * 0.02 * now)

        ibi = 60.0 / hr  
        if now >= next_beat_time:
            beat_times.append(now)
            next_beat_time = now + ibi

        while beat_times and (now - beat_times[0]) > 1.0:
            beat_times.popleft()

        ecg = 0.0
        for bt in beat_times:
            ecg += ecg_template(now - bt)

        wander_phase += 2 * math.pi * 0.3 * DT   
        wander = 0.05 * math.sin(wander_phase)
        ecg = ecg + wander + random.uniform(-0.03, 0.03)

        rsp_freq = br / 60.0
        phase_rsp += 2 * math.pi * rsp_freq * DT
        rsp = 0.9 * math.sin(phase_rsp) + 0.1 * math.sin(2 * phase_rsp) + random.uniform(-0.03, 0.03)


        outlet_ecg.push_sample([float(ecg)])
        outlet_rsp.push_sample([float(rsp)])

        buf_ecg.append(float(ecg))
        buf_rsp.append(float(rsp))

        if now >= next_metrics_time:
            next_metrics_time = now + METRICS_PERIOD

            ecg_arr = np.asarray(buf_ecg, dtype=np.float32)
            rsp_arr = np.asarray(buf_rsp, dtype=np.float32)

            thr_ecg = float(ecg_arr.mean() + 1.2 * ecg_arr.std()) if ecg_arr.size else 0.0
            r_peaks = detect_peaks_simple(ecg_arr, FS, min_distance_sec=0.35, threshold=thr_ecg)

            hr_bpm = 0.0
            hrv = 0.0
            if r_peaks.size >= 3:
                rr = np.diff(r_peaks) / FS  
                
                rr = rr[(rr > 0.3) & (rr < 2.0)]
                if rr.size >= 2:
                    hr_bpm = float(60.0 / rr.mean())
                    hrv = rmssd_ms(rr)

            
            thr_rsp = float(rsp_arr.mean() + 0.3 * rsp_arr.std()) if rsp_arr.size else 0.0
            b_peaks = detect_peaks_simple(rsp_arr, FS, min_distance_sec=1.0, threshold=thr_rsp)

            br_bpm = 0.0
            brv = 0.0
            if b_peaks.size >= 3:
                bb = np.diff(b_peaks) / FS  
                bb = bb[(bb > 1.0) & (bb < 10.0)]
                if bb.size >= 2:
                    br_bpm = float(60.0 / bb.mean())
                    brv = rmssd_ms(bb)

            outlet_met.push_sample([hr_bpm, hrv, br_bpm, brv])

            print(f"HR={hr_bpm:6.1f} bpm | HRV={hrv:6.1f} ms | BR={br_bpm:5.1f} /min | BRV={brv:6.1f} ms")

        time.sleep(DT)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
