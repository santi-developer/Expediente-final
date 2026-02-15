import streamlit as st
import os
import requests  
import base64   
from streamlit_pdf_viewer import pdf_viewer  # ← AGREGAR ESTA LÍNEA


st.title("Expedientes 📂")
st.write("aqui se gestionaran los expedientes")

PASSWORD = "1234"
RUTA_BASE_1 = "Carpeta Reservada"

# ⚙️ ========== CAMBIA SOLO ESTAS 2 LÍNEAS ========== ⚙️
BREVO_API_KEY = st.secrets["brevo"]["api_key"]
EMAIL_SENDER = st.secrets["email"]["sender"]            # ← 2️⃣ PON el email que quieras que aparezca
# ⚙️ ================================================= ⚙️

if "acceso_reservado" not in st.session_state:
    st.session_state.acceso_reservado = False

def enviar_email_brevo(destinatario, archivos_a_enviar, mensaje=""):
    """Envía email usando Brevo API"""
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
        
        # Preparar archivos adjuntos
        attachments = []
        for archivo_path in archivos_a_enviar:
            with open(archivo_path, 'rb') as f:
                contenido = base64.b64encode(f.read()).decode()
                
                attachments.append({
                    "content": contenido,
                    "name": os.path.basename(archivo_path)
                })
        
        # Mensaje HTML
        html_mensaje = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">📄 Documentos de procesos</h2>
            <p>Hola,</p>
            <p>Adjunto encontrarás los documentos solicitados.</p>
            {f'<p style="background: #f8f9fa; padding: 10px; border-left: 3px solid #3498db;"><i>{mensaje}</i></p>' if mensaje else ''}
            <p>Saludos cordiales.</p>
        </body>
        </html>
        """
        
        # Preparar email
        payload = {
            "sender": {
                "name": "Carpeta Reservada",
                "email": EMAIL_SENDER
            },
            "to": [{"email": destinatario}],
            "subject": "📄 Documentos importantes",
            "htmlContent": html_mensaje,
            "attachment": attachments
        }
        
        # Enviar
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return True, "✅ Email enviado exitosamente"
        else:
            error_msg = response.json()
            return False, f"❌ Error: {error_msg.get('message', 'Error desconocido')}"
            
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
    




RUTA_BASE = "Expedientes"

etapas_proceso = os.listdir(RUTA_BASE)

carpetas = sorted(
        os.listdir(RUTA_BASE),
        key=lambda x: int(x.split(".")[0]) if x.split(".")[0].isdigit() else 999
    )
EXPEDIENTE_NOMBRE = "110016000028202601438"

archivos_seleccionados_publicos = []

with st.expander(f"📁 {EXPEDIENTE_NOMBRE}", expanded=False):
    if not carpetas:
        st.warning("No hay carpetas dentro de este expediente.")

    else:

        for carpeta in carpetas:
            ruta_carpeta = os.path.join(RUTA_BASE, carpeta)

            # Asegurarnos que sea carpeta
            if os.path.isdir(ruta_carpeta):

                archivos = os.listdir(ruta_carpeta)

                # 👉 Regla especial
                if carpeta == "17. Recurso de apelación o impugnación especial (desaparecer carpeta)" and len(archivos) == 0:
                    continue  # no mostrar si está vacía

                # 📂 Carpeta desplegable
                with st.expander(f"📁 {carpeta}"):

                    if archivos:
                        for archivo in archivos:
                            ruta_completa = os.path.join(ruta_carpeta, archivo)

                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write("📄", archivo)
                            # ✅ DESPUÉS (abre en nueva pestaña):
                            with col2:
                                if st.button("👁️ Ver", key=f"ver_pub_{ruta_completa}"):
                                    st.session_state[f"mostrar_{ruta_completa}"] = not st.session_state.get(f"mostrar_{ruta_completa}", False)

                            # Mostrar PDF si está activado (agregar después de col3)
                            if st.session_state.get(f"mostrar_{ruta_completa}", False):
                                pdf_viewer(ruta_completa, width=700, height=600)
                            with col3:
                                if st.checkbox("✓", key=f"pub_{ruta_completa}", label_visibility="hidden"):
                                    archivos_seleccionados_publicos.append(ruta_completa)
                    else:
                        st.info("Carpeta vacía")

# 📧 ENVÍO DE EMAIL - CARPETA PÚBLICA
if archivos_seleccionados_publicos:
    st.divider()
    st.subheader("📧 Enviar documentos por correo electrónico")

    with st.form("formulario_email_publico", clear_on_submit=False):
        destinatario = st.text_input(
            "📮 Email del destinatario",
            placeholder="ejemplo@correo.com"
        )

        mensaje_adicional = st.text_area(
            "💬 Mensaje adicional (opcional)",
            placeholder="Agrega un mensaje personalizado...",
            height=100
        )

        st.write(f"**📎 Archivos seleccionados:** {len(archivos_seleccionados_publicos)}")
        for arch in archivos_seleccionados_publicos:
            st.write(f"  • {os.path.basename(arch)}")

        enviar = st.form_submit_button("📤 Enviar correo", use_container_width=True, type="primary")

        if enviar:
            if not destinatario or "@" not in destinatario:
                st.error("❌ Por favor ingresa un email válido")
            else:
                with st.spinner("📮 Enviando correo..."):
                    exito, mensaje_resultado = enviar_email_brevo(
                        destinatario,
                        archivos_seleccionados_publicos,
                        mensaje_adicional
                    )

                    if exito:
                        st.success(mensaje_resultado)
                        st.balloons()
                    else:
                        st.error(mensaje_resultado)







        

# 🔒 BLOQUE VISUAL DE ACCESO
if not st.session_state.acceso_reservado:
    st.warning("🔒 **Carpeta Reservada** — Acceso restringido")

    with st.container(border=True):
        st.write("Esta sección requiere contraseña para abrir los documentos.")

        clave = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Escribe la clave aquí..."
        )

        if st.button("🔓 Abrir carpeta"):
            if clave == PASSWORD:
                st.session_state.acceso_reservado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

# ✅ CARPETA ABIERTA
else:
    st.success("🔓 Carpeta Reservada abierta")

    carpet = sorted(
        os.listdir(RUTA_BASE_1),
        key=lambda x: int(x.split(".")[0]) if x.split(".")[0].isdigit() else 999
    )

    archivos_seleccionados = []

    with st.expander("📁 Carpeta Reservada", expanded=False):
        if not carpet:
            st.warning("No hay carpetas dentro.")
        else:
            for carpeta in carpet:
                ruta_carpeta = os.path.join(RUTA_BASE_1, carpeta)
                if os.path.isdir(ruta_carpeta):
                    archivos = os.listdir(ruta_carpeta)

                    with st.expander(f"📁 {carpeta}"):
                        if archivos:
                            for archivo in archivos:
                                ruta_completa = os.path.join(ruta_carpeta, archivo)
                                
                                col1, col2, col3 = st.columns([3, 1, 1])
                                with col1:
                                    st.write("📄", archivo)
                                with col2:
                                    if st.button("👁️ Ver", key=f"ver_res_{ruta_completa}"):
                                        st.session_state[f"mostrar_{ruta_completa}"] = not st.session_state.get(f"mostrar_{ruta_completa}", False)

                                # Mostrar PDF si está activado
                                if st.session_state.get(f"mostrar_{ruta_completa}", False):
                                    pdf_viewer(ruta_completa, width=700, height=600)

                                with col3:
                                    if st.checkbox("✓", key=ruta_completa, label_visibility="hidden"):
                                        archivos_seleccionados.append(ruta_completa)
                        else:
                            st.info("Carpeta vacía")

    # 📧 SECCIÓN DE ENVÍO DE EMAIL (ESTO ES NUEVO)
    if archivos_seleccionados:
        st.divider()
        st.subheader("📧 Enviar documentos por correo electrónico")
        
        with st.form("formulario_email", clear_on_submit=False):
            destinatario = st.text_input(
                "📮 Email del destinatario",
                placeholder="ejemplo@correo.com"
            )
            
            mensaje_adicional = st.text_area(
                "💬 Mensaje adicional (opcional)",
                placeholder="Agrega un mensaje personalizado...",
                height=100
            )
            
            st.write(f"**📎 Archivos seleccionados:** {len(archivos_seleccionados)}")
            for arch in archivos_seleccionados:
                st.write(f"  • {os.path.basename(arch)}")
            
            enviar = st.form_submit_button("📤 Enviar correo", use_container_width=True, type="primary")
            
            if enviar:
                if not destinatario or "@" not in destinatario:
                    st.error("❌ Por favor ingresa un email válido")
                else:
                    with st.spinner("📮 Enviando correo..."):
                        exito, mensaje_resultado = enviar_email_brevo(
                            destinatario,
                            archivos_seleccionados,
                            mensaje_adicional
                        )
                        
                        if exito:
                            st.success(mensaje_resultado)
                            st.balloons()
                        else:
                            st.error(mensaje_resultado)

    # BOTONES DE CONTROL
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔒 Cerrar carpeta", use_container_width=True):
            st.session_state.acceso_reservado = False
            st.rerun()
    
    with col2:
        if archivos_seleccionados:
            if st.button("🗑️ Limpiar selección", use_container_width=True):
                st.rerun()



CARPETA_FIJA = "17. Recurso de apelación o impugnación especial (desaparecer carpeta)"
RUTA_DESTINO = os.path.join(RUTA_BASE, CARPETA_FIJA)

# 🎭 MODO DEMO (oculto)
with st.expander("⚙️ Modo demostración (simulación)", expanded=False):

    pdf_subido = st.file_uploader(
        "Subir PDF de prueba",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if pdf_subido:
        ruta_archivo = os.path.join(RUTA_DESTINO, pdf_subido.name)

        os.makedirs(RUTA_DESTINO, exist_ok=True)
        with open(ruta_archivo, "wb") as f:
            f.write(pdf_subido.getbuffer())

        st.success("Documento de prueba cargado")
        st.rerun()

    # 🗑️ ELIMINAR documentos de la carpeta
    archivos_demo = os.listdir(RUTA_DESTINO) if os.path.exists(RUTA_DESTINO) else []

    if archivos_demo:
        st.divider()
        st.write("🗑️ Eliminar documento de prueba:")

        for archivo in archivos_demo:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write("📄", archivo)
            with col2:
                if st.button("🗑️", key=f"del_{archivo}"):
                    os.remove(os.path.join(RUTA_DESTINO, archivo))
                    st.rerun()    
