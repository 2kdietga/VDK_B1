from django.apps import AppConfig
import os


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        try:
            # Chỉ chạy trong worker thật (tránh double khi dev)
            if os.environ.get("RUN_MAIN") == "true" or "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
                from .mqtt_client import start_mqtt
                start_mqtt()

        except Exception as e:
            print("MQTT error:", e)