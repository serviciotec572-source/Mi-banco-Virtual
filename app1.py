import streamlit as st
import random
import json
import os
from datetime import datetime

# Configuración premium de la interfaz
st.set_page_config(page_title="Alfanumérica Premium Bank", page_icon="🏦", layout="centered")

# --- ESTILOS VISUALES PREMIUM (Estilo Banco Digital) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #0056b3 !important; 
        color: white !important;
        border-color: #0056b3 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Imagen de portada de alta calidad (Banner de Banco Digital Moderno)
st.image("https://unsplash.com", 
         caption="Alfanumérica Bank Pro — Tu Ecosistema Financiero Digital Seguro", use_container_width=True)

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
    if not os.path.exists(ARCHIVO_BD):
        bd_inicial = {
            "carlos.mendoza@correo.com": {
                "nombre": "Carlos Mendoza",
                "password": "123",
                "cuenta": "ACC-5491B",
                "saldo": 4500000.0,
                "creditos": [],
                "historial": [{"fecha": "2026-10-19 08:00:00", "tipo": "Apertura", "detalle": "Depósito Inicial", "monto": 4500000.0}]
            },
            "andrea.restrepo@correo.com": {
                "nombre": "Andrea Restrepo",
                "password": "123",
                "cuenta": "ACC-9218F",
                "saldo": 2800000.0,
                "creditos": [],
                "historial": [{"fecha": "2026-10-19 09:15:00", "tipo": "Apertura", "detalle": "Depósito Inicial", "monto": 2800000.0}]
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
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = cargar_base_datos()

if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None

st.session_state.usuarios_db = cargar_base_datos()

# ==========================================
# PANTALLA 1: AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================
if st.session_state.usuario_logueado is None:
    st.subheader("🔐 Acceso Seguro a la Banca Virtual")
    tab_login, tab_registro = st.tabs(["🔒 Iniciar Sesión", "📝 Abrir Cuenta Nueva"])
    
    with tab_login:
        correo_login = st.text_input("Correo corporativo o personal:", key="login_email").strip().lower()
        pass_login = st.text_input("Contraseña bancaria:", type="password", key="login_pass")
        
        if st.button("🔓 Ingresar de forma segura", use_container_width=True):
            if correo_login in st.session_state.usuarios_db and st.session_state.usuarios_db[correo_login]["password"] == pass_login:
                st.session_state.usuario_logueado = correo_login
                st.success(f"¡Bienvenido de nuevo, {st.session_state.usuarios_db[correo_login]['nombre']}!")
                st.rerun()
            else:
                st.error("Credenciales inválidas. Por favor verifique correo y clave.")
                
    with tab_registro:
        st.markdown("### Formulario de Registro de Clientes")
        reg_nombre = st.text_input("Nombre Completo (Real):", placeholder="Ej: Juan Pablo Díaz")
        correo_reg = st.text_input("Correo electrónico único:", key="reg_email").strip().lower()
        pass_reg = st.text_input("Asigna tu contraseña de seguridad:", type="password", key="reg_pass")
        
        # REQUERIMIENTO: El usuario ahora escoge su propio monto / saldo inicial
        monto_inicial = st.number_input("Monto / Depósito Inicial de Apertura (COP):", min_value=10000.0, value=1500000.0, step=50000.0)
        
        if st.button("🚀 Crear mi Cuenta de Ahorros", use_container_width=True):
            if not reg_nombre or not correo_reg or not pass_reg:
                st.error("Por favor, rellene todos los campos obligatorios del formulario.")
            elif correo_reg in st.session_state.usuarios_db:
                st.error("Este correo ya se encuentra registrado en nuestro sistema central.")
            else:
                num_random = random.randint(1000, 9999)
                nueva_cuenta = f"ACC-{num_random}X"
                
                st.session_state.usuarios_db[correo_reg] = {
                    "nombre": reg_nombre.strip(),
                    "password": pass_reg,
                    "cuenta": nueva_cuenta,
                    "saldo": float(monto_inicial),
                    "creditos": [],
                    "historial": [{
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tipo": "Apertura de Cuenta",
                        "detalle": f"Saldo inicial fondeado por {reg_nombre}",
                        "monto": float(monto_inicial)
                    }]
                }
                guardar_base_datos(st.session_state.usuarios_db)
                st.success(f"¡Cuenta aprobada! Bienvenido a bordo {reg_nombre}. Ya puede iniciar sesión.")
else:
    # ==========================================
    # PANTALLA 2: ENTORNO DEL USUARIO LOGUEADO
    # ==========================================
    u_email = st.session_state.usuario_logueado
    u_datos = st.session_state.usuarios_db[u_email]
    
    if "historial" not in u_datos:
        u_datos["historial"] = []
    
    # Barra lateral estilizada
    st.sidebar.markdown("### 🏦 Tu Perfil Bancario")
    st.sidebar.markdown(f"**Cliente:**\n`{u_datos['nombre']}`")
    st.sidebar.markdown(f"**Cuenta Única:**\n`{u_datos['cuenta']}`")
    st.sidebar.metric(label="Saldo Neto Disponible", value=f"${u_datos['saldo']:,.0f} COP")
    
    if st.sidebar.button("🔒 Salida Segura", use_container_width=True):
        st.session_state.usuario_logueado = None
        st.rerun()
        
    tab_nomina, tab_trans, tab_creditos, tab_auditoria = st.tabs([
        "🧮 Liquidación Nómina", 
        "🔄 Transferir Fondos", 
        "🏦 Créditos Exprés",
        "🔍 Extracto y Auditoría"
    ])
    
    # 1. NOMINA
    with tab_nomina:
        st.subheader("Simulación de Nómina Legal Vigente")
        opcion = st.radio("Fijar salario mensual base:", ["1 Salario Mínimo (SMLMV)", "Sueldo de 2 Millones COP"])
        
        sueldo_base = float(SMLMV) if opcion == "1 Salario Mínimo (SMLMV)" else 2000000.0
        transporte = float(AUX_TRANSPORTE) if sueldo_base <= (2 * SMLMV) else 0.0
        descuento_salud = sueldo_base * 0.04
        descuento_pension = sueldo_base * 0.04
        sueldo_neto = sueldo_base + transporte - (descuento_salud + descuento_pension)
        
        st.write(f"🔹 **Sueldo Base:** ${sueldo_base:,.0f}")
        st.write(f"🔹 **Auxilio Transporte:** ${transporte:,.0f}")
        st.write(f"🔹 **Aportes Seguridad Social (Salud + Pensión):** -${(descuento_salud + descuento_pension):,.0f}")
        st.success(f"💰 **Total a Abonar:** ${sueldo_neto:,.0f} COP")
        
        if st.button("💵 Confirmar y Abonar al Saldo", use_container_width=True):
            u_datos["saldo"] += sueldo_neto
            u_datos["historial"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": "Abono de Nómina",
                "detalle": f"Pago por concepto de nómina ({opcion})",
                "monto": sueldo_neto
            })
            guardar_base_datos(st.session_state.usuarios_db)
            st.success("¡Nómina depositada con éxito en sus saldos principales!")
            st.rerun()

    # 2. TRANSFERENCIAS CON NOMBRES REALES Y MONTOS
    with tab_trans:
        st.subheader("Transferencias Interbancarias en Segundos")
        
        # Mapeamos usando el nombre real del destinatario en lugar del correo
        cuentas_destino = {
            datos["cuenta"]: f"{datos['nombre']} ({datos['cuenta']})" 
            for correo, datos in st.session_state.usuarios_db.items() if correo != u_email
        }
        
        if cuentas_destino:
            cuenta_elegida = st.selectbox("Seleccione el Beneficiario:", list(cuentas_destino.keys()), format_func=lambda x: cuentas_destino[x])
            monto_transferir = st.number_input("Monto total a transferir (COP):", min_value=5000.0, step=10000.0)
            
            if st.button("🚀 Ejecutar Transferencia Inmediata", use_container_width=True):
                if u_datos["saldo"] < monto_transferir:
                    st.error("Fondos insuficientes para autorizar este débito.")
                else:
                    # Encontrar correo del receptor
                    correo_receptor = None
                    for correo, datos in st.session_state.usuarios_db.items():
                        if datos["cuenta"] == cuenta_elegida:
                            correo_receptor = correo
                            break
                            
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")