import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# ===== 1. 실제 언론기사·SNS 공개 게시글에서 수집한 사례 코퍼스 =====
# 네이버지도 개별 리뷰는 로그인해야 보이는 비공개 콘텐츠라 수집할 수 없었음.
# 대신 검색으로 실제 확인 가능한 뉴스 기사·SNS 공개 게시글만 사용.
# 주의: 무작위 표본이 아닌 소규모 정성 자료(n=12)로 대표성에 한계가 있음
# (정량분석의 보완 지표로만 활용, 보고서에도 이 한계를 명시)

data = [
    {"출처유형": "뉴스", "매체": "프레시안", "날짜": "2025-08-30", "형식": "직접인용",
     "내용": "일반버스는 위험할 수 있으니 승차를 거부할 수 있다고 하더라도 휠체어와 유아차 타기 편하라고 만든 저상버스마저 못 타는 것은 문제",
     "이슈유형": "승차거부",
     "URL": "https://www.pressian.com/pages/articles/2025082916154710432"},
    {"출처유형": "뉴스", "매체": "프레시안", "날짜": "2025-08-30", "형식": "사례요약",
     "내용": "유아차로 버스 탑승을 수차례 거부당해 주위 시민들이 유아차를 들어올린 후에야 탑승할 수 있었다는 사례",
     "이슈유형": "승차거부",
     "URL": "https://www.pressian.com/pages/articles/2025082916154710432"},
    {"출처유형": "뉴스", "매체": "더스쿠프", "날짜": "2025", "형식": "직접인용",
     "내용": "말을 꺼냈다가 서로 기분이 상하거나 괜히 해코지라도 당할까 봐 그냥 가만히 서 있게 돼요",
     "이슈유형": "배려부족",
     "URL": "https://www.thescoop.co.kr/news/articleView.html?idxno=304013"},
    {"출처유형": "뉴스", "매체": "더스쿠프", "날짜": "2025", "형식": "직접인용",
     "내용": "어머님들이나 비슷한 또래 여성분 외에는 양해를 잘 안 해주시는 거 같아요",
     "이슈유형": "배려부족",
     "URL": "https://www.thescoop.co.kr/news/articleView.html?idxno=304013"},
    {"출처유형": "뉴스", "매체": "에이블뉴스", "날짜": "미상", "형식": "직접인용",
     "내용": "유모차는 그래도 보이는데 시장바구니를 앞에 밀고 들어가면 잘 안 보여서 전동스쿠터 바퀴에 걸릴 수도 있다",
     "이슈유형": "혼잡·포화",
     "URL": "https://www.ablenews.co.kr/news/articleView.html?idxno=97024"},
    {"출처유형": "뉴스", "매체": "에이블뉴스", "날짜": "미상", "형식": "직접인용",
     "내용": "엘리베이터를 타는 사람이 두세 명이면 밀고 들어가는데 사오 명이면 다음을 기다릴 수밖에 없다",
     "이슈유형": "혼잡·포화",
     "URL": "https://www.ablenews.co.kr/news/articleView.html?idxno=97024"},
    {"출처유형": "뉴스", "매체": "뉴시스", "날짜": "2013-08-16", "형식": "직접인용",
     "내용": "가끔 유모차를 끌고 지하철을 이용하지만 엘리베이터가 없는 환승통로에서는 참 곤란하다",
     "이슈유형": "위치·접근성",
     "URL": "https://www.newsis.com/view/NISX20130816_0012292014"},
    {"출처유형": "뉴스", "매체": "뉴시스", "날짜": "2013-08-16", "형식": "직접인용",
     "내용": "하필 사람이 많은 이곳에 엘리베이터가 없는지 모르겠다",
     "이슈유형": "위치·접근성",
     "URL": "https://www.newsis.com/view/NISX20130816_0012292014"},
    {"출처유형": "SNS", "매체": "Threads", "날짜": "2026", "형식": "사례요약",
     "내용": "지하철 엘베 앞에서 유모차를 끌고 네 번째로 기다리고 있었는데, 뒤에 온 휠체어를 먼저 태워야 한다는 안내에 순서가 밀렸다는 게시글",
     "이슈유형": "이용자갈등",
     "URL": "https://www.threads.com/@ey_luckiii/post/DQHGh4Skp3I"},
    {"출처유형": "뉴스", "매체": "오마이뉴스", "날짜": "2025-12-30", "형식": "사례요약",
     "내용": "1999년 혜화역에서 중증장애인이 추락해 중상을 입었고, 2001년 오이도역에서는 장애인이 리프트카에서 추락해 사망한 사건",
     "이슈유형": "정책요구",
     "URL": "https://www.ohmynews.com/NWS_Web/View/at_pg.aspx?CNTN_CD=A0003194827"},
    {"출처유형": "뉴스", "매체": "오마이뉴스", "날짜": "2025-12-30", "형식": "사례요약",
     "내용": "장애인이동권연대가 지하철 선로를 점거하며 엘리베이터 설치를 요구하는 투쟁을 벌인 사건",
     "이슈유형": "정책요구",
     "URL": "https://www.ohmynews.com/NWS_Web/View/at_pg.aspx?CNTN_CD=A0003194827"},
    {"출처유형": "뉴스", "매체": "뉴시스", "날짜": "2013-08-16", "형식": "사례요약",
     "내용": "안내센터에 엘리베이터 위치를 문의했으나 직원은 다른 통로가 있다고만 답한 에피소드",
     "이슈유형": "위치·접근성",
     "URL": "https://www.newsis.com/view/NISX20130816_0012292014"},
]

df = pd.DataFrame(data)
df.to_csv("실제사례_코퍼스.csv", index=False, encoding="utf-8-sig")
print(f"총 수집 사례: {len(df)}건 (뉴스 {sum(df['출처유형']=='뉴스')}건, SNS {sum(df['출처유형']=='SNS')}건 / 직접인용 {sum(df['형식']=='직접인용')}건, 사례요약 {sum(df['형식']=='사례요약')}건)")

# ===== 2. 키워드 빈도 =====
keywords = ["엘리베이터", "유모차", "휠체어", "거부", "혼잡", "갈등", "배려", "계단", "위험", "추락"]
all_text = " ".join(df["내용"])
freq = {kw: all_text.count(kw) for kw in keywords}
freq_df = pd.DataFrame(sorted(freq.items(), key=lambda x: -x[1]), columns=["키워드", "빈도"])
print("\n=== 키워드 빈도 ===")
print(freq_df.to_string(index=False))

# ===== 3. 이슈유형별 집계 및 시각화 =====
issue_count = df["이슈유형"].value_counts().sort_values()

seq_ramp = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]
muted_axis = "#898781"
grid_color = "#e1e0d9"
text_primary = "#0b0b0b"
text_secondary = "#52514e"
surface = "#fcfcfb"

fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
fig.patch.set_facecolor(surface)
ax.set_facecolor(surface)

n = len(issue_count)
colors = [seq_ramp[int(i / max(n - 1, 1) * (len(seq_ramp) - 1))] for i in range(n)]
ax.barh(range(n), issue_count.values, color=colors, height=0.6, zorder=3)

for y, (label, val) in enumerate(zip(issue_count.index, issue_count.values)):
    ax.text(val + 0.05, y, f"{label}  {val}건", va="center", ha="left",
            fontsize=10.5, color=text_primary, zorder=4)

ax.set_yticks([])
ax.set_xlabel("언급 건수", fontsize=10, color=text_secondary)
ax.set_title("유아차·임산부·휠체어 이용자 이동 불편 이슈 유형\n(언론·SNS 공개 게시글 12건 분석)",
              fontsize=12.5, color=text_primary, fontweight="bold", pad=14, loc="left")
ax.set_xlim(0, issue_count.values.max() * 1.35)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(muted_axis)
ax.tick_params(axis="x", colors=text_secondary, labelsize=9)
ax.grid(axis="x", color=grid_color, linewidth=0.8, zorder=1)
ax.set_axisbelow(True)

fig.text(0.01, 0.01, "자료: 뉴스·SNS 공개 게시글 수집(2026.9) · 소규모 정성 표본(n=12)으로 대표성에 한계 있음",
          fontsize=7.5, color=muted_axis)

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig("이슈유형_빈도_차트.png", facecolor=surface, bbox_inches="tight")
print("\n차트 저장 완료: 이슈유형_빈도_차트.png")