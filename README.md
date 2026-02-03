# BioSignal LSL Analyzer 🧠💓

Ovaj projekat predstavlja sistem za akviziciju, strimovanje i analizu fizioloških signala (EKG i respiracija) u realnom vremenu koristeći **Python** i **Lab Streaming Layer (LSL)** protokol.

## 🚀 Glavne Funkcije
- **BLE Akvizicija:** Direktno povezivanje sa medicinskim senzorima putem Bluetooth Low Energy protokola (`Bleak` biblioteka).
- **LSL Strimovanje:** Standardizovano slanje podataka kroz lokalnu mrežu, omogućavajući sinhronizaciju sa drugim uređajima.
- **Digitalna obrada signala (DSP):** Detekcija R-piksela (otkucaja) i izračunavanje HR (Heart Rate) i HRV (Heart Rate Variability) metrika u realnom vremenu.
- **Simulacija signala:** Ugrađen generator sintetičkih EKG i RSP signala za testiranje sistema bez hardvera.



## 🛠 Tehnologije
- **Python 3.x**
- **PyLSL:** Za mrežni striming podataka.
- **Bleak:** Za Bluetooth komunikaciju sa senzorima.
- **NumPy & SciPy:** Za matematičku obradu signala i detekciju peak-ova.

## 📂 Struktura fajlova
- `srce.py`: Prikuplja podatke o pulsu sa Polar senzora.
- `disanje.py`: Prikuplja i normalizuje podatke o disanju.
- `klk2_prvi_deo_lsl.py`: Glavni analizator koji računa metrike (HRV, RMSSD, BR).
- `zadatak.py`: Simulator signala koji emituje podatke na LSL kanale.
- `check_lsl.py`: Pomoćni alat za proveru aktivnih strimova na mreži.

## ⚙️ Kako pokrenuti
1. Instalirajte potrebne biblioteke:
   ```bash
   pip install bleak pylsl numpy
