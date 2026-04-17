from django.shortcuts import render
from django.http import JsonResponse
from .mqtt_client import latest_data, publish_age, publish_mode

def index(request):
    return render(request, "index.html")

def mode_auto(request):
    publish_mode("AUTO")
    return JsonResponse({"ok": True, "mode": "AUTO"})

def mode_silent(request):
    publish_mode("SILENT")
    return JsonResponse({"ok": True, "mode": "SILENT"})

def api_data(request):
    return JsonResponse(latest_data)

def set_age(request, age):
    ok = publish_age(age)
    return JsonResponse({"ok": ok, "age": age})