import xlrd
import xlwt
from maintenance_cost_calculator import get_output

DATA_FILENAME = "데이터.xls"
PRINT_FILENAME = "소액관리비분류완료.xls"

FREE_PASS_FILENAME = "관리비비용청구불필요.xls"
EXCEPTION_FILENAME = "수리비기준.xls"
DEFAULT_COST_FILENAME = "기본비용.xls"

DATA_PRINT_COL_GAP = 1

# 입력 엑셀 속성 이름
COST_ATT = "입금금액"
NAME_ATT = "거래기록사항"

# 출력 엑셀 속성 이름
DEPOSIT_HISTORY = "입금내역"
DEPOSIT_SPECIFIC = "입금상세내역"
MAINTENANCE_COST = "수입금액"
REMAIN_BALANCE = "수입제외금액"
STATUS = "관리비 결정 방식"

################################### 박제

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
        write_file.write(7, col_start + i, col_name[i])

# 출력 파일의 속성을 가져온다(데이터 파일 속성 + 추가 속성)
def get_added_col(read_file, add_col_names, col_start):
    col_names = []
    for i in range(col_start):
        if i < read_file.ncols:
            col_names.append(read_file.cell_value(7, i))
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
################################### 박제

# 데이터로 활용해야 할 파일들을 열어서 데이터 화 해둔 뒤,
# 각 열마다 데이터를 처리하려고 할 때 파라미터로 같이 보내면 메모리와 시간을 절약.

def get_default_cost_data():
    default_cost = {}

    read_wb = xlrd.open_workbook(DEFAULT_COST_FILENAME)
    sheet = read_wb.sheet_by_index(0)

    for row in range(sheet.nrows):
        default_cost[sheet.cell_value(row, 0)] = sheet.cell_value(row, 1)

    return default_cost

def get_free_pass_data():
    wb = xlrd.open_workbook(FREE_PASS_FILENAME)
    read_file = wb.sheet_by_index(0)

    free_pass_data = {}
    for row in range(1, read_file.nrows):
        deposit_specific = str(read_file.cell_value(row, 0))
        name = str(read_file.cell_value(row, 1))
        free_pass_data[deposit_specific + name] = (read_file.cell_value(row, 2), read_file.cell_value(row, 3))

    return free_pass_data

def get_exception_data():
    wb = xlrd.open_workbook(EXCEPTION_FILENAME)
    read_file = wb.sheet_by_index(0)

    exception_data = {}
    for row in range(1, read_file.nrows):
        exception_data[read_file.cell_value(row, 0)] = (read_file.cell_value(row, 1), read_file.cell_value(row, 2), read_file.cell_value(row, 3))
    return exception_data

# 프로그램 실행
def process_maintenance_data():
    # 파일에서 건물 기본값, 계산초과기준비용 가져오기

    # 데이터 및 출력 파일 불러오기
    read_wb = xlrd.open_workbook(DATA_FILENAME)
    read_ws = read_wb.sheet_by_index(0)

    write_wb = xlwt.Workbook(encoding="utf-8")
    write_ws = write_wb.add_sheet("sheet1", cell_overwrite_ok=True)

    # 출력 파일 초기화 및 col 설정
    minimum_col_start = init_write_file(write_ws, read_ws)
    add_col_start = get_add_col_start(minimum_col_start)

    add_col_names = [ STATUS ]
    add_col_to_write_file(write_ws, add_col_names, add_col_start)
    col_names = get_added_col(read_ws, add_col_names, add_col_start)

    # 파일 작성 시 col 값 인덱싱
    indexing = index_col(col_names)

    # 데이터 처리 시 필요한 파일 데이터 가공
    free_pass_data = get_free_pass_data()
    exception_data = get_exception_data()
    default_cost_data = get_default_cost_data()

    # 각 데이터 별 처리
    for cur_row in range(8, read_ws.nrows - 1):
        # 입력된 데이터가 있는 경우 계산하지 않는다.
        if read_ws.cell_value(cur_row, indexing[REMAIN_BALANCE]):
            continue

        # 입금내역과 거래기록사항을 가져온다
        cost = read_ws.cell_value(cur_row, indexing[COST_ATT])
        name = str(read_ws.cell_value(cur_row, indexing[NAME_ATT]))

        # 관리비와 상태(계산방식 등)을 구한다
        deposit_history, deposit_specific, maintenance_cost, status = get_output(cost, name, free_pass_data, exception_data, default_cost_data)

        # 파일에 작성
        try:
            write_ws.write(cur_row, indexing[STATUS], status)
            write_ws.write(cur_row, indexing[DEPOSIT_HISTORY], deposit_history)
            write_ws.write(cur_row, indexing[DEPOSIT_SPECIFIC], deposit_specific)
            write_ws.write(cur_row, indexing[MAINTENANCE_COST], maintenance_cost)
            write_ws.write(cur_row, indexing[REMAIN_BALANCE], int(cost) - maintenance_cost)
        except:
            continue

        if int(cost) < maintenance_cost:
            print(f"on row num: {cur_row}, there's a negative balance!")

    # 파일 저장
    write_wb.save(PRINT_FILENAME)
