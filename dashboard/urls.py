from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("api/data/", views.api_data),
    path("mode/auto/", views.mode_auto),
    path("mode/silent/", views.mode_silent),
    path("set-age/<int:age>/", views.set_age, name="set_age"),
    path("led-mode/on/", views.led_mode_on),
    path("led-mode/off/", views.led_mode_off),
]