
MAXIMUM_MOVING_COST = 300000
MAXIMUM_MAINTENANCE_COST = 160000
MAXIMUM_CALCULATE_COST = 100000
DIVIDE_BY = 1000
OVER_CALCULATION_MAINTENANCE_COST = 26000

# 이름에 호수가 포함된 경우 저장된 이름으로 변경해준다.
def get_labeled_name(input_name, labeled_names):
    for labeled_name in labeled_names:
        if input_name.find(labeled_name) >= 0:
            print(f"found labeled name! for {input_name} -> {labeled_name}")
            return labeled_name
    return "no_labeled_name"

# 입금상세내역 주택, 집단 오피스텔 확인
def get_deposit_specific(name):
     if name.find("크리스탈") >= 0 or name.find("야베스") >= 0:
        return "집단 오피스텔"
     else: return "주택"

# 관리비 계산식
def get_maintenance_cost(cost):
    if cost // 10000 == 1:
        return 12000
    return 10000 + (cost // 10000) * 1000

def get_discounted_cost(cost):
    return round(float(cost) / 2, 0)

# 3, 4번 기본값 받아오기
def no_data_maintenance_cost_calculator(cost, name, default_cost):

    cost = int(cost)
    default_cost_names = []
    for key in default_cost.keys():
        default_cost_names.append(key)

    final_cost = default_cost.get(get_labeled_name(name, default_cost_names))
    if get_deposit_specific(name) == "집단 오피스텔":
        if not final_cost:
            final_cost = get_maintenance_cost(cost)
        if cost < final_cost:
            final_cost = get_discounted_cost(cost)
        return "관리비 수익", get_deposit_specific(name), final_cost, "집단 오피스텔"

    # 계산초과기준금액 초과인 경우
    if cost > MAXIMUM_MOVING_COST:
        return "", "", "", "계산 기준 금액 초과, 추후 계산"
    elif MAXIMUM_MAINTENANCE_COST <= cost < MAXIMUM_MOVING_COST:
        return "대납비", "이사정산", 0, "이사정산"
    elif cost % DIVIDE_BY == 0:
        return "대납비", "수리비", 0, "깔끔하게 떨어지는 수리비"
    elif MAXIMUM_CALCULATE_COST <= cost < MAXIMUM_MAINTENANCE_COST:
        return "관리비 수익", get_deposit_specific(name), OVER_CALCULATION_MAINTENANCE_COST, "10만 이상 관리비"

    # 건물 관리 비용 없음, 계산식에 의한 계산
    if not final_cost:
        final_cost = get_maintenance_cost(cost)
        status = "건물 기본 등록비용 없음. 계산에 의한 관리비"
    else:
        status = "건물 기본 등록비용"

    # 건물 관리 비용 존재, 보다 아래인 경우 50%
    if cost < final_cost:
        final_cost = get_discounted_cost(cost)
        status = "건물 기본 등록비용 미만, 수정된 가격"

    # 건물 관리 비용 존재, 보다 이상인 경우
    return "관리비 수익", get_deposit_specific(name), final_cost, status

# 1번 관리비비용청구 불필요인 경우
def free_pass_calculator(name, free_pass_data):
    labeled_name = []
    for key in free_pass_data.keys():
        labeled_name.append(key)
    name = get_labeled_name(name, labeled_name)

    deposit_data = free_pass_data.get(name)
    if not deposit_data:
        return "", ""
    return deposit_data[0], deposit_data[1]

# 2번 특수 경우 처리
def exception_calculator(cost, name, exception_data):
    labeled_name = []
    for key in exception_data.keys():
        labeled_name.append(key)
    name = get_labeled_name(name, labeled_name)
    if name == "no_labeled_name":
        return "", "", "", ""

    if name == "정성용" or name == "이해권":
        if cost < int(exception_data[name][2]):
            return "대납액", "수리비", 0, "대납액 수리비 처리"
        else:
            return "", "", "", "계산 기준 금액 초과, 추후 처리"
    if name == "이석재":
        if cost == int(exception_data[name][2]):
            return exception_data[name][0], get_deposit_specific(name), exception_data[name][2], "관리비 수입 처리"
        else :
            return "대납액", "수리비", 0, "대납액 수리비 처리"

    if exception_data[name][0] == "대납액":
        return exception_data[name][0], exception_data[name][1], 0, "대납액 수리비 처리"
    else:
        if cost < int(exception_data[name][2]):
            return "대납액", "수리비", 0, "대납액 수리비 처리"
        else:
            return exception_data[name][0], get_deposit_specific(name), exception_data[name][2], "관리비 수입 처리"

# 새로운 maintenance_calculator
def get_output(cost, name, free_pass_data, exception_data, default_cost_data):

    # 입금이 아닌 출금인 경우 -> cost 가 비어있음. 손댈필요 x
    if cost == "":
        return "", "", "", "출금"

    # 1. 관리비비용청구 불필요
    deposit_history, deposit_specific = free_pass_calculator(name, free_pass_data)
    if deposit_history != "":
        return deposit_history, deposit_specific, 0, "기신고 및 수리비(관리비청구불필요)"

    # 2. 특수 경우 처리(수리비 판단 여부 기준, 특수 경우 예외처리)
    deposit_history, deposit_specific, final_cost, status = exception_calculator(cost, name, exception_data)
    if deposit_history != "":
        return deposit_history, deposit_specific, final_cost, status

    # 3, 4. 기본값 확인 후 없는경우 계산식으로 처리.
    return no_data_maintenance_cost_calculator(cost, name, default_cost_data)
