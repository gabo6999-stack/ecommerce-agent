#!/usr/bin/env python3
"""Prueba la puerta de acceso de web.py.

    python3 scripts/prueba_acceso.py

Extrae del propio `web.py` el bloque que va de `app = Flask(__name__)` al
final de `/logout` —la puerta entera— y lo ejecuta con dos rutas falsas que
imitan a las peligrosas. No toca el resto de la aplicación ni necesita sus
dependencias pesadas: solo Flask.

Qué comprueba, y por qué cada cosa:

  · Los endpoints que escriben en sitios en vivo responden 401 sin
    credenciales. Ese era el agujero: `/pys-product-update`,
    `/raditech-page-update` y unos cuarenta más estaban abiertos al público
    en una URL de Railway.
  · `/healthz` queda abierto, o Railway marca el servicio como caído.
  · El token de API compara en tiempo constante y rechaza el vacío.
  · La contraseña **con acentos** funciona. `hmac.compare_digest` sobre
    `str` solo admite ASCII y levanta TypeError con una ñ o una tilde: sin
    esta prueba, una contraseña en español daba 500 y no entraba nadie.
  · `?siguiente=` no puede mandar a otro dominio.
  · Hay freno por intentos.
  · Sin PANEL_PASSWORD ni API_TOKEN la aplicación se cierra (503), no se
    abre. Fallar abierto es justo el fallo que esto arregla.
"""
import os
import sys
import types

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAVE_CON_ACENTOS = "contraseña-con-ñ-y-tildé"
TOKEN = "token-de-prueba-123"


def carga_puerta():
    """Ejecuta solo el bloque de la puerta, sin el resto de web.py."""
    with open(os.path.join(RAIZ, "web.py"), encoding="utf-8-sig") as f:
        fuente = f.read()
    ini = fuente.index("app = Flask(__name__)")
    marca = '    return redirect(url_for("login"))'
    fin = fuente.index(marca) + len(marca)
    bloque = "\n".join(l for l in fuente[ini:fin].split("\n")
                       if not l.startswith("client = anthropic"))
    cabecera = ("from flask import Flask, request, jsonify, redirect, session\n"
                "import os, time, secrets\n"
                "from datetime import timedelta\n")
    mod = types.ModuleType("puerta")
    exec(compile(cabecera + bloque, "web.py:puerta", "exec"), mod.__dict__)

    app = mod.app
    app.logger.disabled = True

    @app.route("/pys-product-update", methods=["POST"])
    def falso_update():
        return {"escrito": True}

    @app.route("/")
    def falso_index():
        return "<html>panel</html>"

    return app


class Actas:
    def __init__(self):
        self.fallos = []

    def __call__(self, desc, real, esperado):
        ok = real == esperado
        print(("  ok   " if ok else "  FALLA ") + desc + "  -> " + repr(real)
              + ("" if ok else "   (esperaba " + repr(esperado) + ")"))
        if not ok:
            self.fallos.append(desc)


def con_credenciales(actas):
    os.environ.update({"PANEL_PASSWORD": CLAVE_CON_ACENTOS, "API_TOKEN": TOKEN,
                       "FLASK_SECRET_KEY": "fija-para-la-prueba",
                       "PANEL_COOKIE_INSEGURA": "1"})
    app = carga_puerta()
    c = app.test_client()
    html = {"Accept": "text/html"}

    print("\nSin credenciales:")
    actas("POST al endpoint que reescribía fichas de producto",
          c.post("/pys-product-update", json={"post_id": 1}).status_code, 401)
    actas("GET / desde navegador redirige a /login",
          c.get("/", headers=html).status_code, 302)
    actas("/healthz abierto para Railway", c.get("/healthz").status_code, 200)
    actas("/login se puede ver", c.get("/login").status_code, 200)

    print("\nCon token de API:")
    actas("X-API-Key correcta", c.post("/pys-product-update", json={},
          headers={"X-API-Key": TOKEN}).status_code, 200)
    actas("X-API-Key incorrecta", c.post("/pys-product-update", json={},
          headers={"X-API-Key": "otra-cosa"}).status_code, 401)
    actas("X-API-Key vacía", c.post("/pys-product-update", json={},
          headers={"X-API-Key": ""}).status_code, 401)

    print("\nEntrando por el navegador (contraseña con ñ y tilde):")
    actas("contraseña incorrecta",
          c.post("/login", data={"password": "mala"}, headers=html).status_code, 401)
    actas("contraseña correcta redirige",
          c.post("/login", data={"password": CLAVE_CON_ACENTOS, "siguiente": "/"},
                 headers=html).status_code, 302)
    actas("con la sesión ya entra al endpoint peligroso",
          c.post("/pys-product-update", json={}).status_code, 200)
    actas("/logout cierra", c.get("/logout").status_code, 302)
    actas("y después vuelve a estar cerrado",
          c.post("/pys-product-update", json={}).status_code, 401)

    print("\nRedirección abierta:")
    r = c.post("/login", data={"password": CLAVE_CON_ACENTOS,
                               "siguiente": "https://malicioso.example/roba"},
               headers=html)
    actas("no manda a otro dominio", r.headers.get("Location", ""), "/")

    print("\nFreno por intentos:")
    c2 = app.test_client()
    ultimo = None
    for i in range(9):
        ultimo = c2.post("/login", data={"password": "mala%d" % i}, headers=html)
    actas("al noveno intento pide esperar",
          "Espera diez minutos" in ultimo.get_data(as_text=True), True)

    print("\nCookie de sesión:")
    actas("HttpOnly", app.config["SESSION_COOKIE_HTTPONLY"], True)
    actas("SameSite=Lax (Strict rompería la vuelta de OAuth de Google)",
          app.config["SESSION_COOKIE_SAMESITE"], "Lax")


def sin_credenciales(actas):
    for v in ("PANEL_PASSWORD", "API_TOKEN"):
        os.environ.pop(v, None)
    c = carga_puerta().test_client()
    print("\nSin PANEL_PASSWORD ni API_TOKEN:")
    actas("la aplicación se cierra en vez de quedar abierta",
          c.post("/pys-product-update", json={}).status_code, 503)
    actas("y /healthz lo dice",
          c.get("/healthz").get_json()["acceso_configurado"], False)


def main():
    try:
        import flask  # noqa: F401
    except ImportError:
        print("Hace falta Flask:  pip install flask")
        return 2
    actas = Actas()
    con_credenciales(actas)
    sin_credenciales(actas)
    print("\n" + ("TODO BIEN" if not actas.fallos
                  else "FALLAN: " + ", ".join(actas.fallos)))
    return 1 if actas.fallos else 0


if __name__ == "__main__":
    sys.exit(main())
