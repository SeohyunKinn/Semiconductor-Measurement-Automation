import sys
import os
import time
import threading

# 1. 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# 2. 프로젝트 모듈 임포트
try:
    from src.core.sweep import current_sweep_1d, stop_measurement
    from configs.device_configs import initialize_directories 
except ImportError as e:
    print(f"[Critical Error] 모듈을 불러오는데 실패했습니다: {e}")
    sys.exit(1)

# --- Mock Classes ---
class MockDevice:
    def set_voltage(self, v): 
        pass 
    def back_zero(self, v): 
        print(f"[Mock GS200] Ramping down from {v}V to 0V")

class MockDMM:
    def read_value(self): 
        return 0.0015 

# --- Test Functions ---
def run_test_sweep():
    """1D Sweep 로직이 데이터 저장까지 오류 없이 완수하는지 테스트합니다."""
    print("\n--- Test 1: Normal Sweep Logic ---")
    mock_v = MockDevice()
    mock_dmm = MockDMM()
    
    # 5단계의 짧은 스윕 실행 (0V ~ 1V)
    print(">> 스윕 시작...")
    
    # [수정됨] 인자 이름을 sweep.py 정의(device, dmm)와 일치시킴
    current_sweep_1d(
        device=mock_v,      # device_v -> device
        dmm=mock_dmm,       # device_i -> dmm
        min_v=0, 
        max_v=1, 
        steps=5, 
        delay=0.05, 
        sensitivity=1e-5, 
        ramping_key=1
    )
    print(">> 스윕 정상 종료 확인.")

def run_test_stop():
    """측정 도중 stop_measurement가 호출되었을 때 루프가 즉시 멈추는지 테스트합니다."""
    print("\n--- Test 2: Stop Functionality ---")
    mock_v = MockDevice()
    mock_dmm = MockDMM()
    
    # [수정됨] 여기도 인자 순서에 맞게 positional arguments로 전달하거나 키워드 수정 필요
    # current_sweep_1d(device, dmm, min_v, max_v, steps, delay, sensitivity, ramping_key)
    t = threading.Thread(target=current_sweep_1d, 
                         args=(mock_v, mock_dmm, 0, 10, 100, 0.1, 1e-5, 1))
    t.start()
    print(">> 백그라운드 측정 스레드 시작됨")
    
    time.sleep(1) 
    
    print(">> [Test] STOP 신호 발생!")
    stop_measurement() 
    
    t.join() 
    print(">> 측정 스레드가 종료되었습니다 (정상적으로 멈춤).")

if __name__ == "__main__":
    print(f"[Test Started] Project Root: {project_root}")
    initialize_directories()
    run_test_sweep()
    run_test_stop()