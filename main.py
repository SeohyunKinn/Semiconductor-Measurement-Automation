import tkinter as tk
from tkinter import messagebox
import pyvisa # VISA 통신
import sys # 시스템 종료

# 프로젝트 내부 모듈 임포트
from configs.device_configs import V1_ADDRESS, V2_ADDRESS, DMM_ADDRESS, initialize_directories # 설정값
from src.core.driver import GS200, DMM # 장비 드라이버
from src.gui.main_ui import MainUI # 메인 UI 클래스

def main():
    # 1. 실험 결과 저장 폴더 구조 생성
    initialize_directories()

    # 2. PyVISA 리소스 관리자 초기화
    rm = pyvisa.ResourceManager()
    
    try:
        # 실제 장비 연결 시도
        v1 = GS200(rm, V1_ADDRESS, alias="V1")
        v2 = GS200(rm, V2_ADDRESS, alias="V2")
        dmm = DMM(rm, DMM_ADDRESS)
        
        print(f"[System] Connected to V1({V1_ADDRESS}), V2({V2_ADDRESS}), DMM({DMM_ADDRESS})")
        
    except Exception as e:
        # [테스트용] 연결 실패 시 Mock(가상) 장비로 자동 전환 (개발 편의성)
        print(f"[Warning] Connection failed: {e}")
        print("[System] Switching to Mock Mode for testing...")
        
        # 가상 장비 클래스 내부 정의
        class MockDev:
            def __init__(self, n): self.n = n
            def write(self, c): print(f"[{self.n}] Write: {c}")
            def set_voltage(self, v): print(f"[{self.n}] Set V: {v}")
            def set_local(self): pass
            def output_control(self, s): print(f"[{self.n}] Output: {s}")
            def set_range(self, r): print(f"[{self.n}] Range: {r}")
            def set_plc(self, p): print(f"[{self.n}] PLC: {p}")
            def read_value(self): return 0.001
            def back_zero(self, v): print(f"[{self.n}] Ramping down...")

        v1 = MockDev("V1")
        v2 = MockDev("V2")
        dmm = MockDev("DMM")

    # 3. 메인 Tkinter 윈도우 실행
    root = tk.Tk()
    app = MainUI(root, v1, v2, dmm)
    
    print("[System] Application started successfully.")
    root.mainloop()

if __name__ == "__main__":
    main()