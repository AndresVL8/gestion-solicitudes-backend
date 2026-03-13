from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import List
import sqlite3

# Forzamos versión 3.0.0 para compatibilidad total con Power Automate
app = FastAPI(title="API Solicitudes Demo", openapi_version="3.0.0")

def get_db():
    conn = sqlite3.connect("solicitudes.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Esta línea asegura que la tabla exista cada vez que se use la API
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacion TEXT,
            nombre TEXT,
            lider TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            total_dias INTEGER,
            estado TEXT
        )
    """)
    conn.commit()
    return conn

class Solicitud(BaseModel):
    identificacion: str
    nombre: str
    lider: str
    fecha_inicio: date
    fecha_fin: date
    estado: str = "Pendiente"

# 1. LISTAR TODO
@app.get("/solicitudes/")
def listar_solicitudes():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM solicitudes").fetchall()
        return [dict(row) for row in rows]

# 2. CREAR
@app.post("/solicitudes/")
def crear_solicitud(s: Solicitud):
    total_dias = (s.fecha_fin - s.fecha_inicio).days
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO solicitudes (identificacion, nombre, lider, fecha_inicio, fecha_fin, total_dias, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (s.identificacion, s.nombre, s.lider, str(s.fecha_inicio), str(s.fecha_fin), total_dias, s.estado))
        conn.commit()
        return {"message": "Creado con éxito", "id": cursor.lastrowid}

# 3. OBTENER UNA SOLICITUD (Por ID)
@app.get("/solicitudes/{solicitud_id}")
def obtener_solicitud(solicitud_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        return dict(row)

# 4. ACTUALIZAR (Para aprobar/rechazar en la demo)
@app.put("/solicitudes/{solicitud_id}")
def actualizar_solicitud(solicitud_id: int, s: Solicitud):
    total_dias = (s.fecha_fin - s.fecha_inicio).days
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE solicitudes 
            SET identificacion=?, nombre=?, lider=?, fecha_inicio=?, fecha_fin=?, total_dias=?, estado=?
            WHERE id = ?
        """, (s.identificacion, s.nombre, s.lider, str(s.fecha_inicio), str(s.fecha_fin), total_dias, s.estado, solicitud_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No se encontró para actualizar")
        return {"message": "Actualizado con éxito"}

# 5. ELIMINAR
@app.delete("/solicitudes/{solicitud_id}")
def eliminar_solicitud(solicitud_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solicitudes WHERE id = ?", (solicitud_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No se encontró para eliminar")
        return {"message": "Eliminado con éxito"}
