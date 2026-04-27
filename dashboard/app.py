import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

st.set_page_config(page_title='E-Commerce Intelligence Dashboard', page_icon='📊', layout='wide')

DB_URI = 'postgresql://ecommerce_user:ecommerce_pass@localhost:5432/ecommerce_db'

@st.cache_resource
def get_engine():
    return create_engine(DB_URI)

@st.cache_data
def load_table(table_name):
    engine = get_engine()
    return pd.read_sql(f'SELECT * FROM {table_name}', engine)

CHARTS = 'charts'

def show_html_chart(filename, height=500):
    path = os.path.join(CHARTS, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            html = f.read()
        st.components.v1.html(html, height=height, scrolling=True)
    else:
        st.warning(f'Chart not found: {filename}')

def show_png_chart(filename):
    path = os.path.join(CHARTS, filename)
    if os.path.exists(path):
        st.image(path, use_column_width=True)
    else:
        st.warning(f'Chart not found: {filename}')

st.sidebar.title('📊 E-Commerce Dashboard')
st.sidebar.markdown('**NCI MSc Data Analytics**')
st.sidebar.markdown('Semester 2, 2025/26')
st.sidebar.markdown('---')
page = st.sidebar.radio('Navigate to', ['🏠 Overview', '📦 Amazon — Consumer Purchases', '🛒 UCI — Shopper Behaviour', '📢 Criteo — Campaign Attribution', '🔗 Cross-Dataset Intelligence'])
st.sidebar.markdown('---')
st.sidebar.markdown('**Team**')
st.sidebar.markdown('- Amber (M3 — Criteo)')
st.sidebar.markdown('- Ibrahim (M1 — Amazon)')
st.sidebar.markdown('- Araf (M2 — UCI)')

if page == '🏠 Overview':
    st.title('E-Commerce Customer Behaviour & Sales Intelligence Dashboard')
    st.markdown('### Multi-Dataset Exploration: Consumer Purchases, Shopper Conversion, and Campaign Attribution')
    st.markdown('---')
    col1, col2, col3 = st.columns(3)
    try:
        df_amazon = load_table('amazon_clean')
        col1.metric('Amazon Records', f'{len(df_amazon):,}')
        col1.metric('Amazon Categories', f"{df_amazon['category'].nunique():,}")
    except:
        col1.metric('Amazon Records', 'Load DB')
    try:
        df_uci = load_table('uci_clean')
        col2.metric('UCI Sessions', f'{len(df_uci):,}')
        col2.metric('Conversion Rate', f"{df_uci['is_conversion'].mean()*100:.1f}%")
    except:
        col2.metric('UCI Sessions', 'Load DB')
    try:
        df_criteo = load_table('criteo_clean')
        col3.metric('Criteo Impressions', f'{len(df_criteo):,}')
        col3.metric('Campaigns', f"{df_criteo['campaign'].nunique():,}")
    except:
        col3.metric('Criteo Impressions', 'Load DB')
    st.markdown('---')
    st.markdown('### Research Questions')
    col1, col2 = st.columns(2)
    with col1:
        st.info('RQ1 — Consumer Purchase Trends: How have spending patterns evolved over time?')
        st.info('RQ2 — Shopper Behaviour: What on-site signals predict purchase conversion?')
    with col2:
        st.info('RQ3 — Campaign Attribution: Which campaigns deliver highest ROI?')
        st.info('RQ4 — Cross-Dataset Intelligence: Can we align RFM, intent signals, and campaign touchpoints?')

elif page == '📦 Amazon — Consumer Purchases':
    st.title('📦 Amazon Consumer Purchase Analysis')
    st.markdown('**Member 1 — Ibrahim | Amazon US Purchase History**')
    st.markdown('---')
    tab1, tab2, tab3 = st.tabs(['Revenue and Trends', 'Categories and Geography', 'RFM Segmentation'])
    with tab1:
        st.subheader('Monthly Revenue Trend')
        show_html_chart('m1_revenue_trend.html')
        st.subheader('Revenue by Day of Week')
        show_html_chart('m1_dow_revenue.html')
    with tab2:
        st.subheader('Top 10 Categories by Revenue')
        show_html_chart('m1_top_categories.html')
        st.subheader('Revenue by US State')
        show_html_chart('m1_state_revenue.html')
        st.subheader('Price Band Distribution')
        show_html_chart('m1_price_band.html')
    with tab3:
        st.subheader('RFM Customer Segmentation')
        show_html_chart('m1_rfm_scatter.html')
        try:
            rfm = load_table('amazon_rfm')
            seg_counts = rfm['segment'].value_counts().reset_index()
            seg_counts.columns = ['segment', 'count']
            fig = px.pie(seg_counts, names='segment', values='count', title='RFM Segment Distribution')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f'Could not load RFM data: {e}')

elif page == '🛒 UCI — Shopper Behaviour':
    st.title('🛒 UCI Online Shopper Behaviour Analysis')
    st.markdown('**Member 2 — Araf | UCI Online Shoppers Intention**')
    st.markdown('---')
    tab1, tab2, tab3 = st.tabs(['Conversion Analysis', 'Traffic and Visitors', 'Session Quality'])
    with tab1:
        st.subheader('Purchase Conversion Funnel')
        show_html_chart('m2_conversion_funnel.html')
        st.subheader('Weekend vs Weekday Conversion')
        show_html_chart('m2_weekend_weekday.html')
        st.subheader('Page Values by Conversion Outcome')
        show_html_chart('m2_page_values_conversion.html')
    with tab2:
        st.subheader('Conversion Rate by Traffic Source')
        show_html_chart('m2_traffic_source.html')
        st.subheader('New vs Returning Visitor Analysis')
        show_html_chart('m2_visitor_type.html')
    with tab3:
        st.subheader('Bounce Rate Heatmap')
        show_png_chart('m2_bounce_heatmap.png')
        st.subheader('Session Quality by Visitor Type')
        show_html_chart('m2_session_quality.html')

elif page == '📢 Criteo — Campaign Attribution':
    st.title('📢 Criteo Digital Campaign Attribution Analysis')
    st.markdown('**Member 3 — Amber | Criteo Attribution Dataset**')
    st.markdown('---')
    tab1, tab2, tab3 = st.tabs(['Campaign Performance', 'Cost and ROAS', 'Attribution and Timing'])
    with tab1:
        st.subheader('Top 20 Campaigns by Conversion Rate')
        show_html_chart('m3_campaign_conversion_rate.html')
        st.subheader('Conversions by Attribution Model')
        show_html_chart('m3_attribution_waterfall.html')
    with tab2:
        st.subheader('Top 20 Most Efficient Campaigns by CPO')
        show_html_chart('m3_cpo_by_campaign.html')
        st.subheader('ROAS vs Average Cost by Campaign')
        show_html_chart('m3_roas_scatter.html')
    with tab3:
        st.subheader('Conversion Rate by Click Recency')
        show_html_chart('m3_click_recency_conversion.html')
        st.subheader('Conversion Rate by Hour of Day')
        show_html_chart('m3_hourly_conversion.html')
        st.subheader('Conversion Rate by Day of Week')
        show_html_chart('m3_dow_conversion.html')

elif page == '🔗 Cross-Dataset Intelligence':
    st.title('🔗 Cross-Dataset Intelligence')
    st.markdown('**Unified view combining insights from all three datasets**')
    st.markdown('---')
    st.subheader('Amazon Price Bands + Criteo Campaign Efficiency')
    st.markdown('Amber — combines Amazon spending patterns with Criteo campaign cost efficiency')
    show_png_chart('cross_amber_amazon_criteo.png')
    st.markdown('---')
    st.subheader('Amazon Quarterly Revenue + Criteo Attribution Performance')
    st.markdown('Ibrahim — Amazon seasonal revenue vs Criteo attribution model comparison')
    show_png_chart('cross_ibrahim_amazon_criteo_quarterly.png')
    st.markdown('---')
    st.subheader('Amazon Hourly Orders + Criteo Hourly Conversion')
    st.markdown('Ibrahim — are ad campaigns running at peak purchase hours')
    show_png_chart('cross_ibrahim_amazon_criteo_hourly.png')
    st.markdown('---')
    st.subheader('Amazon RFM Segments + UCI Session Quality')
    st.markdown('Araf — maps Amazon customer value tiers against UCI shopper session behaviour')
    show_png_chart('cross_araf_rfm_vs_uci_sessions.png')