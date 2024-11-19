import os
import streamlit as st
import streamlit.components.v1 as components
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from pygame import mixer

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
st.subheader("CONTROL DE TRAJE")
image = Image.open('Warrior.png')
st.image(image, width = 720)
st.write("Activa algún modo del traje")

# Botón para reconocimiento de voz
stt_button = Button(label=" Presiona y habla ", width=400)
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
        ret = client1.publish("Cosplay", message)



def load_sounds():
    """
    Cargar los sonidos y devolverlos en un diccionario.
    Los archivos de sonido deben estar en una carpeta 'sounds' en el mismo directorio.
    """
    sounds = {
        'sound1': 'sounds/sound1.mp3',
        'sound2': 'sounds/sound2.mp3',
        'sound3': 'sounds/sound3.mp3'
    }
    return sounds

def play_sound(sound_file, current_sound):
    """
    Reproducir un sonido y detener cualquier otro que esté sonando
    """
    try:
        # Si hay algún sonido reproduciéndose, detenerlo
        if mixer.music.get_busy():
            mixer.music.stop()
        
        # Si el sonido actual es diferente al nuevo sonido
        if current_sound != sound_file:
            mixer.music.load(sound_file)
            mixer.music.play()
            return sound_file
        else:
            # Si es el mismo sonido, solo lo detenemos
            return None
    except Exception as e:
        st.error(f"Error al reproducir el sonido: {str(e)}")
        return None


# Crear columnas para los controles manuales
col1, col2, col3 = st.columns(3)

# Columna para Control de luz manual
with col1:
    st.subheader("Modo: DEFENSA")
    if st.button("DEFENSA"):
        message = json.dumps({"Act1": "defensa"})
        client1.publish("Cosplay", message)
        st.success("Modo activado: DEFENSA")
with col2:
    st.subheader("Modo: ATAQUE")
    if st.button("ATAQUE"):
        message = json.dumps({"Act1": "ataca"})
        client1.publish("Cosplay", message)
        st.success("Modo activado: ATAQUE")
with col3:
    st.subheader("Modo: CALMADO")
    if st.button("CALMADO"):
        message = json.dumps({"Act1": "calmado"})
        client1.publish("Cosplay", message)
        st.success("Modo activado: CALMADO")
        
st.subheader("APAGAR")
if st.button("APAGAR"):
    message = json.dumps({"Act1": "apagar"})
    client1.publish("Cosplay", message)
    st.success("Se ha apagado el LED")

try:
    os.mkdir("temp")
except:
    pass
