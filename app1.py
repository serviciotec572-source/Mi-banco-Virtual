import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# 1. Configuración de la página web
st.set_page_config(page_title="Mi Banco Virtual Pro", page_icon="💰", layout="centered")
st.title("💰 Mi Banco Virtual Pro")
st.write("Red de créditos independiente de circuito cerrado.")

# 2. Inicializar la base de datos extendida (Más nombres precargados)
if "cuentas" not in st.session_state:
    st.session_state.cuentas = {
        "Carlos": 50000, 
        "Andrea": 10000, 
        "Tienda_Oficina": 0,
        "Juan": 25000,
        "Maria": 75000,
        "Santiago": 15000,
        "Valentina": 40000
    }

# Almacenamos también la fecha en que se unió cada miembro
if "fechas_registro" not in st.session_state:
    ahora_mismo = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.fechas_registro = {u: ahora_mismo for u in st.session_state.cuentas}

if "historial" not in st.session_state:
    st.session_state.historial = []

# ==========================================
# PANEL LATERAL: CONTROL DE ACCESO Y REGISTRO
# ==========================================
st.sidebar.header("🔐 Acceso Administrador")
password_ingresada = st.sidebar.text_input("Contraseña de red:", type="password")

# Cambia "TuClave123" por la clave que quieras o déjala vacía para pruebas locales
clave_correcta = "TuClave123" 

if password_ingresada == clave_correcta:
    st.sidebar.success("🔑 Acceso concedido")
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Registrar Nuevo Usuario")
    
    nuevo_usuario = st.sidebar.text_input("Nombre del nuevo miembro:")
    saldo_inicial = st.sidebar.number_input("Saldo inicial (Créditos):", min_value=0, value=0, step=1000)

    # BOTÓN PARA CREAR CUENTA
    if st.sidebar.button("➕ Crear Cuenta Nueva", use_container_width=True):
        if nuevo_usuario.strip() == "":
            st.sidebar.error("El nombre no puede estar vacío.")
        elif nuevo_usuario in st.session_state.cuentas:
            st.sidebar.error("Este usuario ya existe en la red.")
        else:
            # Registramos el saldo y capturamos la FECHA/HORA exacta del registro
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.cuentas[nuevo_usuario] = saldo_inicial
            st.session_state.fechas_registro[nuevo_usuario] = fecha_actual
            
            st.sidebar.success(f"¡{nuevo_usuario} registrado con éxito el {fecha_actual}!")
            st.rerun()
else:
    if password_ingresada != "":
        st.sidebar.error("❌ Contraseña incorrecta")
    else:
        st.sidebar.info("Introduce la contraseña para habilitar el botón de creación.")

# ==========================================
# CUERPO PRINCIPAL: SALDOS Y FECHAS
# ==========================================
st.subheader("💵 Listado General de Miembros")

# Unimos los saldos y las fechas de registro en una sola tabla bonita
datos_tabla = []
for usuario in st.session_state.cuentas:
    datos_tabla.append({
        "Usuario": usuario,
        "Saldo (Créditos)": st.session_state.cuentas[usuario],
        "Fecha de Ingreso": st.session_state.fechas_registro.get(usuario, "N/A")
    })

df_saldos = pd.DataFrame(datos_tabla)
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

# BOTÓN INTERACTIVO PARA TRANSFERIR
if st.button("🚀 Confirmar Envío de Fondos", use_container_width=True):
    if st.session_state.cuentas[emisor] < monto:
        st.error(f"❌ Transferencia rechazada: {emisor} no tiene fondos suficientes (Saldo: {st.session_state.cuentas[emisor]}).")
    else:
        st.session_state.cuentas[emisor] -= monto
        st.session_state.cuentas[receptor] += monto
        
        tx_id = str(uuid.uuid4())[:8]
        registro = {
            "ID Transacción": tx_id,
            "Fecha/Hora Envío": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Origen": emisor,
            "Destino": receptor,
            "Monto Transaccionado": monto
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