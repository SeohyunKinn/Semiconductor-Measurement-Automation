import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class PLCWindow:
    """DMM의 PLC를 설정하는 창 (main3.py의 open_plc_ui 로직 이식)"""
    def __init__(self, parent, dmm_device):
        self.window = tk.Toplevel(parent)
        self.window.title("DMM:Set PLC")
        self.window.geometry("400x600")
        self.dmm = dmm_device

        tk.Label(self.window, text="DMM:Set PLC\n \nSelect NPLC:", font=("Arial", 16, "bold")).pack()
        ranges = [0.02, 0.06, 0.2, 1, 10, 100]

        for r in ranges:
            tk.Button(self.window, text=f"{r} V", command=lambda val=r: self.set_plc(val), font=("Arial", 16)).pack()

    def set_plc(self, value):
        self.dmm.set_plc(value)
        print(f"PLC set to {value}")

class RangeWindow:
    """GS200의 전압 범위를 설정하는 창 (main3.py의 open_voltage_range_ui 로직 이식)"""
    def __init__(self, parent, v1, v2):
        self.window = tk.Toplevel(parent)
        self.window.title("Yoko:Voltage Range")
        self.window.geometry("400x600")
        self.v1 = v1
        self.v2 = v2

        tk.Label(self.window, text="Yoko:Voltage Range\n \n Select Device", font=("Arial", 16, "bold")).pack()
        self.device_var = tk.StringVar(value="GS200-#1")
        tk.Radiobutton(self.window, text="GS200-#1", variable=self.device_var, value="GS200-#1", font=("Arial", 16)).pack()
        tk.Radiobutton(self.window, text="GS200-#2", variable=self.device_var, value="GS200-#2", font=("Arial", 16)).pack()

        tk.Label(self.window, text="Select Range (V):", font=("Arial", 16, "bold")).pack()
        ranges = [0.01, 0.1, 1, 10, 30]

        for r in ranges:
            tk.Button(self.window, text=f"{r} V", command=lambda val=r: self.set_range(val), font=("Arial", 16)).pack()

    def set_range(self, value):
        device_name = self.device_var.get()
        target = self.v1 if device_name == "GS200-#1" else self.v2
        target.set_range(value)
        print(f"{device_name} Voltage range set to {value}V")

# 개별 기기 Local 모드 선택 창
class LocalModeWindow:
    def __init__(self, parent, v1, v2, dmm):
        self.window = tk.Toplevel(parent)
        self.window.title("Local Mode Settings")
        self.window.geometry("300x400")
        
        self.v1 = v1
        self.v2 = v2
        self.dmm = dmm

        tk.Label(self.window, text="Select Device to Local", font=("Arial", 14, "bold")).pack(pady=15)

        # 각 장비별 버튼 생성
        tk.Button(self.window, text="GS200-#1 (V1)", width=20, font=("Arial", 12),
                  command=lambda: self.set_device_local(self.v1, "V1")).pack(pady=5)
        
        tk.Button(self.window, text="GS200-#2 (V2)", width=20, font=("Arial", 12),
                  command=lambda: self.set_device_local(self.v2, "V2")).pack(pady=5)
        
        tk.Button(self.window, text="DMM", width=20, font=("Arial", 12),
                  command=lambda: self.set_device_local(self.dmm, "DMM")).pack(pady=5)
        
        tk.Label(self.window, text="--- OR ---", font=("Arial", 10)).pack(pady=5)

        tk.Button(self.window, text="Set ALL Local", width=20, bg="lightblue", font=("Arial", 12),
                  command=self.set_all_local).pack(pady=5)

    def set_device_local(self, device, name):
        try:
            device.set_local()
            print(f"[System] {name} set to Local Mode.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set {name} local: {e}")

    def set_all_local(self):
        try:
            self.v1.set_local()
            self.v2.set_local()
            self.dmm.set_local()
            print("[System] All devices set to Local Mode.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set all local: {e}")

class OutputControlWindow:
    """V1, V2의 Output을 개별적으로 ON/OFF 하는 창"""
    def __init__(self, parent, v1, v2):
        self.window = tk.Toplevel(parent)
        self.window.title("Output Control")
        self.window.geometry("300x300")
        
        tk.Label(self.window, text="Yoko Output Control", font=("Arial", 14, "bold")).pack(pady=15)

        # V1 Control
        frame_v1 = tk.Frame(self.window)
        frame_v1.pack(pady=10)
        tk.Label(frame_v1, text="GS200 #1 (V1): ", font=("Arial", 12)).pack(side="left")
        tk.Button(frame_v1, text="ON", bg="green", fg="white", width=5, 
                  command=lambda: self.toggle_output(v1, "ON", "V1")).pack(side="left", padx=5)
        tk.Button(frame_v1, text="OFF", bg="red", fg="white", width=5, 
                  command=lambda: self.toggle_output(v1, "OFF", "V1")).pack(side="left", padx=5)

        # V2 Control
        frame_v2 = tk.Frame(self.window)
        frame_v2.pack(pady=10)
        tk.Label(frame_v2, text="GS200 #2 (V2): ", font=("Arial", 12)).pack(side="left")
        tk.Button(frame_v2, text="ON", bg="green", fg="white", width=5, 
                  command=lambda: self.toggle_output(v2, "ON", "V2")).pack(side="left", padx=5)
        tk.Button(frame_v2, text="OFF", bg="red", fg="white", width=5, 
                  command=lambda: self.toggle_output(v2, "OFF", "V2")).pack(side="left", padx=5)

    def toggle_output(self, device, state, name):
        try:
            device.output_control(state)
            print(f"[System] {name} Output turned {state}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set {name} output: {e}")

# 1D Sweep UI
class SweepInputWindow:
    """1D Sweep 설정을 위한 창 (main3.py의 open_current_sweep_ui 로직 이식)"""
    def __init__(self, parent, v1, v2, dmm, sweep_func):
        self.window = tk.Toplevel(parent)
        self.window.title("Current(1D: V)")
        self.window.geometry("400x600")
        self.v1 = v1
        self.v2 = v2
        self.dmm = dmm
        self.sweep_func = sweep_func

        tk.Label(self.window, text="Current(1D: V)\n \n Select Device:", font=("Arial", 16, "bold")).pack()
        self.device_var = tk.StringVar(value="GS200-#1")
        tk.Radiobutton(self.window, text="GS200-#1", variable=self.device_var, value="GS200-#1", font=("Arial", 14)).pack()
        tk.Radiobutton(self.window, text="GS200-#2", variable=self.device_var, value="GS200-#2", font=("Arial", 14)).pack()

        tk.Label(self.window, text="Start Voltage (V):", font=("Arial", 16)).pack()
        self.min_v_entry = tk.Entry(self.window); self.min_v_entry.pack()
        
        tk.Label(self.window, text="Stop Voltage (V):", font=("Arial", 16)).pack()
        self.max_v_entry = tk.Entry(self.window); self.max_v_entry.pack()
        
        tk.Label(self.window, text="# of points:", font=("Arial", 16)).pack()
        self.steps_entry = tk.Entry(self.window); self.steps_entry.pack()
        
        tk.Label(self.window, text="Delay (s):", font=("Arial", 16)).pack()
        self.delay_entry = tk.Entry(self.window); self.delay_entry.pack()

        tk.Label(self.window, text="Sensitivity(A/V): (Ex: 1E-5)", font=("Arial", 16)).pack()
        self.sensitivity_entry = tk.Entry(self.window); self.sensitivity_entry.pack()

        tk.Label(self.window, text="Ramping key [1:ramping, 2:maintain]:", font=("Arial", 16)).pack()
        self.ramping_entry = tk.Entry(self.window); self.ramping_entry.pack()

        tk.Button(self.window, text="Start Sweep", font=("Arial", 16), bg="blue", fg="white", command=self.start_sweep).pack(pady=10)

    def start_sweep(self):
        target_dev = self.v1 if self.device_var.get() == "GS200-#1" else self.v2
        
        self.sweep_func(
            device=target_dev,
            dmm=self.dmm,
            min_v=float(self.min_v_entry.get()),
            max_v=float(self.max_v_entry.get()),
            steps=int(self.steps_entry.get()),
            delay=float(self.delay_entry.get()),
            sensitivity=float(self.sensitivity_entry.get()),
            ramping_key=int(self.ramping_entry.get())
        )

# 2D Sweep UI
class MosfetMeasurementWindow:
    """
    MOSFET Measurement Interface (V vs I)
    - Case 1 (Output Char.): Sweep V1 (Drain), Step V2 (Gate) -> Standard 2D Sweep
    - Case 2 (Transfer Char.): Sweep V2 (Gate), Fixed Bias V1 (Drain) -> 2D Sweep with 1 step for V1
    """
    def __init__(self, parent, v1, v2, dmm, sweep_func):
        self.window = tk.Toplevel(parent)
        self.window.title("MOSFET Measurement (V vs I)")
        self.window.geometry("450x650")
        
        self.v1 = v1
        self.v2 = v2
        self.dmm = dmm
        self.sweep_func = sweep_func 

        # --- 1. Mode Selection (Radio Buttons) ---
        tk.Label(self.window, text="Select Measurement Mode:", font=("Arial", 14, "bold")).pack(pady=10)
        self.mode_var = tk.IntVar(value=1)
        
        # Case 1: Output Characteristics (Standard V1 sweep with V2 steps)
        tk.Radiobutton(self.window, text="Case 1: Output Char.\n(X-Axis: V1, Step: V2)", 
                       variable=self.mode_var, value=1, font=("Arial", 12),
                       command=self.update_ui_fields).pack(anchor="w", padx=20)
        
        # Case 2: Transfer Characteristics (V2 sweep with fixed V1 bias)
        tk.Radiobutton(self.window, text="Case 2: Transfer Char.\n(X-Axis: V2, Bias: V1)", 
                       variable=self.mode_var, value=2, font=("Arial", 12),
                       command=self.update_ui_fields).pack(anchor="w", padx=20)

        tk.Frame(self.window, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)

        # --- 2. Dynamic Input Fields Frame ---
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(pady=5)
        
        self.entries = {} # Store entry widgets here
        self.update_ui_fields() # Initialize fields based on default mode

        # --- 3. Common Settings ---
        tk.Frame(self.window, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)
        self.common_entries = {}
        for label, default in [("Delay (s)", "0.1"), ("Sensitivity (A/V)", "1e-5")]:
            f = tk.Frame(self.window)
            f.pack(pady=2)
            tk.Label(f, text=label, width=20, anchor="e").pack(side="left")
            e = tk.Entry(f, width=10)
            e.insert(0, default)
            e.pack(side="left")
            self.common_entries[label] = e

        # --- 4. Start Button ---
        tk.Button(self.window, text="START MEASUREMENT", font=("Arial", 14, "bold"), bg="blue", fg="white",
                  command=self.start_measurement).pack(pady=20)

    def update_ui_fields(self):
        """Updates input fields based on the selected mode."""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.entries = {}

        mode = self.mode_var.get()
        
        if mode == 1: # Case 1: Output Characteristics
            tk.Label(self.input_frame, text="[X-Axis: V1 (Drain)]", fg="blue", font=("Arial", 10, "bold")).pack()
            self.add_entry("V1 Start (V)", "0")
            self.add_entry("V1 Stop (V)", "1")
            self.add_entry("V1 Points", "11")
            
            tk.Label(self.input_frame, text="[Step: V2 (Gate)]", fg="green", font=("Arial", 10, "bold")).pack(pady=(10,0))
            self.add_entry("V2 Start (V)", "0")
            self.add_entry("V2 Stop (V)", "1")
            self.add_entry("V2 Points", "3") # Multiple steps for V2
            
        else: # Case 2: Transfer Characteristics
            tk.Label(self.input_frame, text="[X-Axis: V2 (Gate)]", fg="green", font=("Arial", 10, "bold")).pack()
            self.add_entry("V2 Start (V)", "0")
            self.add_entry("V2 Stop (V)", "1")
            self.add_entry("V2 Points", "11")
            
            tk.Label(self.input_frame, text="[Bias: V1 (Drain)]", fg="blue", font=("Arial", 10, "bold")).pack(pady=(10,0))
            # Only one voltage needed for V1 since it is a fixed bias
            self.add_entry("V1 Voltage (V)", "0.1") 

    def add_entry(self, label_text, default_val):
        f = tk.Frame(self.input_frame)
        f.pack(pady=2)
        tk.Label(f, text=label_text, width=20, anchor="e").pack(side="left")
        e = tk.Entry(f, width=10)
        e.insert(0, default_val)
        e.pack(side="left")
        self.entries[label_text] = e

    def start_measurement(self):
        try:
            delay = float(self.common_entries["Delay (s)"].get())
            sens = float(self.common_entries["Sensitivity (A/V)"].get())
            mode = self.mode_var.get()

            if mode == 1: # Case 1: Output Char.
                v1_p = (float(self.entries["V1 Start (V)"].get()), 
                        float(self.entries["V1 Stop (V)"].get()), 
                        int(self.entries["V1 Points"].get()))
                v2_p = (float(self.entries["V2 Start (V)"].get()), 
                        float(self.entries["V2 Stop (V)"].get()), 
                        int(self.entries["V2 Points"].get()))
                
                self.sweep_func(
                    v1=self.v1, v2=self.v2, dmm=self.dmm,
                    v1_params=v1_p, v2_params=v2_p,
                    delay=delay, sensitivity=sens,
                    x_axis_name="V1"  # [추가] 명시적으로 V1임을 전달
                )

            else: # Case 2: Transfer Char.
                bias_v = float(self.entries["V1 Voltage (V)"].get())
                v1_fixed_p = (bias_v, bias_v, 1) 
                
                v2_sweep_p = (float(self.entries["V2 Start (V)"].get()), 
                              float(self.entries["V2 Stop (V)"].get()), 
                              int(self.entries["V2 Points"].get()))
                
                # [중요] 장비를 바꿨으므로 이름도 V2로 알려줘야 저장될 때 헷갈리지 않습니다.
                self.sweep_func(
                    v1=self.v2,             # Inner Loop (실제 V2)
                    v2=self.v1,             # Outer Loop (실제 V1)
                    dmm=self.dmm,
                    v1_params=v2_sweep_p,   # V2 파라미터
                    v2_params=v1_fixed_p,   # V1 파라미터
                    delay=delay, sensitivity=sens,
                    x_axis_name="V2"        # [추가] "지금 X축은 V2입니다"라고 전달
                )

            # 창 닫지 않음 (요청사항 반영)
            print("[System] Measurement Started")

        except ValueError:
            messagebox.showerror("Input Error", "Please check all numeric inputs.")
class RealTimeGraphWindow:
    def __init__(self, parent, title="Real-Time Plot"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x500")
        
        # 1. Matplotlib Figure 생성 (Tkinter 내장용)
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel("Current (A)")
        self.ax.grid(True)
        
        # 2. Canvas 생성 (그림판)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # 데이터 저장소
        self.x_data = []
        self.y_data = []
        
        # 2D용 (여러 선 그리기)
        self.lines = [] 
        self.current_line, = self.ax.plot([], [], 'b.-') # 첫 번째 선
        self.lines.append(self.current_line)

    def update_plot(self, x, y):
        """데이터 점 하나를 추가하고 그래프 갱신"""
        self.x_data.append(x)
        self.y_data.append(y)
        
        self.current_line.set_xdata(self.x_data)
        self.current_line.set_ydata(self.y_data)
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def new_step(self):
        """2D 측정 시 새로운 Step(새로운 선) 시작"""
        # 1. 데이터 초기화
        self.x_data = []
        self.y_data = []
        # 2. 범례에 들어갈 텍스트 생성 (그래프 선에 붙는 이름표가 아니라, 박스 안의 설명입니다)
        # 예: "V2=1.0V", "Gate=2.0V" 등
        legend_label = f"Step: {voltage_val:.2f} V"
        
        # 3. 새로운 선 생성 (label=... 옵션이 범례에 표시될 내용입니다)
        # 색상은 Matplotlib이 알아서 주황, 초록, 빨강 순으로 바꿔줍니다.
        self.current_line, = self.ax.plot([], [], '.-', label=legend_label)
        self.lines.append(self.current_line)
        
        # 4. [핵심 수정] 범례를 'best' 위치에 표시
        # loc='best': 데이터가 없는 빈 공간을 자동으로 찾아 범례를 그립니다.
        self.ax.legend(loc='best', fontsize='small', framealpha=0.7)

        self.canvas.draw()