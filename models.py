from sqlalchemy import Column, Integer, String
from database import Base  # Importamos la base declarativa desde database.py

class Producto(Base):
    __tablename__ = 'producto'  # Nombre de la tabla en SQLite

    # Definimos las columnas de la tabla

    # ID autoincremental y clave primaria
    id = Column(Integer, primary_key=True, index=True)

    # Nombre del producto, obligatorio (no puede ser NULL)
    nombre = Column(String, nullable=False)

    # Precio del producto, obligatorio
    precio = Column(Integer, nullable=False)

    # Categoría del producto, opcional (puede ser NULL)
    categoria = Column(String, nullable=True)

    # Cantidad en stock, opcional (puede ser NULL)
    stock = Column(Integer, nullable=True)

    # Método para mostrar información legible del producto
    def __str__(self):
        return f"Producto(id={self.id}, nombre='{self.nombre}', precio={self.precio}, categoria='{self.categoria}', stock={self.stock})"
