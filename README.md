# 🧩Semiconductor Measurement System (Python)
A modular automation framework for Yoko GS200 and DMM-based device characterization (Diode & Transistor). 
이 프로젝트는 반도체 소자의 I-V 및 V-V 특성을 측정하기 위한 전압 스윕(Sweep), 실시간 모니터링, 그리고 데이터 로깅을 자동화한다.

## 🎥 Demo & Visuals
<p align="center">
  <img src="https://github.com/user-attachments/assets/8d74dabd-9edf-4daf-a711-c11e4c1c1959" width="400"/>
  <img src="https://github.com/user-attachments/assets/f93f1993-ccfa-435d-a001-1cda1971ecb1" width="400"/>
</p>


##📁 Folder Structure
Si_MOSFET_measurement_app/
├── archive/              # Deprecated scripts (e.g., main3.py)
│
├── configs/              # Device and experiment configuration
│   └── device_config.py  # GPIB addresses, voltage ranges, save paths
│
├── experiments/          # Automatically saved results
│   ├── data/             # Raw measurement data (.txt, .csv)
│   └── figures/          # Generated plots (.png)
│
├── src/                  # Core source code
│   ├── main.py           # Entry point (Main UI execution)
│   │
│   ├── core/             # Hardware control & measurement logic
│   │   ├── driver.py     # PyVISA-based instrument classes
│   │   ├── sweep.py      # 1D/2D Sweep algorithms & Threading
│   │   └── monitor.py    # Time-based DMM reading
│   │
│   ├── gui/              # User Interface (Tkinter)
│   │   ├── main_ui.py    # Primary control window
│   │   └── sub_ui.py     # Pop-up windows for specific tasks
│   │
│   └── utils/            # Common utilities
│       ├── logger.py     # Data formatting & file I/O
│       └── plotter.py    # Real-time Matplotlib visualization
│
└── README.md

## 🚀 How to Run
1. Open Visual Studio Code and navigate to:
	```
	root/Si_MOSFET_measurement_app
	```
2. Run:
	```
	cd src
	mian
	```
3.The system will:
	- Initialize GPIB connections for GS200 (#1, #2) and DMM.
	- Provide a GUI for setting voltage, range, and sweep parameters.

## ⚙️Configuration
모든 장비 설정 및 경로 변수는 configs/device_config.py에서 관리된다.

Example:

```
cfg.devices.gs200_1 = "GPIB0::1::INSTR"
cfg.devices.gs200_2 = "GPIB0::11::INSTR"
cfg.devices.dmm = "GPIB0::22::INSTR"
```

## 📊 Output
측정 결과는 experiments/ 폴더 내에 타임스탬프와 함께 자동으로 분류되어 저장된다.

```
experiments/
├── data/    → [Type]_results_[YYYYMMDD_HHMMSS].txt
└── figures/ → [Type]_plot_[YYYYMMDD_HHMMSS].png
```

## 🧱 Components Overview
Component | Description
Driver (core) | GS200 및 DMM의 VISA 통신 추상화 (Output ON/OFF, Local Mode 등)
Sweep (core) | 별도 스레드에서 실행되는 1D/2D 전압 스윕 알고리즘 (Stop 기능 지원)
Sub UI (gui) | PLC 설정, 전압 범위 선택, 측정 파라미터 입력을 위한 팝업창"
Plotter (utils) | 측정 중 실시간 피드백을 제공하는 동적 그래프 생성


## ⚠️ Safety Notes
	- Emergency Stop: 측정 중 'STOP' 버튼을 누르면 back_zero 함수가 즉시 실행되어 전압을 안전하게 0.01V 단위로 하강시킴.
	- Auto Reset: GUI 창을 닫을 경우 모든 Output은 OFF로 전환되며 기기는 Local Mode로 복구됨.

