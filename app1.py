import streamlit as st
import random

# Configuración básica de la aplicación
st.set_page_config(page_title="Mi Banco Alfanumérico Pro", page_icon="⚡", layout="centered")
st.title("⚡ Mi Banco Virtual Alfanumérico Pro")

# ==========================================
# CONSTANTES LEGALES COLOMBIA
# ==========================================
SMLMV = 1750905
AUX_TRANSPORTE = 249095

# ==========================================
# INICIALIZACIÓN DEL SISTEMA (Base de datos simulada)
# ==========================================
if "usuarios_db" not in st.session_state:
    # Cuenta principal por defecto para pruebas rápidas
    st.session_state.usuarios_db = {
        "test@correo.com": {
            "password": "123",
            "cuenta": "ACC-7777X",
            "saldo": 1000000.0,
            "creditos": []
        },
        "maria@correo.com": {
            "password": "123",
            "cuenta": "ACC-8888X",
            "saldo": 500000.0,
            "creditos": []
        }
    }

if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None

# ==========================================
# PANTALLA 1: AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================
if st.session_state.usuario_logueado is None:
    st.subheader("🔐 Acceso al Sistema Financiero")
    pestana_auth = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with pestana_auth[0]:
        correo_login = st.text_input("Correo electrónico:", key="login_email").strip().lower()
        pass_login = st.text_input("Contraseña:", type="password", key="login_pass")
        
        if st.button("🔓 Entrar", use_container_width=True):
            if correo_login in st.session_state.usuarios_db and st.session_state.usuarios_db[correo_login]["password"] == pass_login:
                st.session_state.usuario_logueado = correo_login
                st.success(f"¡Bienvenido, {correo_login}!")
                st.rerun()
            else:
                st.error("Correo o contraseña incorrectos.")
                
    with pestana_auth[1]:
        correo_reg = st.text_input("Crea tu correo electrónico:", key="reg_email").strip().lower()
        pass_reg = st.text_input("Crea tu contraseña:", type="password", key="reg_pass")
        
        if st.button("🚀 Crear Cuenta", use_container_width=True):
            if not correo_reg or not pass_reg:
                st.error("Por favor, llena todos los campos.")
            elif correo_reg in st.session_state.usuarios_db:
                st.error("Este correo ya está registrado.")
            else:
                # Generar datos bancarios únicos para el nuevo usuario
                num_random = random.randint(1000, 9999)
                nueva_cuenta = f"ACC-{num_random}X"
                
                st.session_state.usuarios_db[correo_reg] = {
                    "password": pass_reg,
                    "cuenta": nueva_cuenta,
                    "saldo": 500000.0,  # Bono de bienvenida
                    "creditos": []
                }
                st.success("¡Registro exitoso! Ya puedes iniciar sesión con tu cuenta.")
else:
    # ==========================================
    # PANTALLA 2: ENTORNO DEL USUARIO LOGUEADO
    # ==========================================
    u_email = st.session_state.usuario_logueado
    u_datos = st.session_state.usuarios_db[u_email]
    
    # Barra lateral con información del perfil y botón de salida
    st.sidebar.markdown(f"### 👤 Usuario:\n`{u_email}`")
    st.sidebar.markdown(f"### 💳 Cuenta:\n`{u_datos['cuenta']}`")
    st.sidebar.metric(label="Saldo Disponible", value=f"\${u_datos['saldo']:,.0f} COP")
    
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logueado = None
        st.rerun()
        
    # Navegación del Banco mediante pestañas superiores
    tab_nomina, tab_trans, tab_creditos = st.tabs([
        "🧮 1. Calculadora de Nómina", 
        "🔄 2. Transferencias", 
        "🏦 3. Solicitar Microcrédito"
    ])
    
    # ------------------------------------------
    # PUNTO 1: CALCULADORA DE NÓMINA COLOMBIANA
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
        
        st.write(f"🔹 **Sueldo Base:** \${sueldo_base:,.0f}")
        st.write(f"🔹 **Auxilio Transporte:** \${transporte:,.0f}")
        st.write(f"🔹 **Descuento Salud (4%):** -\${descuento_salud:,.0f}")
        st.write(f"🔹 **Descuento Pensión (4%):** -\${descuento_pension:,.0f}")
        st.success(f"💰 **Total Neto a Recibir:** \${sueldo_neto:,.0f} COP")
        
        if st.button("💵 Cobrar y Depositar Nómina a mi Saldo", use_container_width=True):
            u_datos["saldo"] += sueldo_neto
            st.success("¡Nómina abonada correctamente a tu cuenta!")
            st.rerun()

    # ------------------------------------------
    # PUNTO 2: TRANSFERENCIAS INTERNAS
    # ------------------------------------------
    with tab_trans:
        st.subheader("Enviar Créditos a otros Usuarios")
        
        # Crear listado dinámico de cuentas existentes excluyendo la propia
        cuentas_destino = {
            datos["cuenta"]: correo 
            for correo, datos in st.session_state.usuarios_db.items() if correo != u_email
        }
        
        if cuentas_destino:
            cuenta_elegida = st.selectbox("Selecciona la cuenta de destino:", list(cuentas_destino.keys()))
            monto_transferir = st.number_input("Monto a enviar (COP):", min_value=5000.0, step=5000.0)
            
            if st.button("🚀 Ejecutar Transferencia", use_container_width=True):
                if u_datos["saldo"] < monto_transferir:
                    st.error("Fondos insuficientes para realizar la transacción.")
                else:
                    # Descontar al origen
                    u_datos["saldo"] -= monto_transferir
                    # Sumar al destino
                    correo_receptor = cuentas_destino[cuenta_elegida]
                    st.session_state.usuarios_db[correo_receptor]["saldo"] += monto_transferir
                    
                    st.success(f"💸 ¡Transferencia de \${monto_transferir:,.0f} COP enviada con éxito a la cuenta {cuenta_elegida}!")
                    st.rerun()
        else:
            st.info("No hay otros usuarios registrados en el sistema para realizar transferencias. Crea un usuario secundario en la pestaña 'Registrarse' para probar.")

    # ------------------------------------------
    # PUNTO 3: SOLICITUD DE MICROCRÉDITOS
    # ------------------------------------------
    with tab_creditos:
        st.subheader("Línea de Financiamiento Inmediato")
        monto_credito = st.number_input("Monto del Préstamo (COP):", min_value=50000.0, max_value=2000000.0, value=200000.0, step=50000.0)
        
        if st.button("🤝 Solicitar Aprobación de Crédito", use_container_width=True):
            id_prestamo = f"CRE-{random.randint(100, 999)}"
            u_datos["saldo"] += monto_credito
            u_datos["creditos"].append({
                "id": id_prestamo,
                "monto": monto_credito,
                "estado": "Aprobado e Inyectado"
            })
            st.success(f"✅ ¡Tu microcrédito {id_prestamo} de \${monto_credito:,.0f} COP ha sido aprobado e inyectado al saldo!")
            st.rerun()
            
        if u_datos["creditos"]:
            st.markdown("#### 📑 Tus Créditos Vigentes")
            for c in u_datos["creditos"]:
                st.info(f"Código: **{c['id']}** | Monto: **\${c['monto']:,.0f} COP** | Estado: `{c['estado']}`")