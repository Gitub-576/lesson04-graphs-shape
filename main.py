import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 영화들의 분포와 관계를 살펴봅니다."
)


# =========================================================
# 데이터 불러오기
# =========================================================
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)

try:
    df = pd.read_csv(DATA_URL)

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)
    st.stop()


# =========================================================
# 데이터 전처리
# =========================================================

# 장르가 여러 개이면 첫 번째 장르만 사용
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

df["genre_first"] = df["genre_first"].replace("", "미상")

# 숫자형 데이터 변환
numeric_columns = [
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 영화명, 국가 결측값 처리
df["movieNm"] = df["movieNm"].fillna("영화명 미상")
df["nation"] = df["nation"].fillna("국가 미상").astype(str)

# 분석에 필요한 관객 수가 없는 행 제거
df = df.dropna(subset=["total_audi"])


# =========================================================
# 그래프 1
# 장르별 영화 편수 도넛 그래프
# =========================================================
st.header("1. 장르별 영화 분포")

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
    textinfo="percent"
)

fig1.update_layout(
    height=550,
    legend_title="장르"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "장르별로 영화가 몇 편씩 포함되어 있는지와 "
    "각 장르가 전체 영화에서 차지하는 비율을 알 수 있습니다."
)


# =========================================================
# 그래프 2
# 장르 안에 영화가 들어 있는 트리맵
# =========================================================
st.divider()
st.header("2. 장르별 영화 총 관객 트리맵")

fig2 = px.treemap(
    df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=650
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "각 장르 안에서 영화별 총 관객 규모가 얼마나 차이가 나는지 "
    "한눈에 비교할 수 있습니다."
)


# =========================================================
# 그래프 3
# 총 관객 히스토그램
# =========================================================
st.divider()
st.header("3. 총 관객 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=15,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 관객이 많은 영화
max_movie = df.loc[df["total_audi"].idxmax()]
max_movie_name = max_movie["movieNm"]
max_movie_audience = max_movie["total_audi"]

# 히스토그램 구간 계산
hist_counts, bin_edges = pd.cut(
    df["total_audi"],
    bins=15,
    include_lowest=True,
    retbins=True
)

bin_counts = hist_counts.value_counts().sort_index()

if len(bin_counts) > 0:
    most_common_bin = bin_counts.idxmax()

    lower = most_common_bin.left
    upper = most_common_bin.right

    if lower >= 1000000:
        lower_text = f"{lower / 1000000:.1f}백만"
    elif lower >= 10000:
        lower_text = f"{lower / 10000:.1f}만"
    else:
        lower_text = f"{lower:,.0f}"

    if upper >= 1000000:
        upper_text = f"{upper / 1000000:.1f}백만"
    elif upper >= 10000:
        upper_text = f"{upper / 10000:.1f}만"
    else:
        upper_text = f"{upper:,.0f}"

    common_range_text = f"{lower_text}~{upper_text}명"
else:
    common_range_text = "확인할 수 없음"

st.markdown("**이 그래프로 알 수 있는 것**")

st.info(
    f"대부분의 영화는 총 관객 약 **{common_range_text}** 구간에 몰려 있으며, "
    f"가장 관객이 많은 영화는 **{max_movie_name}**으로 "
    f"총 **{max_movie_audience:,.0f}명**의 관객을 기록했습니다."
)


# =========================================================
# 그래프 4
# 개봉일 스크린수와 총 관객 산점도
# =========================================================
st.divider()
st.header("4. 개봉일 스크린수와 총 관객의 관계")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi"]
).copy()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre_first": "장르"
    }
)

fig4.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=600
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "영화의 개봉일 스크린수와 총 관객 사이의 관계를 살펴보고 "
    "장르별로 분포가 어떻게 다른지 비교할 수 있습니다."
)


# =========================================================
# 그래프 5
# 영화가 10편 이상인 장르의 총 관객 박스플롯
# =========================================================
st.divider()
st.header("5. 장르별 총 관객 분포")

# 장르별 영화 수 계산
genre_counts = df["genre_first"].value_counts()

# 10편 이상인 장르만 선택
selected_genres = genre_counts[genre_counts >= 10].index.tolist()

box_df = df[
    df["genre_first"].isin(selected_genres)
].copy()

if len(selected_genres) > 0:

    fig5 = px.box(
        box_df,
        x="genre_first",
        y="total_audi",
        color="genre_first",
        points="outliers",
        hover_name="movieNm",
        title="영화가 10편 이상인 장르의 총 관객 분포",
        labels={
            "genre_first": "장르",
            "total_audi": "총 관객"
        }
    )

    fig5.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "총 관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig5.update_layout(
        height=600,
        showlegend=False
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("**이 그래프로 알 수 있는 것**")
    st.info(
        "영화가 10편 이상인 장르를 대상으로 총 관객의 중앙값과 "
        "분포 범위, 그리고 다른 영화보다 관객 수가 크게 차이 나는 영화를 비교할 수 있습니다."
    )

else:
    st.warning("영화가 10편 이상인 장르가 없습니다.")


# =========================================================
# 그래프 6
# 첫 주 관객을 점 크기로 사용한 버블 그래프
# =========================================================
st.divider()
st.header("6. 개봉일 스크린수·총 관객·첫 주 관객의 관계")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
).copy()

# 첫 주 관객이 0 이하인 경우 버블 크기 계산에 문제가 생기지 않도록 처리
bubble_df["bubble_size"] = bubble_df["first_week_audi"].clip(lower=1)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    size="bubble_size",
    hover_name="movieNm",
    size_max=50,
    title="개봉일 스크린수와 총 관객 - 첫 주 관객 버블 크기",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre_first": "장르",
        "bubble_size": "첫 주 관객"
    }
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명<br>"
        "첫 주 관객: %{marker.size:,.0f}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    height=650
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "개봉일 스크린수와 총 관객의 관계를 확인하면서 "
    "첫 주 관객 규모가 영화마다 어떻게 다른지도 함께 비교할 수 있습니다."
)


# =========================================================
# 그래프 7
# 제작 국가 → 장르 선버스트 그래프
# =========================================================
st.divider()
st.header("7. 제작 국가와 장르별 영화 분포")

sunburst_df = df.copy()

# 국가가 여러 개 기록되어 있는 경우 첫 번째 국가 사용
sunburst_df["nation_first"] = (
    sunburst_df["nation"]
    .fillna("국가 미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

sunburst_df["nation_first"] = sunburst_df[
    "nation_first"
].replace("", "국가 미상")

# 영화 한 편당 1개의 값이므로 편수 계산을 위해 count용 열 생성
sunburst_df["movie_count"] = 1

fig7 = px.sunburst(
    sunburst_df,
    path=["nation_first", "genre_first"],
    values="movie_count",
    title="제작 국가 → 장르별 영화 편수",
    labels={
        "nation_first": "제작 국가",
        "genre_first": "장르"
    }
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=700
)

st.plotly_chart(fig7, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "제작 국가별로 어떤 장르의 영화가 많이 포함되어 있는지와 "
    "각 국가와 장르의 영화 편수를 함께 확인할 수 있습니다."
)


# =========================================================
# 데이터 정보
# =========================================================
st.divider()
st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("분석 영화 수", f"{len(df):,}편")

with col2:
    st.metric("분석 장르 수", f"{genre_count.shape[0]:,}개")

with col3:
    st.metric("10편 이상 장르 수", f"{len(selected_genres):,}개")

st.caption(
    "※ 장르가 여러 개 기록된 영화는 첫 번째 장르만 사용했습니다."
)
