from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean
from database import Base
from datetime import datetime

class Usuario(BaseModel):
    nombre: str
    rol: str
    contrasena: str

class AutenticacionRequest(BaseModel):
    nombre_usuario: str
    contrasena: str

class PagoRequest(BaseModel):
    nombre_producto: str
    cantidad: int
    moneda: str = "clp"
    precio_unitario: int

class ProductoInfo(Base):
    __tablename__ = "productos_info"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(String, unique=True, index=True)
    nombre = Column(String)
    descripcion = Column(String)
    fecha_agregado = Column(Date)
    descuento = Column(Integer, default=0)
    es_novedad = Column(Boolean, default=False)