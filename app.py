import json
import os
import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

HOST = os.getenv("MYSQL_HOST", "localhost")
USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
DB = os.getenv("MYSQL_DATABASE", "pendientes")

if not USER or not PASSWORD:
    raise RuntimeError("Faltan MYSQL_USER o MYSQL_PASSWORD en el archivo .env")


def conectar(con_db=True):
    return pymysql.connect(
        host=HOST, user=USER, password=PASSWORD,
        database=DB if con_db else None,
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, autocommit=True,
    )


def preparar():
    con = conectar(con_db=False)
    with con.cursor() as c:
        c.execute(f"CREATE DATABASE IF NOT EXISTS `{DB}` CHARACTER SET utf8mb4")
    con.close()
    con = conectar()
    with con.cursor() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tareas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            texto VARCHAR(255) NOT NULL,
            hecha TINYINT(1) NOT NULL DEFAULT 0,
            creada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS habitos_estado (
            id TINYINT PRIMARY KEY,
            datos LONGTEXT NOT NULL,
            actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )""")
    con.close()


@app.route("/")
def inicio():
    return send_from_directory(".", "index.html")

@app.route("/mochila")
def mochila():
    return send_from_directory(".", "checklist-mochila.html")

@app.route("/morral")
def morral():
    return send_from_directory(".", "checklist-morral.html")

@app.route("/habitos")
def habitos():
    return send_from_directory(".", "habitos.html")

@app.route("/api/habitos", methods=["GET", "PUT"])
def api_habitos():
    datos = None
    if request.method == "PUT":
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict) or "habits" not in datos:
            return jsonify(error="Datos inválidos"), 400
    try:
        con = conectar()
        with con.cursor() as c:
            if datos is not None:
                c.execute(
                    "INSERT INTO habitos_estado (id, datos) VALUES (1, %s) "
                    "ON DUPLICATE KEY UPDATE datos = VALUES(datos)",
                    (json.dumps(datos, ensure_ascii=False),))
            c.execute("SELECT datos FROM habitos_estado WHERE id = 1")
            fila = c.fetchone()
        con.close()
        return jsonify(json.loads(fila["datos"]) if fila else None)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/menu.js")
def menu():
    return send_from_directory(".", "menu.js")

@app.route("/api", methods=["GET", "POST"])
def api():
    accion = request.args.get("accion", "listar")
    datos = request.get_json(silent=True) or {}
    try:
        con = conectar()
        with con.cursor() as c:
            if accion == "agregar":
                texto = (datos.get("texto") or "").strip()[:255]
                if not texto:
                    return jsonify(error="Texto vacío"), 400
                c.execute("INSERT INTO tareas (texto) VALUES (%s)", (texto,))
            elif accion == "alternar":
                c.execute("UPDATE tareas SET hecha = 1 - hecha WHERE id = %s", (int(datos.get("id", 0)),))
            elif accion == "borrar":
                c.execute("DELETE FROM tareas WHERE id = %s", (int(datos.get("id", 0)),))
            elif accion == "limpiar":
                c.execute("DELETE FROM tareas WHERE hecha = 1")
            c.execute("SELECT id, texto, hecha FROM tareas ORDER BY hecha, id DESC")
            filas = c.fetchall()
        con.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    preparar()
    print("Listo: abre http://localhost:5000")
    app.run(port=5000)
