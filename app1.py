import streamlit as st
import random

# Configuración básica
st.set_page_config(page_title="Mi Banco Corto", page_icon="⚡")
st.title("⚡ Mi Banco Virtual Alfanumérico")

# Inicializar variables en la memoria de la aplicación
if "saldo" not in st.session_state:
    st.session_state.saldo = 500000.0  # Saldo inicial de cortesía
if "cuenta" not in st.session_state:
    num_random = random.randint(1000, 9999)
    st.session_state.cuenta = f"ACC-{num_random}X"

# Valores Legales Colombia
SMLMV = 1750905
AUX_TRANSPORTE = 249095

# --- SECCIÓN 1: DATOS DE LA CUENTA ---
st.subheader("📊 Estado de tu Cuenta")
st.metric(label="Número de Cuenta Alfanumérica", value=st.session_state.cuenta)
st.metric(label="Saldo Disponible", value=f"${st.session_state.saldo:,.0f} COP")

# --- SECCIÓN 2: CALCULADORA DE NÓMINA ---
st.subheader("🧮 Calculadora de Nómina Rápida")
opcion = st.radio("Selecciona tu sueldo:", ["1 Salario Mínimo", "Sueldo de 2 Millones"])

if opcion == "1 Salario Mínimo":
    sueldo_base = float(SMLMV)
    transporte = float(AUX_TRANSPORTE)
else:
    sueldo_base = 2000000.0
    transporte = float(AUX_TRANSPORTE)  # Sigue aplicando por ser menor a 2 SMLMV

# Descuentos de ley (4% Salud y 4% Pensión)
descuento_salud = sueldo_base * 0.04
descuento_pension = sueldo_base * 0.04
sueldo_neto = sueldo_base + transporte - (descuento_salud + descuento_pension)

# Mostrar resumen corto
st.write(f"🔹 **Sueldo Base:** ${sueldo_base:,.0f}")
st.write(f"🔹 **Auxilio Transporte:** ${transporte:,.0f}")
st.write(f"🔹 **Descuentos (Salud + Pensión):** -${(descuento_salud + descuento_pension):,.0f}")
st.success(f"💰 **Total Neto a Recibir:** ${sueldo_neto:,.0f} COP")

# --- SECCIÓN 3: ACCIONES ---
st.subheader("⚙️ Acciones Disponibles")

if st.button("💵 Depositar mi Nómina al Saldo", use_container_width=True):
    st.session_state.saldo += sueldo_neto
    st.success("¡Nómina depositada con éxito!")
    st.rerun()

if st.button("🔄 Reiniciar Cuenta (Borrar Todo)", use_container_width=True):
    st.session_state.saldo = 500000.0
    num_random = random.randint(1000, 9999)
    st.session_state.cuenta = f"ACC-{num_random}X"
    st.rerun()