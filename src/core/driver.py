import pyvisa # PyVISA 라이브러리 임포트
import time # 지연 시간 설정을 위한 모듈
import numpy as np # 전압 배열 생성을 위한 모듈

class GS200:
    """Yokogawa GS200 전압 소스 드라이버 클래스 (V1, V2 각각 생성하여 사용)"""
    
    def __init__(self, resource_manager, address, alias="GS200"):
        # resource manager를 통해 개별 장비(주소로 식별)에 연결
        self.device = resource_manager.open_resource(address)
        # 장비 식별을 위한 별칭 설정 (V1 또는 V2)
        self.alias = alias
        # 초기화 시 전압 모드로 설정
        self.device.write("SOUR:FUNC VOLT")

    def set_voltage(self, value):
        # 특정 전압 값을 인가
        self.device.write(f"SOUR:LEV {value}")

    def set_range(self, r_value):
        # 전압 출력 범위를 설정
        self.device.write(f"SOUR:RANG {r_value}")

    def output_control(self, state):
        # 출력을 ON 또는 OFF로 설정
        self.device.write(f"OUTP {state}")

    def set_local(self):
        # 장비 패널에서 직접 조작 가능한 LOCAL 모드로 전환
        self.device.write("SYST:LOC")

    def back_zero(self, current_voltage, step_size=0.01, step_time=0.1):
        """현재 전압에서 0V까지 안전하게 단계적으로 낮춤 (main3.py의 back_zero 함수 로직)"""
        # 전압 이동 방향 결정 
        step_direction = -step_size if current_voltage > 0 else step_size
        # np.arange를 사용하여 이동할 전압 리스트 생성
        voltages = np.arange(current_voltage, 0, step_direction)

        for v in voltages:
            self.set_voltage(v) # 각 단계 전압 설정
            time.sleep(step_time) # 지연 시간 대기

        self.set_voltage(0) # 마지막에 정확히 0V 인가
        print(f"[{self.alias}] Voltage successfully adjusted to 0V.")

    def close(self):
        # VISA 리소스 연결 해제
        self.device.close()


class DMM:
    """디지털 멀티미터 드라이버 클래스"""

    def __init__(self, resource_manager, address):
        # 개별 DMM 장비 연결
        self.device = resource_manager.open_resource(address)

    def set_plc(self, value):
        # 측정 정밀도(NPLC) 설정
        self.device.write(f"SENS:VOLT:DC:NPLC {value}")

    def read_value(self):
        # 현재 측정값을 쿼리하고 실수형으로 변환
        return float(self.device.query("READ?").strip())

    def set_local(self):
        # DMM을 로컬 모드로 전환
        self.device.write("SYST:LOC")

    def close(self):
        # VISA 리소스 연결 해제
        self.device.close()