import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_connection
import mysql.connector
import math
from decimal import Decimal, getcontext

# Configurar precisión decimal para coincidir con SQL DECIMAL(10,2)
getcontext().prec = 28


class EvaluarInventariosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.datos_originales = []
        self.crear_panel_titulo()
        self.crear_panel_busqueda()
        self.crear_tabla_metricas()
        self.cargar_metricas()

    def crear_panel_titulo(self):
        # Panel superior con fondo azul elegante
        self.panel_titulo = tk.Frame(self, bg="#0A1F44")
        self.panel_titulo.pack(fill="x", padx=10, pady=10)
        
        # Título principal
        titulo = tk.Label(
            self.panel_titulo,
            text="Evaluación de Inventarios",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#0A1F44"
        )
        titulo.pack(pady=(10, 5))
        
        # Subtítulo
        subtitulo = tk.Label(
            self.panel_titulo,
            text="Resultados de modelos cuantitativos",
            font=("Segoe UI", 10, "italic"),
            fg="#555",
            bg="#0A1F44"
        )
        subtitulo.pack(pady=(0, 10))
        
        # Línea separadora
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

    def crear_tabla_metricas(self):
        # Contenedor principal para el contenido debajo del título
        self.contenido_frame = tk.Frame(self)
        self.contenido_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.contenido_frame.grid_rowconfigure(0, weight=1)
        self.contenido_frame.grid_columnconfigure(0, weight=1)

        # Frame para la tabla
        self.frame_tabla = tk.Frame(self.contenido_frame)
        self.frame_tabla.grid(row=0, column=0, sticky="nsew")

        # Estilo para el Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", 
                       background="#0A1F44", 
                       foreground="white", 
                       font=("Segoe UI", 10, "bold"))
        
        # Estilo para filas alternadas
        style.configure("Treeview", 
                       background="white", 
                       foreground="black", 
                       fieldbackground="white",
                       rowheight=25)
        
        style.map("Treeview", 
                 background=[('selected', '#347083')])

        # Treeview con columnas actualizadas
        columnas = ("Código", "Producto", "Ventas Anuales", "Porcentaje", "Porcentaje Acumulado", 
                   "EOQ", "Punto Reorden", "Costo Ordenar", "Costo Conservación", "Costo Total", "Clasificación ABC")
        self.tree = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", height=15)
        
        # Configurar tags para filas alternadas (después de crear el tree)
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('oddrow', background='#F7F7F7')
        
        # Configurar encabezados y anchos
        anchos = {"Código": 80, "Producto": 180, "Ventas Anuales": 110, "Porcentaje": 100, "Porcentaje Acumulado": 110,
                 "EOQ": 70, "Punto Reorden": 100, "Costo Ordenar": 100, "Costo Conservación": 120, "Costo Total": 90, "Clasificación ABC": 90}
        
        for col in columnas:
            self.tree.heading(col, text=col)
            # Alinear texto a la izquierda para producto, centrado para otros
            if col == "Producto":
                align = "w"
            else:
                align = "center"
            self.tree.column(col, width=anchos.get(col, 100), anchor=align)

        # Scrollbar vertical y horizontal
        v_scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Empaquetar widgets
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configurar grid weights
        self.frame_tabla.grid_rowconfigure(0, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        # Frame para indicadores globales
        self.frame_indicadores = tk.Frame(self.contenido_frame, bg="#F7F7F7")
        self.frame_indicadores.grid(row=1, column=0, sticky="ew", padx=0, pady=(10, 10))

        self.lbl_costo_ordenar = tk.Label(self.frame_indicadores, text="Co Anual: Cargando...", 
                                       font=("Segoe UI", 10, "bold"), fg="#0A1F44", bg="#F7F7F7")
        self.lbl_costo_ordenar.pack(side="left", padx=20)

        self.lbl_costo_conservacion = tk.Label(self.frame_indicadores, text="Ch Anual: Cargando...", 
                                           font=("Segoe UI", 10, "bold"), fg="#0A1F44", bg="#F7F7F7")
        self.lbl_costo_conservacion.pack(side="left", padx=20)

        self.lbl_costo_total_global = tk.Label(self.frame_indicadores, text="Costo Total: Cargando...", 
                                           font=("Segoe UI", 10, "bold"), fg="#0A1F44", bg="#F7F7F7")
        self.lbl_costo_total_global.pack(side="left", padx=20)

        self.lbl_ventas_anuales = tk.Label(self.frame_indicadores, text="Ventas Anuales: Cargando...",
                                           font=("Segoe UI", 10, "bold"), fg="#0A1F44", bg="#F7F7F7")
        self.lbl_ventas_anuales.pack(side="left", padx=20)
        
        # Frame para botón guardar
        self.frame_botones = tk.Frame(self.contenido_frame, bg="#F7F7F7")
        self.frame_botones.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 10))
        
        # Estilo personalizado para el botón. Si el tema no admite Accent.TButton, se usa el estilo por defecto.
        style = ttk.Style()
        button_style = "Accent.TButton"
        try:
            style.configure(button_style, 
                           background="#0A1F44", 
                           foreground="white", 
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           focuscolor='none')
            style.map(button_style, 
                     background=[('active', '#1E3A5F'), ('pressed', '#0A1F44')])
        except tk.TclError:
            button_style = "TButton"

        self.btn_guardar = ttk.Button(self.frame_botones, text="Guardar resultados", 
                                      command=self.guardar_resultados, style=button_style)
        self.btn_guardar.pack(side="right", padx=20, pady=10)

    def cargar_metricas(self):
        connection = get_connection()
        if connection is None:
            print("Error: No se pudo conectar a la base de datos.")
            return

        try:
            cursor = connection.cursor(dictionary=True)

            # Query para obtener datos de productos y parámetros
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

            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Calcular métricas para cada producto
            productos_calculados = []
            ventas_anuales_totales = 0
            
            # Primero calcular ventas anuales para porcentajes
            for prod in productos:
                if prod['demanda_anual'] and prod['costo_unitario']:
                    ventas_anuales = Decimal(str(prod['demanda_anual'])) * Decimal(str(prod['costo_unitario']))
                    prod['ventas_anuales'] = ventas_anuales
                    ventas_anuales_totales += ventas_anuales
                else:
                    prod['ventas_anuales'] = Decimal('0')
            
            # Calcular porcentajes y clasificación ABC
            porcentaje_acumulado = 0
            # Los productos ya vienen ordenados por código desde la consulta SQL
            
            for prod in productos:
                if prod['demanda_anual'] and prod['costo_unitario'] and prod['costo_pedido'] and prod['costo_mantenimiento']:
                    # Ventas anuales y porcentajes
                    ventas_anuales = prod['ventas_anuales']
                    porcentaje = (ventas_anuales / ventas_anuales_totales * Decimal('100')) if ventas_anuales_totales > 0 else Decimal('0')
                    porcentaje_acumulado += porcentaje
                    
                    # EOQ - cálculo con Decimal
                    demanda_anual = Decimal(str(prod['demanda_anual']))
                    costo_pedido = Decimal(str(prod['costo_pedido']))
                    costo_mantenimiento = Decimal(str(prod['costo_mantenimiento']))
                    
                    # EOQ = sqrt(2 * D * Co / Ch)
                    eoq_calc = (Decimal('2') * demanda_anual * costo_pedido / costo_mantenimiento)
                    eoq = eoq_calc.sqrt()
                    
                    # Costos con precisión Decimal
                    costo_anual_ordenar = (demanda_anual / eoq) * costo_pedido
                    costo_anual_conservacion = (eoq / Decimal('2')) * costo_mantenimiento
                    costo_total = costo_anual_ordenar + costo_anual_conservacion
                    
                    # Punto de Reorden (PRO) - cálculo simplificado
                    # PRO = (demanda_anual / 365) * tiempo_entrega + Inventario Seguridad
                    # El Inventario de Seguridad se delega a módulo aparte
                    punto_reorden = Decimal('0')
                    inventario_seguridad = Decimal('0')  # Se calculará en módulo separado
                    
                    if prod['tiempo_entrega']:
                        demanda_diaria = demanda_anual / Decimal('365')
                        tiempo_entrega = Decimal(str(prod['tiempo_entrega']))
                        punto_reorden = demanda_diaria * tiempo_entrega + inventario_seguridad
                    
                    # Clasificación ABC
                    if porcentaje_acumulado <= 80:
                        clasificacion_abc = 'A'
                    elif porcentaje_acumulado <= 95:
                        clasificacion_abc = 'B'
                    else:
                        clasificacion_abc = 'C'
                    
                    # Guardar producto con cálculos
                    producto_calculado = {
                        'id_producto': prod['id_producto'],
                        'codigo': prod['codigo'],
                        'nombre': prod['nombre'],
                        'ventas_anuales': ventas_anuales,
                        'porcentaje': porcentaje,
                        'porcentaje_acumulado': porcentaje_acumulado,
                        'eoq': eoq,
                        'punto_reorden': punto_reorden,
                        'costo_anual_ordenar': costo_anual_ordenar,
                        'costo_anual_conservacion': costo_anual_conservacion,
                        'costo_total': costo_total,
                        'clasificacion_abc': clasificacion_abc
                    }
                    productos_calculados.append(producto_calculado)
                else:
                    # Producto sin parámetros completos
                    producto_calculado = {
                        'id_producto': prod['id_producto'],
                        'codigo': prod['codigo'],
                        'nombre': prod['nombre'],
                        'ventas_anuales': Decimal('0'),
                        'porcentaje': Decimal('0'),
                        'porcentaje_acumulado': Decimal('0'),
                        'eoq': Decimal('0'),
                        'punto_reorden': Decimal('0'),
                        'costo_anual_ordenar': Decimal('0'),
                        'costo_anual_conservacion': Decimal('0'),
                        'costo_total': Decimal('0'),
                        'clasificacion_abc': 'N/A'
                    }
                    productos_calculados.append(producto_calculado)

            # Guardar datos originales para búsqueda
            self.datos_originales = productos_calculados

            # Insertar en tabla
            for i, prod in enumerate(productos_calculados):
                valores = (
                    prod['codigo'],
                    prod['nombre'],
                    f"₡{prod['ventas_anuales']:.2f}",
                    f"{prod['porcentaje']:.2f}%",
                    f"{prod['porcentaje_acumulado']:.2f}%",
                    f"{prod['eoq']:.0f}",
                    f"{prod['punto_reorden']:.0f}",
                    f"₡{prod['costo_anual_ordenar']:.2f}",
                    f"₡{prod['costo_anual_conservacion']:.2f}",
                    f"₡{prod['costo_total']:.2f}",
                    prod['clasificacion_abc']
                )
                # Alternar colores de filas
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=valores, tags=(tag,))

            # Calcular indicadores globales
            productos_con_calculos = [p for p in productos_calculados if p['eoq'] > 0]
            
            if productos_con_calculos:
                costo_ordenar_total = sum(p['costo_anual_ordenar'] for p in productos_con_calculos)
                costo_conservacion_total = sum(p['costo_anual_conservacion'] for p in productos_con_calculos)
                costo_total_suma = sum(p['costo_total'] for p in productos_con_calculos)
            else:
                costo_ordenar_total = 0
                costo_conservacion_total = 0
                costo_total_suma = 0

            # Actualizar labels
            self.lbl_costo_ordenar.config(text=f"Co Anual: ₡{costo_ordenar_total:,.2f}")
            self.lbl_costo_conservacion.config(text=f"Ch Anual: ₡{costo_conservacion_total:,.2f}")
            self.lbl_costo_total_global.config(text=f"Costo Total: ₡{costo_total_suma:,.2f}")
            self.lbl_ventas_anuales.config(text=f"Ventas Anuales: ₡{ventas_anuales_totales:,.2f}")
            
            # Guardar resultados para posible guardado posterior
            self.resultados_calculados = productos_calculados

        except mysql.connector.Error as e:
            print(f"Error al ejecutar consultas: {e}")
        finally:
            if connection:
                connection.close()

    def guardar_resultados(self):
        """Guarda los resultados calculados en la tabla Resultados_Modelos"""
        if not hasattr(self, 'resultados_calculados'):
            messagebox.showwarning("Advertencia", "No hay resultados calculados para guardar.")
            return
        
        connection = get_connection()
        if connection is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return
        
        try:
            cursor = connection.cursor()
            
            # Insertar cada producto calculado en Resultados_Modelos
            for resultado in self.resultados_calculados:
                query_insert = """
                    INSERT INTO Resultados_Modelos 
                    (id_producto, EOQ, PRO, inventario_seguridad, ventas_anuales, porcentaje, porcentaje_acumulado,
                     costo_anual_ordenar, costo_anual_conservacion, costo_total, punto_reorden, clasificacion_ABC, fecha_calculo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                
                # Calcular inventario de seguridad para guardar
                Z = Decimal('1.65')  # Factor Z para 95% nivel de servicio
                inventario_seguridad = Decimal('0')
                
                # Obtener parámetros para calcular inventario de seguridad
                query_params = """
                    SELECT variabilidad_demanda, tiempo_entrega 
                    FROM Parametros 
                    WHERE id_producto = %s
                """
                cursor.execute(query_params, (resultado['id_producto'],))
                params = cursor.fetchone()
                
                if params and params[0] and params[1]:
                    # Convertir a Decimal para cálculo de inventario de seguridad
                    variabilidad_demanda = Decimal(str(params[0]))
                    tiempo_entrega = Decimal(str(params[1]))
                    inventario_seguridad = Z * variabilidad_demanda * (tiempo_entrega.sqrt())
                
                values = (
                    resultado['id_producto'],
                    int(resultado['eoq']) if resultado['eoq'] > 0 else 0,
                    int(resultado['punto_reorden']) if resultado['punto_reorden'] > 0 else 0,
                    int(inventario_seguridad) if inventario_seguridad > 0 else 0,
                    float(resultado['ventas_anuales']),
                    float(resultado['porcentaje']),
                    float(resultado['porcentaje_acumulado']),
                    float(resultado['costo_anual_ordenar']),
                    float(resultado['costo_anual_conservacion']),
                    float(resultado['costo_total']),
                    int(resultado['punto_reorden']) if resultado['punto_reorden'] > 0 else 0,
                    resultado['clasificacion_abc'] if resultado['clasificacion_abc'] != 'N/A' else None
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
        for i, prod in enumerate(datos_filtrados):
            valores = (
                prod['codigo'],
                prod['nombre'],
                f"₡{prod['ventas_anuales']:.2f}",
                f"{prod['porcentaje']:.2f}%",
                f"{prod['porcentaje_acumulado']:.2f}%",
                f"{prod['eoq']:.0f}",
                f"{prod['punto_reorden']:.0f}",
                f"₡{prod['costo_anual_ordenar']:.2f}",
                f"₡{prod['costo_anual_conservacion']:.2f}",
                f"₡{prod['costo_total']:.2f}",
                prod['clasificacion_abc']
            )
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=valores, tags=(tag,))