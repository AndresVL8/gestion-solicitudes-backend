from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import List, Optional
import sqlite3

app = FastAPI(title="API Solicitudes Demo")

# Modelo para recibir datos
class Solicitud(BaseModel):
    identificacion: str
    nombre: str
    lider: str
    fecha_inicio: date
    fecha_fin: date
    estado: str = "Pendiente"

# Modelo para devolver datos (incluye el ID y el cálculo)
class SolicitudOut(Solicitud):
    id: int
    total_dias: int

def get_db_connection():
    conn = sqlite3.connect("solicitudes.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1. CREATE: Crear una solicitud
@app.post("/solicitudes/", response_model=dict)
def crear_solicitud(s: Solicitud):
    total_dias = (s.fecha_fin - s.fecha_inicio).days
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO solicitudes (identificacion, nombre, lider, fecha_inicio, fecha_fin, total_dias, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (s.identificacion, s.nombre, s.lider, str(s.fecha_inicio), str(s.fecha_fin), total_dias, s.estado))
        return {"message": "Creado", "id": cursor.lastrowid}

# 2. READ: Ver todas las solicitudes
@app.get("/solicitudes/", response_model=List[SolicitudOut])
def listar_solicitudes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM solicitudes").fetchall()
        return [dict(row) for row in rows]

# 3. READ: Ver una sola solicitud por ID
@app.get("/solicitudes/{solicitud_id}", response_model=SolicitudOut)
def obtener_solicitud(solicitud_id: int):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No encontrada")
        return dict(row)

# 4. UPDATE: Actualizar estado o datos
@app.put("/solicitudes/{solicitud_id}")
def actualizar_solicitud(solicitud_id: int, s: Solicitud):
    total_dias = (s.fecha_fin - s.fecha_inicio).days
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE solicitudes 
            SET identificacion=?, nombre=?, lider=?, fecha_inicio=?, fecha_fin=?, total_dias=?, estado=?
            WHERE id = ?
        """, (s.identificacion, s.nombre, s.lider, str(s.fecha_inicio), str(s.fecha_fin), total_dias, s.estado, solicitud_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No encontrada")
        return {"message": "Actualizada correctamente"}

# 5. DELETE: Borrar solicitud
@app.delete("/solicitudes/{solicitud_id}")
def eliminar_solicitud(solicitud_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solicitudes WHERE id = ?", (solicitud_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No encontrada")
        return {"message": "Eliminada"}