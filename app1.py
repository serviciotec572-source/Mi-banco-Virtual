import streamlit as st
import random
import json
import os
from datetime import datetime

# Configuración básica de la aplicación
st.set_page_config(page_title="Mi Banco Alfanumérico Pro", page_icon="⚡", layout="centered")
st.title("⚡ Mi Banco Virtual Alfanumérico Pro (Persistente)")

# ==========================================
# CONSTANTES LEGALES COLOMBIA
# ==========================================
SMLMV = 1750905
AUX_TRANSPORTE = 249095
ARCHIVO_BD = "base_datos_banco.json"

# ==========================================
# GESTIÓN DE BASE DE DATOS PERSISTENTE (JSON)
# ==========================================
def cargar_base_datos():
    """Carga los datos desde el archivo JSON seguro. Si no existe, crea la base inicial."""
    if not os.path.exists(ARCHIVO_BD):
        # Crear base de datos por defecto si el archivo no existe
        bd_inicial = {
            "test@correo.com": {
                "password": "123",
                "cuenta": "ACC-7777X",
                "saldo": 1000000.0,
                "creditos": [],
                "historial": []
            },
            "maria@correo.com": {
                "password": "123",
                "cuenta": "ACC-8888X",
                "saldo": 500000.0,
                "creditos": [],
                "historial": []
            }
        }
        with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
            json.dump(bd_inicial, f, ensure_ascii=False, indent=4)
        return bd_inicial
    try:
        with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_base_datos(datos):
    """Guarda el estado actual del sistema en el archivo JSON."""
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Inicializar los datos del sistema leyendo el almacenamiento físico de la nube
if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = cargar_base_datos()

if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None

# Sincronizar siempre el estado local con la base de datos real
st.session_state.usuarios_db = cargar_base_datos()

# ==========================================
# PANTALLA 1: AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================
if st.session_state.usuario_logueado is None:
    st.subheader("🔐 Acceso al Sistema Financiero")
    pestana_auth = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with pestana_auth:
        correo_login = st.text_input("Correo electrónico:", key="login_email").strip().lower()
        pass_login = st.text_input("Contraseña:", type="password", key="login_pass")
        
        if st.button("🔓 Entrar", use_container_width=True):
            if correo_login in st.session_state.usuarios_db and st.session_state.usuarios_db[correo_login]["password"] == pass_login:
                st.session_state.usuario_logueado = correo_login
                st.success(f"¡Bienvenido, {correo_login}!")
                st.rerun()
            else:
                st.error("Correo o contraseña incorrectos.")
                
    with pestana_auth:
        correo_reg = st.text_input("Crea tu correo electrónico:", key="reg_email").strip().lower()
        pass_reg = st.text_input("Crea tu contraseña:", type="password", key="reg_pass")
        
        if st.button("🚀 Crear Cuenta", use_container_width=True):
            if not correo_reg or not pass_reg:
                st.error("Por favor, llena todos los campos.")
            elif correo_reg in st.session_state.usuarios_db:
                st.error("Este correo ya está registrado.")
            else:
                num_random = random.randint(1000, 9999)
                nueva_cuenta = f"ACC-{num_random}X"
                
                st.session_state.usuarios_db[correo_reg] = {
                    "password": pass_reg,
                    "cuenta": nueva_cuenta,
                    "saldo": 500000.0,  # Bono de bienvenida
                    "creditos": [],
                    "historial": [{
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tipo": "Bono de bienvenida",
                        "detalle": "Activación de espacio financiero",
                        "monto": 500000.0
                    }]
                }
                guardar_base_datos(st.session_state.usuarios_db)
                st.success("¡Registro exitoso! Ya puedes iniciar sesión con tu cuenta.")
else:
    # ==========================================
    # PANTALLA 2: ENTORNO DEL USUARIO LOGUEADO
    # ==========================================
    u_email = st.session_state.usuario_logueado
    u_datos = st.session_state.usuarios_db[u_email]
    
    # Asegurar que existan las listas de historial
    if "historial" not in u_datos:
        u_datos["historial"] = []
    
    # Barra lateral con información del perfil y botón de salida
    st.sidebar.markdown(f"### 👤 Usuario:\n`{u_email}`")
    st.sidebar.markdown(f"### 💳 Cuenta:\n`{u_datos['cuenta']}`")
    st.sidebar.metric(label="Saldo Disponible", value=f"${u_datos['saldo']:,.0f} COP")
    
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logueado = None
        st.rerun()
        
    # Navegación del Banco mediante pestañas superiores
    tab_nomina, tab_trans, tab_creditos, tab_auditoria = st.tabs([
        "🧮 Nómina", 
        "🔄 Transferencias", 
        "🏦 Microcrédito",
        "🔍 Historial (Auditoría)"
    ])
    
    # ------------------------------------------
    # NOVEDAD NÓMINA (Añade historial)
    # ------------------------------------------
    with tab_nomina:
        st.subheader("Simulación y Depósito de Nómina")
        opcion = st.radio("Selecciona tu sueldo mensual:", ["1 Salario Mínimo (SMLMV)", "Sueldo de 2 Millones COP"])
        
        if opcion == "1 Salario Mínimo (SMLMV)":
            sueldo_base = float(SMLMV)
        else:
            sueldo_base = 2000000.0
            
        transporte = float(AUX_TRANSPORTE) if sueldo_base <= (2 * SMLMV) else 0.0
        descuento_salud = sueldo_base * 0.04
        descuento_pension = sueldo_base * 0.04
        sueldo_neto = sueldo_base + transporte - (descuento_salud + descuento_pension)
        
        st.write(f"🔹 **Sueldo Base:** ${sueldo_base:,.0f}")
        st.write(f"🔹 **Auxilio Transporte:** ${transporte:,.0f}")
        st.write(f"🔹 **Descuentos (Salud 4% + Pensión 4%):** -${(descuento_salud + descuento_pension):,.0f}")
        st.success(f"💰 **Total Neto a Recibir:** ${sueldo_neto:,.0f} COP")
        
        if st.button("💵 Cobrar y Depositar Nómina a mi Saldo", use_container_width=True):
            u_datos["saldo"] += sueldo_neto
            
            # Registrar auditoría de nómina
            u_datos["historial"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": "Ingreso de Nómina",
                "detalle": f"Abono por concepto de simulación ({opcion})",
                "monto": sueldo_neto
            })
            
            guardar_base_datos(st.session_state.usuarios_db)
            st.success("¡Nómina abonada y registrada en auditoría!")
            st.rerun()

    # ------------------------------------------
    # NOVEDAD TRANSFERENCIAS (Doble registro de auditoría)
    # ------------------------------------------
    with tab_trans:
        st.subheader("Enviar Créditos a otros Usuarios")
        
        cuentas_destino = {
            datos["cuenta"]: correo 
            for correo, datos in st.session_state.usuarios_db.items() if correo != u_email
        }
        
        if cuentas_destino:
            cuenta_elegida = st.selectbox("Selecciona la cuenta de destino:", list(cuentas_destino.keys()))
            monto_transferir = st.number_input("Monto a enviar (COP):", min_value=5000.0, step=5000.0)
            
            if st.button("🚀 Ejecutar Transferencia", use_container_width=True):
                if u_datos["saldo"] < monto_transferir:
                    st.error("Fondos insuficientes.")
                else:
                    correo_receptor = cuentas_destino[cuenta_elegida]
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 1. Operación origen (Tú envías)
                    u_datos["saldo"] -= monto_transferir
                    u_datos["historial"].append({
                        "fecha": fecha_actual,
                        "tipo": "Egreso (Envío)",
                        "detalle": f"Transferencia enviada a la cuenta {cuenta_elegida}",
                        "monto": -monto_transferir
                    })
                    
                    # 2. Operación destino (Ellos reciben)
                    st.session_state.usuarios_db[correo_receptor]["saldo"] += monto_transferir
                    if "historial" not in st.session_state.usuarios_db[correo_receptor]:
                        st.session_state.usuarios_db[correo_receptor]["historial"] = []
                        
                    st.session_state.usuarios_db[correo_receptor]["historial"].append({
                        "fecha": fecha_actual,
                        "tipo": "Ingreso (Recepción)",
                        "detalle": f"Dinero recibido desde el usuario {u_email}",
                        "monto": monto_transferir
                    })
                    
                    guardar_base_datos(st.session_state.usuarios_db)
                    st.success(f"💸 ¡Transferencia de ${monto_transferir:,.0f} COP enviada con éxito!")
                    st.rerun()
        else:
            st.info("Registra otro correo electrónico en el sistema (Cerrando sesión) para poder enviarle dinero.")

    # ------------------------------------------
    # NOVEDAD MICROCRÉDITOS (Añade historial)