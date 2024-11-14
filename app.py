import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

def on_publish(cliente, datos_usuario, resultado):  # Callback
    print("Se ha publicado el dato \n")
    pass

def on_message(cliente, datos_usuario, mensaje):
    global mensaje_recibido
    time.sleep(2)
    mensaje_recibido = str(mensaje.payload.decode("utf-8"))
    st.write(mensaje_recibido)

broker = "broker.emqx.io"
port = 1883
cliente1 = paho.Client("AppEspadaVoz")
cliente1.on_message = on_message

st.title("Interfaces Multimodales")
st.subheader("CONTROL DE TRAJE")
imagen = Image.open('Warrior.png')
st.image(imagen, width=720)
st.write("Activa algún modo del traje")

# Botón para reconocimiento de voz
boton_stt = Button(label=" Presiona y habla ", width=400)
boton_stt.js_on_event("button_click", CustomJS(code="""
    var reconocimiento = new webkitSpeechRecognition();
    reconocimiento.continuous = true;
    reconocimiento.interimResults = true;

    reconocimiento.onresult = function (e) {
        var valor = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                valor += e.results[i][0].transcript;
            }
        }
        if (valor != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", { detail: valor }));
        }
    }
    reconocimiento.start();
"""))

# Variable para almacenar el texto reconocido
texto_reconocido = ""
resultado = streamlit_bokeh_events(
    boton_stt,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)
if resultado:
    if "GET_TEXT" in resultado:
        texto_reconocido = resultado.get("GET_TEXT").strip()  # Almacena el texto reconocido
        st.write("Texto reconocido:", texto_reconocido)
        # Publica el texto reconocido en MQTT
        cliente1.on_publish = on_publish
        cliente1.connect(broker, port)
        mensaje = json.dumps({"Act1": texto_reconocido})
        ret = cliente1.publish("Cosplay", mensaje)

# Crear columnas para los controles manuales
col1, col2, col3, col4 = st.columns(4)

# Columna para Control de luz manual
with col1:
    st.subheader("Modo: DEFENSA")
    if st.button("DEFENSA"):
        mensaje = json.dumps({"Act1": "defensa"})
        cliente1.publish("Cosplay", mensaje)
        st.success("Modo activado: DEFENSA")

with col2:
    st.subheader("Modo: ATAQUE")
    if st.button("ATAQUE"):
        mensaje = json.dumps({"Act1": "ataca"})
        cliente1.publish("Cosplay", mensaje)
        st.success("Modo activado: ATAQUE")

with col3:
    st.subheader("Modo: CALMADO")
    if st.button("CALMADO"):
        mensaje = json.dumps({"Act1": "calmado"})
        cliente1.publish("Cosplay", mensaje)
        st.success("Modo activado: CALMADO")

with col4:
    st.subheader("Modo: LIBRE")
    if st.button("LIBRE"):
        mensaje = json.dumps({"Act1": "libre"})
        cliente1.publish("Cosplay", mensaje)
        st.success("Modo activado: LIBRE")

# Controles RGB para el modo LIBRE
with st.expander("Controles RGB"):
    r = st.slider("Rojo", 0, 255, 0)
    g = st.slider("Verde", 0, 255, 0)
    b = st.slider("Azul", 0, 255, 0)
    if st.button("Establecer Color"):
        mensaje = json.dumps({"Act1": "libre", "r": r, "g": g, "b": b})
        cliente1.publish("Cosplay", mensaje)
        st.success(f"Color establecido: RGB({r}, {g}, {b})")

try:
    os.mkdir("temp")
except:
    pass
