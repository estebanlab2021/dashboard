import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Dashboard de Negocios", layout="wide")

st.title("📊 Dashboard de Negocios")

# Cargar archivo
#uploaded_file = st.sidebar.file_uploader("Carga tu archivo CSV", type=["csv"])
df = pd.read_csv("base_negocios.csv", sep=";", decimal=',') 

st.write("Vista previa de los datos")
st.dataframe(df.head())


# Limpiar y formatear columnas numéricas si usan ',' decimal
for col in ['ingreso', 'cantidad', 'utilidad']:
    df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convertir fecha
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

# Sidebar - Filtros
productos = ['Todos'] + sorted(df['producto'].dropna().unique().tolist())
regiones = ['Todas'] + sorted(df['region'].dropna().unique().tolist())
canales = ['Todos'] + sorted(df['canal_venta'].dropna().unique().tolist())

producto_sel = st.sidebar.selectbox("Filtrar por producto", productos)
region_sel = st.sidebar.selectbox("Filtrar por región", regiones)
canal_sel = st.sidebar.selectbox("Filtrar por canal de venta", canales)

# Aplicar filtros
df_filtrado = df.copy()
if producto_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['producto'] == producto_sel]
if region_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['region'] == region_sel]
if canal_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['canal_venta'] == canal_sel]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("💰 Ingreso Total", f"${df_filtrado['ingreso'].sum():,.0f}")
col2.metric("📦 Unidades Vendidas", f"{df_filtrado['cantidad'].sum():,.0f}")
col3.metric("👥 Prom. por Cliente", f"${df_filtrado.groupby('cliente_id')['ingreso'].sum().mean():,.0f}")
    

col4, col5, col6 = st.columns(3)
col4.metric("📈 Rentabilidad Prom.", f"${df_filtrado['utilidad'].mean():,.0f}")
col5.metric("🌎 Prom. por Región", f"${df_filtrado.groupby('region')['ingreso'].sum().mean():,.0f}")
col6.metric("🛍️ Prom. por Producto", f"${df_filtrado.groupby('producto')['ingreso'].sum().mean():,.0f}")

# Gráficos
st.markdown("## Visualizaciones")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Ventas por Región")
    fig1, ax1 = plt.subplots()
    df_filtrado.groupby('region')['ingreso'].sum().plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_ylabel("Ingreso")
    st.pyplot(fig1)

with col2:
    st.subheader("Ventas por Canal")
    fig_pie, ax_pie = plt.subplots()
    canales = df_filtrado.groupby('canal_venta')['ingreso'].sum()
    wedges, texts, autotexts = ax_pie.pie(
        canales,
        labels=canales.index,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops=dict(width=0.4)  # ancho < 1 crea el efecto "dona"
    )
    ax_pie.axis('equal')  # Hace el círculo perfecto
    ax_pie.set_title("Distribución de Ingresos por Canal de Venta")
    st.pyplot(fig_pie)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Ingresos en el Tiempo")
    fig3, ax3 = plt.subplots()
    df_filtrado.groupby('fecha')['ingreso'].sum().plot(ax=ax3, color='green')
    ax3.set_ylabel("Ingreso")
    st.pyplot(fig3)

with col4:
    st.subheader("Unidades Vendidas por Producto")
    fig4, ax4 = plt.subplots()
    df_filtrado.groupby('producto')['cantidad'].sum().sort_values().plot(kind='barh', ax=ax4, color='orange')
    ax4.set_xlabel("Cantidad")
    st.pyplot(fig4)

col5, col6 = st.columns(2)
with col5:
    st.subheader("Ventas por Canal en el Tiempo")
    serie_canal = df_filtrado.groupby(['fecha', 'canal_venta'])['ingreso'].sum().reset_index()
    fig5, ax5 = plt.subplots()
    for canal, datos in serie_canal.groupby('canal_venta'):
        ax5.plot(datos['fecha'], datos['ingreso'], label=canal)
    ax5.set_xlabel("Fecha")
    ax5.set_ylabel("Ingreso")
    ax5.set_title("Ingresos por Canal de Venta")
    ax5.legend(title="Canal", fontsize="small", loc="upper left")
    ax5.grid(True)
    st.pyplot(fig5)

with col6:
    st.subheader("Unidades por Producto en el Tiempo")
    serie_producto = df_filtrado.groupby(['fecha', 'producto'])['cantidad'].sum().reset_index()
    fig6, ax6 = plt.subplots()
    for producto, datos in serie_producto.groupby('producto'):
        ax6.plot(datos['fecha'], datos['cantidad'], label=producto)
    ax6.set_xlabel("Fecha")
    ax6.set_ylabel("Unidades")
    ax6.set_title("Unidades Vendidas por Producto")
    ax6.legend(title="Producto", fontsize="small", loc="upper left")
    ax6.grid(True)
    st.pyplot(fig6)

# Botón para exportar datos filtrados
csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Descargar datos filtrados", data=csv_export, file_name="datos_filtrados.csv", mime="text/csv")

