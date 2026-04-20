import json
import ssl
import threading
import paho.mqtt.client as mqtt

# dữ liệu realtime (RAM)
latest_data = {
    "heart_rate": 0,
    "spo2": 0,
    "motor": "OFF",
    "status": "Mất tín hiệu",
    "mode": "AUTO",
    "age": 65,
    "age_group": "Người già",
    "device_status": "OFFLINE",
    "led_mode": "OFF",
    "led": "OFF",
}

data_lock = threading.Lock()

# ===== HIVEMQ CLOUD =====
BROKER = "23876fe7f57d410b9a0c41b405e675ec.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "toighecnhung"
PASSWORD = "Huy12012005"

TOPIC_DATA = "esp32/max30100/data"
TOPIC_MOTOR_STATUS = "esp32/motor/status"
TOPIC_MOTOR_MODE = "esp32/motor/mode"
TOPIC_PROFILE_AGE = "esp32/profile/age"
TOPIC_STATUS = "esp32/max30100/status"
TOPIC_LED_MODE = "esp32/led/mode"
TOPIC_LED_STATUS = "esp32/led/status"


def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT Connected:", rc)

    if rc == 0:
        client.subscribe(TOPIC_DATA)
        client.subscribe(TOPIC_MOTOR_STATUS)
        client.subscribe(TOPIC_MOTOR_MODE)
        client.subscribe(TOPIC_PROFILE_AGE)
        client.subscribe(TOPIC_STATUS)
        client.subscribe(TOPIC_LED_MODE)
        client.subscribe(TOPIC_LED_STATUS)
        print("Đã subscribe topic")
    else:
        print("MQTT connection failed with code:", rc)


def on_message(client, userdata, msg):
    payload_text = msg.payload.decode(errors="ignore").strip()

    with data_lock:
        if msg.topic == TOPIC_DATA:
            try:
                payload = json.loads(payload_text)
                latest_data["heart_rate"] = payload.get("heart_rate", 0)
                latest_data["spo2"] = payload.get("spo2", 0)
                latest_data["status"] = payload.get("status", "Mất tín hiệu")
                latest_data["mode"] = payload.get("mode", latest_data["mode"])
                latest_data["age"] = payload.get("age", latest_data["age"])
                latest_data["age_group"] = payload.get("age_group", latest_data["age_group"])
            except Exception as e:
                print("Lỗi parse TOPIC_DATA:", e)

        elif msg.topic == TOPIC_MOTOR_STATUS:
            latest_data["motor"] = payload_text

        elif msg.topic == TOPIC_MOTOR_MODE:
            latest_data["mode"] = payload_text

        elif msg.topic == TOPIC_PROFILE_AGE:
            try:
                age = int(payload_text)
                if 0 <= age < 130:
                    latest_data["age"] = age
            except ValueError:
                print("Tuổi không hợp lệ:", payload_text)
        elif msg.topic == TOPIC_STATUS:
            if payload_text.upper() == "ONLINE":
                latest_data["device_status"] = "ONLINE"
            elif payload_text.upper() == "OFFLINE":
                latest_data["device_status"] = "OFFLINE"
                latest_data["heart_rate"] = 0
                latest_data["spo2"] = 0
                latest_data["motor"] = "OFF"  
        elif msg.topic == TOPIC_LED_MODE:
            latest_data["led_mode"] = payload_text
        elif msg.topic == TOPIC_LED_STATUS:
            latest_data["led"] = payload_text


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.username_pw_set(USERNAME, PASSWORD)

    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.tls_insecure_set(False)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)

    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()

    return client


mqtt_client = start_mqtt()


def publish_mode(mode: str):
    if mode not in ["AUTO", "SILENT", "ON", "OFF"]:
        return False
    if mode in ["ON", "OFF"]:
        mqtt_client.publish(TOPIC_LED_MODE, mode, retain=True)
    else:
        mqtt_client.publish(TOPIC_MOTOR_MODE, mode, retain=True)

    with data_lock:
        latest_data["mode"] = mode

    return True


def publish_age(age: int):
    if not isinstance(age, int):
        return False

    if age < 0 or age >= 130:
        return False

    mqtt_client.publish(TOPIC_PROFILE_AGE, str(age), retain=True)

    with data_lock:
        latest_data["age"] = age

    return True


def get_latest_data():
    with data_lock:
        return latest_data.copy()