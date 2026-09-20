import pandas as pd
import re
import matplotlib.pyplot as plt

# ===== 0. 폰트 설정 (맥 기준) =====
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# ===== 1. 파일 경로 =====
PATH_FACILITY = "서울시 지하철 역사 노약자 장애인 편의시설 현황.csv"
PATH_ADDRESS  = "서울교통공사_역주소 및 전화번호.csv"
PATH_RIDERSHIP = "CARD_SUBWAY_MONTH_202608.csv"

# ===== 2. 데이터 로드 =====
fac = pd.read_csv(PATH_FACILITY, encoding="cp949")
addr = pd.read_csv(PATH_ADDRESS, encoding="cp949")
ride = pd.read_csv(PATH_RIDERSHIP, encoding="utf-8-sig", index_col=False)

# ===== 3. 정규화 함수 =====
def norm(n):
    return re.sub(r'\(.*?\)', '', str(n)).strip()

def norm_line(l):
    return re.sub(r'\(.*?\)', '', str(l)).strip()

def extract_gu(road_addr):
    if pd.isna(road_addr):
        return None
    m = re.search(r'(\S+?[시도])\s+(\S+?[구군])\s', road_addr)
    if m:
        return m.group(2)
    m2 = re.search(r'(\S+?[시도])\s+(\S+?시)\s', road_addr)
    if m2:
        return m2.group(2)
    return None

# ===== 4. 자치구 추출 + 역명 정규화 =====
addr["자치구"] = addr["도로명주소"].apply(extract_gu)
addr["역명_정규화"] = addr["역명"].apply(norm)
addr.loc[addr["역명_정규화"] == "서울", "역명_정규화"] = "서울역"
addr_dedup = addr.drop_duplicates(subset="역명_정규화", keep="first")[["역명_정규화", "자치구"]]

fac["역명_정규화"] = fac["역명"].apply(norm)
fac["호선_정규화"] = fac["호선"].apply(norm_line)

# ===== 5. 승하차인원 호선별 월간 합계 (같은 역이라도 호선별로 따로 집계) =====
ride["역명_정규화"] = ride["역명"].apply(norm)
ride["호선_정규화"] = ride["노선명"].apply(norm_line)
ride_line_sum = ride.groupby(["호선_정규화", "역명_정규화"])[["승차총승객수", "하차총승객수"]].sum().reset_index()
ride_line_sum["월간총이용객수"] = ride_line_sum["승차총승객수"] + ride_line_sum["하차총승객수"]

# ===== 6. 전체 병합 =====
final = fac.merge(addr_dedup, on="역명_정규화", how="left")
final.loc[final["역명"].str.contains("암사역사공원", na=False), "자치구"] = "강동구"
final = final.merge(
    ride_line_sum[["호선_정규화", "역명_정규화", "월간총이용객수"]],
    on=["호선_정규화", "역명_정규화"], how="left"
)

# ===== 7. 엘리베이터 1대당 이용객수 =====
final["EV1대당_이용객수"] = final.apply(
    lambda r: r["월간총이용객수"] / r["엘리베이터(E/V)"] if r["엘리베이터(E/V)"] > 0 else None,
    axis=1
)
median_val = final["EV1대당_이용객수"].median()
print("전체 274개 역(호선별) 중앙값:", round(median_val))

final.to_csv("최종_역별_통합데이터.csv", index=False, encoding="utf-8-sig")

# ===== 8. TOP 10 + 도곡역(엘리베이터 0대) 강조 차트 =====
top10 = final.sort_values("EV1대당_이용객수", ascending=False).head(10).copy()
top10["표시명"] = top10["역명"].str.replace(r"\(.*?\)", "", regex=True) + " (" + top10["자치구"] + ")"
top10 = top10.sort_values("EV1대당_이용객수")

dogok = final[final["역명"].str.contains("도곡", na=False)].iloc[0]

seq_ramp = ["#9ec5f4","#86b6ef","#6da7ec","#5598e7","#3987e5","#2a78d6","#256abf","#1c5cab","#184f95","#104281"]
accent = "#eb6834"
muted_axis = "#898781"
grid_color = "#e1e0d9"
text_primary = "#0b0b0b"
text_secondary = "#52514e"
surface = "#fcfcfb"

fig, ax = plt.subplots(figsize=(9, 7.2), dpi=150)
fig.patch.set_facecolor(surface)
ax.set_facecolor(surface)

max_val = top10["EV1대당_이용객수"].max()
dogok_bar_len = max_val * 1.08

bar_positions = list(range(len(top10)))
colors = [seq_ramp[min(i, len(seq_ramp)-1)] for i in range(len(top10))]
ax.barh(bar_positions, top10["EV1대당_이용객수"], color=colors, height=0.62, zorder=3)

dogok_y = len(top10) + 1.0
ax.barh([dogok_y], [dogok_bar_len], color=accent, height=0.62, zorder=3,
        hatch="////", edgecolor="white", linewidth=0.6)

for y, (val, name) in zip(bar_positions, zip(top10["EV1대당_이용객수"], top10["표시명"])):
    ax.text(val - max_val*0.015, y, f"{name}  {val/10000:.0f}만명/대", va="center", ha="right",
             fontsize=9.5, color="white" if val > max_val*0.35 else text_primary, zorder=4)

ax.text(dogok_bar_len - max_val*0.015, dogok_y,
        f"도곡역 (강남구)  월 {dogok['월간총이용객수']/10000:.1f}만명 · 엘리베이터 0대",
        va="center", ha="right", fontsize=10, color="white", fontweight="bold", zorder=4)

ax.axvline(median_val, color=muted_axis, linestyle="--", linewidth=1.1, zorder=2)
ax.text(median_val, dogok_y + 1.0, f"전체 274개 역(호선별) 중앙값\n{median_val/10000:.1f}만명/대",
        ha="center", va="bottom", fontsize=8.5, color=text_secondary)

ax.set_yticks([])
ax.set_xlabel("엘리베이터 1대당 월간 이용객수 (명)", fontsize=10, color=text_secondary)
ax.set_title("서울 지하철 엘리베이터 1대당 이용 부담 상위 역 (2026년 8월 기준)",
              fontsize=13, color=text_primary, fontweight="bold", pad=14, loc="left")
ax.set_xlim(0, dogok_bar_len * 1.05)
ax.set_ylim(-1, dogok_y + 1.8)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(muted_axis)
ax.tick_params(axis="x", colors=text_secondary, labelsize=9)
ax.grid(axis="x", color=grid_color, linewidth=0.8, zorder=1)
ax.set_axisbelow(True)

fig.text(0.01, 0.01, "자료: 서울교통공사 승하차인원(2026.8, 호선별) · 노약자장애인 편의시설 현황 · 역주소 데이터 종합",
          fontsize=7.5, color=muted_axis)

plt.tight_layout(rect=[0, 0.02, 1, 1])
plt.savefig("엘리베이터_부담지수_차트.png", facecolor=surface, bbox_inches="tight")
print("차트 저장 완료: 엘리베이터_부담지수_차트.png")

# ===== 9. 자치구별 엘리베이터 보유율 집계 (정책 통계상 "거의 100%"인 그림) =====
final["EV없음_리프트만"] = (final["엘리베이터(E/V)"] == 0) & (final["휠체어리프트(W/L)"] > 0)
final["EV전무"] = final["엘리베이터(E/V)"] == 0

gu_summary = final.groupby("자치구").agg(
    역_수=("역명", "count"),
    EV보유역수=("엘리베이터(E/V)", lambda x: (x > 0).sum()),
    EV전무역수=("EV전무", "sum"),
    리프트만있는역수=("EV없음_리프트만", "sum"),
).reset_index()

gu_summary["EV보유율"] = (gu_summary["EV보유역수"] / gu_summary["역_수"] * 100).round(1)
gu_summary = gu_summary.sort_values("EV보유율")

print("\n=== 자치구별 엘리베이터 보유율 ===")
print(gu_summary.to_string(index=False))

gu_summary.to_csv("자치구별_유아차_이동편의성_집계.csv", index=False, encoding="utf-8-sig")

# ===== 10. 서울 지하철 전체 이동편의설비 구성비 =====
# 유모차·휠체어가 실제로 단독 이용 가능한 설비는 엘리베이터뿐임을 수치로 보여줌

totals = {
    "엘리베이터": fac["엘리베이터(E/V)"].sum(),
    "에스컬레이터": fac["에스컬레이터(E/S)"].sum(),
    "휠체어리프트": fac["휠체어리프트(W/L)"].sum(),
    "수평자동보도": fac["수평자동보도(M/W)"].sum(),
}
grand_total = sum(totals.values())
print("\n=== 서울 지하철 전체 이동편의설비 구성 ===")
for k, v in totals.items():
    print(f"{k}: {v}대 ({v/grand_total*100:.1f}%)")
print(f"※ 유모차·휠체어가 실제로 단독 이용 가능한 설비는 엘리베이터뿐이며, 전체의 {totals['엘리베이터']/grand_total*100:.1f}%에 불과함")

order = ["엘리베이터", "에스컬레이터", "휠체어리프트", "수평자동보도"]
color_map = {"엘리베이터": "#eb6834", "에스컬레이터": "#c3c2b7", "휠체어리프트": "#a8a79f", "수평자동보도": "#dcdbd4"}
surface = "#fcfcfb"
text_primary = "#0b0b0b"

fig, ax = plt.subplots(figsize=(9, 2.6), dpi=150)
fig.patch.set_facecolor(surface)
ax.set_facecolor(surface)

left = 0
for k in order:
    pct = totals[k] / grand_total * 100
    ax.barh(0, pct, left=left, color=color_map[k], height=0.5, zorder=3)
    if pct > 4:
        label_color = "white" if k == "엘리베이터" else text_primary
        weight = "bold" if k == "엘리베이터" else "normal"
        ax.text(left + pct / 2, 0, f"{k}\n{pct:.1f}%", ha="center", va="center",
                fontsize=10 if k == "엘리베이터" else 9, color=label_color, fontweight=weight, zorder=4)
    left += pct

ax.set_xlim(0, 100)
ax.set_ylim(-1, 1)
ax.axis("off")
ax.set_title("서울 지하철 이동편의설비 구성비 — 엘리베이터는 전체의 30% 남짓",
              fontsize=12.5, color=text_primary, fontweight="bold", pad=10, loc="left")

fig.text(0.01, 0.02, f"자료: 서울시 지하철 역사 노약자 장애인 편의시설 현황 · 전체 {grand_total}대 중 엘리베이터 {totals['엘리베이터']}대",
          fontsize=7.5, color="#898781")

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig("이동편의설비_구성비_차트.png", facecolor=surface, bbox_inches="tight")
print("차트 저장 완료: 이동편의설비_구성비_차트.png")