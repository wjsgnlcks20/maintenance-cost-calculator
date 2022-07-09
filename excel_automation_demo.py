import xlrd
import xlwt
from maintenance_cost_calculator import maintenance_cost_calculator

DATA_FILENAME = "데이터.xls"
PRINT_FILENAME = "소액관리비분류완료.xls"
BUILDING_DEFAULT_COST_FILENAME = "건물기본비용.xls"
DATA_PRINT_COL_GAP = 1

# 입력 엑셀 속성 이름
COST_ATT = "입금"
BUILDING_ATT = "건물이름"
MAXIMUM_CALCULATE_COST = 150000

# 출력 엑셀 속성 이름
COST_CLASS = "비용 분류"
MAINTENANCE_COST = "관리비"
REMAIN_BALANCE = "그 외 비용"
STATUS = "관리비 결정 방식"


# 건물 기본값 받아오기
def get_building_default_cost():
    building_default_cost = {}

    read_wb = xlrd.open_workbook(BUILDING_DEFAULT_COST_FILENAME)
    sheet = read_wb.sheet_by_index(0)

    for row in range(sheet.nrows):
        building_default_cost[sheet.cell_value(row, 0)] = sheet.cell_value(row, 1)

    return building_default_cost

# 출력 파일의 기초값 설정 (기존 파일 값 복사하기)
# 새로운 값을 작성할 수 있는 최소 col 값 반환.
def init_write_file(write_file, read_file):
    for i in range(read_file.nrows):
        for j in range(read_file.ncols):
            write_file.write(i, j, read_file.cell_value(i, j))

    return read_file.ncols

# 추가 속성이 시작될 수 있는 위치를 결정
def get_add_col_start(minimum_col_start):
    return minimum_col_start + DATA_PRINT_COL_GAP

# 출력 파일 속성 작성
def add_col_to_write_file(write_file, col_name, col_start):
    for i in range(len(col_name)):
        write_file.write(0, col_start + i, col_name[i])

# 출력 파일의 속성을 가져온다(데이터 파일 속성 + 추가 속성)
def get_added_col(read_file, add_col_names, col_start):
    col_names = []
    for i in range(col_start):
        if i < read_file.ncols:
            col_names.append(read_file.cell_value(0, i))
        else:
            col_names.append(f"blank{i}")
    col_names += add_col_names
    return col_names

# 속성의 이름들에 대해서 인덱싱을 해줌
def index_col(col_names):
    indexing = {}
    for i, col_name in enumerate(col_names):
        indexing[col_name] = i
    return indexing

# 프로그램 실행
def process_maintenance_data():
    # 파일에서 건물 기본값, 계산초과기준비용 가져오기
    building_default_cost = get_building_default_cost()
    maximum_calculate_cost = MAXIMUM_CALCULATE_COST

    # 데이터 및 출력 파일 불러오기
    read_wb = xlrd.open_workbook(DATA_FILENAME)
    read_ws = read_wb.sheet_by_index(0)

    write_wb = xlwt.Workbook(encoding="utf-8")
    write_ws = write_wb.add_sheet("sheet1")

    # 출력 파일 초기화 및 col 설정
    minimum_col_start = init_write_file(write_ws, read_ws)
    add_col_start = get_add_col_start(minimum_col_start)

    add_col_names = [ COST_CLASS, MAINTENANCE_COST, REMAIN_BALANCE, STATUS ]
    add_col_to_write_file(write_ws, add_col_names, add_col_start)
    col_names = get_added_col(read_ws, add_col_names, add_col_start)

    # 파일 작성 시 col 값 인덱싱
    indexing = index_col(col_names)

    # 각 데이터 별 처리
    for cur_row in range(1, read_ws.nrows):

        # 입금내역과 건물이름을 가져온다
        cost = read_ws.cell_value(cur_row, indexing[COST_ATT])
        building_name = read_ws.cell_value(cur_row, indexing[BUILDING_ATT])

        # 관리비와 상태(계산방식 등)을 구한다
        maintenance_cost, status = maintenance_cost_calculator(cost, building_name, building_default_cost, maximum_calculate_cost)

        # 셀이 빈 ""이 int 처리되어야 하는 경우에 대해서 조금 더 깔끔하게 처리해보고 싶은데...
        write_ws.write(cur_row, indexing[STATUS], status)
        if maintenance_cost == "":
            continue
        write_ws.write(cur_row, indexing[COST_CLASS], "관리비")
        write_ws.write(cur_row, indexing[MAINTENANCE_COST], maintenance_cost)
        write_ws.write(cur_row, indexing[REMAIN_BALANCE], int(cost) - maintenance_cost)
        # 남은 금액 음수 나오는 경우 확인
        if int(cost) - maintenance_cost < 0:
            print(f"on row num: {cur_row}, there's a negative balance!")

    # 파일 저장
    write_wb.save(PRINT_FILENAME)
