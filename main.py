from auth import get_current_user, check_role, fake_users
import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Header, Path
from models import Base, ProductoInfo, AutenticacionRequest, Usuario, PagoRequest
from database import SessionLocal, engine
from datetime import datetime, timedelta, date
from random import randint
from sqlalchemy.orm import Session
import random
import stripe
from dotenv import load_dotenv
import os
print("STRIPE_API_KEY:", os.getenv("STRIPE_API_KEY"))
load_dotenv() 
EXTERNAL_API_URL = "https://ea2p2assets-production.up.railway.app/"
app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fecha_random_reciente():
    hoy = datetime.now()
    hace_60_dias = hoy - timedelta(days=60)
    fecha_random = hace_60_dias + timedelta(days=random.randint(0, 60))
    return fecha_random.date()

#@app.on_event("startup")
#async def cargar_productos_externos():
#    load_dotenv() 
#    x_auth = os.getenv("EXTERNAL_API_TOKEN")
#    db = SessionLocal()
#    async with httpx.AsyncClient() as client:
#        try:
#            headers = {"x-authentication": x_auth}
#            response = await client.get(EXTERNAL_API_URL + "data/articulos", headers=headers)
#            response.raise_for_status()
#            productos = response.json()
#            db = SessionLocal()

#            for producto in productos:
#                pid = producto.get("id")
#                nombre = producto.get("nombre", "")
#                descripcion = producto.get("descripcion", "")
#                existe = db.query(ProductoInfo).filter_by(producto_id=pid).first()
#                if not existe:
#                    nuevo = ProductoInfo(
#                        producto_id=pid,
#                        nombre=nombre,
#                        descripcion=descripcion,
#                        fecha_agregado=fecha_random_reciente(),
#                        descuento=randint(5, 30),
#                        es_novedad=(date.today() - fecha_random_reciente()).days <= 30
#                    )
#                    db.add(nuevo)
#            db.commit()
#        except Exception as e:
#            print(f"Error al cargar productos: {e}")
#        finally:
#            db.close()#
#

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/autenticar-usuario")

def autenticar_usuario(nombre_usuario : str = Header(...), contrasena : str = Header(...)):
    for token, usuario in fake_users.items():
        if usuario.nombre == nombre_usuario:
            if usuario.contrasena == contrasena:
                return {"token": token}
            else:
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    raise HTTPException(status_code=401, detail="Usuario no encontrado")

@app.get("/novedades")
def get_novedades(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "client"])
    return db.query(ProductoInfo).all()

@app.get("/catalogo_productos")
def obtener_productos(x_authentication: str = Header(...), user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "client"])
    headers = {"x-authentication": x_authentication}
    
    try:
        response = httpx.get(EXTERNAL_API_URL + "data/articulos", headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API externa: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

@app.get("/catalogo_productos/{producto_id}")
def obtener_productos(
    producto_id: str = Path(..., description="ID del producto"),
    x_authentication: str = Header(...),
    user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "client"])
    headers = {"x-authentication": x_authentication}
    
    try:
        response = httpx.get(f"{EXTERNAL_API_URL}data/articulos/{producto_id}", headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API externa: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

@app.get("/sucursales")
def obtener_sucursales(x_authentication: str = Header(...), user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "client"])
    headers = {"x-authentication": x_authentication}
    
    try:
        response = httpx.get(EXTERNAL_API_URL + "data/sucursales", headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API externa: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

@app.get("/sucursales/{sucursal_id}")
def obtener_sucursal(
    sucursal_id: str = Path(..., description="ID de la sucursal"),
    x_authentication: str = Header(...),
    user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "client"])
    headers = {"x-authentication": x_authentication}
    
    try:
        response = httpx.get(f"{EXTERNAL_API_URL}data/sucursales/{sucursal_id}", headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API externa: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

@app.get("/vendedores")
def obtener_vendedores(x_authentication: str = Header(...), user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "store_manager"])
    headers = {"x-authentication": x_authentication}
    
    try:
        response = httpx.get(EXTERNAL_API_URL + "data/vendedores", headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API externa: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

@app.get("/vendedores/{vendedor_id}")
def obtener_sucursal(
    vendedor_id: str = Path(..., description="ID del vendedor"),
    x_authentication: str = Header(...),
    user: Usuario = Depends(get_current_user)):
    check_role(user, ["admin", "store_manager"])
    headers = {"x-authentication": x_authentication}
    
    try:
        response = httpx.get(f"{EXTERNAL_API_URL}data/vendedores/{vendedor_id}", headers=headers)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API externa: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

##================================Pago============================================================##
stripe.api_key = os.getenv("STRIPE_API_KEY")


@app.post("/pago")
def pago(data: PagoRequest, user: Usuario = Depends(get_current_user)):
    print("Stripe Key:", stripe.api_key)
    check_role(user, ["admin", "service_account"])
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": data.moneda,
                        "product_data": {
                            "name": data.nombre_producto,
                        },
                        "unit_amount": data.precio_unitario,
                    },
                    "quantity": data.cantidad,
                }
            ],
            mode="payment",
            success_url="https://ea2p2assets-production.up.railway.app/success.html",
            cancel_url="https://ea2p2assets-production.up.railway.app/cancel.html",
        )
        return {"checkout_url": session.url, "Stripe Key:" : stripe.api_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la sesion de pago: {str(e)}")


##============================Conversor================================================================##

CURRENCY_API_KEY = "cur_live_qd1K78yUEOalPJc0hCXOUAZhgwc7ElO33aWMhnY5" 

@app.get("/convertir_moneda")
def convertir_moneda(
    moneda_origen: str = "USD",
    moneda_destino: str = "CLP",
    cantidad: float = 1.0
):
    url = f"https://api.currencyapi.com/v3/latest?apikey={CURRENCY_API_KEY}&base_currency={moneda_origen}&currencies={moneda_destino}"

    try:
        response = httpx.get(url)
        data = response.json()

        if "data" not in data or moneda_destino not in data["data"]:
            raise HTTPException(
                status_code=400,
                detail="Una o ambas monedas no son válidas o no estan soportadas por la API.Prueba con otra moneda o usa mayusculas."
            )

        tasa = data["data"][moneda_destino]["value"]
        valor_convertido = cantidad * tasa

        return {
            "moneda_origen": moneda_origen.upper(),
            "moneda_destino": moneda_destino.upper(),
            "cantidad": cantidad,
            "valor_convertido": round(valor_convertido, 2)
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectarse con la API: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error general: {str(e)}")
