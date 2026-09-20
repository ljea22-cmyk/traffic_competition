import pandas as pd

# ===== 저상버스 보유율 낮은 노선 TOP 10 (보조지표) =====
PATH_BUS = "서울시 저상버스 도입 노선 및 노선별 보유율.csv"
bus = pd.read_csv(PATH_BUS, encoding="cp949")

print("전체 노선 평균 저상보유율:", round(bus["보유율"].mean(), 1), "%")

bus_low10 = bus.sort_values("보유율").head(10)
print("\n=== 저상버스 보유율 낮은 노선 TOP 10 ===")
print(bus_low10.to_string(index=False))

bus_low10.to_csv("저상버스_보유율_낮은노선_TOP10.csv", index=False, encoding="utf-8-sig")