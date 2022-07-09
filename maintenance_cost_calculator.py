# 관리비 계산식
def get_maintenance_cost(cost):
    return 10000 + (cost // 10000) * 1000

def get_discounted_cost(cost):
    return round(float(cost) / 2, 0)

# 입금 금액에 따라 최종 관리비와 그 외 비용을 결정함. 결정 상태도 반환.
def maintenance_cost_calculator(cost, building_name, building_default_cost, maximum_calculate_cost):
    # 입금이 아닌 출금인 경우 -> cost 가 비어있음. 손댈필요 x
    if cost == "":
        return "", "출금"

    cost = int(cost)
    # 계산초과기준금액 초과인 경우
    if cost > maximum_calculate_cost:
        return "", "기준금액 초과, 추후 계산 필요"

    default_cost = building_default_cost.get(building_name)
    # 건물 관리 비용 없음, 계산식에 의한 계산
    if not default_cost:
        default_cost = get_maintenance_cost(cost)
        status = "건물 기본 등록비용 없음. 계산에 의한 관리비"
    # 건물 관리 비용 존재
    else:
        status = "건물 기본 등록비용"

    # 입금 금액보다 비용이 큰 경우 입금 금액의 50% 청구
    if cost < default_cost:
        return get_discounted_cost(cost), "건물 기본 등록비용 미만, 수정된 가격"

    return default_cost, status
