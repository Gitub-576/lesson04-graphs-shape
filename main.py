import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 분석합니다."
)

# -----------------------------------
# 데이터 불러오기
# -----------------------------------
DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 여러 장르가 있는 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    df["genre"] = df["genre"].replace("", "미상")

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

    return df


try:
    df = load_data()

    st.success(f"총 {len(df)}편의 영화 데이터를 불러왔습니다.")

    # ===================================
    # 그래프 1
    # 장르별 영화 편수 - 도넛 그래프
    # ===================================
    st.header("1. 장르별 영화 편수")

    genre_count = (
        df["genre"]
        .value_counts()
        .reset_index()
    )

    genre_count.columns = ["장르", "영화 편수"]

    fig1 = px.pie(
        genre_count,
        names="장르",
        values="영화 편수",
        hole=0.45,
        title="장르별 영화 편수 분포"
    )

    fig1.update_traces(
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value}편<br>"
            "비율: %{percent}"
            "<extra></extra>"
        )
    )

    fig1.update_layout(
        height=550,
        legend_title="장르"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "장르별로 10위권에 진입한 영화가 몇 편씩 분포하는지 비교할 수 있습니다."
    )


    # ===================================
    # 그래프 2
    # 장르 → 영화 트리맵
    # ===================================
    st.header("2. 장르별 총 관객 트리맵")

    treemap_df = df[
        ["genre", "movieNm", "total_audi"]
    ].dropna(subset=["genre", "movieNm", "total_audi"])

    fig2 = px.treemap(
        treemap_df,
        path=["genre", "movieNm"],
        values="total_audi",
        title="장르별 영화의 총 관객 분포"
    )

    fig2.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,.0f}명"
            "<extra></extra>"
        )
    )

    fig2.update_layout(height=650)

    st.plotly_chart(fig2, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "각 장르 안에서 어떤 영화가 많은 관객을 기록했는지와 영화별 관객 규모를 비교할 수 있습니다."
    )


    # ===================================
    # 그래프 3
    # 총 관객 히스토그램
    # ===================================
    st.header("3. 총 관객 분포")

    fig3 = px.histogram(
        df,
        x="total_audi",
        nbins=20,
        title="영화별 총 관객 히스토그램",
        labels={
            "total_audi": "총 관객",
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

    fig3.update_layout(height=550)

    st.plotly_chart(fig3, use_container_width=True)

    # 가장 관객이 많은 영화
    max_audience_movie = df.loc[
        df["total_audi"].idxmax()
    ]

    # 대부분의 영화가 몰려 있는 구간 계산
    counts, bins = pd.cut(
        df["total_audi"],
        bins=20,
        retbins=True
    )
    bin_counts = counts.value_counts().sort_index()

    most_common_bin = bin_counts.idxmax()

    st.info(
        f"이 그래프로 알 수 있는 것: "
        f"대부분의 영화는 약 {most_common_bin.left:,.0f}명~"
        f"{most_common_bin.right:,.0f}명 구간에 몰려 있으며, "
        f"가장 많은 관객을 기록한 영화는 "
        f"'{max_audience_movie['movieNm']}'으로 "
        f"{max_audience_movie['total_audi']:,.0f}명의 관객을 기록했습니다."
    )


    # ===================================
    # 그래프 4
    # 개봉일 스크린수 vs 총 관객 산점도
    # ===================================
    st.header("4. 개봉일 스크린수와 총 관객의 관계")

    scatter_df = df.dropna(
        subset=["first_scrn", "total_audi", "movieNm", "genre"]
    )

    fig4 = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        title="개봉일 스크린수와 총 관객의 관계",
        labels={
            "first_scrn": "개봉일 스크린수",
            "total_audi": "총 관객",
            "genre": "장르"
        }
    )

    fig4.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "개봉일 스크린수: %{x:,.0f}<br>"
            "총 관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig4.update_layout(height=600)

    st.plotly_chart(fig4, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "개봉일에 확보한 스크린 수와 영화의 총 관객 사이의 관계를 장르별로 비교할 수 있습니다."
    )


    # ===================================
    # 그래프 5
    # 장르별 총 관객 박스플롯
    # ===================================
    st.header("5. 장르별 총 관객 분포")

    # 영화가 10편 이상인 장르만 선택
    genre_10plus = (
        df["genre"]
        .value_counts()
    )

    valid_genres = genre_10plus[
        genre_10plus >= 10
    ].index

    box_df = df[
        df["genre"].isin(valid_genres)
    ].dropna(
        subset=["genre", "total_audi", "movieNm"]
    )

    fig5 = px.box(
        box_df,
        x="genre",
        y="total_audi",
        points="outliers",
        hover_name="movieNm",
        title="영화가 10편 이상인 장르의 총 관객 분포",
        labels={
            "genre": "장르",
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

    fig5.update_layout(height=600)

    st.plotly_chart(fig5, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "영화가 10편 이상인 장르끼리 총 관객의 중앙값과 분포, 그리고 유난히 높은 관객을 기록한 영화를 비교할 수 있습니다."
    )


    # ===================================
    # 그래프 6
    # 개봉일 스크린수 vs 총 관객 버블 그래프
    # ===================================
    st.header("6. 개봉일 스크린수와 총 관객의 관계 - 버블 그래프")

    bubble_df = df.dropna(
        subset=[
            "first_scrn",
            "total_audi",
            "first_week_audi",
            "movieNm",
            "genre"
        ]
    ).copy()

    # 0 또는 음수인 값은 버블 크기 계산에서 제외
    bubble_df = bubble_df[
        bubble_df["first_week_audi"] > 0
    ]

    fig6 = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        size="first_week_audi",
        hover_name="movieNm",
        size_max=50,
        title="개봉일 스크린수와 총 관객의 관계 - 첫 주 관객 버블 크기",
        labels={
            "first_scrn": "개봉일 스크린수",
            "total_audi": "총 관객",
            "genre": "장르",
            "first_week_audi": "첫 주 관객"
        }
    )

    fig6.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "개봉일 스크린수: %{x:,.0f}<br>"
            "총 관객: %{y:,.0f}명<br>"
            "첫 주 관객: %{marker.size:,.0f}명"
            "<extra></extra>"
        )
    )

    fig6.update_layout(height=650)

    st.plotly_chart(fig6, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "개봉일 스크린수와 총 관객의 관계뿐만 아니라 첫 주 관객 규모까지 함께 비교할 수 있습니다."
    )


    # ===================================
    # 그래프 7
    # 제작 국가 → 장르 선버스트
    # ===================================
    st.header("7. 제작 국가와 장르별 영화 분포")

    sunburst_df = (
        df[
            ["nation", "genre", "movieNm"]
        ]
        .copy()
    )

    sunburst_df["nation"] = (
        sunburst_df["nation"]
        .fillna("미상")
        .astype(str)
        .str.strip()
    )

    sunburst_df["genre"] = (
        sunburst_df["genre"]
        .fillna("미상")
        .astype(str)
        .str.strip()
    )

    # 제작 국가와 장르별 영화 편수 계산
    sunburst_count = (
        sunburst_df
        .groupby(["nation", "genre"])
        .size()
        .reset_index(name="영화 편수")
    )

    fig7 = px.sunburst(
        sunburst_count,
        path=["nation", "genre"],
        values="영화 편수",
        title="제작 국가 → 장르별 영화 분포"
    )

    fig7.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value}편"
            "<extra></extra>"
        )
    )

    fig7.update_layout(height=700)

    st.plotly_chart(fig7, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "제작 국가별로 어떤 장르의 영화가 많이 분포하는지와 전체 영화에서 차지하는 비중을 볼 수 있습니다."
    )


except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
