import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# ===== 1. 데이터 로드 (elevator_analysis.py 실행 결과물 사용) =====
df = pd.read_csv("최종_역별_통합데이터.csv", encoding="utf-8-sig")

# ===== 2. 역 상태 구분 =====
df["EV전무"] = df["엘리베이터(E/V)"] == 0
df["리프트만있음"] = (df["엘리베이터(E/V)"] == 0) & (df["휠체어리프트(W/L)"] > 0)

# ===== 3. 우선순위 점수 계산 =====
# - 엘리베이터가 아예 없는 역: 접근성 자체가 없으므로 무조건 최우선 그룹(100점대)으로 두고,
#   그 안에서는 이용객이 많을수록(방치하면 더 많은 사람이 불편을 겪으므로) 점수를 더 준다.
# - 엘리베이터가 있는 역: EV1대당 이용객수(부담지수)를 0~99점으로 정규화해 순위를 매긴다.
# => 이렇게 하면 "완전 소외(0대)"가 항상 "있지만 부담 큰 역"보다 우선순위가 높게 나온다.

has_ev = df[df["EV1대당_이용객수"].notna()].copy()
min_v, max_v = has_ev["EV1대당_이용객수"].min(), has_ev["EV1대당_이용객수"].max()
has_ev["우선순위점수"] = 99 * (has_ev["EV1대당_이용객수"] - min_v) / (max_v - min_v)
has_ev["그룹"] = "있지만 부담 큰 역"

no_ev = df[df["EV전무"]].copy()
r_min, r_max = no_ev["월간총이용객수"].min(), no_ev["월간총이용객수"].max()
no_ev["우선순위점수"] = 100 + 20 * (no_ev["월간총이용객수"] - r_min) / max(r_max - r_min, 1)
no_ev["그룹"] = "엘리베이터 전무"

scored = pd.concat([has_ev, no_ev], ignore_index=True).sort_values("우선순위점수", ascending=False)

top15 = scored.head(15)[["역명", "자치구", "호선_정규화", "그룹", "엘리베이터(E/V)", "월간총이용객수", "EV1대당_이용객수", "우선순위점수"]]
top15.to_csv("우선순위_개선대상_TOP15.csv", index=False, encoding="utf-8-sig")

print("=== 개선 우선순위 TOP 15 ===")
print(top15.to_string(index=False))

# ===== 4. 시각화 (TOP 10, 그룹별 색 구분) =====
top10 = scored.head(10).sort_values("우선순위점수")
top10["표시명"] = top10["역명"].str.replace(r"\(.*?\)", "", regex=True) + " (" + top10["자치구"] + ")"

color_map = {"엘리베이터 전무": "#eb6834", "있지만 부담 큰 역": "#2a78d6"}
colors = top10["그룹"].map(color_map)

muted_axis = "#898781"
grid_color = "#e1e0d9"
text_primary = "#0b0b0b"
text_secondary = "#52514e"
surface = "#fcfcfb"

fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
fig.patch.set_facecolor(surface)
ax.set_facecolor(surface)

ax.barh(range(len(top10)), top10["우선순위점수"], color=colors, height=0.6, zorder=3)

for y, (label, val) in enumerate(zip(top10["표시명"], top10["우선순위점수"])):
    ax.text(val + 1, y, label, va="center", ha="left", fontsize=9.5, color=text_primary, zorder=4)

ax.set_yticks([])
ax.set_xlabel("개선 우선순위 점수", fontsize=10, color=text_secondary)
ax.set_title("유아차·임산부·휠체어 이용자 관점 개선 우선순위 TOP 10",
              fontsize=13, color=text_primary, fontweight="bold", pad=14, loc="left")
ax.set_xlim(0, top10["우선순위점수"].max() * 1.35)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(muted_axis)
ax.tick_params(axis="x", colors=text_secondary, labelsize=9)
ax.grid(axis="x", color=grid_color, linewidth=0.8, zorder=1)
ax.set_axisbelow(True)

handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in color_map.values()]
ax.legend(handles, color_map.keys(), loc="lower right", frameon=False, fontsize=9)

fig.text(0.01, 0.01, "자료: 노약자장애인 편의시설 현황 · 승하차인원(2026.8) 종합 산출 (우선순위점수 = 접근성 완전결여 여부 + 이용객 대비 엘리베이터 부담)",
          fontsize=7.5, color=muted_axis)

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig("우선순위_TOP10_차트.png", facecolor=surface, bbox_inches="tight")
print("\n차트 저장 완료: 우선순위_TOP10_차트.png")