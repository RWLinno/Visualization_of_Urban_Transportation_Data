import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import folium
from streamlit_folium import st_folium

# 随机生成停车场数据
def generate_parking_data():
    return [
        {"id": i, "name": f"停车场 {i+1}", "lat": random.uniform(1.25, 1.4), "lon": random.uniform(103.7, 104)}
        for i in range(10)
    ]

# 生成随机停车量数据
def generate_parking_volume():
    return [random.randint(50, 200) for _ in range(30)] + [random.randint(60, 150) for _ in range(7)]

# 生成随机车型数据
def generate_vehicle_data():
    car_types = ["轿车", "SUV", "皮卡", "货车"]
    return {car_type: {"燃油车": random.randint(50, 200), "新能源": random.randint(20, 80)} for car_type in car_types}

# 初始化 Streamlit
st.set_page_config(layout="wide")
st.title("新加坡停车场可视化仪表盘")

# 使用 session_state 管理停车场和选中状态
if "parking_data" not in st.session_state:
    st.session_state["parking_data"] = generate_parking_data()
if "selected_parking_lot" not in st.session_state:
    st.session_state["selected_parking_lot"] = None

# 主布局：左侧地图，右侧两个图表
col1, col2 = st.columns([1, 2])

# 左侧地图
with col1:
    st.subheader("新加坡停车场分布")

    # 初始化地图
    m = folium.Map(location=[1.35, 103.85], zoom_start=12)
    for lot in st.session_state["parking_data"]:
        icon_color = "red" if lot["id"] == st.session_state["selected_parking_lot"] else "blue"
        folium.Marker(
            location=[lot["lat"], lot["lon"]],
            popup=lot["name"],
            tooltip=lot["name"],
            icon=folium.Icon(color=icon_color)
        ).add_to(m)

    # 显示地图并捕获交互
    map_data = st_folium(m, width=600, height=600)

    # 检查选中状态
    if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
        for lot in st.session_state["parking_data"]:
            if lot["lat"] == map_data["last_object_clicked"]["lat"] and lot["lon"] == map_data["last_object_clicked"]["lng"]:
                st.session_state["selected_parking_lot"] = lot["id"]
                break

# 右侧图表
with col2:
    if st.session_state["selected_parking_lot"] is not None:
        selected_lot = next(
            lot for lot in st.session_state["parking_data"] if lot["id"] == st.session_state["selected_parking_lot"]
        )

        st.write(f"**停车场名称**: {selected_lot['name']}")
        st.write(f"**经纬度**: {selected_lot['lat']:.6f}, {selected_lot['lon']:.6f}")

        # 停车量折线图
        parking_volume = generate_parking_volume()
        dates = pd.date_range(start="2024-01-01", periods=30).tolist() + pd.date_range(start="2024-02-01", periods=7).tolist()
        df_parking_volume = pd.DataFrame({
            "日期": dates,
            "停车量": parking_volume,
            "类型": ["历史数据"] * 30 + ["预测数据"] * 7
        })

        # 车型堆叠柱状图
        vehicle_data = generate_vehicle_data()
        car_types = list(vehicle_data.keys())
        fuel_cars = [vehicle_data[car]["燃油车"] for car in car_types]
        electric_cars = [vehicle_data[car]["新能源"] for car in car_types]

        # 横向分布的图表布局
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.subheader("停车量折线图")
            fig_line = px.line(df_parking_volume, x="日期", y="停车量", color="类型", markers=True,
                               title="停车场一个月内的停车量及未来一周预测")
            st.plotly_chart(fig_line, use_container_width=True)

        with fig_col2:
            st.subheader("车型堆叠柱状图")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="燃油车", x=car_types, y=fuel_cars, marker_color="blue"))
            fig_bar.add_trace(go.Bar(name="新能源", x=car_types, y=electric_cars, marker_color="green"))
            fig_bar.update_layout(
                barmode="stack",
                title="不同车型的新能源和燃油车数量对比",
                xaxis_title="车型",
                yaxis_title="车辆数量"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("请选择一个停车场以查看详细信息")