from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Ruta absoluta donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta al archivo SQLite
DB_PATH = os.path.join(BASE_DIR, 'productos.db')

# URI para conexión SQLite
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Motor de conexión con SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Base para declarar modelos
Base = declarative_base()

# Fábrica para crear sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Nota: No creamos 'session = SessionLocal()' aquí para evitar sesiones globales
