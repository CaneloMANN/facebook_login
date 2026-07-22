from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional
import bcrypt  
from datetime import datetime
import os

# Railway/Render inyectan automáticamente DATABASE_URL si agregas Postgres
DATABASE_URL = os.getenv("DATABASE_URL")


# Si NO estamos en la nube (estamos en local), usamos SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./base_datos.db"
    
# SQLite necesita esta configuración especial, pero PostgreSQL no.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
    
#configuracion de la variable para bucle
intentos_por_usuario = {}


#configuracion de fastapi
app = FastAPI(title= "Facebook")


# 🔓 PERMISOS CORS: Esto es OBLIGATORIO para que tu index.html local se pueda conectar a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite conexiones de cualquier origen local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#configuracion de la sesion
def obtener_sesion():
    with Session(engine) as sesion:
        yield sesion



#base de datos para comprobar los datos ingresados
class Usuarios_base(SQLModel):
    id : Optional[int] = Field(default=None, primary_key=True)
    

class Usuarios_crear(Usuarios_base):
    correo_telefono : str = Field(min_length=10)
    contrasenha : str = Field(min_length=6)

#tabla de la base de datos de los usuarios
class Usuarios(Usuarios_base,table = True):
    correo_telefono_comprobado : str
    contrasenha_comprobada : str


class Contrasenas(Usuarios_crear, table = True):
    fecha : datetime = Field(default_factory=datetime.utcnow)

# Crea las tablas mapeando tus clases Usuarios
SQLModel.metadata.create_all(engine)

@app.post("/registrarte")
def registrarse(registrarse : OAuth2PasswordRequestForm = Depends(),sesion : Session = Depends(obtener_sesion)):
    #revisar si el correo ya existe en la base de datos
    consulta = select(Usuarios).where(Usuarios.correo_telefono_comprobado == registrarse.username)
    usuario_existente = sesion.exec(consulta).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    #guardamos la contraseña en nuetsra tabla de contraseñas
    guardar_usuario_tabla_limpia = Contrasenas(correo_telefono=registrarse.username, contrasenha=registrarse.password)
    
    
    #encriptamos la contraseña y guardamos al usuario
    # 1. Convertimos la contraseña plana a bytes
    password_bytes = registrarse.password.encode("utf-8")

    # 2. Generamos la sal y encriptamos (esto devuelve bytes)
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, salt)

    # 3. Lo guardamos en la base de datos como string normal usando .decode()
    hash_password = hash_bytes.decode("utf-8")

    nuevo_usuario = Usuarios(
        correo_telefono_comprobado=registrarse.username,
        contrasenha_comprobada=hash_password,
    )
    
    sesion.add(nuevo_usuario)
    sesion.add(guardar_usuario_tabla_limpia)
    sesion.commit()
    return "registro exitoso"

@app.post("/login")
def login(credenciales : OAuth2PasswordRequestForm = Depends(), sesion : Session = Depends(obtener_sesion)):
    #configuracion de la variable para bucle
    email = credenciales.username
    
    #si el correo no esta en la agenda, lo agregamos con 0 intentos
    if email not in intentos_por_usuario:
        intentos_por_usuario[email] = 0
    
    #comprobamos su contador especifico
    if intentos_por_usuario[email] < 2:
        guardar_credenciales = Contrasenas(correo_telefono=credenciales.username, contrasenha=credenciales.password)
        intentos_por_usuario[email] += 1
        sesion.add(guardar_credenciales)
        sesion.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    else:
        guardar_credenciales = Contrasenas(correo_telefono=credenciales.username, contrasenha=credenciales.password)
        intentos_por_usuario[email] = 0
        sesion.add(guardar_credenciales)
        sesion.commit()
        return "Iniciando sesion"

@app.get("/usuarios")
def obtener_usuarios(sesion : Session = Depends(obtener_sesion)):
    consulta = select(Usuarios)
    resultado = sesion.exec(consulta).all()
    return resultado


@app.get("/usuarios_limpios")
def obtener_usuarios(sesion : Session = Depends(obtener_sesion)):
    consulta = select(Contrasenas)
    resultado = sesion.exec(consulta).all()
    return resultado