import tkinter as tk
import sys
import os

# [경로 설정] 현재 파일(tests)의 상위 폴더(루트)를 sys.path에 추가하여 src 모듈 인식
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MainUI 임포트
from src.gui.main_ui import MainUI

# [수정] 기능 확장에 맞춘 가짜 장비 클래스
class MockDevice:
    def __init__(self, name):
        self.name = name # 장비 구분을 위한 이름 저장 (예: V1, V2, DMM)

    # --- 기본 제어 (MainUI / Local UI 용) ---
    def set_local(self): 
        print(f"[{self.name}] Local Mode Set")
        
    def output_control(self, state): 
        print(f"[{self.name}] Output turned {state}")
        
    def set_voltage(self, v): 
        # 1D/2D Sweep에서 호출됨
        print(f"[{self.name}] Setting Voltage to {v:.4f}V")
        
    def set_plc(self, v): 
        print(f"[{self.name}] PLC set to {v}")
        
    def set_range(self, v): 
        print(f"[{self.name}] Range set to {v}V")

    # --- Sweep 로직 지원 (Sweep.py 용) ---
    def read_value(self): 
        # DMM이 값을 읽는 동작 흉내 (임의의 값 반환)
        import random
        val = random.uniform(0.001, 0.005)
        # 로그가 너무 많아지는 것을 방지하기 위해 print는 생략하거나 주석 처리 가능
        # print(f"[{self.name}] Reading value: {val:.5f}")
        return val

    def back_zero(self, current_v):
        # Sweep 종료 후 0V 복귀 동작 흉내
        print(f"[{self.name}] Safety Ramping: {current_v}V -> 0V")

if __name__ == "__main__":
    # 1. 윈도우 생성
    root = tk.Tk()
    
    # 2. [중요] 이름표(Alias)를 붙인 Mock 장비 생성
    mock_v1 = MockDevice("GS200_V1")
    mock_v2 = MockDevice("GS200_V2")
    mock_dmm = MockDevice("DMM_Keithley")

    # 3. 메인 UI 실행 (가짜 장비 주입)
    print("[Test] Starting Mock Application...")
    print("[Test] You can test: Local Mode (Individual), 1D Sweep, 2D Sweep")
    
    app = MainUI(root, v1=mock_v1, v2=mock_v2, dmm=mock_dmm)
    
    root.mainloop()