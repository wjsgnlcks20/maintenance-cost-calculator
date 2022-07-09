import xlwt
import random

TEST_LIMIT = 10000

def generate_random_data():
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet('sheet1')

    col_names = [ "이름", "출금", "입금", "건물이름" ]
    building_names = [ "A빌라", "A아파트", "B빌라", "B아파트", "C빌라", "C아파트" ]

    for i, col_name in enumerate(col_names):
        ws.write(0, i, col_name)

    for i in range(TEST_LIMIT):
        ws.write(i + 1, 2, random.randrange(9000, 200000))
        ws.write(i + 1, 3, building_names[random.randrange(0, len(building_names))])

    wb.save("데이터.xls")
