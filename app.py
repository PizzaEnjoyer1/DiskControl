import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

def on_publish(client, userdata, result):  # Callback
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.emqx.io"
port = 1883
client1 = paho.Client("AppEspadaVoz")
client1.on_message = on_message

st.title("Interfaces Multimodales")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.write("Toca el Botón y habla ")

# Botón para reconocimiento de voz
stt_button = Button(label=" Inicio ", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", { detail: value }));
        }
    }
    recognition.start();
"""))

# Variable para almacenar el texto reconocido
recognized_text = ""

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        recognized_text = result.get("GET_TEXT").strip()  # Almacena el texto reconocido
        st.write("Texto reconocido:", recognized_text)

        # Publica el texto reconocido en MQTT
        client1.on_publish = on_publish                            
        client1.connect(broker, port)  
        message = json.dumps({"Act1": recognized_text})
        ret = client1.publish("Cosplay/Espada", message)

# Crear columnas para los controles manuales
col1, col2 = st.columns(2)

# Columna para Control de luz manual
with col1:
    st.subheader("Control de luz manual")
    if st.button("Encender"):
        message = json.dumps({"Act1": "enciende las luces"})
        client1.publish("Cosplay/Espada", message)
        st.success("Mensaje enviado: enciende las luces")
    if st.button("Apagar"):
        message = json.dumps({"Act1": "apaga las luces"})
        client1.publish("Cosplay/Espada", message)
        st.success("Mensaje enviado: apaga las luces")

with col2:
    st.subheader("XD")

try:
    os.mkdir("temp")
except:
    pass
