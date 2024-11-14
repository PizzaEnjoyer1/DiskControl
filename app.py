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
    print("Data has been published \n")
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

st.title("Multimodal Interfaces")
st.subheader("COSTUME CONTROL")
image = Image.open('Warrior.png')
st.image(image, width=720)
st.write("Activate a costume mode")

# Speech-to-text button
stt_button = Button(label=" Press and speak ", width=400)
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

# Variable to store the recognized text
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
        recognized_text = result.get("GET_TEXT").strip()  # Store the recognized text
        st.write("Recognized text:", recognized_text)
        # Publish the recognized text to MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": recognized_text})
        ret = client1.publish("Cosplay", message)

# Create columns for manual controls
col1, col2, col3, col4 = st.columns(4)

# Column for manual light control
with col1:
    st.subheader("Mode: DEFENSE")
    if st.button("DEFENSE"):
        message = json.dumps({"Act1": "defensa"})
        client1.publish("Cosplay", message)
        st.success("Mode activated: DEFENSE")

with col2:
    st.subheader("Mode: ATTACK")
    if st.button("ATTACK"):
        message = json.dumps({"Act1": "ataca"})
        client1.publish("Cosplay", message)
        st.success("Mode activated: ATTACK")

with col3:
    st.subheader("Mode: CALM")
    if st.button("CALM"):
        message = json.dumps({"Act1": "calmado"})
        client1.publish("Cosplay", message)
        st.success("Mode activated: CALM")

with col4:
    st.subheader("Mode: FREE")
    if st.button("FREE"):
        message = json.dumps({"Act1": "libre"})
        client1.publish("Cosplay", message)
        st.success("Mode activated: FREE")

# RGB controls for FREE mode
with st.expander("RGB Controls"):
    r = st.slider("Red", 0, 255, 0)
    g = st.slider("Green", 0, 255, 0)
    b = st.slider("Blue", 0, 255, 0)
    if st.button("Set Color"):
        message = json.dumps({"Act1": "libre", "r": r, "g": g, "b": b})
        client1.publish("Cosplay", message)
        st.success(f"Color set: RGB({r}, {g}, {b})")

try:
    os.mkdir("temp")
except:
    pass
