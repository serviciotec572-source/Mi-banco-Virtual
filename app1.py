import streamlit as st
import pandas as pd
import uuid
import json
import os
import io
from datetime import datetime

# 1. Configuración estética de la plataforma
st.set_page_config(page_title="Mi Red Virtual Personal", page_icon="👤", layout="centered")
st.title("💰 Mi Red Virtual Personal")
st.write("Cada usuario cuenta con un espacio privado y seguro para gestionar sus créditos.")

# 2. SISTEMA DE BASE DE DATOS PERMANENTE (Archivo JSON en el Servidor)
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

# Inicializar la base de datos leyendo el archivo JSON seguro
if "base_datos_usuarios" not in st.session_state:
    st.session_state.base_datos_usuarios = cargar_base_datos()

# ==========================================
# BARRA LATERAL: CONTROL DE ACCESO ESTRICTO
# ==========================================
st.sidebar.header("🔐 Acceso a tu Espacio Personal")
opcion_ingreso = st.sidebar.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])

usuario_actual = None

if opcion_ingreso == "Registrarse":
    st.sidebar.subheader("📝 Crear nueva cuenta")
    reg_usuario = st.sidebar.text_input("Elige tu usuario:", key="reg_u").strip()
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
                "cuentas": {
                    "Cuenta_Principal": 10000000,
                    "Amigo_Ejemplo": 2000000,
                    "Tienda_Oficina": 0
                },
                "historial": []
            }
            guardar_base_datos(st.session_state.base_datos_usuarios)
            st.sidebar.success("¡Espacio guardado! Cambia a 'Iniciar Sesión' e ingresa.")

elif opcion_ingreso == "Iniciar Sesión":
    st.sidebar.subheader("🔑 Ingresar al Sistema")
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

# Control de sesión activa y botón de guardado total
if "usuario_logueado" in st.session_state:
    usuario_actual = st.session_state["usuario_logueado"]
    st.sidebar.markdown("---")
    st.sidebar.success(f"👤 Sesión activa: {usuario_actual}")
    
    if st.sidebar.button("💾 Cerrar Sesión y Guardar", use_container_width=True):
        guardar_base_datos(st.session_state.base_datos_usuarios)
        del st.session_state["usuario_logueado"]
        st.rerun()

# ==========================================
# CUERPO PRINCIPAL: BLOQUEADO SIN INICIO DE SESIÓN
# ==========================================
if usuario_actual:
    mis_datos = st.session_state.base_datos_usuarios[usuario_actual]
    tab1, tab2, tab3 = st.tabs(["📊 Gestión de Cuentas y Saldos", "⚡ Enviar Fondos", "🔍 Historial, Fechas y Filtros"])
    
    # PESTAÑA 1: MOSTRAR SALDOS Y CAMBIAR NOMBRES
    with tab1:
        st.subheader("💵 Listado de Cuentas en tu Red")
        df_saldos = pd.DataFrame(list(mis_datos["cuentas"].items()), columns=["Nombre de Cuenta", "Saldo Actual (Créditos)"])
        st.dataframe(df_saldos, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("✏️ Cambiar Nombre o Configurar Monto de una Cuenta")
        cuenta_a_cambiar = st.selectbox("Selecciona la cuenta a modificar:", list(mis_datos["cuentas"].keys()))
        nuevo_nombre = st.text_input("Modificar Nombre:", value=cuenta_a_cambiar)
        nuevo_monto_directo = st.number_input("Modificar Monto Directamente:", min_value=0, value=int(mis_datos["cuentas"][cuenta_a_cambiar]), step=1000)
        
        if st.button("💾 Guardar Cambios en la Cuenta", use_container_width=True):
            nuevo_nombre = nuevo_nombre.strip()
            if nuevo_nombre == "":
                st.error("El nombre no puede estar vacío.")
            else:
                if nuevo_nombre != cuenta_a_cambiar:
                    mis_datos["cuentas"].pop(cuenta_a_cambiar)
                mis_datos["cuentas"][nuevo_nombre] = nuevo_monto_directo
                guardar_base_datos(st.session_state.base_datos_usuarios)
                st.success(f"¡Cambios guardados! '{cuenta_a_cambiar}' se actualizó correctamente.")
                st.rerun()

    # PESTAÑA 2: ENVIAR DINERO CON CONTROL DE MONTOS
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
            monto = st.number_input("Monto a enviar:", min_value=1, value=5000, step=500)
            
        if st.button("🚀 Confirmar Envío Inmediato", use_container_width=True):
            if mis_datos["cuentas"][emisor] < monto:
                st.error(f"❌ Transferencia rechazada: {emisor} no tiene fondos suficientes.")
            else:
                mis_datos["cuentas"][emisor] -= monto
                mis_datos["cuentas"][receptor] += monto
                
                ahora = datetime.now()
                tx_id = str(uuid.uuid4())[:8]
                registro = {
                    "ID Transacción": tx_id,
                    "Fecha": ahora.strftime("%Y-%m-%d"),
                    "Hora": ahora.strftime("%H:%M:%S"),
                    "Origen (Envía)": emisor,
                    "Destino (Recibe)": receptor,
                    "Monto Enviado": monto
                }
                mis_datos["historial"].insert(0, registro)
                guardar_base_datos(st.session_state.base_datos_usuarios)
                st.success(f"⚡ ¡Éxito! [{tx_id}] Enviado correctamente.")
                st.rerun()

    # PESTAÑA 3: FILTROS, HISTORIAL CON FECHA/HORA Y EXCEL
    with tab3:
        st.subheader("📜 Libro Contable (Historial de Envíos)")
        
        if len(mis_datos["historial"]) == 0:
            st.info("Aún no registras movimientos en tu historial de envíos.")
        else:
            df_historial = pd.DataFrame(mis_datos["historial"])
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_persona = st.text_input("🔍 Buscar por Nombre (Quién envía o recibe):").strip()
            with col_f2:
                monto_minimo = st.number_input("💰 Filtrar por Montos mayores o iguales a:", min_value=0, value=0)
                
            df_filtrado = df_historial.copy()
            if filtro_persona != "":
                df_filtrado = df_filtrado[
                    (df_filtrado["Origen (Envía)"].str.contains(filtro_persona, case=False)) | 
                    (df_filtrado["Destino (Recibe)"].str.contains(filtro_persona, case=False))
                ]
            if monto_minimo > 0:
                df_filtrado = df_filtrado[df_filtrado["Monto Enviado"] >= monto_minimo]
                
            if df_filtrado.empty:
                st.warning("No se encontraron transferencias que coincidan con la búsqueda.")
            
            # Lógica plana sin bloques 'else' conflictivos para prevenir fugas y errores de sangría
            if not df_filtrado.empty:
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                st.markdown("---")
                st.subheader("📥 Descargar Reporte")
                
               
                
                
                   
                    file_name=f"reporte_banco_{usuario_actual}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
else:
    st.warning("👋 Tu espacio está protegido. Por favor, crea una cuenta en la pestaña 'Registrarse' o inicia sesión para ingresar a ver tus montos y realizar envíos.")