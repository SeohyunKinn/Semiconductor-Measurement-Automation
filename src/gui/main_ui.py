import tkinter as tk
import threading 
import queue

from src.gui.sub_ui import PLCWindow, RangeWindow, SweepInputWindow, LocalModeWindow, OutputControlWindow, MosfetMeasurementWindow, RealTimeGraphWindow
from src.core.sweep import stop_measurement, current_sweep_1d, current_sweep_2d # 측정 로직과 중단 함수를 가져옵니다.

class MainUI:
    def __init__(self, root, v1, v2, dmm):
        self.root = root
        self.root.title("Main UI")
        self.root.geometry("400x700")
        
        # 장비 객체 저장
        self.v1 = v1
        self.v2 = v2
        self.dmm = dmm

        tk.Label(self.root, text="Measurement System", font=("Arial", 16, "bold")).pack(pady=20)

        # 1. 설정 관련 버튼들
        tk.Button(self.root, text="DMM:Set PLC", width=25, font=("Arial", 12),
                  command=self.open_plc).pack(pady=5)
        
        tk.Button(self.root, text="Yoko:Voltage Range", width=25, font=("Arial", 12),
                  command=self.open_range).pack(pady=5)
        
        tk.Button(self.root, text="Local Mode Settings", width=25, font=("Arial", 12), 
                  command=self.open_local_ui).pack(pady=5)

        # 2. 제어 관련 버튼들
        tk.Button(self.root, text="Yoko:Output Control", width=25, font=("Arial", 12),
                  command=self.open_output_control).pack(pady=5)

        # 3. 측정 관련 버튼들
        tk.Button(self.root, text="Current(1D: V)", width=25, font=("Arial", 12), bg="lightblue",
                  command=self.open_sweep_input).pack(pady=20)
        
        tk.Button(self.root, text="Current(V vs I)", width=25, font=("Arial", 12), bg="lightgreen",
                  command=self.open_mosfet_ui).pack(pady=5)
        
        # 4. 비상 정지 버튼
        tk.Button(self.root, text="STOP MEASUREMENT", width=25, font=("Arial", 12, "bold"), 
                  bg="red", fg="white", command=stop_measurement).pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.data_queue = queue.Queue()

    # --- 버튼 연결 함수들 ---

    def open_plc(self):
        self.plc_window = PLCWindow(self.root, self.dmm) # 변수에 할당하여 참조 유지

    def open_range(self):
        self.range_window = RangeWindow(self.root, self.v1, self.v2)

    def open_local_ui(self):
        self.local_win = LocalModeWindow(self.root, self.v1, self.v2, self.dmm)

    def open_output_control(self):
        self.output_win = OutputControlWindow(self.root, self.v1, self.v2)

    def open_sweep_input(self):
        self.sweep_window = SweepInputWindow(self.root, self.v1, self.v2, self.dmm, self.start_sweep_1d_thread)
    
    def open_mosfet_ui(self):
        self.mosfet_win = MosfetMeasurementWindow(self.root, self.v1, self.v2, self.dmm, self.start_sweep_2d_thread)
    
    # --- 스레드 실행 함수들 ---

    def start_sweep_1d_thread(self, device, dmm, **kwargs):
        # 1. 그래프 창 열기
        self.graph_win = RealTimeGraphWindow(self.root, "1D Real-Time Sweep")
        
        # 2. 큐 초기화 및 인자 추가
        self.data_queue = queue.Queue()
        kwargs['data_queue'] = self.data_queue # sweep 함수에 큐 전달
        
        # 3. 스레드 시작
        t = threading.Thread(target=current_sweep_1d, args=(device, dmm), kwargs=kwargs)
        t.daemon = True
        t.start()
        
        # 4. 감시 시작 (0.1초마다 큐 확인)
        self.root.after(100, self.process_queue)

    def start_sweep_2d_thread(self, v1, v2, dmm, **kwargs):
        self.graph_win = RealTimeGraphWindow(self.root, "2D Real-Time Sweep")
        
        self.data_queue = queue.Queue()
        kwargs['data_queue'] = self.data_queue
        
        t = threading.Thread(target=current_sweep_2d, args=(v1, v2, dmm), kwargs=kwargs)
        t.daemon = True
        t.start()
        
        self.root.after(100, self.process_queue)

    def process_queue(self):
        """큐에서 데이터를 꺼내 그래프를 업데이트하는 함수 (메인 스레드에서 실행됨)"""
        try:
            # 큐에 쌓인 데이터 처리 (비어있지 않은 동안 계속)
            while not self.data_queue.empty():
                msg = self.data_queue.get_nowait()
                
                command = msg[0]
                
                if command in ["data_1d", "data_2d"]:
                    x, y = msg[1], msg[2]
                    # 그래프 창이 살아있을 때만 업데이트
                    if self.graph_win.window.winfo_exists():
                        self.graph_win.update_plot(x, y)
                
                elif command == "new_step":
                    # msg[1]에 들어있는 전압값(v2_val)을 꺼냅니다.
                    step_voltage = msg[1]
                    
                    if self.graph_win.window.winfo_exists():
                        # [핵심] 그래프 창에 전압값을 그대로 전달합니다.
                        self.graph_win.new_step(step_voltage)
                
                elif command == "finish":
                    print("[System] Measurement Complete.")
                    return # 감시 종료

        except queue.Empty:
            pass
        
        # 0.1초 뒤에 다시 확인
        self.root.after(100, self.process_queue)
    
    def on_exit(self):
        """프로그램 우측 상단 X 버튼을 눌렀을 때 실행되는 안전 종료 로직"""
        print("[System] Exiting and cleaning up...")
        try:
            stop_measurement()         
            self.v1.output_control("OFF")
            self.v2.output_control("OFF")
            self.v1.set_voltage(0)
            self.v2.set_voltage(0)
            self.v1.set_local()
            self.v2.set_local()
            self.dmm.set_local()
        except Exception as e:
            print(f"[Warning] Error during cleanup: {e}")
        self.root.destroy()