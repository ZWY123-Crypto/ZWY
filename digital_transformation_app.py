import pandas as pd
import streamlit as st
import plotly.express as px

# 设置页面配置
st.set_page_config(
    page_title="企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载数据
@st.cache_data

def load_data():
    # 加载数字化转型指数数据
    df = pd.read_excel('1999-2023数值化转型指数数据汇总表.xlsx')
    # 确保股票代码为6位字符串格式，便于显示和查询
    df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)
    # 去除列名中的空格和换行符
    df.columns = [col.replace(' ', '').replace('\n', '') for col in df.columns]
    
    # 加载行业信息数据
    industry_df = pd.read_excel('最终数据dta格式-上市公司年度行业代码至2021.xlsx')
    # 确保股票代码为6位字符串格式
    industry_df['股票代码全称'] = industry_df['股票代码全称'].astype(str).str.zfill(6)
    # 重命名列名以匹配
    industry_df = industry_df.rename(columns={
        '股票代码全称': '股票代码',
        '年度': '年份',
        '行业代码': '行业代码',
        '行业名称': '行业名称'
    })
    # 选择需要的列
    industry_df = industry_df[['股票代码', '年份', '行业代码', '行业名称']]
    
    # 将行业信息与数字化转型指数数据合并
    df = pd.merge(df, industry_df, on=['股票代码', '年份'], how='left')
    
    return df

df = load_data()

# 侧边栏
st.sidebar.title("查询条件")

# 获取所有股票代码和年份
years = sorted(df['年份'].unique())

# 创建股票代码和企业名称的映射字典
stock_name_map = df.drop_duplicates(subset=['股票代码'])[['股票代码', '企业名称']].set_index('股票代码')['企业名称'].to_dict()

# 生成格式化的股票代码选项（股票代码 - 企业名称）
formatted_stock_options = [f"{code} - {stock_name_map[code]}" for code in sorted(stock_name_map.keys())]

# 股票代码选择
selected_stock_option = st.sidebar.selectbox(
    "选择股票代码",
    options=formatted_stock_options,
    index=0
)

# 从选择的选项中提取股票代码
selected_stock = selected_stock_option.split(" - ")[0]

# 年份选择（下拉模式）
selected_year = st.sidebar.selectbox(
    "选择年份",
    options=years,
    index=0
)

# 主标题
st.title("企业数字化转型指数查询系统")

# 数据概览部分
st.header("数据概览")
overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    total_companies = df['股票代码'].nunique()
    st.metric("企业总数", total_companies)

with overview_col2:
    total_years = df['年份'].nunique()
    st.metric("年份跨度", f"{min(years)}-{max(years)}")

with overview_col3:
    avg_index = df['数字化转型指数'].mean()
    st.metric("平均数字化转型指数", f"{avg_index:.4f}")

with overview_col4:
    max_index = df['数字化转型指数'].max()
    st.metric("最高数字化转型指数", f"{max_index:.4f}")

# 数字化转型指数查询部分
st.header("数字化转型指数查询")

# 根据选择的股票代码获取该企业所有数据
company_all_data = df[df['股票代码'] == selected_stock].sort_values('年份')

# 根据选择的股票代码和年份筛选数据
filtered_data = df[(df['股票代码'] == selected_stock) & (df['年份'] == selected_year)]

# 检查股票是否存在
if company_all_data.empty:
    st.warning("未找到该股票的任何数据")
else:
    # 获取企业名称
    company_name = filtered_data['企业名称'].iloc[0] if not filtered_data.empty else company_all_data['企业名称'].iloc[0]
    
    # 显示企业名称和行业信息
    st.subheader(f"{company_name} ({selected_stock}) 数字化转型指数")
    
    if not filtered_data.empty:
        # 获取行业信息
        industry_name = filtered_data['行业名称'].iloc[0] if '行业名称' in filtered_data.columns and not pd.isna(filtered_data['行业名称'].iloc[0]) else '未知'
        industry_code = filtered_data['行业代码'].iloc[0] if '行业代码' in filtered_data.columns and not pd.isna(filtered_data['行业代码'].iloc[0]) else '未知'
        st.write(f"**行业信息**：{industry_name} ({industry_code})")
        
        # 数字化转型指数详细统计
        st.subheader("数字化转型指数详细统计")
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            avg_digital_index = filtered_data['数字化转型指数'].mean()
            st.metric("平均数字化转型指数", f"{avg_digital_index:.4f}")
            
            max_digital_index = filtered_data['数字化转型指数'].max()
            st.metric("最高数字化转型指数", f"{max_digital_index:.4f}")
            
            min_digital_index = filtered_data['数字化转型指数'].min()
            st.metric("最低数字化转型指数", f"{min_digital_index:.4f}")
        
        with stats_col2:
            avg_tech_dim = filtered_data['技术维度'].mean()
            st.metric("平均技术维度", f"{avg_tech_dim:.4f}")
            
            avg_app_dim = filtered_data['应用维度'].mean()
            st.metric("平均应用维度", f"{avg_app_dim:.4f}")
            
            avg_total_words = filtered_data['词总'].mean()
            st.metric("平均词总数", f"{avg_total_words:.4f}")
        
        with stats_col3:
            avg_ai_words = filtered_data['人工智能词频数'].mean()
            st.metric("平均人工智能词频数", f"{avg_ai_words:.2f}")
            
            avg_bigdata_words = filtered_data['大数据词频数'].mean()
            st.metric("平均大数据词频数", f"{avg_bigdata_words:.2f}")
            
            avg_cloud_words = filtered_data['云计算词频数'].mean()
            st.metric("平均云计算词频数", f"{avg_cloud_words:.2f}")
    
    # 历史指数折线图
    st.subheader("历史指数折线图")
    
    # 准备折线图数据（显示该企业所有年份的数据）
    chart_data = company_all_data[['年份', '数字化转型指数']]
    
    # 创建折线图
    fig = px.line(
        chart_data,
        x='年份',
        y=['数字化转型指数'],
        title=f"{company_name} ({selected_stock}) 数字化转型指数趋势",
        labels={'value': '指数值', 'variable': '指数类型'},
        markers=True
    )
    
    # 标注选择年份的数据点（如果存在）
    selected_year_data = company_all_data[company_all_data['年份'] == selected_year]
    if not selected_year_data.empty:
        selected_value = selected_year_data['数字化转型指数'].iloc[0]
        fig.add_scatter(
            x=[selected_year],
            y=[selected_value],
            mode='markers+text',
            text=[f"{selected_value:.2f}"],
            textposition='top center',
            marker=dict(color='red', size=12),
            showlegend=False
        )
    else:
        st.warning(f"未找到 {company_name} ({selected_stock}) 在 {selected_year} 年的数据")
    
    # 美化图表
    fig.update_layout(
        xaxis_title="年份",
        yaxis_title="指数值",
        hovermode="x unified",
        legend_title="指数类型",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, width='stretch')
    
    if not filtered_data.empty:
        # 显示详细数据表格
        st.subheader("详细数据")
        st.dataframe(filtered_data.sort_values('年份'), width='stretch')
    else:
        # 只显示提示信息，不显示所有年份数据
        st.warning(f"未找到 {company_name} ({selected_stock}) 在 {selected_year} 年的数据")

# 原始数据预览（当前股票的1999-2023年数据）
st.subheader("原始数据预览")
# 筛选当前股票的1999-2023年数据
original_data = df[(df['股票代码'] == selected_stock) & (df['年份'] >= 1999) & (df['年份'] <= 2023)].sort_values('年份')
st.dataframe(original_data, width='stretch')

# 数据下载功能
st.subheader("数据下载")
# 准备下载数据（与原始数据预览相同的数据）
download_data = original_data.copy()
# 转换为CSV格式
csv = download_data.to_csv(index=False, encoding='utf-8-sig')
# 添加下载按钮
st.download_button(
    label="下载1999-2023年原始数据 (CSV)",
    data=csv,
    file_name="1999-2023_数字化转型指数原始数据.csv",
    mime="text/csv",
    key="download_csv"
)

# 页脚
st.markdown("---")
st.markdown("© 2024 企业数字化转型指数查询系统")