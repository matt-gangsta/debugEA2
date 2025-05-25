from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2, HTTPBearer, HTTPAuthorizationCredentials 
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from models import Usuario

bearer_scheme = HTTPBearer()

fake_users = {
    "token_admin": Usuario(nombre="javier_thompson", rol="admin", contrasena="aONF4d6aNBIxRjlgjBRRzrS"),
    "token_client": Usuario(nombre="ignacio_tapia", rol="client", contrasena="f7rWChmQS1JYfThT"),
    "token_stripe": Usuario(nombre="stripe_sa", rol="service_account", contrasena="dzkQqDL9XZH33YDzhmsf"),
    "token_maintainer": Usuario(nombre="mantenedor", rol="maintainer", contrasena="supersecurepass1"),
    "token_store_manager": Usuario(nombre="jefe_de_tienda", rol="store_manager", contrasena="supersecurepass2"),
    "token_storage": Usuario(nombre="bodega", rol="storage", contrasena="supersecurepass3"),
}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Usuario:
    token = credentials.credentials
    user = fake_users.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user

def check_role(user: Usuario, roles_permitidos: list):
    if user.rol not in roles_permitidos:
        raise HTTPException(status_code=403, detail="No autorizado")