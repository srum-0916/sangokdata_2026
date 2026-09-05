from calendar import isleap
from io import StringIO
from math import floor
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_URL = 'https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv'


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    """같은 폴더의 CSV를 우선 사용하고, 없으면 지정된 URL에서 읽는다."""
    local = Path(__file__).with_name('seoul.csv')
    if local.exists():
        raw = local.read_bytes()
    else:
        with urlopen(DATA_URL, timeout=30) as response:
            raw = response.read()
    for encoding in ('utf-8-sig', 'cp949'):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError('CSV의 문자 인코딩을 확인해 주세요.')
    df = pd.read_csv(StringIO(text))
    df.columns = df.columns.str.strip().str.replace(r'\(.*?\)', '', regex=True)
    required = {'날짜', '지점', '평균기온', '최저기온', '최고기온'}
    if not required.issubset(df.columns):
        raise ValueError('날짜·지점·평균기온·최저기온·최고기온 열이 필요합니다.')
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str).str.strip(), errors='coerce')
    for column in ['지점', '평균기온', '최저기온', '최고기온']:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    df = df.loc[df['지점'].eq(108)].dropna(subset=['날짜'])
    df = df.sort_values('날짜').drop_duplicates('날짜')
    if df.empty:
        raise ValueError('서울(지점 108)의 유효한 날짜가 없습니다.')
    return df


def annual_summary(df):
    annual = df.groupby(df['날짜'].dt.year)['평균기온'].agg(
        연평균기온='mean', 관측일수='count'
    )
    years = range(int(annual.index.min()), int(annual.index.max()) + 1)
    annual = annual.reindex(years).rename_axis('연도')
    annual['관측일수'] = annual['관측일수'].fillna(0).astype(int)
    annual['연간일수'] = [366 if isleap(year) else 365 for year in annual.index]
    annual['완전한연도'] = annual['관측일수'].eq(annual['연간일수'])
    # 일부 계절만 관측된 해가 연평균 비교를 왜곡하지 않도록 제외한다.
    annual.loc[~annual['완전한연도'], '연평균기온'] = float('nan')
    return annual



def show_histogram(df, start, end):
    st.subheader('일별 평균기온은 어느 구간에 몰려 있을까?')
    scope = st.radio('분석 기간', ['최근 100년', '원자료 전체'], horizontal=True)
    selected = df.loc[df['날짜'].dt.year.between(start, end)] if scope == '최근 100년' else df
    temperatures = selected['평균기온'].dropna()
    st.caption(f"대상 기간: {selected['날짜'].min():%Y-%m-%d}–{selected['날짜'].max():%Y-%m-%d} · "
               f'유효 관측 {len(temperatures):,}일 · 평균기온 결측 {selected["평균기온"].isna().sum():,}일 제외')
    st.caption('관측이 불완전한 연도도 기온 값이 있는 날은 포함합니다. 원자료에 없는 날짜는 채우지 않습니다.')
    if temperatures.empty:
        st.info('선택한 기간에 유효한 일별 평균기온이 없습니다.')
        return
    width = st.select_slider('기온 구간 너비 (°C)', options=[1, 2, 5, 10], value=2)
    lower = floor(temperatures.min() / width) * width
    upper = (floor(temperatures.max() / width) + 1) * width
    edges = list(range(lower, upper + width, width))
    counts = pd.cut(temperatures, bins=edges, right=False).value_counts(sort=False)
    labels = [f'{item.left:g} 이상 {item.right:g} 미만' for item in counts.index]
    shares = counts / counts.sum() * 100
    chart = go.Figure(go.Bar(
        x=[(item.left + item.right) / 2 for item in counts.index],
        y=counts.values, width=width,
        marker=dict(color='#4496cf', line=dict(color='white', width=1)),
        customdata=list(zip(labels, shares)),
        hovertemplate='%{customdata[0]} °C<br>%{y:,}일 (%{customdata[1]:.1f}%)<extra></extra>',
    ))
    chart.update_layout(height=460, template='plotly_white', bargap=0,
                        xaxis_title='일별 평균기온 (°C)', yaxis_title='날짜 수 (일)',
                        margin=dict(l=30, r=25, t=25, b=30))
    st.plotly_chart(chart, width='stretch', config={'displayModeBar': False})
    peaks = [labels[i] for i, count in enumerate(counts) if count == counts.max()]
    st.write('가장 많이 관측된 구간: **' + ' / '.join(peaks) + ' °C**'
             + f' · 각 **{counts.max():,}일 ({counts.max() / counts.sum():.1%})**')
    with st.expander('기온 구간별 날짜 수 보기'):
        st.dataframe(pd.DataFrame({'기온 구간 (°C)': labels, '날짜 수 (일)': counts.values,
                                   '비율 (%)': shares.round(2).values}), hide_index=True)



def show_scatter(df, start, end):
    st.subheader('날마다의 최저기온과 최고기온은 어떤 관계일까?')
    scope = st.radio('산점도 분석 기간', ['최근 100년', '원자료 전체'],
                     horizontal=True, key='scatter_period')
    selected = df.loc[df['날짜'].dt.year.between(start, end)] if scope == '최근 100년' else df
    paired = selected.dropna(subset=['최저기온', '최고기온']).copy()
    st.caption(f"대상 기간: {selected['날짜'].min():%Y-%m-%d}–{selected['날짜'].max():%Y-%m-%d} · "
               f'유효 관측 {len(paired):,}일 · 두 기온 중 결측이 있는 {len(selected) - len(paired):,}일 제외')
    st.caption('점 하나는 하루입니다. 관측이 불완전한 연도도 두 기온이 모두 있는 날은 포함합니다.')
    if paired.empty:
        st.info('선택한 기간에 최저기온과 최고기온이 모두 있는 날짜가 없습니다.')
        return
    paired['일교차'] = paired['최고기온'] - paired['최저기온']
    chart = go.Figure(go.Scattergl(
        x=paired['최저기온'], y=paired['최고기온'], mode='markers', name='일별 관측',
        marker=dict(size=4, color='#4496cf', opacity=0.25),
        customdata=list(zip(paired['날짜'].dt.strftime('%Y-%m-%d'), paired['일교차'])),
        hovertemplate='%{customdata[0]}<br>최저기온: %{x:.1f} °C<br>'
                      '최고기온: %{y:.1f} °C<br>일교차: %{customdata[1]:.1f} °C<extra></extra>',
    ))
    lower = float(paired[['최저기온', '최고기온']].min().min()) - 2
    upper = float(paired[['최저기온', '최고기온']].max().max()) + 2
    chart.add_trace(go.Scatter(x=[lower, upper], y=[lower, upper], mode='lines',
                              name='최고기온 = 최저기온',
                              line=dict(color='#e66b35', dash='dash', width=2), hoverinfo='skip'))
    chart.update_layout(height=550, template='plotly_white',
                        xaxis_title='최저기온 (°C)', yaxis_title='최고기온 (°C)',
                        legend=dict(orientation='h', y=1.12),
                        margin=dict(l=30, r=25, t=65, b=30))
    chart.update_xaxes(range=[lower, upper])
    chart.update_yaxes(range=[lower, upper])
    st.plotly_chart(chart, width='stretch', config={'displayModeBar': False})
    st.caption('점이 진하게 겹치는 곳일수록 관측이 많습니다. 점선에서 위로 떨어진 기온 차이가 그날의 일교차입니다.')
    correlation = paired['최저기온'].corr(paired['최고기온']) if len(paired) > 1 else float('nan')
    left, right = st.columns(2)
    left.metric('최저·최고기온 상관계수 (피어슨)',
                f'{correlation:.3f}' if pd.notna(correlation) else '계산 불가')
    right.metric('평균 일교차', f'{paired["일교차"].mean():.2f} °C')
    st.caption('상관계수가 +1에 가까울수록 두 기온이 함께 높아지는 선형 관계가 강합니다. '
               '여러 계절을 합친 관계이며, 인과관계를 뜻하지는 않습니다.')


def main():
    st.set_page_config(page_title='서울의 100년 기온 변화', page_icon='🌡️', layout='wide')
    st.title('서울의 100년, 얼마나 따뜻해졌을까?')
    st.write('해마다 달라지는 연평균 기온과 10년 이동평균으로 긴 흐름을 살펴보세요.')
    try:
        with st.spinner('서울 기온 데이터를 읽고 있어요…'):
            df = load_data()
            annual = annual_summary(df)
    except Exception:
        st.error('데이터를 읽지 못했습니다. 데이터 URL과 CSV의 열 이름을 확인해 주세요. '
                 'main.py와 같은 폴더에 seoul.csv를 넣어도 됩니다.')
        st.stop()
    complete = annual.index[annual['완전한연도']]
    if complete.empty:
        st.warning('한 해 전체의 평균기온이 있는 연도가 없습니다.')
        st.stop()
    end = int(complete.max())
    start = max(int(annual.index.min()), end - 99)
    view = annual.loc[start:end].copy()
    # 결측 연도를 건너뛰지 않고 연속된 10개 연도의 평균만 계산한다.
    view['10년 이동평균'] = view['연평균기온'].rolling(10, min_periods=10).mean()
    st.caption(f'표시 기간: {start}–{end}년 ({end - start + 1}개 연도) · '
               f'원자료: {df["날짜"].min():%Y-%m-%d}–{df["날짜"].max():%Y-%m-%d}')
    show_scatter(df, start, end)
    show_histogram(df, start, end)
    st.subheader('100년간 연평균 기온 변화')
    first = view['연평균기온'].iloc[:10].dropna()
    last = view['연평균기온'].iloc[-10:].dropna()
    left, center, right = st.columns(3)
    left.metric(f'처음 10년 평균 ({start}–{start + 9})',
                f'{first.mean():.2f} °C' if len(first) == 10 else '자료 부족')
    center.metric(f'마지막 10년 평균 ({end - 9}–{end})',
                  f'{last.mean():.2f} °C' if len(last) == 10 else '자료 부족')
    right.metric('두 10년 평균의 차이',
                 f'{last.mean() - first.mean():+.2f} °C'
                 if len(first) == len(last) == 10 else '비교 불가')
    fig = go.Figure()
    for column, color, width in [('연평균기온', '#4496cf', 2), ('10년 이동평균', '#e66b35', 4)]:
        fig.add_trace(go.Scatter(
            x=view.index, y=view[column], name=column,
            mode='lines+markers' if column == '연평균기온' else 'lines',
            line=dict(color=color, width=width), marker=dict(size=4),
            connectgaps=False,
            hovertemplate='%{x}년<br>%{y:.2f} °C<extra>' + column + '</extra>',
        ))
    fig.update_layout(
        height=500, xaxis_title='연도', yaxis_title='기온 (°C)',
        hovermode='x unified', template='plotly_white',
        font=dict(family='sans-serif'),
        legend=dict(orientation='h', y=1.12, x=0),
        margin=dict(l=30, r=25, t=65, b=30),
    )
    fig.update_xaxes(tickformat='d', range=[start, end])
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    st.caption('파란색: 일평균 기온의 연평균 · 주황색: 해당 연도를 포함한 직전 10년의 연평균 기온 평균')
    missing = view.index[~view['완전한연도']].tolist()
    if missing:
        st.info('관측일이 부족한 해는 값을 채우지 않고 그래프를 끊어 표시했습니다: '
                + ', '.join(map(str, missing)) + '년')
    with st.expander('계산 방법과 연도별 데이터'):
        st.write('365일(윤년 366일)의 일평균 기온이 모두 있는 해만 비교합니다. '
                 '표시 기간은 데이터에서 마지막으로 완전하게 관측된 해까지 최대 100개 연도입니다. '
                 '10년 이동평균은 연속된 10개 연도에 결측이 없을 때만 표시합니다. '
                 '위 차이는 처음과 마지막 10년의 비교이며, 직선 추세의 기울기는 아닙니다.')
        table = view.reset_index().rename(columns={'완전한연도': '연평균 사용 여부'})
        st.dataframe(table, hide_index=True)
        st.download_button('연도별 데이터 내려받기',
                           table.to_csv(index=False).encode('utf-8-sig'),
                           file_name='서울_연평균_기온.csv', mime='text/csv')
    st.markdown(f'[원본 데이터 보기]({DATA_URL})')


if __name__ == '__main__':
    main()
