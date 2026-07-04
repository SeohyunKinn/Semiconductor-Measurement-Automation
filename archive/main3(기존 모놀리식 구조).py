#Library
import tkinter as tk
from tkinter import messagebox
import pyvisa
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import threading
import datetime
import signal


# Main UI 
root = tk.Tk()
root.title("Main UI")
root.geometry("400x700")



# PyVISA 초기화. 장비 꺼져있으면 error
rm = pyvisa.ResourceManager()
try:
    gs200 = rm.open_resource("GPIB0::1::INSTR")
    gs200_2 = rm.open_resource("GPIB0::11::INSTR")  
    dmm = rm.open_resource("GPIB0::22::INSTR")

    gs200.write("SOUR:FUNC VOLT")
    gs200_2.write("SOUR:FUNC VOLT")
except pyvisa.errors.VisaIOError as e:
    messagebox.showerror("Connection Error", f"Could not connect to instruments: {e}")
    exit()

V1 = gs200
V2 = gs200_2

# Signal handler to reset voltage when script is interrupted or window is closed
def reset_voltage(device):
    print("Sweep interrupted. Resetting voltage to 0V.")
    device.write("SOUR:LEV 0")

def back_zero(device, current_voltage, step_size=0.01, step_time=0.1):
    """
    현재 전압에서 0V까지 0.01V씩 감소 또는 증가. 

    :param device: GS200 장비 (V1 또는 V2)
    :param current_voltage: 현재 전압 값
    :param step_size: 한 번에 이동할 전압 크기 (기본값: 0.01V)
    :param step_time: 한 단계당 대기 시간 (기본값: 1ms)
    """
    print(f"Rapidly adjusting voltage from {current_voltage}V to 0V with step size {step_size}V and step time {step_time}s")

    # 양수 → 0V로 감소, 음수 → 0V로 증가
    step_direction = -step_size if current_voltage > 0 else step_size
    voltages = np.arange(current_voltage, 0, step_direction)

    for voltage in voltages:
        device.write(f"SOUR:LEV {voltage}")
        time.sleep(step_time)  # 1ms 대기 

    device.write("SOUR:LEV 0")  # 마지막으로 정확히 0V 설정
    print("Voltage successfully adjusted to 0V.")


# Output Control/GS200 output on/off
def output_control(device, state):
    try:
        if device == "GS200-#1":
            V1.write(f"OUTP {state}")
            print(f"GS200-#1 (V1) Output {state}")
        elif device == "GS200-#2":
            V2.write(f"OUTP {state}")
            print(f"GS200-#2 (V2) Output {state}")
    except Exception as e:
        print(f"Error setting output: {e}")

def open_output_control_ui():
    output_window = tk.Toplevel(root)
    output_window.title("Yoko:Output Control")
    output_window.geometry("300x400")

    tk.Label(output_window, text="Yoko:Output Control \n \n Select Device:", font=("Arial", 16, "bold")).pack()
    device_var = tk.StringVar(value="GS200-#1")

    tk.Radiobutton(output_window, text="GS200-#1", variable=device_var, value="GS200-#1", font=("Arial", 14)).pack()
    tk.Radiobutton(output_window, text="GS200-#2", variable=device_var, value="GS200-#2", font=("Arial", 14)).pack()

    tk.Label(output_window, text="Control Output:", font=("Arial", 16, "bold")).pack()
    
    tk.Button(output_window, text="Turn ON", font=("Arial", 14), command=lambda: output_control(device_var.get(), "ON")).pack(pady=5)
    tk.Button(output_window, text="Turn OFF", font=("Arial", 14), command=lambda: output_control(device_var.get(), "OFF")).pack(pady=5)





# PLC 설정 
def set_plc(value):
    try:
        dmm.write(f"SENS:VOLT:DC:NPLC {value}")  
        print(f"PLC set to {value}")
    except Exception as e:
        print(f"Error setting PLC: {e}")



def open_plc_ui():
    plc_window = tk.Toplevel(root)
    plc_window.title("DMM:Set PLC")
    plc_window.geometry("400x600")

    tk.Label(plc_window, text="DMM:Set PLC\n \nSelect NPLC:",font=("Arial", 16, "bold")).pack()
    ranges = [0.02, 0.06, 0.2, 1, 10, 100]

    for r in ranges:
        tk.Button(plc_window, text=f"{r} V", command=lambda r=r: set_plc(r),font=("Arial", 16)).pack()




# Local Mode (local mode로 동작)
def set_local_mode_V1():
    try:
        V1.write("SYST:LOC")  
        print("V1 is now in Local Mode.")
    except Exception as e:
        print(f"Error setting Local Mode: {e}")

def set_local_mode_V2(): 
    try:
        V2.write("SYST:LOC")  
        print("V2 is now in Local Mode.")
    except Exception as e:
        print(f"Error setting Local Mode: {e}")

def set_local_mode_dmm():
    try:
        dmm.write("SYST:LOC")  
        print("DMM is now in Local Mode.")
    except Exception as e:
        print(f"Error setting Local Mode: {e}")



def open_local_mode_ui():
    local_mode_window = tk.Toplevel(root)
    local_mode_window.title("Local Mode Setting")
    local_mode_window.geometry("400x300")

    tk.Label(local_mode_window, text="Local Mode Setting \n \n Set GS200 & DMM to Local Mode", font=("Arial", 16, "bold")).pack()
    tk.Button(local_mode_window, text="GS200-#1 LOCAL", font=("Arial", 12), width=15, height=2, command=set_local_mode_V1).pack()
    tk.Button(local_mode_window, text="GS200-#2 LOCAL", font=("Arial", 12), width=15, height=2, command=set_local_mode_V2).pack()
    tk.Button(local_mode_window, text="DMM LOCAL", font=("Arial", 12), width=15, height=2, command=set_local_mode_dmm).pack()



#  Voltage 설정(gs200 dc voltage, 고정값)
def set_voltage(device, value):
    try:
        if device == "GS200-#1":
            V1.write(f"SOUR:LEV {value}")
            print(f"GS200-#1 (V1) voltage set to {value}V")
        elif device == "GS200-#2":
            V2.write(f"SOUR:LEV {value}")
            print(f"GS200-#2 (V2) voltage set to {value}V")
    except Exception as e:
        print(f"Error setting voltage: {e}")


def open_voltage_ui():
    voltage_window = tk.Toplevel(root)
    voltage_window.title("Set Voltage")
    voltage_window.geometry("300x500")

    tk.Label(voltage_window, text="Set Voltage\n \n Select Device:", font=("Arial", 16, "bold")).pack()
    device_var = tk.StringVar(value="GS200-#1")
    
    tk.Radiobutton(voltage_window, text="GS200-#1", variable=device_var, value="GS200-#1", font=("Arial", 14)).pack()
    tk.Radiobutton(voltage_window, text="GS200-#2", variable=device_var, value="GS200-#2", font=("Arial", 14)).pack()

    tk.Label(voltage_window, text="Set Voltage Value:", font=("Arial", 16)).pack()
    voltage_entry = tk.Entry(voltage_window)
    voltage_entry.pack()
    tk.Button(voltage_window, text="Set Voltage", font=("Arial", 16), command=lambda: set_voltage(device_var.get(), voltage_entry.get())).pack()
   

#voltage sweep(1 device), V-V curve diode에 전압 걸고 dmm에서 전압 측정정
def voltage_sweep(device, min_v, max_v, steps, delay, ramping_key, back_zero_step_time=0.01):

    voltages = np.linspace(min_v, max_v, steps)
    measured_values = []

    print(f"Voltage Sweep: {min_v}V → {max_v}V, {steps} steps, delay: {delay}s")
    
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'bo-', label="Measured Voltage")
    ax.set_xlim(min_v, max_v)
    ax.set_ylim(min_v, max_v)
    ax.set_xlabel("Set Voltage (V)")
    ax.set_ylabel("Measured Voltage (V)")
    ax.legend()

    for voltage in voltages:
        device.write(f"SOUR:LEV {voltage}")
        time.sleep(delay)
        measured_voltage = float(dmm.query("READ?").strip())
        measured_values.append(measured_voltage)
        line.set_xdata(voltages[:len(measured_values)])
        line.set_ydata(measured_values)
        ax.relim()
        ax.autoscale_view()
        
        plt.draw()
        plt.pause(0.1)

    if ramping_key==1:
        back_zero(device, max_v, step_size=0.01, step_time=back_zero_step_time)
    elif ramping_key==2:
        device.write(f"SOUR:LEV {max_v}")  # 최대 전압 유지

    plt.ioff()
    plt.show()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame({"Set Voltage (V)": voltages, "Measured Voltage (V)": measured_values})
    df.to_csv(f"C:\\Users\\user\\Desktop\\result\\voltage_results_{timestamp}.txt", sep="\t", index=False)
    print(f"Results saved: voltage_results_{timestamp}.txt")


def open_sweep_ui():
    sweep_window = tk.Toplevel(root)
    sweep_window.title("Voltage Sweep")
    sweep_window.geometry("300x500")

    tk.Label(sweep_window, text="Select Device:", font=("Arial", 16, "bold")).pack()
    device_var = tk.StringVar(value="GS200-#1")

    tk.Radiobutton(sweep_window, text="GS200-#1", variable=device_var, value="GS200-#1", font=("Arial", 14)).pack()
    tk.Radiobutton(sweep_window, text="GS200-#2", variable=device_var, value="GS200-#2", font=("Arial", 14)).pack()

    tk.Label(sweep_window, text="Min Voltage (V):", font=("Arial", 16)).pack()
    min_v_entry = tk.Entry(sweep_window)
    min_v_entry.pack()
    
    tk.Label(sweep_window, text="Max Voltage (V):", font=("Arial", 16)).pack()
    max_v_entry = tk.Entry(sweep_window)
    max_v_entry.pack()
    
    tk.Label(sweep_window, text="Steps:", font=("Arial", 16)).pack()
    steps_entry = tk.Entry(sweep_window)
    steps_entry.pack()
    
    tk.Label(sweep_window, text="Delay (s):", font=("Arial", 16)).pack()
    delay_entry = tk.Entry(sweep_window)
    delay_entry.pack()

    tk.Label(sweep_window, text="Ramping key [1:ramping, 2:maintain]:", font=("Arial", 16)).pack()
    ramping_entry = tk.Entry(sweep_window)
    ramping_entry.pack()


    def start_sweep(): #ui 내부함수로 voltage_sweep 함수 동작시킨다. 
        voltage_sweep(
            V1 if device_var.get() == "GS200-#1" else V2,
            float(min_v_entry.get()),
            float(max_v_entry.get()),
            int(steps_entry.get()),
            float(delay_entry.get()),
            int(ramping_entry.get())
        )

    tk.Button(sweep_window, text="Start Sweep", font=("Arial", 16), command=start_sweep).pack(pady=10)

  

# current sweep(1 device) diode, I-V curve
def current_sweep(device, min_v, max_v, steps, delay, sensitivity, ramping_key, back_zero_step_time=0.01): 

    voltages = np.linspace(min_v, max_v, steps)
    measured_values = []

    print(f"전압 스윕: {min_v}V → {max_v}V, {steps} 단계, 딜레이: {delay}s")

    plt.ion()
    fig, ax = plt.subplots()

    #abort funtion
    def handle_close(event): 
        reset_voltage(device)
    fig.canvas.mpl_connect("close_event", handle_close)

    line, = ax.plot([], [], 'bo-', label="Measured Current")
    ax.set_xlim(min_v, max_v)
    ax.set_xlabel("Set Voltage (V)")
    ax.set_ylabel("Current (A)")
    ax.legend()
    
    for voltage in voltages:
        device.write(f"SOUR:LEV {voltage}") 
        time.sleep(delay)  
        measured_voltage = float(dmm.query("READ?").strip()) 
        measured_values.append(-measured_voltage)

        measured_currents = np.array(measured_values) *(sensitivity)

 
        line.set_xdata(voltages[:len(measured_currents)])
        line.set_ydata(measured_currents)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.1)

    if ramping_key==1:
        back_zero(device, max_v, step_size=0.01, step_time=back_zero_step_time)
    elif ramping_key==2:
        device.write(f"SOUR:LEV {max_v}")  # 최대 전압 유지

    plt.ioff()
    plt.show()

    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame({"Set Voltage (V)": voltages, "Measured Current (A)": measured_currents})
    df.to_csv(f"C:\\Users\\user\\Desktop\\result\\current_results_{timestamp}.txt",  sep="\t", index=False)
    print(f"결과 저장: current_results_{timestamp}.txt")    
    


def open_current_sweep_ui():
    sweep_window = tk.Toplevel(root)
    sweep_window.title("Current(1D: V)")
    sweep_window.geometry("400x600")

    tk.Label(sweep_window, text="Current(1D: V)\n \n Select Device:", font=("Arial", 16, "bold")).pack()
    device_var = tk.StringVar(value="GS200")

    tk.Radiobutton(sweep_window, text="GS200-#1", variable=device_var, value="GS200-#1", font=("Arial", 14)).pack()
    tk.Radiobutton(sweep_window, text="GS200-#2", variable=device_var, value="GS200-#2", font=("Arial", 14)).pack()#device 선택

    tk.Label(sweep_window, text="Start Voltage (V):", font=("Arial", 16)).pack()
    min_v_entry = tk.Entry(sweep_window)
    min_v_entry.pack()
    
    tk.Label(sweep_window, text="Stop Voltage (V):", font=("Arial", 16)).pack()
    max_v_entry = tk.Entry(sweep_window)
    max_v_entry.pack()
    
    tk.Label(sweep_window, text="# of points:", font=("Arial", 16)).pack()
    steps_entry = tk.Entry(sweep_window)
    steps_entry.pack()
    
    tk.Label(sweep_window, text="Delay (s):", font=("Arial", 16)).pack()
    delay_entry = tk.Entry(sweep_window)
    delay_entry.pack()

    tk.Label(sweep_window, text="Sensitivity(A/V): (Ex: 1E-5)", font=("Arial", 16)).pack()
    sensitivity_entry = tk.Entry(sweep_window)
    sensitivity_entry.pack()

    tk.Label(sweep_window, text="Ramping key [1:ramping, 2:maintain]:", font=("Arial", 16)).pack()
    ramping_entry = tk.Entry(sweep_window)
    ramping_entry.pack()

    tk.Label(sweep_window, text="back zero step time [default=0.01]:", font=("Arial", 16)).pack()
    back_zero_entry = tk.Entry(sweep_window)
    back_zero_entry.pack()

    def start_sweep():
        current_sweep(
            V1 if device_var.get() == "GS200-#1" else V2,
            float(min_v_entry.get()),
            float(max_v_entry.get()),
            int(steps_entry.get()),
            float(delay_entry.get()),
            float(sensitivity_entry.get()),
            int(ramping_entry.get()),
            float(back_zero_entry.get())
        )

    tk.Button(sweep_window, text="Start Sweep", font=("Arial", 16), command=start_sweep).pack(pady=10)






#V-V(2device)-color map /Vg-Vds/I는 color로
def dual_current_sweep(v1_min, v1_max, v1_steps, v2_min, v2_max, v2_steps, delay, x_axis, sensitivity):
    v1_values = np.linspace(v1_min, v1_max, v1_steps)
    v2_values = np.linspace(v2_min, v2_max, v2_steps)

    results = []  # 데이터를 저장할 리스트

    print(f"Sweep: V1({v1_min}V → {v1_max}V), V2({v2_min}V → {v2_max}V), Delay: {delay}s")

    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 6))

    if x_axis=="V2":
        ext=[v2_min, v2_max, v1_min, v1_max]
        y_axis="V1"
        currents = np.zeros((v1_steps, v2_steps))
    else:
        ext=[v1_min, v1_max, v2_min, v2_max]
        y_axis="V2"
        currents = np.zeros((v2_steps, v1_steps))

    heatmap = ax.imshow(currents, cmap="plasma", origin="lower",extent=ext, aspect='auto')
    cbar = plt.colorbar(heatmap, ax=ax, label="Measured Current (A)")

    ax.set_xlabel(f"{x_axis} (V)")
    ax.set_ylabel(f"{y_axis} (V)")

    if x_axis=="V2":
        for i, v1 in enumerate(v1_values):
            V1.write(f"SOUR:LEV {v1}")  
            for j, v2 in enumerate(v2_values):
                V2.write(f"SOUR:LEV {v2}") 
                time.sleep(delay)
                measured_voltage = float(dmm.query("READ?").strip())
                measured_current = measured_voltage * sensitivity
                currents[i, j] = measured_current
                results.append([v1, v2, measured_current])  # 리스트에 추가

                heatmap.set_data(currents)
                heatmap.set_clim(currents.min(), currents.max()) 
                plt.draw()
                plt.pause(0.1)

    else:
        for i, v2 in enumerate(v2_values):
            V2.write(f"SOUR:LEV {v2}")  
            for j, v1 in enumerate(v1_values):
                V1.write(f"SOUR:LEV {v1}") 
                time.sleep(delay)
                measured_voltage = float(dmm.query("READ?").strip())
                measured_current = measured_voltage * sensitivity
                currents[i, j] = measured_current
                results.append([v2, v1, measured_current])  
                heatmap.set_data(currents)
                heatmap.set_clim(currents.min(), currents.max()) 
                plt.draw()
                plt.pause(0.1)
    
    back_zero(V1, v1_max, step_size=0.01, step_time=0.01)
    back_zero(V2, v2_max, step_size=0.01, step_time=0.01)
    
    plt.ioff()
    plt.show()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\Users\\user\\Desktop\\result\\transistor_current_{timestamp}.txt"
    with open(filename,"w") as f:
        f.write(f"{y_axis} values are in the first column (↓)\n")
        f.write(f"{x_axis} values are in the first row (→)\n")
        f.write(f"Sweep: V1({v1_min}V → {v1_max}V-----{v1_steps}) \n")
        f.write(f"Sweep: V2({v2_min}V → {v2_max}V-----{v2_steps}) \n")

    if x_axis=="V2":
        df = pd.DataFrame(currents, index=v1_values, columns=v2_values)

    else:
        df = pd.DataFrame(currents, index=v2_values, columns=v1_values)
    df.to_csv(filename, sep="\t", mode="a")
    print(f"Results saved: {filename}")




def open_dual_current_sweep_ui():
    sweep_window = tk.Toplevel(root)
    sweep_window.geometry("400x600")
    sweep_window.title("Current(2D: V1, V2)")

    tk.Label(sweep_window, text="Current(2D: V1, V2)\n \nSelect X-Axis:", font=("Arial", 16, "bold")).pack()
    x_axis_var = tk.StringVar(value="V1")

    tk.Radiobutton(sweep_window, text="GS200-#1 (V1)", variable=x_axis_var, value="V1", font=("Arial", 14)).pack()
    tk.Radiobutton(sweep_window, text="GS200-#2 (V2)", variable=x_axis_var, value="V2", font=("Arial", 14)).pack()

    entries = {}
    params = ["[V1] Start Voltage: ", "[V1] Stop Voltage: ", "[V1] # of points:", "[V2] Start Voltage:", "[V2] Stop Voltage:", "[V2] # of points:", "Delay (s):","Sensitivity (A/V): (Ex: 1E-5)"]
    for p in params:
        tk.Label(sweep_window, text=f"{p}", font=("Arial", 14)).pack()
        entry = tk.Entry(sweep_window)
        entry.pack()
        entries[p] = entry

    def start_sweep():
        dual_current_sweep(
            float(entries["[V1] Start Voltage:"].get()), 
            float(entries["[V1] Stop Voltage:"].get()), 
            int(entries["[V1] # of points:"].get()),
            float(entries["[V2] Start Voltage:"].get()), float(entries["[V2] Stop Voltage:"].get()), 
            int(entries["[V2] # of points:"].get()),
            float(entries["Delay (s):"].get()),
            x_axis_var.get(),
            float(entries["Sensitivity (A/V): (Ex: 1E-5)"].get())
        )

    tk.Button(sweep_window, text="Start Sweep", font=("Arial", 16), command=start_sweep).pack(pady=10)






#dual V-V(2 device)/ measured voltage=color ->dmm에서 voltage를 측정. 
def dual_voltage_sweep(v1_min, v1_max, v1_steps, v2_min, v2_max, v2_steps, delay, x_axis):
    v1_values = np.linspace(v1_min, v1_max, v1_steps)
    v2_values = np.linspace(v2_min, v2_max, v2_steps)

    results = []  # 데이터를 저장할 리스트

    print(f"Sweep: V1({v1_min}V → {v1_max}V), V2({v2_min}V → {v2_max}V), Delay: {delay}s")

    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 6))

    if x_axis=="V2":
        ext=[v2_min, v2_max, v1_min, v1_max]
        y_axis="V1"
        voltages = np.zeros((v1_steps, v2_steps))
    else:
        ext=[v1_min, v1_max, v2_min, v2_max]
        y_axis="V2"
        voltages= np.zeros((v2_steps, v1_steps))

    heatmap = ax.imshow(voltages, cmap="plasma", origin="lower",extent=ext, aspect='auto')
    cbar = plt.colorbar(heatmap, ax=ax, label="Measured Voltage (V)")

    ax.set_xlabel(f"{x_axis} (V)")
    ax.set_ylabel(f"{y_axis} (V)")

    if x_axis=="V2":
        for i, v1 in enumerate(v1_values):
            V1.write(f"SOUR:LEV {v1}")  
            for j, v2 in enumerate(v2_values):
                V2.write(f"SOUR:LEV {v2}") 
                time.sleep(delay)
                measured_voltage = float(dmm.query("READ?").strip())
                voltages[i, j] = measured_voltage
                results.append([v1, v2, measured_voltage])  # 리스트에 추가

                heatmap.set_data(voltages)
                heatmap.set_clim(voltages.min(),voltages.max()) 
                plt.draw()
                plt.pause(0.1)

    else:
        for i, v2 in enumerate(v2_values):
            V2.write(f"SOUR:LEV {v2}")  
            for j, v1 in enumerate(v1_values):
                V1.write(f"SOUR:LEV {v1}") 
                time.sleep(delay)
                measured_voltage = float(dmm.query("READ?").strip())
                voltages[i, j] = measured_voltage
                results.append([v2, v1, measured_voltage])  
                heatmap.set_data(voltages)
                heatmap.set_clim(voltages.min(), voltages.max()) 
                plt.draw()
                plt.pause(0.1)
    back_zero(V1, v1_max, step_size=0.01, step_time=0.01)
    back_zero(V2, v2_max, step_size=0.01, step_time=0.01)
    plt.ioff()
    plt.show()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\Users\\user\\Desktop\\result\\transistor_voltage_{timestamp}.txt"
    with open(filename,"w") as f:
        f.write(f"{y_axis} values are in the first column (↓)\n")
        f.write(f"{x_axis} values are in the first row (→)\n")
        f.write(f"Sweep: V1({v1_min}V → {v1_max}V-----{v1_steps}) \n")
        f.write(f"Sweep: V2({v2_min}V → {v2_max}V-----{v2_steps}) \n")

    if x_axis=="V2":
        df = pd.DataFrame(voltages, index=v1_values, columns=v2_values)

    else:
        df = pd.DataFrame(voltages, index=v2_values, columns=v1_values)
    df.to_csv(filename, sep="\t", mode="a")
    print(f"Results saved: {filename}")




def open_dual_voltage_sweep_ui():
    sweep_window = tk.Toplevel(root)
    sweep_window.geometry("400x600")

    tk.Label(sweep_window, text="Select X-Axis:", font=("Arial", 16, "bold")).pack()
    x_axis_var = tk.StringVar(value="V1")

    tk.Radiobutton(sweep_window, text="GS200-#1 (V1)", variable=x_axis_var, value="V1", font=("Arial", 14)).pack()
    tk.Radiobutton(sweep_window, text="GS200-#2 (V2)", variable=x_axis_var, value="V2", font=("Arial", 14)).pack()

    entries = {}
    params = ["V1 Min", "V1 Max", "V1 # of points", "V2 Min", "V2 Max", "V2 # of points", "Delay (s)"]
    for p in params:
        tk.Label(sweep_window, text=f"{p}:", font=("Arial", 14)).pack()
        entry = tk.Entry(sweep_window)
        entry.pack()
        entries[p] = entry


    def start_sweep():
        dual_voltage_sweep(
            float(entries["V1 Min"].get()), 
            float(entries["V1 Max"].get()), 
            int(entries["V1 # of points"].get()),
            float(entries["V2 Min"].get()), float(entries["V2 Max"].get()), 
            int(entries["V2 # of points"].get()),
            float(entries["Delay (s)"].get()), 
            x_axis_var.get()
        )

    tk.Button(sweep_window, text="Start Sweep", font=("Arial", 16), command=start_sweep).pack(pady=10)




#range 설정
def set_range(device, value):
    try:
        if device == "GS200-#1":
            V1.write(f"SOUR:RANG {value}")
            print(f"V1 Voltage range set to {value}V")
        elif device == "GS200-#2":
            V2.write(f"SOUR:RANG {value}")
            print(f"V2 Voltage range set to {value}V")
    except Exception as e:
        print(f"Error setting voltage: {e}")


def open_voltage_range_ui():
    range_window = tk.Toplevel(root)
    range_window.title("Yoko:Voltage Range")
    range_window.geometry("400x600")

    tk.Label(range_window, text="Yoko:Voltage Range\n \n Select Device",font=("Arial", 16, "bold")).pack()

    device_var = tk.StringVar(value="GS200-#1")

    tk.Radiobutton(range_window, text="GS200-#1", variable=device_var, value="GS200-#1", font=("Arial", 16)).pack()
    tk.Radiobutton(range_window, text="GS200-#2", variable=device_var, value="GS200-#2", font=("Arial", 16)).pack()#device 선택


    tk.Label(range_window, text="Select Range (V):",font=("Arial", 16, "bold")).pack()
    ranges = [0.01, 0.1, 1, 10, 30]#gs200에서 설정 가능한 range

    for r in ranges:
        tk.Button(range_window, text=f"{r} V", command=lambda r=r: set_range(device_var.get(), r),font=("Arial", 16)).pack()





#command 직접입력(장비에서 읽을 수 있는 명령어 입력해야함) query는 안됨됨
def command(device, command):
    try:
        if device=="GS200-#1":
            V1.write(command)
        elif device=="GS200-#2":
            V2.write(command)
        elif device=="dmm":
            dmm.write(command)
    except Exception as e:
        print(f"Error: {e}")


def open_command_ui():
    command_window=tk.Toplevel(root)
    command_window.geometry("400x500")
    command_window.title("Command")

    tk.Label(command_window, text="Command \n \n Select Device:", font=("Arial", 16, "bold")).pack()
    device_var = tk.StringVar(value="GS200-#1")

    tk.Radiobutton(command_window, text="GS200-#1", variable=device_var, value="GS200-#1", font=("Arial", 14)).pack()
    tk.Radiobutton(command_window, text="GS200-#2", variable=device_var, value="GS200-#2", font=("Arial", 14)).pack()
    tk.Radiobutton(command_window, text="DMM", variable=device_var, value="dmm", font=("Arial", 14)).pack()

    tk.Label(command_window, text="Enter Command:", font=("Arial", 16)).pack()
    command_entry = tk.Entry(command_window)
    command_entry.pack()

    tk.Button(command_window, text="Enter",font=("Arial", 16), command=lambda: command(device_var.get(),command_entry.get())).pack()
    



# read dmm voltage - 시간에 따른 전압 측정
def read_dmm_voltage(duration):
    times = []
    voltages = []
    interval=0.05

    print(f"Reading DMM Voltage for {duration} seconds...")

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'bo-', label="Measured Voltage")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("DMM Voltage Measurement")
    ax.legend()

    start_time = time.time()
    while (time.time() - start_time) < duration:
        current_time = time.time() - start_time
        measured_voltage = float(dmm.query("READ?").strip())

        times.append(current_time)
        voltages.append(measured_voltage)

        line.set_xdata(times)
        line.set_ydata(voltages)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(interval)

    plt.ioff()
    plt.show()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\Users\\user\\Desktop\\result\\dmm_voltage_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("Time (s)\tVoltage (V)\n")  
        for t, v in zip(times, voltages):
            f.write(f"{t:.6f}\t{v:.6f}\n")  

    print(f"Results saved: {filename}")



# read dmm current - 시간에 따른 전류 측정
def read_dmm_current(duration, sensitivity):
    times = []
    currents = []
    interval=0.05

    print(f"Reading DMM Current for {duration} seconds...")

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'ro-', label="Measured Current")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Current (A)")
    ax.set_title("DMM Current Measurement")
    ax.legend()

    start_time = time.time()
    while (time.time() - start_time) < duration:
        current_time=time.time()-start_time
        measured_voltage = float(dmm.query("READ?").strip())
        
        measured_current = measured_voltage * sensitivity

        times.append(current_time)
        currents.append(measured_current)

        line.set_xdata(times)
        line.set_ydata(currents)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(interval)

    plt.ioff()
    plt.show()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\Users\\user\\Desktop\\result\\dmm_current_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("Time (s)\tCurrent (A)\n") 
        for t, c in zip(times, currents):
            f.write(f"{t:.6f}\t{c:.6e}\n")  

    print(f"Results saved: {filename}")


def open_dmm_measurement_ui():
    measurement_window = tk.Toplevel(root)
    measurement_window.title("DMM Reading")
    measurement_window.geometry("400x400")

    tk.Label(measurement_window, text="DMM Reading \n \n Select Measurement Type:", font=("Arial", 16, 'bold')).pack()
    measurement_type = tk.StringVar(value="Voltage")

    tk.Radiobutton(measurement_window, text="Voltage", variable=measurement_type, value="Voltage", font=("Arial", 14)).pack()
    tk.Radiobutton(measurement_window, text="Current", variable=measurement_type, value="Current", font=("Arial", 14)).pack()

    tk.Label(measurement_window, text="Measurement Duration (s):", font=("Arial", 16)).pack()
    duration_entry = tk.Entry(measurement_window)
    duration_entry.pack()

    # tk.Label(measurement_window, text="Sampling Interval (s):", font=("Arial", 16)).pack()
    # interval_entry = tk.Entry(measurement_window)
    # interval_entry.pack()

    sensitivity_label = None
    sensitivity_entry = None

    def show_sensitivity():
        nonlocal sensitivity_label, sensitivity_entry
        if measurement_type.get() == "Current":
            if not sensitivity_entry:
                sensitivity_label = tk.Label(measurement_window, text="Sensitivity (A/V):", font=("Arial", 16))
                sensitivity_label.pack()
                sensitivity_entry = tk.Entry(measurement_window)
                sensitivity_entry.pack()
        else:
            if sensitivity_label:
                sensitivity_label.pack_forget()
                sensitivity_entry.pack_forget()
                sensitivity_label = None
                sensitivity_entry = None

    measurement_type.trace("w", lambda *args: show_sensitivity())

    def start_measurement():
        duration = float(duration_entry.get())
        #interval = float(interval_entry.get())

        if measurement_type.get() == "Voltage":
            read_dmm_voltage(duration)
        else:
            sensitivity = float(sensitivity_entry.get())
            read_dmm_current(duration, sensitivity)

    tk.Button(measurement_window, text="Start Read", font=("Arial", 16), command=start_measurement).pack(pady=10, side="bottom")




#transistor current측정
def plot_v1_vs_current(v1_min, v1_max, v1_steps, v2_min, v2_max, v2_steps, delay, sensitivity):
    v1_values = np.linspace(v1_min, v1_max, v1_steps)
    v2_values = np.linspace(v2_min, v2_max, v2_steps)
    currents = np.zeros((v1_steps, v2_steps))

    print(f"Measuring Current for V1 sweep ({v1_min}V → {v1_max}V, steps: {v1_steps}) "
          f"at different V2 values ({v2_min}V → {v2_max}V, steps: {v2_steps})")

    plt.ion()  
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlabel("V1 (V)")
    ax.set_ylabel("Current (A)")
    ax.set_title("V1 vs. Current at Different V2 Values")
    ax.grid(True)

    lines = []  
    for v2 in v2_values:
        line, = ax.plot([], [], marker='o', linestyle='-', label=f"V2 = {v2:.2f}V")
        lines.append(line)

    ax.legend()
    plt.draw()


    for j, v2 in enumerate(v2_values):
        V2.write(f"SOUR:LEV {v2}")  # V2 설정
        current_list = []  # 현재 V2에서의 current 저장용

        for i, v1 in enumerate(v1_values):
            V1.write(f"SOUR:LEV {v1}")  # V1 설정
            time.sleep(delay)
            measured_voltage = float(dmm.query("READ?").strip())  # 측정
            measured_current = -measured_voltage * sensitivity  # 전류 계산
            currents[i, j] = measured_current  # 데이터 저장
            current_list.append(measured_current)  # 그래프용 데이터 저장

            # 실시간으로 그래프 업데이트
            lines[j].set_xdata(v1_values[:len(current_list)])
            lines[j].set_ydata(current_list)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)

    back_zero(V1, v1_max, step_size=0.01, step_time=0.01)
    back_zero(V2, v2_max, step_size=0.01, step_time=0.01)

    plt.ioff()
    plt.show()

    # 텍스트 파일 저장 (V1이 첫 번째 열)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\Users\\user\\Desktop\\result\\v1_vs_current_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("### Measurement Data: V1 vs. Current at Different V2 Values ###\n")
        f.write(f"V1 (vertical axis) sweep range: {v1_min}V → {v1_max}V, Steps: {v1_steps}\n")
        f.write(f"V2 (horizontal axis) range: {v2_min}V → {v2_max}V, Steps: {v2_steps}\n")
        f.write(f"Sensitivity: {sensitivity} A/V\n")
        f.write(f"Delay per step: {delay} seconds\n")
        f.write("\n")
        f.write("V1 (V) -> Current (A) for each V2\n")
        f.write("\t".join([f"{v2:.2f}V" for v2 in v2_values]) + "\n")

        for i, v1 in enumerate(v1_values):
            f.write(f"{v1:.6f}\t" + "\t".join([f"{currents[i, j]:.6e}" for j in range(v2_steps)]) + "\n")

    print(f"Results saved: {filename}")




def plot_v2_vs_current(v1_min, v1_max, v1_steps, v2_min, v2_max, v2_steps, delay, sensitivity):
    v1_values = np.linspace(v1_min, v1_max, v1_steps)
    v2_values = np.linspace(v2_min, v2_max, v2_steps)
    currents = np.zeros((v1_steps, v2_steps))

    print(f"Measuring Current for V2 sweep ({v2_min}V → {v2_max}V, steps: {v2_steps}) "
          f"at different V1 values ({v1_min}V → {v1_max}V, steps: {v1_steps})")

    plt.ion()  
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlabel("V2 (V)")
    ax.set_ylabel("Current (A)")
    ax.set_title("V2 vs. Current at Different V1 Values")
    ax.grid(True)

    lines = []  # 
    for v1 in v1_values:
        line, = ax.plot([], [], marker='o', linestyle='-', label=f"V1 = {v1:.2f}V")
        lines.append(line)

    ax.legend()
    plt.draw()

    for i, v1 in enumerate(v1_values):
        V1.write(f"SOUR:LEV {v1}")  # V1 설정
        current_list = []  # 현재 V1에서의 current 저장용

        for j, v2 in enumerate(v2_values):
            V2.write(f"SOUR:LEV {v2}")  # V2 설정
            time.sleep(delay)
            measured_voltage = float(dmm.query("READ?").strip())  # 측정
            measured_current = measured_voltage * sensitivity  # 전류 계산
            currents[i, j] = measured_current  
            current_list.append(measured_current)  

            lines[i].set_xdata(v2_values[:len(current_list)])
            lines[i].set_ydata(current_list)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)

    back_zero(V1, v1_max, step_size=0.01, step_time=0.01)
    back_zero(V2, v2_max, step_size=0.01, step_time=0.01)

    plt.ioff()
    plt.show()

    # 텍스트 파일 저장 (V2가 첫 번째 열)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\Users\\user\\Desktop\\result\\v2_vs_current_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("### Measurement Data: V2 vs. Current at Different V1 Values ###\n")
        f.write(f"V2 (horizontal axis) sweep range: {v2_min}V → {v2_max}V, Steps: {v2_steps}\n")
        f.write(f"V1 (legend values) range: {v1_min}V → {v1_max}V, Steps: {v1_steps}\n")
        f.write(f"Sensitivity: {sensitivity} A/V\n")
        f.write(f"Delay per step: {delay} seconds\n")
        f.write("\n")
        f.write("V2 (V) -> Current (A) for each V1\n")
        f.write("\t".join([f"{v1:.2f}V" for v1 in v1_values]) + "\n")

        for j, v2 in enumerate(v2_values):
            f.write(f"{v2:.6f}\t" + "\t".join([f"{currents[i, j]:.6e}" for i in range(v1_steps)]) + "\n")

    print(f"Results saved: {filename}")



def open_v_vs_current_ui():
    measurement_window = tk.Toplevel(root)
    measurement_window.title("V vs. Current Measurement")
    measurement_window.geometry("400x600")

    tk.Label(measurement_window, text="Select X-Axis:", font=("Arial", 16)).pack()
    x_axis_var = tk.StringVar(value="V1")

    tk.Radiobutton(measurement_window, text="V1 (Source-Drain)", variable=x_axis_var, value="V1", font=("Arial", 14)).pack()
    tk.Radiobutton(measurement_window, text="V2 (Gate)", variable=x_axis_var, value="V2", font=("Arial", 14)).pack()

    entries = {}
    params = ["V1 Min", "V1 Max", "V1 # of points", "V2 Min", "V2 Max", "V2 # of points", "Delay (s)", "Sensitivity (A/V)"]
    for p in params:
        tk.Label(measurement_window, text=f"{p}:", font=("Arial", 14)).pack()
        entry = tk.Entry(measurement_window)
        entry.pack()
        entries[p] = entry

    def start_measurement():
        v1_min = float(entries["V1 Min"].get())
        v1_max = float(entries["V1 Max"].get())
        v1_steps = int(entries["V1 # of points"].get())
        v2_min = float(entries["V2 Min"].get())
        v2_max = float(entries["V2 Max"].get())
        v2_steps = int(entries["V2 # of points"].get())
        delay = float(entries["Delay (s)"].get())
        sensitivity = float(entries["Sensitivity (A/V)"].get())

        if x_axis_var.get() == "V1":
            plot_v1_vs_current(v1_min, v1_max, v1_steps, v2_min, v2_max, v2_steps, delay, sensitivity)
        else:
            plot_v2_vs_current(v1_min, v1_max, v1_steps, v2_min, v2_max, v2_steps, delay, sensitivity)

    tk.Button(measurement_window, text="Start Measurement", font=("Arial", 16), command=start_measurement).pack(pady=10)





#종료함수. main ui와 연결
def exit_program():
    print("Exiting program...")
    V1.write("OUTP OFF")
    V2.write("OUTP OFF")
    V1.write(f"SOUR:LEV 0")
    V2.write(f"SOUR:LEV 0")
    set_local_mode_V1()
    set_local_mode_V2()
    set_local_mode_dmm()


    V1.close()
    V2.close()
    dmm.close()
    rm.close()
    root.destroy()



# Main UI 버튼설정
tk.Button(root, text="DMM:Set PLC", command=open_plc_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Yoko:Voltage Range", command=open_voltage_range_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Local Mode Settings", command=open_local_mode_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Setval (set voltage)", command=open_voltage_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Yoko:Output Control", command=open_output_control_ui, font=("Arial", 14)).pack(pady=10)  
#tk.Button(root, text="Voltage(diode)", command=open_sweep_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Current(1D: V)", command=open_current_sweep_ui, font=("Arial", 14)).pack()
#tk.Button(root, text="Voltage(transistor)2D", command=open_dual_voltage_sweep_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Current(2D: V1, V2)", command=open_dual_current_sweep_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Current(1D: V1, V2)", command=open_v_vs_current_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Command", command=open_command_ui, font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Time Based DMM Reading", font=("Arial", 16), command=open_dmm_measurement_ui).pack(pady=10)

#종료함수 실행(main ui를 닫으면 실행)
root.protocol("WM_DELETE_WINDOW",exit_program)


# Tkinter loop
root.mainloop()


#프로그램으로 만들기(terminal에 입력)
#pyinstaller --onefile --noconsole "C:\Users\user\Desktop\main2.py"