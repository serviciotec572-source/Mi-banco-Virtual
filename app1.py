import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# 1. Configuración de la página web
st.set_page_config(page_title="Mi Banco Virtual Bobo", page_icon="💰", layout="centered")
st.title("💰 Mi Banco Virtual Bobo")
st.write("Una red de créditos 100% independiente de los bancos reales.")

# 2. Inicializar la base de datos en la memoria de la página web
if "cuentas" not in st.session_state:
    st.session_state.cuentas = {"Carlos": 50000, "Andrea": 10000, "Tienda_Oficina": 0}

if "historial" not in st.session_state:
    st.session_state.historial = []

# ==========================================
# PANEL LATERAL: CREAR NUEVOS USUARIOS
# ==========================================
st.sidebar.header("👤 Registrar Usuario")
nuevo_usuario = st.sidebar.text_input("Nombre del nuevo miembro:")
saldo_inicial = st.sidebar.number_input("Saldo inicial (Créditos):", min_value=0, value=0, step=1000)

if st.sidebar.button("Crear Cuenta"):
    if nuevo_usuario.strip() == "":
        st.sidebar.error("El nombre no puede estar vacío.")
    elif nuevo_usuario in st.session_state.cuentas:
        st.sidebar.error("Este usuario ya existe en la red.")
    else:
        st.session_state.cuentas[nuevo_usuario] = saldo_inicial
        st.sidebar.success(f"¡{nuevo_usuario} registrado con éxito!")
        st.rerun()

# ==========================================
# CUERPO PRINCIPAL: SALDOS ACTUALES
# ==========================================
st.subheader("💵 Saldos en la Red")
df_saldos = pd.DataFrame(list(st.session_state.cuentas.items()), columns=["Usuario", "Saldo (Créditos)"])
st.dataframe(df_saldos, use_container_width=True, hide_index=True)

# ==========================================
# SECCIÓN: HACER TRANSFERENCIA ÁGIL
# ==========================================
st.subheader("⚡ Transferencia Inmediata")

usuarios_disponibles = list(st.session_state.cuentas.keys())

col1, col2, col3 = st.columns(3)
with col1:
    emisor = st.selectbox("¿Quién envía?", usuarios_disponibles, key="emisor")
with col2:
    receptores_filtrados = [u for u in usuarios_disponibles if u != emisor]
    receptor = st.selectbox("¿Quién recibe?", receptores_filtrados, key="receptor")
with col3:
    monto = st.number_input("Monto a enviar:", min_value=1, value=1000, step=500)

if st.button("🚀 Confirmar Transferencia", use_container_width=True):
    if st.session_state.cuentas[emisor] < monto:
        st.error(f"❌ Transferencia rechazada: {emisor} no tiene fondos suficientes (Saldo: {st.session_state.cuentas[emisor]}).")
    else:
        st.session_state.cuentas[emisor] -= monto
        st.session_state.cuentas[receptor] += monto
        
        tx_id = str(uuid.uuid4())[:8]
        registro = {
            "ID Transacción": tx_id,
            "Fecha/Hora": datetime.now().strftime("%H:%M:%S"),
            "Origen": emisor,
            "Destino": receptor,
            "Monto": monto
        }
        st.session_state.historial.insert(0, registro)
        st.success(f"⚡ ¡Éxito! [{tx_id}] {emisor} envió {monto} créditos a {receptor}.")
        st.rerun()

# ==========================================
# SECCIÓN: HISTORIAL DE MOVIMIENTOS
# ==========================================
st.subheader("📜 Libro Contable (Historial Global)")
if len(st.session_state.historial) == 0:
    st.info("Aún no se han realizado transferencias en esta sesión.")
else:
    df_historial = pd.DataFrame(st.session_state.historial)
    st.table(df_historial)

