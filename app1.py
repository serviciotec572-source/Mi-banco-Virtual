import streamlit as st
import pandas as pd
import uuid
import json
import os
import io
from datetime import datetime

# 1. Configuración de la página web
st.set_page_config(page_title="Mi Red Virtual Personal", page_icon="👤", layout="centered")
st.title("💰 Mi Red Virtual Personal")
st.write("Tus datos se guardan permanentemente. Ahora puedes exportar tus movimientos a Excel.")

# 2. FUNCIONES DE BASE DE DATOS (Leer y Escribir en Archivo JSON)
ARCHIVO_BD = "base_datos_banco.json"

def cargar_base_datos():
    if not os.path.exists(ARCHIVO_BD):
        return {}
    try:
        with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_base_datos(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

if "base_datos_usuarios" not in st.session_state:
    st.session_state.base_datos_usuarios = cargar_base_datos()

# ==========================================
# BARRA LATERAL: REGISTRO E INICIO DE SESIÓN
# ==========================================
st.sidebar.header("🔐 Acceso a tu Espacio Personal")
opcion_ingreso = st.sidebar.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])

usuario_actual = None

if opcion_ingreso == "Registrarse":
    st.sidebar.subheader("📝 Crear nueva red propia")
    reg_usuario = st.sidebar.text_input("Elige tu nombre de usuario:", key="reg_u").strip()
    reg_password = st.sidebar.text_input("Crea tu contraseña:", type="password", key="reg_p")
    
    if st.sidebar.button("🚀 Registrar mi espacio", use_container_width=True):
        st.session_state.base_datos_usuarios = cargar_base_datos()
        if reg_usuario == "" or reg_password == "":
            st.sidebar.error("Completa todos los campos.")
        elif reg_usuario in st.session_state.base_datos_usuarios:
            st.sidebar.error("Este usuario ya está registrado.")
        else:
            st.session_state.base_datos_usuarios[reg_usuario] = {
                "password": reg_password,
                "cuentas": {"Mi_Cuenta_Principal": 100000, "Amigo_Ejemplo": 20000, "Tienda": 0},
                "historial": []
            }
            guardar_base_datos(st.session_state.base_datos_usuarios)
            st.sidebar.success("¡Espacio guardado! Cambia a 'Iniciar Sesión'.")

elif opcion_ingreso == "Iniciar Sesión":
    st.sidebar.subheader("🔑 Ingresar")
    login_usuario = st.sidebar.text_input("Usuario:", key="log_u").strip()
    login_password = st.sidebar.text_input("Contraseña:", type="password", key="log_p")
    
    if st.sidebar.button("🔓 Entrar", use_container_width=True):
        st.session_state.base_datos_usuarios = cargar_base_datos()
        if login_usuario in st.session_state.base_datos_usuarios and st.session_state.base_datos_usuarios[login_usuario]["password"] == login_password:
            st.session_state["usuario_logueado"] = login_usuario
            st.sidebar.success(f"¡Bienvenido {login_usuario}!")
            st.rerun()
        else:
            st.sidebar.error("Usuario o contraseña incorrectos.")

if "usuario_logueado" in st.session_state:
    usuario_actual = st.session_state["usuario_logueado"]
    st.sidebar.markdown("---")
    st.sidebar.success(f"👤 Sesión activa: {usuario_actual}")
    
    if st.sidebar.button("💾 Cerrar Sesión y Guardar", use_container_width=True):
        guardar_base_datos(st.session_state.base_datos_usuarios)
        del st.session_state["usuario_logueado"]
        st.success("¡Datos guardados con éxito!")
        st.rerun()

# ==========================================
# CUERPO PRINCIPAL: SOLO VISIBLE CON SESIÓN
# ==========================================
if usuario_actual:
    mis_datos = st.session_state.base_datos_usuarios[usuario_actual]
    tab1, tab2, tab3 = st.tabs(["📊 Saldos y Nombres", "⚡ Transferencias", "🔍 Filtros e Historial"])
    
    with tab1:
        st.subheader("💵 Listado de Cuentas en tu Red")
        df_saldos = pd.DataFrame(list(mis_datos["cuentas"].items()), columns=["Nombre de Cuenta", "Saldo (Créditos)"])
        st.dataframe(df_saldos, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("✏️ Cambiar Nombre a una Cuenta")
        cuenta_a_cambiar = st.selectbox("Selecciona la cuenta que deseas renombrar:", list(mis_datos["cuentas"].keys()))
        nuevo_nombre = st.text_input("Escribe el nuevo nombre:", value=cuenta_a_cambiar)
        
        if st.button("💾 Guardar Nuevo Nombre", use_container_width=True):
            nuevo_nombre = nuevo_nombre.strip()
            if nuevo_nombre == "":
                st.error("El nombre no puede estar vacío.")
            elif nuevo_nombre in mis_datos["cuentas"] and nuevo_nombre != cuenta_a_cambiar:
                st.error("Ya existe una cuenta con ese nombre.")
            else:
                saldo_actual = mis_datos["cuentas"].pop(cuenta_a_cambiar)
                mis_datos["cuentas"][nuevo_nombre] = saldo_actual
                guardar_base_datos(st.session_state.base_datos_usuarios)
                st.success(f"¡Nombre cambiado! Guardado en el sistema.")
                st.rerun()

    with tab2:
        st.subheader("⚡ Transferencia Inmediata")
        usuarios_disponibles = list(mis_datos["cuentas"].keys())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            emisor = st.selectbox("¿Quién envía?", usuarios_disponibles, key="emisor")
        with col2:
            receptores_filtrados = [u for u in usuarios_disponibles if u != emisor]
            receptor = st.selectbox("¿Quién recibe?", receptores_filtrados, key="receptor")
        with col3:
            monto = st.number_input("Monto:", min_value=1, value=1000, step=500)
            
        if st.button("🚀 Confirmar Envío", use_container_width=True):
            if mis_datos["cuentas"][emisor] < monto:
                st.error(f"❌ Fondos insuficientes.")
            else:
                mis_datos["cuentas"][emisor] -= monto
                mis_datos["cuentas"][receptor] += monto
                
                tx_id = str(uuid.uuid4())[:8]
                registro = {
                    "ID": tx_id,
                    "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Origen": emisor,
                    "Destino": receptor,
                    "Monto": monto
                }
                mis_datos["historial"].insert(0, registro)
                guardar_base_datos(st.session_state.base_datos_usuarios)
                st.success(f"⚡ ¡Éxito! [{tx_id}] enviado.")
                st.rerun()

    # ------------------------------------------
    # PESTAÑA 3: FILTROS E HISTORIAL + BOTÓN EXCEL
    # ------------------------------------------
    with tab3:
        st.subheader("📜 Libro Contable con Filtros Inteligentes")
        if len(mis_datos["historial"]) == 0:
            st.info("Aún no registras movimientos en tu red.")
        else:
            df_historial = pd.DataFrame(mis_datos["historial"])
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_persona = st.text_input("🔍 Filtrar por nombre:").strip()
            with col_f2:
                monto_minimo = st.number_input("💰 Mostrar montos mayores o iguales a:", min_value=0, value=0)
                
            df_filtrado = df_historial.copy()
            if filtro_persona != "":
                df_filtrado = df_filtrado[(df_filtrado["Origen"].str.contains(filtro_persona, case=False)) | (df_filtrado["Destino"].str.contains(filtro_persona, case=False))]
            if monto_minimo > 0:
                df_filtrado = df_filtrado[df_filtrado["Monto"] >= monto_minimo]
                
            if df_filtrado.empty:
                st.warning("No se encontraron transacciones.")
            else:
                # Mostrar la tabla filtrada en pantalla
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("📥 Exportar Reporte Financiero")
                
                # Convertimos el DataFrame a un formato de memoria binario que entienda Excel
                buffer_excel = io.BytesIO()
                with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
                    df_filtrado.to_excel(writer, index=False, sheet_name="Transacciones")
                
                # BOTÓN INTERACTIVO DE DESCARGA
                st.download_button(
                    label="🟢 Descargar Historial en Excel (.xlsx)",
                    data=buffer_excel.getvalue(),
                    file_name=f"reporte_banco_{usuario_actual}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
else:
    st.warning("👋 Por favor, regístrate o inicia sesión en la barra lateral para ver tus datos.")