import streamlit as st
import pandas as pd
import uuid
import json
import os
import io
import random
import urllib.parse
from datetime import datetime

# 1. Configuración estética de la plataforma
st.set_page_config(page_title="Mi Red Virtual Alfanumérica", page_icon="⚡", layout="centered")
st.title("⚡ Red Virtual Financiera Alfanumérica Pro")
st.write("Manejo de créditos avanzados, transferencias globales, préstamos y analíticas.")

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

def generar_codigo_cuenta():
    """Genera un código de cuenta alfanumérico único, ej: ACC-4F92B"""
    codigo = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
    return f"ACC-{codigo}"

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
    
    # Campo opcional para ingresar el código de invitación de un amigo
    codigo_invitacion = st.sidebar.text_input("Código de Invitación (Opcional):", key="reg_inv").strip().upper()
    
    if st.sidebar.button("🚀 Registrar mi espacio", use_container_width=True):
        st.session_state.base_datos_usuarios = cargar_base_datos()
        
        if reg_usuario == "" or reg_password == "":
            st.sidebar.error("Completa todos los campos.")
        elif reg_usuario in st.session_state.base_datos_usuarios:
            st.sidebar.error("Este usuario ya está registrado.")
        else:
            # Generar lista de personas base
            nombres_base = [
                "Tu_Cuenta_Principal", "Carlos_Mendoza", "Andrea_Restrepo", 
                "Tienda_Oficina_Express", "Juan_Pablo_Diaz", "Maria_Camila_Silva", 
                "Santiago_Gomez", "Valentina_Herrera", "Supermercado_Central", "Estacion_Servicio_Alfa"
            ]
            
            cuentas_alfanumericas = {}
            for i, nombre in enumerate(nombres_base):
                codigo_acc = generar_codigo_cuenta()
                saldo = 10000000 if i == 0 else random.randint(500000, 3000000)
                cuentas_alfanumericas[codigo_acc] = {
                    "titular": nombre,
                    "saldo": saldo
                }
            
            codigo_referido_propio = f"REF-{reg_usuario[:4].upper()}{random.randint(10,99)}"
            
            st.session_state.base_datos_usuarios[reg_usuario] = {
                "password": reg_password,
                "codigo_referido": codigo_referido_propio,
                "cuentas": cuentas_alfanumericas,
                "historial": [],
                "prestamos": []
            }
            
            bono_aplicado = False
            if codigo_invitacion != "":
                for usuario_sistema, datos_sistema in st.session_state.base_datos_usuarios.items():
                    if datos_sistema.get("codigo_referido") == codigo_invitacion:
                        cuentas_anfitrion = list(datos_sistema["cuentas"].keys())
                        if cuentas_anfitrion:
                            primera_cuenta_anfitrion = cuentas_anfitrion[0]
                            datos_sistema["cuentas"][primera_cuenta_anfitrion]["saldo"] += 50000
                        
                        cuentas_nuevas = list(cuentas_alfanumericas.keys())
                        if cuentas_nuevas:
                            primera_cuenta_nuevo = cuentas_nuevas[0]
                            cuentas_alfanumericas[primera_cuenta_nuevo]["saldo"] += 50000
                        
                        bono_aplicado = True
                        break
            
            guardar_base_datos(st.session_state.base_datos_usuarios)
            if bono_aplicado:
                st.sidebar.success("🎁 ¡Bono activado! +50.000 créditos para ambos. Inicia sesión.")
            else:
                st.sidebar.success("¡Espacio guardado! Inicia sesión.")

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

if "usuario_logueado" in st.session_state:
    usuario_actual = st.session_state["usuario_logueado"]
    st.sidebar.markdown("---")
    st.sidebar.success(f"👤 Sesión activa: {usuario_actual}")
    
    if st.sidebar.button("💾 Cerrar Sesión y Guardar", use_container_width=True):
        guardar_base_datos(st.session_state.base_datos_usuarios)
        del st.session_state["usuario_logueado"]
        st.rerun()

# ==========================================
# CUERPO PRINCIPAL: VISIBLE CON SESIÓN
# ==========================================
if usuario_actual:
    if "prestamos" not in st.session_state.base_datos_usuarios[usuario_actual]:
        st.session_state.base_datos_usuarios[usuario_actual]["prestamos"] = []
        
    mis_datos = st.session_state.base_datos_usuarios[usuario_actual]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Directorio y Saldos", "⚡ Envíos Alfanuméricos", "🏦 Solicitud Préstamos",
        "📈 Analíticas Visuales", "🔍 Auditoría y Reportes", "📢 Invitar Amigos"
    ])
    
    # ------------------------------------------
    # PESTAÑA 1: DIRECTORIO DE CUENTAS Y CREACIÓN
    # ------------------------------------------
    with tab1:
        st.subheader("📋 Cuentas Alfanuméricas Autorizadas")
        tabla_saldos = []
        for codigo, info in mis_datos["cuentas"].items():
            tabla_saldos.append({
                "Código de Cuenta": codigo,
                "Titular de la Cuenta": info["titular"],
                "Saldo Disponible (COP)": info["saldo"]
            })
        
        df_saldos = pd.DataFrame(tabla_saldos)
        st.dataframe(df_saldos, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ➕ Crear Nueva Cuenta")
            nombre_nueva_cuenta = st.text_input("Nombre del Titular de la cuenta:", placeholder="Ej: Mi Caja de Ahorros")
            if st.button("✨ Generar Cuenta Única", use_container_width=True):
                if nombre_nueva_cuenta.strip() == "":
                    st.error("Por favor, ingresa un nombre para el titular.")
                else:
                    nuevo_cod = generar_codigo_cuenta()
                    mis_datos["cuentas"][nuevo_cod] = {"titular": nombre_nueva_cuenta.strip(), "saldo": 0}
                    guardar_base_datos(st.session_state.base_datos_usuarios)
                    st.success(f"Cuenta {nuevo_cod} creada con éxito.")
                    st.rerun()
                    
        with col2:
            st.markdown("### ✏️ Configurar Existente")
            cuenta_a_cambiar = st.selectbox("Selecciona cuenta a editar:", list(mis_datos["cuentas"].keys()))
            nombre_actual = mis_datos["cuentas"][cuenta_a_cambiar]["titular"]
            monto_actual = mis_datos["cuentas"][cuenta_a_cambiar]["saldo"]
            
            nuevo_titular = st.text_input("Modificar Titular:", value=nombre_actual)
            nuevo_monto_directo = st.number_input("Modificar Saldo:", min_value=0, value=int(monto_actual), step=1000)
            
            if st.button("💾 Guardar Cambios", use_container_width=True):
                if nuevo_titular.strip() == "":
                    st.error("El titular no puede estar vacío.")
                else:
                    mis_datos["cuentas"][cuenta_a_cambiar]["titular"] = nuevo_titular.strip()
                    mis_datos["cuentas"][cuenta_a_cambiar]["saldo"] = nuevo_monto_directo
                    guardar_base_datos(st.session_state.base_datos_usuarios)
                    st.success("Cambios aplicados correctamente.")
                    st.rerun()

    # ------------------------------------------
    # PESTAÑA 2: ENVÍOS ALFANUMÉRICOS (INTERBANCARIOS)
    # ------------------------------------------
    with tab2:
        st.subheader("💸 Transferencias de Créditos Extensivas")
        tipo_envio = st.radio("Tipo de transferencia:", ["Mis Cuentas Propias", "A otro Usuario del Sistema"])
        
        cuenta_origen = st.selectbox("Selecciona tu cuenta de origen:", list(mis_datos["cuentas"].keys()), key="origen_pro")
        monto_transferir = st.number_input("Monto a enviar (COP):", min_value=1, value=10000, step=5000)
        
        if tipo_envio == "Mis Cuentas Propias":