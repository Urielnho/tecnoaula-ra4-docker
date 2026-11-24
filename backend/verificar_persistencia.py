"""Consulta real de un usuario para verificar persistencia, sin exponer su clave."""
import json
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tecnoaula.settings")
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import connection
if len(sys.argv) != 2:
    raise SystemExit("Uso: python verificar_persistencia.py correo@ejemplo.com")
u = get_user_model().objects.get(email=sys.argv[1])
print(json.dumps({"motor": connection.vendor, "id": u.pk, "email": u.email, "matricula": u.matricula, "activo": u.is_active}, ensure_ascii=False))
