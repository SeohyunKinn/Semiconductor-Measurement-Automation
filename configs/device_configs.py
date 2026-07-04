import os 

# 1. 장비 주소 설정
V1_ADDRESS = "GPIB0::1::INSTR"
V2_ADDRESS = "GPIB0::11::INSTR"
DMM_ADDRESS = "GPIB0::22::INSTR"

# 2. 경로 설정 
BASE_EXP_PATH = "experiments"
DATA_SAVE_PATH = os.path.join(BASE_EXP_PATH, "data")      # 수치 데이터 (.txt, .csv) 저장 경로
FIGURE_SAVE_PATH = os.path.join(BASE_EXP_PATH, "figures")  # 그래프 이미지 (.png) 저장 경로

# 프로그램 실행 시 폴더가 없으면 에러가 발생하므로, 자동으로 폴더를 생성하는 함수를 정의.
def initialize_directories():
    for path in [DATA_SAVE_PATH, FIGURE_SAVE_PATH]:
        if not os.path.exists(path):
            os.makedirs(path) # 하위 폴더까지 한꺼번에 생성합니다.
            print(f"[System] Created directory: {path}")

initialize_directories()