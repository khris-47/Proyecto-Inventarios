import tkinter as tk
from tkinter import ttk
from db_config import get_connection
import mysql.connector
from decimal import Decimal, getcontext

# Configurar precisión decimal para los cálculos de inventario de seguridad
getcontext().prec = 28


class InventarioSeguridadFrame(tk.Frame):
    Z_FACTOR = Decimal('1.65')

    def __init__(self, parent):
        super().__init__(parent)
        self.datos_originales = []
        self.crear_panel_titulo()
        self.crear_panel_busqueda()
        self.crear_tabla_seguridad()
        self.cargar_seguridad()

    def crear_panel_titulo(self):
        panel_titulo = tk.Frame(self, bg="#0A1F44")
        panel_titulo.pack(fill="x", padx=10, pady=10)

        titulo = tk.Label(
            panel_titulo,
            text="Inventario de Seguridad",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#0A1F44"
        )
        titulo.pack(pady=(10, 5))

        subtitulo = tk.Label(
            panel_titulo,
            text="Cálculo de inventario de seguridad y estado de stock",
            font=("Segoe UI", 10, "italic"),
            fg="#DDDDDD",
            bg="#0A1F44"
        )
        subtitulo.pack(pady=(0, 10))

        linea = tk.Frame(self, height=2, bg="#DDDDDD")
        linea.pack(fill="x", padx=10, pady=(0, 10))

    def crear_panel_busqueda(self):
        """Crea el panel de búsqueda en tiempo real."""
        panel_busqueda = tk.Frame(self, bg="white")
        panel_busqueda.pack(fill="x", padx=10, pady=(0, 10))

        lbl_buscar = tk.Label(
            panel_busqueda,
            text="Buscar:",
            font=("Segoe UI", 11),
            bg="white",
            fg="#0A1F44"
        )
        lbl_buscar.pack(side=tk.LEFT, padx=(0, 10))

        self.entry_busqueda = tk.Entry(
            panel_busqueda,
            font=("Segoe UI", 11),
            relief=tk.SOLID,
            bd=2,
            bg="#E8E8E8",
            fg="#0A1F44",
            insertbackground="#0A1F44"
        )
        self.entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_busqueda.bind('<KeyRelease>', self.on_buscar_tiempo_real)

    def crear_tabla_seguridad(self):
        self.contenido_frame = tk.Frame(self)
        self.contenido_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.contenido_frame.grid_rowconfigure(0, weight=1)
        self.contenido_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Seguridad.Treeview.Heading",
                        background="#0A1F44",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.configure("Seguridad.Treeview",
                        background="white",
                        foreground="black",
                        fieldbackground="white",
                        rowheight=25)
        style.map("Seguridad.Treeview",
                  background=[('selected', '#347083')])

        columnas = (
            "Código", "Producto", "Stock Actual", "Variabilidad de Demanda",
            "Días de Entrega", "Inventario de Seguridad", "Estado"
        )
        self.tree = ttk.Treeview(self.contenido_frame,
                                 columns=columnas,
                                 show="headings",
                                 height=15,
                                 style="Seguridad.Treeview")

        anchos = {
            "Código": 90,
            "Producto": 220,
            "Stock Actual": 100,
            "Variabilidad de Demanda": 160,
            "Días de Entrega": 120,
            "Inventario de Seguridad": 160,
            "Estado": 120
        }

        for col in columnas:
            self.tree.heading(col, text=col)
            if col == "Producto":
                anchor = "w"
            else:
                anchor = "center"
            self.tree.column(col, width=anchos.get(col, 100), anchor=anchor)

        v_scrollbar = ttk.Scrollbar(self.contenido_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.contenido_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")


    def cargar_seguridad(self):
        connection = get_connection()
        if connection is None:
            print("Error: No se pudo conectar a la base de datos.")
            return

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT p.id_producto, p.codigo, p.nombre, p.stock_actual,
                       par.variabilidad_demanda, par.tiempo_entrega
                FROM Productos p
                LEFT JOIN Parametros par ON p.id_producto = par.id_producto
                ORDER BY p.codigo
            """
            cursor.execute(query)
            productos = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            productos_seguridad = []

            for prod in productos:
                stock_actual = Decimal(str(prod['stock_actual'])) if prod['stock_actual'] is not None else Decimal('0')
                variabilidad = Decimal(str(prod['variabilidad_demanda'])) if prod['variabilidad_demanda'] is not None else Decimal('0')
                tiempo_entrega = Decimal(str(prod['tiempo_entrega'])) if prod['tiempo_entrega'] is not None else Decimal('0')

                inventario_seguridad = Decimal('0')
                if variabilidad > 0 and tiempo_entrega > 0:
                    inventario_seguridad = self.Z_FACTOR * variabilidad * tiempo_entrega.sqrt()

                inventario_seguridad_entero = inventario_seguridad.to_integral_value()
                estado = "❌ Riesgo" if stock_actual < inventario_seguridad_entero else "✅ Seguro"

                producto_seguridad = {
                    'id_producto': prod['id_producto'],
                    'codigo': prod['codigo'],
                    'nombre': prod['nombre'],
                    'stock_actual': stock_actual,
                    'variabilidad_demanda': variabilidad,
                    'tiempo_entrega': tiempo_entrega,
                    'inventario_seguridad': inventario_seguridad_entero,
                    'estado': estado
                }
                productos_seguridad.append(producto_seguridad)

            # Guardar datos originales para búsqueda
            self.datos_originales = productos_seguridad

            for prod in productos_seguridad:
                valores = (
                    prod['codigo'],
                    prod['nombre'],
                    f"{prod['stock_actual']:.0f}",
                    f"{prod['variabilidad_demanda']}",
                    f"{prod['tiempo_entrega']:.0f}",
                    f"{prod['inventario_seguridad']:.0f}",
                    prod['estado']
                )
                self.tree.insert('', 'end', values=valores)

        except mysql.connector.Error as e:
            print(f"Error al ejecutar consulta de inventario de seguridad: {e}")
        finally:
            if connection:
                connection.close()

    def on_buscar_tiempo_real(self, event=None):
        """Realiza búsqueda en tiempo real mientras se escribe en el campo."""
        termino_busqueda = self.entry_busqueda.get().strip().lower()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Si no hay término de búsqueda, mostrar todos los datos
        if not termino_busqueda:
            datos_filtrados = self.datos_originales
        else:
            # Filtrar datos que coincidan con el término de búsqueda
            datos_filtrados = []
            for producto in self.datos_originales:
                # Buscar en código y nombre
                if (termino_busqueda in str(producto['codigo']).lower() or
                    termino_busqueda in str(producto['nombre']).lower()):
                    datos_filtrados.append(producto)
        
        # Insertar datos filtrados en la tabla
        for prod in datos_filtrados:
            valores = (
                prod['codigo'],
                prod['nombre'],
                f"{prod['stock_actual']:.0f}",
                f"{prod['variabilidad_demanda']}",
                f"{prod['tiempo_entrega']:.0f}",
                f"{prod['inventario_seguridad']:.0f}",
                prod['estado']
            )
            self.tree.insert('', 'end', values=valores)

