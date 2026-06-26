import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk  # Importación de la librería moderna
from db_config import get_connection
import mysql.connector
import math
from decimal import Decimal, getcontext
from datetime import datetime

# Configurar precisión decimal para coincidir con SQL DECIMAL(10,2)
getcontext().prec = 28

class EvaluarInventariosFrame(ctk.CTkFrame):  # Ahora hereda de CTkFrame
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
        self.crear_tabla_metricas()
        self.cargar_metricas()

    def crear_panel_titulo(self):
        """Crea el encabezado estilizado con esquinas redondeadas."""
        self.panel_titulo = ctk.CTkFrame(
            self, 
            fg_color=self.color_primario, 
            corner_radius=12
        )
        self.panel_titulo.pack(fill="x", padx=20, pady=(20, 10))
        
        titulo = ctk.CTkLabel(
            self.panel_titulo,
            text="Evaluación de Inventarios",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        titulo.pack(pady=(12, 2))
        
        subtitulo = ctk.CTkLabel(
            self.panel_titulo,
            text="Resultados analíticos de modelos cuantitativos y clasificación ABC",
            font=("Segoe UI", 11, "italic"),
            text_color="#94A3B8"
        )
        subtitulo.pack(pady=(0, 12))

    def crear_panel_busqueda(self):
        """Crea la sección de filtros dentro de una tarjeta limpia."""
        self.tarjeta_busqueda = ctk.CTkFrame(
            self, 
            fg_color=self.color_tarjetas, 
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.tarjeta_busqueda.pack(fill="x", padx=20, pady=10)

        lbl_buscar = ctk.CTkLabel(
            self.tarjeta_busqueda,
            text="Buscar Producto:",
            font=("Segoe UI", 12, "bold"),
            text_color=self.color_texto
        )
        lbl_buscar.pack(side=tk.LEFT, padx=(15, 10), pady=12)

        self.entry_busqueda = ctk.CTkEntry(
            self.tarjeta_busqueda,
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

    def crear_tabla_metricas(self):
        """Contenedor principal estructurado para la tabla y sus métricas inferiores."""
        self.contenido_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tarjeta contenedora de la Tabla Treeview
        self.tarjeta_tabla = ctk.CTkFrame(
            self.contenido_frame, 
            fg_color=self.color_tarjetas,
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.tarjeta_tabla.pack(fill="both", expand=True, pady=(0, 10))
        
        # Contenedor interno clásico para empaquetado seguro de Tkinter
        frame_interno_tabla = tk.Frame(self.tarjeta_tabla, bg=self.color_tarjetas)
        frame_interno_tabla.pack(fill="both", expand=True, padx=12, pady=12)

        # Configuración Estilo ttk
        style = ttk.Style()
        style.configure("Treeview.Heading", 
                        background=self.color_primario, 
                        foreground="white", 
                        font=("Segoe UI", 10, "bold"))
        
        style.configure("Treeview", 
                        background="white", 
                        foreground="#334155", 
                        fieldbackground="white",
                        rowheight=28,
                        font=("Segoe UI", 10))
        
        style.map("Treeview", background=[('selected', '#0EA5E9')], foreground=[('selected', 'white')])

        columnas = ("Código", "Producto", "Ventas Anuales", "Porcentaje", "Porcentaje Acumulado", 
                    "EOQ", "Punto Reorden", "Costo Ordenar", "Costo Conservación", "Costo Total", "Clasificación ABC")
        
        self.tree = ttk.Treeview(frame_interno_tabla, columns=columnas, show="headings")
        
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('oddrow', background=self.color_gris_claro)
        
        anchos = {"Código": 75, "Producto": 170, "Ventas Anuales": 120, "Porcentaje": 85, "Porcentaje Acumulado": 125,
                  "EOQ": 65, "Punto Reorden": 100, "Costo Ordenar": 110, "Costo Conservación": 125, "Costo Total": 110, "Clasificación ABC": 105}
        
        for col in columnas:
            self.tree.heading(col, text=col)
            align = "w" if col == "Producto" else "center"
            self.tree.column(col, width=anchos.get(col, 100), anchor=align)

        v_scrollbar = ttk.Scrollbar(frame_interno_tabla, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(frame_interno_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        frame_interno_tabla.grid_rowconfigure(0, weight=1)
        frame_interno_tabla.grid_columnconfigure(0, weight=1)

        # --- PANEL DE INDICADORES GLOBALES (MODERNIZADO COMO TARJETA) ---
        self.tarjeta_indicadores = ctk.CTkFrame(
            self.contenido_frame, 
            fg_color=self.color_tarjetas,
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.tarjeta_indicadores.pack(fill="x", pady=(0, 10))

        # Grid interno para distribuir los 4 KPIs equilibradamente
        self.tarjeta_indicadores.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_costo_ordenar = ctk.CTkLabel(self.tarjeta_indicadores, text="Co Anual: --", font=("Segoe UI", 12, "bold"), text_color="#0F172A")
        self.lbl_costo_ordenar.grid(row=0, column=0, pady=15)

        self.lbl_costo_conservacion = ctk.CTkLabel(self.tarjeta_indicadores, text="Ch Anual: --", font=("Segoe UI", 12, "bold"), text_color="#0F172A")
        self.lbl_costo_conservacion.grid(row=0, column=1, pady=15)

        self.lbl_costo_total_global = ctk.CTkLabel(self.tarjeta_indicadores, text="Costo Total: --", font=("Segoe UI", 12, "bold"), text_color="#10B981")
        self.lbl_costo_total_global.grid(row=0, column=2, pady=15)

        self.lbl_ventas_anuales = ctk.CTkLabel(self.tarjeta_indicadores, text="Ventas Anuales: --", font=("Segoe UI", 12, "bold"), text_color=self.color_primario)
        self.lbl_ventas_anuales.grid(row=0, column=3, pady=15)
        
        # --- PANEL INFERIOR DE ACCIONES ---
        self.frame_botones = ctk.CTkFrame(self.contenido_frame, fg_color="transparent")
        self.frame_botones.pack(fill="x")
        
        self.btn_guardar = ctk.CTkButton(
            self.frame_botones, 
            text="Guardar Resultados Módulos", 
            font=("Segoe UI", 12, "bold"),
            fg_color=self.color_primario,
            hover_color="#1E3A5F",
            height=36,
            corner_radius=8,
            command=self.guardar_resultados
        )
        self.btn_guardar.pack(side="right", pady=5)

    def cargar_metricas(self):
        connection = get_connection()
        if connection is None:
            return

        try:
            cursor = connection.cursor(dictionary=True)
            query_productos = """
                SELECT p.id_producto, p.codigo, p.nombre, p.costo_unitario,
                       par.demanda_anual, par.costo_pedido, par.costo_mantenimiento,
                       par.tiempo_entrega, par.variabilidad_demanda
                FROM Productos p
                LEFT JOIN Parametros par ON p.id_producto = par.id_producto
                ORDER BY p.codigo
            """
            cursor.execute(query_productos)
            productos = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            productos_calculados = []
            ventas_anuales_totales = 0
            
            for prod in productos:
                if prod['demanda_anual'] and prod['costo_unitario']:
                    ventas_anuales = Decimal(str(prod['demanda_anual'])) * Decimal(str(prod['costo_unitario']))
                    prod['ventas_anuales'] = ventas_anuales
                    ventas_anuales_totales += ventas_anuales
                else:
                    prod['ventas_anuales'] = Decimal('0')
            
            porcentaje_acumulado = 0
            
            for prod in productos:
                if prod['demanda_anual'] and prod['costo_unitario'] and prod['costo_pedido'] and prod['costo_mantenimiento']:
                    ventas_anuales = prod['ventas_anuales']
                    porcentaje = (ventas_anuales / ventas_anuales_totales * Decimal('100')) if ventas_anuales_totales > 0 else Decimal('0')
                    porcentaje_acumulado += porcentaje
                    
                    demanda_anual = Decimal(str(prod['demanda_anual']))
                    costo_pedido = Decimal(str(prod['costo_pedido']))
                    costo_mantenimiento = Decimal(str(prod['costo_mantenimiento']))
                    
                    eoq_calc = (Decimal('2') * demanda_anual * costo_pedido / costo_mantenimiento)
                    eoq = eoq_calc.sqrt()
                    
                    costo_anual_ordenar = (demanda_anual / eoq) * costo_pedido
                    costo_anual_conservacion = (eoq / Decimal('2')) * costo_mantenimiento
                    costo_total = costo_anual_ordenar + costo_anual_conservacion
                    
                    punto_reorden = Decimal('0')
                    inventario_seguridad = Decimal('0')
                    
                    if prod['tiempo_entrega']:
                        demanda_diaria = demanda_anual / Decimal('365')
                        tiempo_entrega = Decimal(str(prod['tiempo_entrega']))
                        punto_reorden = demanda_diaria * tiempo_entrega + inventario_seguridad
                    
                    if porcentaje_acumulado <= 80:
                        clasificacion_abc = 'A'
                    elif porcentaje_acumulado <= 95:
                        clasificacion_abc = 'B'
                    else:
                        clasificacion_abc = 'C'
                    
                    producto_calculado = {
                        'id_producto': prod['id_producto'], 'codigo': prod['codigo'], 'nombre': prod['nombre'],
                        'ventas_anuales': ventas_anuales, 'porcentaje': porcentaje, 'porcentaje_acumulado': porcentaje_acumulado,
                        'eoq': eoq, 'punto_reorden': punto_reorden, 'costo_anual_ordenar': costo_anual_ordenar,
                        'costo_anual_conservacion': costo_anual_conservacion, 'costo_total': costo_total, 'clasificacion_abc': clasificacion_abc
                    }
                    productos_calculados.append(producto_calculado)
                else:
                    producto_calculado = {
                        'id_producto': prod['id_producto'], 'codigo': prod['codigo'], 'nombre': prod['nombre'],
                        'ventas_anuales': Decimal('0'), 'porcentaje': Decimal('0'), 'porcentaje_acumulado': Decimal('0'),
                        'eoq': Decimal('0'), 'punto_reorden': Decimal('0'), 'costo_anual_ordenar': Decimal('0'),
                        'costo_anual_conservacion': Decimal('0'), 'costo_total': Decimal('0'), 'clasificacion_abc': 'N/A'
                    }
                    productos_calculados.append(producto_calculado)

            self.datos_originales = productos_calculados

            for i, prod in enumerate(productos_calculados):
                valores = (
                    prod['codigo'], prod['nombre'], f"₡{prod['ventas_anuales']:.2f}",
                    f"{prod['porcentaje']:.2f}%", f"{prod['porcentaje_acumulado']:.2f}%",
                    f"{prod['eoq']:.0f}", f"{prod['punto_reorden']:.0f}",
                    f"₡{prod['costo_anual_ordenar']:.2f}", f"₡{prod['costo_anual_conservacion']:.2f}",
                    f"₡{prod['costo_total']:.2f}", prod['clasificacion_abc']
                )
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=valores, tags=(tag,))

            productos_con_calculos = [p for p in productos_calculados if p['eoq'] > 0]
            
            if productos_con_calculos:
                costo_ordenar_total = sum(p['costo_anual_ordenar'] for p in productos_con_calculos)
                costo_conservacion_total = sum(p['costo_anual_conservacion'] for p in productos_con_calculos)
                costo_total_suma = sum(p['costo_total'] for p in productos_con_calculos)
            else:
                costo_ordenar_total = costo_conservacion_total = costo_total_suma = 0

            # Actualizar los objetos CTkLabel de forma nativa
            self.lbl_costo_ordenar.configure(text=f"Co Anual: ₡{costo_ordenar_total:,.2f}")
            self.lbl_costo_conservacion.configure(text=f"Ch Anual: ₡{costo_conservacion_total:,.2f}")
            self.lbl_costo_total_global.configure(text=f"Costo Total: ₡{costo_total_suma:,.2f}")
            self.lbl_ventas_anuales.configure(text=f"Ventas Anuales: ₡{ventas_anuales_totales:,.2f}")
            
            self.resultados_calculados = productos_calculados

        except mysql.connector.Error as e:
            print(f"Error al ejecutar consultas: {e}")
        finally:
            if connection:
                connection.close()

    def guardar_resultados(self):
        if not hasattr(self, 'resultados_calculados'):
            messagebox.showwarning("Advertencia", "No hay resultados calculados para guardar.")
            return
        
        connection = get_connection()
        if connection is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return
        
        try:
            cursor = connection.cursor()
            fecha_ejecucion = datetime.now().replace(microsecond=0)
            
            for resultado in self.resultados_calculados:
                query_insert = """
                    INSERT INTO Resultados_Modelos 
                    (id_producto, EOQ, PRO, inventario_seguridad, ventas_anuales, porcentaje, porcentaje_acumulado,
                     costo_anual_ordenar, costo_anual_conservacion, costo_total, punto_reorden, clasificacion_ABC, fecha_calculo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                Z = Decimal('1.65')
                inventario_seguridad = Decimal('0')
                
                query_params = """
                    SELECT variabilidad_demanda, tiempo_entrega FROM Parametros WHERE id_producto = %s
                """
                cursor.execute(query_params, (resultado['id_producto'],))
                params = cursor.fetchone()
                
                if params and params[0] and params[1]:
                    variabilidad_demanda = Decimal(str(params[0]))
                    tiempo_entrega = Decimal(str(params[1]))
                    inventario_seguridad = Z * variabilidad_demanda * (tiempo_entrega.sqrt())
                
                values = (
                    resultado['id_producto'],
                    int(resultado['eoq']) if resultado['eoq'] > 0 else 0,
                    int(resultado['punto_reorden']) if resultado['punto_reorden'] > 0 else 0,
                    int(inventario_seguridad) if inventario_seguridad > 0 else 0,
                    float(resultado['ventas_anuales']), float(resultado['porcentaje']), float(resultado['porcentaje_acumulado']),
                    float(resultado['costo_anual_ordenar']), float(resultado['costo_anual_conservacion']), float(resultado['costo_total']),
                    int(resultado['punto_reorden']) if resultado['punto_reorden'] > 0 else 0,
                    resultado['clasificacion_abc'] if resultado['clasificacion_abc'] != 'N/A' else None,
                    fecha_ejecucion
                )
                cursor.execute(query_insert, values)
            
            connection.commit()
            messagebox.showinfo("Éxito", f"Se guardaron {len(self.resultados_calculados)} resultados en la base de datos.")
            
        except mysql.connector.Error as e:
            connection.rollback()
            messagebox.showerror("Error", f"Error al guardar resultados: {e}")
        finally:
            if connection:
                connection.close()

    def on_buscar_tiempo_real(self, event=None):
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
                prod['codigo'], prod['nombre'], f"₡{prod['ventas_anuales']:.2f}",
                f"{prod['porcentaje']:.2f}%", f"{prod['porcentaje_acumulado']:.2f}%",
                f"{prod['eoq']:.0f}", f"{prod['punto_reorden']:.0f}",
                f"₡{prod['costo_anual_ordenar']:.2f}", f"₡{prod['costo_anual_conservacion']:.2f}",
                f"₡{prod['costo_total']:.2f}", prod['clasificacion_abc']
            )
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=valores, tags=(tag,))