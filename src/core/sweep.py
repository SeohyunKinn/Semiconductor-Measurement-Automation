import time
import datetime
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from configs.device_configs import DATA_SAVE_PATH, FIGURE_SAVE_PATH

# 측정 중단 플래그
is_measuring = False

def stop_measurement():
    global is_measuring
    is_measuring = False
    print("[System] Stop signal triggered.")

def current_sweep_1d(device, dmm, min_v, max_v, steps, delay, sensitivity, ramping_key, data_queue=None):
    global is_measuring
    is_measuring = True
    
    voltages = np.linspace(min_v, max_v, steps)
    measured_currents = []
    last_v = 0
    
    print(f"[System] 1D Sweep Started ({steps} pts)")

    for v in voltages:
        if not is_measuring: break
        
        device.set_voltage(v)
        time.sleep(delay)
        
        m_volt = dmm.read_value()
        # [확인됨] 양의 방향 계산 (우상향 그래프용)
        m_curr = m_volt * sensitivity
        measured_currents.append(m_curr)
        last_v = v

        # 실시간 그래프용 큐 전송
        if data_queue:
            data_queue.put(("data_1d", v, m_curr))

    # 데이터 저장 (헤더 정보 포함하여 전달)
    if len(measured_currents) > 0:
        valid_voltages = voltages[:len(measured_currents)]
        
        # 저장용 그래프 생성 (백그라운드)
        fig, ax = plt.subplots()
        ax.plot(valid_voltages, measured_currents, 'bo-')
        ax.set_title("1D Sweep Result")
        ax.set_xlabel("Voltage (V)")
        ax.set_ylabel("Current (A)")
        ax.grid(True)
        
        # [핵심] 변경된 저장 함수 호출
        _save_results(
            prefix="1D_Sweep", 
            voltages=valid_voltages, 
            currents=measured_currents, 
            figure=fig,
            meta={
                "Sweep Range": f"{min_v}V -> {max_v}V",
                "Steps": steps,
                "Sensitivity": sensitivity,
                "Delay": delay
            }
        )
        plt.close(fig)

    if ramping_key == 1:
        device.back_zero(last_v)
    
    # 측정 종료 알림
    if data_queue:
        data_queue.put(("finish", None, None))
        
    is_measuring = False

def current_sweep_2d(v1_dev, v2_dev, dmm, v1_params, v2_params, delay, sensitivity, x_axis_name="V1", data_queue=None):
    global is_measuring
    is_measuring = True
    
    # 파라미터 언패킹
    v1_start, v1_stop, v1_steps = v1_params
    v2_start, v2_stop, v2_steps = v2_params
    
    v1_list = np.linspace(v1_start, v1_stop, int(v1_steps)) # Inner (Sweep)
    v2_list = np.linspace(v2_start, v2_stop, int(v2_steps)) # Outer (Step)
    
    results_matrix = []
    print(f"[System] 2D Sweep Started. X-Axis: {x_axis_name}")

    for i, v2_val in enumerate(v2_list):
        if not is_measuring: break
        v2_dev.set_voltage(v2_val)
        current_row = [] 
        
        # [핵심] 새로운 Step 시작 알림 (전압값 포함 -> 그래프 범례용)
        if data_queue:
            data_queue.put(("new_step", v2_val, None))

        for v1_val in v1_list:
            if not is_measuring: break
            v1_dev.set_voltage(v1_val)
            time.sleep(delay)
            
            # [확인됨] 양의 방향 계산
            m_curr = dmm.read_value() * sensitivity