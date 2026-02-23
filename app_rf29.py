import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # ttl=0 obliga a Streamlit a descargar los datos en vivo, ignorando la caché
        df = conn.read(ttl=0)
        
        # Limpiamos filas completamente vacías que Google Sheets suele generar
        df = df.dropna(how="all") 
        
        if df.empty:
            return pd.DataFrame(columns=["Fecha_Hora", "Movimiento", "Nombre", "RUT_SAP", "Empresa", "Cuerpo_Liquido", "Autorizador", "Motivo"])
        return df
    except Exception:
        # Si hay un error de conexión, devuelve un formato en blanco
        return pd.DataFrame(columns=["Fecha_Hora", "Movimiento", "Nombre", "RUT_SAP", "Empresa", "Cuerpo_Liquido", "Autorizador", "Motivo"])

# --- LISTAS EXACTAS EXTRAÍDAS DE TU PDF ---
LISTA_AUTORIZADORES = [
    "Seleccione una persona...",
    "1. Manuel Figueroa", "2. Danae Scheuermann", "3. Abel Tejerina", 
    "4. Fernando Aranguiz", "5. Ana Rojas", "6. Percy Parra", 
    "7. Marcial Lara", "8. Farid Duk", "9. Roberto Flores", "10. Wladimir Jacobs"
]

LISTA_CUERPOS_LIQUIDOS = [
    "Seleccione el cuerpo líquido...",
    "1. Reservorios", "2. Pond ERASO", "3. Piscinas Oriente y Poniente", 
    "4. Piscina Quebrada Sur", "5. Piscina Quebrada Norte", "6. Piscina Laguna Seca", 
    "7. Piscina Laguna Sur", "8. Pozón Tranque Talabre", "9. Decantadores Salado", 
    "10. Decantadores OSP", "11. Decantadores Inacaliri"
]
# ------------------------------------------

# Configuración de la página
st.set_page_config(page_title="Control RF 29 - GAR", layout="wide")

# --- CONTROL DE ETAPAS (PÁGINAS) ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
if 'movimiento' not in st.session_state:
    st.session_state.movimiento = ""
if 'autorizador' not in st.session_state:
    st.session_state.autorizador = ""
if 'motivo' not in st.session_state:
    st.session_state.motivo = ""

# --- SISTEMA DE SEGURIDAD PARA EL DASHBOARD ---
st.sidebar.markdown("---")
clave = st.sidebar.text_input("🔑 Acceso Administrador", type="password")

opciones_menu = ["Formulario de Acceso"]
if clave == "GAR2026": 
    opciones_menu.append("Dashboard en Vivo")

menu = st.sidebar.radio("Navegación", opciones_menu)
st.sidebar.markdown("---")

if menu == "Formulario de Acceso":
    st.title("Control ingreso y salida recinto cuerpo líquido")
    st.write("Este control de ingreso y salida es obligatorio para trabajadores y/o visitas que requieran acceder a un recinto de cuerpo liquido de la Gerencia Aguas y Relaves.")
    st.markdown("---")
    
    # --- PASO 1: PREGUNTA INICIAL ---
    if st.session_state.paso == 1:
        st.markdown("### Sección 1: Pregunta *")
        movimiento = st.radio("Seleccione opción:", ["Ingreso", "Salida"], label_visibility="collapsed")
        
        if st.button("Siguiente ➡️"):
            st.session_state.movimiento = movimiento
            if movimiento == "Ingreso":
                st.session_state.paso = 2
            else:
                st.session_state.paso = 3
            st.rerun()

    # --- PASO 2: AUTORIZACIÓN (SOLO PARA INGRESO) ---
    elif st.session_state.paso == 2:
        st.header("Sección 2: Autorización")
        
        autorizador = st.selectbox("Persona que autoriza *", LISTA_AUTORIZADORES)
        motivo = st.text_area("Motivo de ingreso *")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.paso = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if autorizador == "Seleccione una persona...":
                    st.error("⚠️ Debe seleccionar a la 'Persona que autoriza'.")
                elif motivo.strip() == "":
                    st.error("⚠️ El 'Motivo de ingreso' es obligatorio.")
                else:
                    st.session_state.autorizador = autorizador
                    st.session_state.motivo = motivo
                    st.session_state.paso = 3
                    st.rerun()

    # --- PASO 3: DATOS PERSONALES Y LUGAR ---
    elif st.session_state.paso == 3:
        st.header("Sección 3: Datos")
        
        nombre = st.text_input("Nombre y Apellido *")
        rut = st.text_input("Rut o SAP *")
        empresa = st.text_input("Empresa *")
        cuerpo_liquido = st.selectbox("Cuerpo liquido *", LISTA_CUERPOS_LIQUIDOS)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("⬅️ Atrás"):
                if st.session_state.movimiento == "Ingreso":
                    st.session_state.paso = 2
                else:
                    st.session_state.paso = 1
                st.rerun()
        with col2:
            if st.button("Enviar ✅"):
                if nombre.strip() == "" or rut.strip() == "" or empresa.strip() == "":
                    st.error("⚠️ Los campos 'Nombre y Apellido', 'Rut o SAP' y 'Empresa' son obligatorios.")
                elif cuerpo_liquido == "Seleccione el cuerpo líquido...":
                    st.error("⚠️ Debe seleccionar el 'Cuerpo liquido'.")
                else:
                    aut_final = st.session_state.autorizador if st.session_state.movimiento == "Ingreso" else "N/A (Salida)"
                    mot_final = st.session_state.motivo if st.session_state.movimiento == "Ingreso" else "N/A (Salida)"
                    
                    nuevo_registro = {
                        "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Movimiento": st.session_state.movimiento,
                        "Nombre": nombre,
                        "RUT_SAP": rut,
                        "Empresa": empresa,
                        "Cuerpo_Liquido": cuerpo_liquido,
                        "Autorizador": aut_final,
                        "Motivo": mot_final
                    }
                    
                    # Carga y actualiza Google Sheets
                    df = cargar_datos()
                    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
                    conn.update(data=df)
                    
                    st.success(f"🎉 ¡Formulario de {st.session_state.movimiento} enviado correctamente!")
                    
                    import time
                    time.sleep(2)
                    st.session_state.paso = 1
                    st.session_state.movimiento = ""
                    st.session_state.autorizador = ""
                    st.session_state.motivo = ""
                    st.rerun()

elif menu == "Dashboard en Vivo":
    st.header("Monitor de Trazabilidad en Tiempo Real")
    df = cargar_datos()
    
    if not df.empty:
        estado_actual = df.sort_values("Fecha_Hora").groupby("RUT_SAP").tail(1)
        adentro = estado_actual[estado_actual["Movimiento"] == "Ingreso"]
        
        col1, col2 = st.columns(2)
        col1.metric("👷 Personal total al interior", len(adentro))
        
        st.subheader("Personal en Cuerpos Líquidos (Sin registro de salida)")
        if not adentro.empty:
            st.dataframe(adentro[["Fecha_Hora", "Nombre", "Empresa", "Cuerpo_Liquido", "Autorizador"]], use_container_width=True)
        else:
            st.success("El área se encuentra totalmente despejada.")
            
        st.markdown("---")
        st.subheader("Historial Completo de Registros")
        st.dataframe(df.tail(15), use_container_width=True)
    else:
        st.info("Aún no hay respuestas en la base de datos.")

