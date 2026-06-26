import tkinter as tk
from tkinter import ttk
import customtkinter as ctk  # Importación de la librería moderna
from db_config import get_connection
import mysql.connector
from decimal import Decimal, getcontext

# Configurar precisión decimal para los cálculos de inventario de seguridad
getcontext().prec = 28


class InventarioSeguridadFrame(ctk.CTkFrame):  # Ahora hereda de CTkFrame
    Z_FACTOR = Decimal('1.65')

    def __init__(self, parent):
        # Inicializar con el fondo del panel derecho
        super().__init__(parent, fg_color="#F8FAFC")
        self.datos_originales = []
        
        # Paleta de colores consistente
        self.color_primario = "#0A1F44"   # Azul elegante
        self.color_tarjetas = "#FFFFFF"   # Fondos de contenedores
        self.color_gris_claro = "#F1F5F9" # Filas alternas de tabla
        self.color_texto = "#1E293B"      # Texto principal

        self.crear_panel_titulo()
        self.crear_panel_busqueda()
        self.crear_tabla_seguridad()
        self.cargar_seguridad()

    def crear_panel_titulo(self):
        """Crea el encabezado estilizado con esquinas redondeadas."""
        panel_titulo = ctk.CTkFrame(
            self, 
            fg_color=self.color_primario, 
            corner_radius=12
        )
        panel_titulo.pack(fill="x", padx=20, pady=(20, 10))

        titulo = ctk.CTkLabel(
            panel_titulo,
            text="Inventario de Seguridad",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        titulo.pack(pady=(12, 2))

        subtitulo = ctk.CTkLabel(
            panel_titulo,
            text="Cálculo de inventario de seguridad y estado de stock crítico",
            font=("Segoe UI", 11, "italic"),
            text_color="#94A3B8"
        )
        subtitulo.pack(pady=(0, 12))

    def crear_panel_busqueda(self):
        """Crea la sección de filtros dentro de una tarjeta limpia."""
        tarjeta_busqueda = ctk.CTkFrame(
            self, 
            fg_color=self.color_tarjetas, 
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        tarjeta_busqueda.pack(fill="x", padx=20, pady=10)

        lbl_buscar = ctk.CTkLabel(
            tarjeta_busqueda,
            text="Buscar Producto:",
            font=("Segoe UI", 12, "bold"),
            text_color=self.color_texto
        )
        lbl_buscar.pack(side=tk.LEFT, padx=(15, 10), pady=12)

        self.entry_busqueda = ctk.CTkEntry(
            tarjeta_busqueda,
            placeholder_text="Escribe el código o nombre para filtrar en tiempo real...",
            font=("Segoe UI", 12),
            height=32,
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            text_color=self.color_texto,
            placeholder_text_color="#94A3B8"
        )
        self.entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15), pady=12)
        self.entry_busqueda.bind('<KeyRelease>', self.on_buscar_tiempo_real)

    def crear_tabla_seguridad(self):
        """Contenedor principal estructurado para la tabla Treeview."""
        self.contenido_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tarjeta contenedora de la Tabla
        tarjeta_tabla = ctk.CTkFrame(
            self.contenido_frame, 
            fg_color=self.color_tarjetas,
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        tarjeta_tabla.pack(fill="both", expand=True)
        
        # Contenedor interno para empaquetado seguro de la tabla clásica
        frame_interno_tabla = tk.Frame(tarjeta_tabla, bg=self.color_tarjetas)
        frame_interno_tabla.pack(fill="both", expand=True, padx=12, pady=12)

        # Configuración Estilo de la tabla clásica ttk para que combine
        style = ttk.Style()
        style.configure("Seguridad.Treeview.Heading",
                        background=self.color_primario,
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        
        style.configure("Seguridad.Treeview",
                        background="white",
                        foreground="#334155",
                        fieldbackground="white",
                        rowheight=28,
                        font=("Segoe UI", 10))
        
        style.map("Seguridad.Treeview",
                  background=[('selected', '#0EA5E9')],
                  foreground=[('selected', 'white')])

        columnas = (
            "Código", "Producto", "Stock Actual", "Variabilidad de Demanda",
            "Días de Entrega", "Inventario de Seguridad", "Estado"
        )
        self.tree = ttk.Treeview(frame_interno_tabla,
                                 columns=columnas,
                                 show="headings",
                                 style="Seguridad.Treeview")

        # Configurar filas alternas
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('oddrow', background=self.color_gris_claro)

        anchos = {
            "Código": 90,
            "Producto": 240,
            "Stock Actual": 110,
            "Variabilidad de Demanda": 170,
            "Días de Entrega": 120,
            "Inventario de Seguridad": 170,
            "Estado": 120
        }

        for col in columnas:
            self.tree.heading(col, text=col)
            anchor = "w" if col == "Producto" else "center"
            self.tree.column(col, width=anchos.get(col, 100), anchor=anchor)

        v_scrollbar = ttk.Scrollbar(frame_interno_tabla, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(frame_interno_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        frame_interno_tabla.grid_rowconfigure(0, weight=1)
        frame_interno_tabla.grid_columnconfigure(0, weight=1)

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

            self.datos_originales = productos_seguridad

            for i, prod in enumerate(productos_seguridad):
                valores = (
                    prod['codigo'],
                    prod['nombre'],
                    f"{prod['stock_actual']:.0f}",
                    f"{prod['variabilidad_demanda']}",
                    f"{prod['tiempo_entrega']:.0f}",
                    f"{prod['inventario_seguridad']:.0f}",
                    prod['estado']
                )
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert('', 'end', values=valores, tags=(tag,))

        except mysql.connector.Error as e:
            print(f"Error al ejecutar consulta de inventario de seguridad: {e}")
        finally:
            if connection:
                connection.close()

    def on_buscar_tiempo_real(self, event=None):
        """Realiza búsqueda en tiempo real mientras se escribe en el campo."""
        termino_busqueda = self.entry_busqueda.get().strip().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not termino_busqueda:
            datos_filtrados = self.datos_originales
        else:
            datos_filtrados = []
            for producto in self.datos_originales:
                if (termino_busqueda in str(producto['codigo']).lower() or
                    termino_busqueda in str(producto['nombre']).lower()):
                    datos_filtrados.append(producto)
        
        for i, prod in enumerate(datos_filtrados):
            valores = (
                prod['codigo'],
                prod['nombre'],
                f"{prod['stock_actual']:.0f}",
                f"{prod['variabilidad_demanda']}",
                f"{prod['tiempo_entrega']:.0f}",
                f"{prod['inventario_seguridad']:.0f}",
                prod['estado']
            )
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end', values=valores, tags=(tag,))