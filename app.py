import tkinter as tk
from tkinter import ttk, StringVar, messagebox
from database import Base, engine, SessionLocal
from models import Producto

# Creamos la sesión para conectar con la base de datos
session = SessionLocal()

# Creamos las tablas en caso de que aún no existan
Base.metadata.create_all(engine)

# Clase principal que contiene toda la interfaz gráfica y la lógica de la app
class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Productos con SQLAlchemy")
        self.root.geometry("600x500")

        # --- Formulario para agregar o editar productos ---
        frame_form = ttk.LabelFrame(root, text="Registrar / Editar producto")
        frame_form.pack(padx=10, pady=10, fill="x")

        # Campo nombre
        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = StringVar()
        self.nombre_entry = ttk.Entry(frame_form, textvariable=self.nombre_var)
        self.nombre_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Campo precio
        ttk.Label(frame_form, text="Precio:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.precio_var = StringVar()
        self.precio_entry = ttk.Entry(frame_form, textvariable=self.precio_var)
        self.precio_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Campo categoría (con desplegable)
        ttk.Label(frame_form, text="Categoría:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.categoria_var = StringVar()
        self.categoria_combobox = ttk.Combobox(frame_form, textvariable=self.categoria_var,
                                               values=["Electrónica", "Alimentos", "Ropa", "Hogar", "Otros"])
        self.categoria_combobox.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.categoria_combobox.set("Otros")

        # Campo stock
        ttk.Label(frame_form, text="Stock:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.stock_var = StringVar()
        self.stock_entry = ttk.Entry(frame_form, textvariable=self.stock_var)
        self.stock_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Botón para guardar nuevo producto
        self.boton_guardar = ttk.Button(frame_form, text="Guardar producto", command=self.guardar_producto)
        self.boton_guardar.grid(row=4, column=0, sticky="ew", padx=5, pady=10)

        # Botón para actualizar producto existente
        self.boton_actualizar = ttk.Button(frame_form, text="Actualizar producto", command=self.actualizar_producto)
        self.boton_actualizar.grid(row=4, column=1, sticky="ew", padx=5, pady=10)
        self.boton_actualizar['state'] = 'disabled'  # Se activa solo al seleccionar un producto

        # Etiqueta para mensajes de error o confirmación
        self.mensaje_var = StringVar()
        self.mensaje_label = ttk.Label(root, textvariable=self.mensaje_var, foreground="red")
        self.mensaje_label.pack()

        # --- Tabla de productos ---
        self.tabla = ttk.Treeview(root, columns=("nombre", "precio", "categoria", "stock"), show="headings", height=15)
        self.tabla.pack(padx=10, pady=10, fill="both", expand=True)

        # Encabezados
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("stock", text="Stock")

        # Tamaños y alineaciones
        self.tabla.column("nombre", width=200)
        self.tabla.column("precio", width=100, anchor="center")
        self.tabla.column("categoria", width=150, anchor="center")
        self.tabla.column("stock", width=80, anchor="center")

        # Botones extra debajo de la tabla
        frame_botones = ttk.Frame(root)
        frame_botones.pack(padx=10, pady=5, fill="x")

        # Botón eliminar producto
        self.boton_eliminar = ttk.Button(frame_botones, text="Eliminar producto", command=self.eliminar_producto)
        self.boton_eliminar.pack(side="left", expand=True, fill="x", padx=5)

        # Botón limpiar formulario
        self.boton_limpiar = ttk.Button(frame_botones, text="Limpiar campos", command=self.limpiar_campos)
        self.boton_limpiar.pack(side="left", expand=True, fill="x", padx=5)

        # Cuando seleccionamos un producto en la tabla, cargamos los datos para editar
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_producto_seleccionado)

        # Cargamos los productos al iniciar la app
        self.cargar_productos()

    def cargar_productos(self):
        # Limpiamos la tabla antes de cargar
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Obtenemos productos de la base de datos
        productos = session.query(Producto).all()
        for prod in productos:
            self.tabla.insert("", "end", iid=prod.id, values=(
                prod.nombre, prod.precio, prod.categoria or "N/A", prod.stock or 0
            ))

    def limpiar_campos(self):
        # Vaciamos los campos del formulario
        self.nombre_var.set("")
        self.precio_var.set("")
        self.categoria_var.set("Otros")
        self.stock_var.set("")
        self.mensaje_var.set("")
        self.tabla.selection_remove(self.tabla.selection())
        self.boton_guardar['state'] = 'normal'
        self.boton_actualizar['state'] = 'disabled'

    def validar_campos(self):
        # Comprobamos que los campos estén bien rellenados
        if not self.nombre_var.get().strip():
            self.mensaje_var.set("El nombre es obligatorio")
            return False

        try:
            precio = int(self.precio_var.get())
            if precio <= 0:
                self.mensaje_var.set("El precio debe ser mayor que 0")
                return False
        except ValueError:
            self.mensaje_var.set("El precio debe ser un número entero")
            return False

        stock_str = self.stock_var.get().strip()
        if stock_str:
            try:
                stock = int(stock_str)
                if stock < 0:
                    self.mensaje_var.set("El stock no puede ser negativo")
                    return False
            except ValueError:
                self.mensaje_var.set("El stock debe ser un número entero")
                return False

        return True

    def guardar_producto(self):
        if not self.validar_campos():
            return

        nuevo_producto = Producto(
            nombre=self.nombre_var.get().strip(),
            precio=int(self.precio_var.get()),
            categoria=self.categoria_var.get().strip() or None,
            stock=int(self.stock_var.get()) if self.stock_var.get().strip() else None
        )

        session.add(nuevo_producto)
        session.commit()

        self.mensaje_var.set("Producto guardado correctamente")
        self.cargar_productos()
        self.limpiar_campos()

    def cargar_producto_seleccionado(self, event):
        seleccionado = self.tabla.selection()
        if seleccionado:
            producto_id = int(seleccionado[0])
            producto = session.query(Producto).filter_by(id=producto_id).first()
            if producto:
                self.nombre_var.set(producto.nombre)
                self.precio_var.set(str(producto.precio))
                self.categoria_var.set(producto.categoria or "Otros")
                self.stock_var.set(str(producto.stock) if producto.stock is not None else "")
                self.boton_guardar['state'] = 'disabled'
                self.boton_actualizar['state'] = 'normal'
                self.mensaje_var.set(f"Editando producto ID {producto.id}")

    def actualizar_producto(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            self.mensaje_var.set("No hay producto seleccionado para actualizar")
            return

        if not self.validar_campos():
            return

        producto_id = int(seleccionado[0])
        producto = session.query(Producto).filter_by(id=producto_id).first()
        if producto:
            producto.nombre = self.nombre_var.get().strip()
            producto.precio = int(self.precio_var.get())
            producto.categoria = self.categoria_var.get().strip() or None
            producto.stock = int(self.stock_var.get()) if self.stock_var.get().strip() else None

            session.commit()
            self.mensaje_var.set("Producto actualizado correctamente")
            self.cargar_productos()
            self.limpiar_campos()

    def eliminar_producto(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Debes seleccionar un producto para eliminar.")
            return

        confirmar = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este producto?")
        if confirmar:
            producto_id = int(seleccionado[0])
            producto = session.query(Producto).get(producto_id)
            if producto:
                session.delete(producto)
                session.commit()
                self.cargar_productos()
                self.limpiar_campos()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()
