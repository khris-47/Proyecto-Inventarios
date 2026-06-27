import os
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk  # Importamos la librería moderna
from db_config import get_connection
import uuid

# Configuración estética global de CustomTkinter
ctk.set_appearance_mode("Light")  # Forzamos modo claro consistente con tu diseño
ctk.set_default_color_theme("blue")

class GestionInventariosFrame(ctk.CTkFrame):
    """
    Frame moderno para la gestión de inventarios de la Ferretería Simkin.
    Hereda de ctk.CTkFrame con diseño redondeado y limpio.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Inicializa el frame de gestión de inventarios.
        """
        # Inicializamos el frame base con el fondo gris claro de la imagen objetivo
        super().__init__(parent, fg_color="#EDF2F7", corner_radius=0, *args, **kwargs)

        # Definir paleta de colores corporativa
        self.color_fondo_app = "#EDF2F7"  # Gris claro para el fondo general
        self.color_tarjetas = "#FFFFFF"   # Blanco para los contenedores redondeados
        self.color_panel = "#0A1F44"      # Azul marino principal
        self.color_hover = "#123D6B"      # Azul con brillo para acciones
        self.color_gris_claro = "#F8FAFC" # Filas alternadas suaves

        # Variable para almacenar datos originales para búsqueda
        self.datos_originales = []
        self.editar_producto_id = None

        # Aplicar estilos para el Treeview nativo que vive dentro del entorno moderno
        self.aplicar_estilos_treeview()

        # Crear la interfaz moderna
        self.crear_panel_acciones()
        self.crear_tabla_inventarios()

        # Cargar datos desde la base de datos
        self.cargar_datos()

    def aplicar_estilos_treeview(self):
        """Define los estilos personalizados exclusivamente para el Treeview."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Estilo para la tabla Treeview (más limpia y espaciada)
        self.style.configure(
            'Treeview',
            background=self.color_tarjetas,
            foreground="#1E293B",
            font=('Segoe UI', 10),
            rowheight=32,  # Mayor altura por fila para dar aire al diseño
            fieldbackground=self.color_tarjetas,
            borderwidth=0
        )

        # Estilo para encabezados de tabla (Azul marino idéntico al diseño)
        self.style.configure(
            'Treeview.Heading',
            background=self.color_panel,
            foreground='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            borderwidth=0,
            padding=(10, 8)
        )

        # Comportamiento al seleccionar y filas alternas
        self.style.map('Treeview',
            background=[('selected', self.color_hover)],
            foreground=[('selected', 'white')])

    def crear_panel_acciones(self):
        """Crea la sección superior con botones modernos y barra de búsqueda estilizada."""
        # Tarjeta blanca redondeada para las acciones superiores
        self.tarjeta_acciones = ctk.CTkFrame(
            self, 
            fg_color=self.color_tarjetas, 
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.tarjeta_acciones.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Fila 1: Botón "Agregar producto" con esquinas curvas
        frame_boton = ctk.CTkFrame(self.tarjeta_acciones, fg_color="transparent")
        frame_boton.pack(fill=tk.X, padx=20, pady=(15, 10))

        btn_agregar = ctk.CTkButton(
            frame_boton,
            text="Agregar producto",
            fg_color=self.color_panel,
            hover_color=self.color_hover,
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            corner_radius=6,
            height=38,
            command=self.on_agregar_producto
        )
        btn_agregar.pack(side=tk.LEFT)

        # Fila 2: Barra de búsqueda refinada
        frame_busqueda = ctk.CTkFrame(self.tarjeta_acciones, fg_color="transparent")
        frame_busqueda.pack(fill=tk.X, padx=20, pady=(0, 15))

        lbl_buscar = ctk.CTkLabel(
            frame_busqueda,
            text="Buscar:",
            font=('Segoe UI', 12, 'bold'),
            text_color=self.color_panel
        )
        lbl_buscar.pack(side=tk.LEFT, padx=(0, 10))

        # Campo de entrada redondeado y elegante
        self.entry_busqueda = ctk.CTkEntry(
            frame_busqueda,
            font=('Segoe UI', 12),
            fg_color="#F1F5F9",
            text_color="#1E293B",
            placeholder_text="Escriba código, nombre, categoría o proveedor...",
            border_color="#CBD5E1",
            border_width=1,
            corner_radius=6,
            height=36
        )
        self.entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_busqueda.bind('<KeyRelease>', self.on_buscar_tiempo_real)

    def crear_tabla_inventarios(self):
        """Crea la estructura de la tabla contenida en una tarjeta redondeada limpia."""
        # Tarjeta blanca contenedora para la tabla
        self.tarjeta_tabla = ctk.CTkFrame(
            self, 
            fg_color=self.color_tarjetas, 
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.tarjeta_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Contenedor interno para empaquetar los widgets de Tkinter clásicos de forma segura
        frame_interno = tk.Frame(self.tarjeta_tabla, bg=self.color_tarjetas)
        frame_interno.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Crear Treeview con columnas
        columnas = ('codigo', 'nombre', 'categoria', 'stock', 'costo_unitario', 'proveedor', 'acciones')
        self.tabla = ttk.Treeview(
            frame_interno,
            columns=columnas,
            show='headings',
            style='Treeview'
        )

        # Configurar encabezados
        encabezados = {
            'codigo': 'Código',
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'stock': 'Stock Actual',
            'costo_unitario': 'Costo Unitario',
            'proveedor': 'Proveedor',
            'acciones': 'Acciones'
        }

        for col, texto in encabezados.items():
            self.tabla.heading(col, text=texto, anchor=tk.W)
            if col == 'codigo':
                self.tabla.column(col, width=100, anchor=tk.W)
            elif col == 'nombre':
                self.tabla.column(col, width=200, anchor=tk.W)
            elif col == 'categoria':
                self.tabla.column(col, width=150, anchor=tk.W)
            elif col == 'stock':
                self.tabla.column(col, width=90, anchor=tk.CENTER)
            elif col == 'costo_unitario':
                self.tabla.column(col, width=120, anchor=tk.E)
            elif col == 'proveedor':
                self.tabla.column(col, width=200, anchor=tk.W)
            elif col == 'acciones':
                self.tabla.column(col, width=90, anchor=tk.CENTER)

        # Scrollbar sutil y estilizada
        scrollbar = ttk.Scrollbar(frame_interno, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabla.bind('<ButtonRelease-1>', self.on_click_tabla)
        self.tabla.tag_configure('oddrow', background=self.color_gris_claro)
        self.tabla.tag_configure('evenrow', background=self.color_tarjetas)

    def cargar_datos(self):
        """Carga los datos de productos desde la base de datos MySQL sin alterar lógica."""
        try:
            connection = get_connection()
            if not connection:
                print("Error: No se pudo establecer conexión con la base de datos")
                return

            cursor = connection.cursor()
            query = "SELECT id_producto, codigo, nombre, categoria, stock_actual, costo_unitario, proveedor FROM Productos ORDER BY nombre"
            cursor.execute(query)
            productos = cursor.fetchall()
            self.datos_originales = productos

            for item in self.tabla.get_children():
                self.tabla.delete(item)

            for i, producto in enumerate(productos):
                costo_formateado = f"₡{producto[5]:,.2f}" if producto[5] else "₡0.00"
                valores = (
                    producto[1],
                    producto[2],
                    producto[3],
                    str(producto[4]),
                    costo_formateado,
                    producto[6] if producto[6] else "N/A",
                    '✏️ 🗑️'
                )
                tag = 'oddrow' if i % 2 else 'evenrow'
                self.tabla.insert('', tk.END, values=valores, tags=(tag,), iid=str(producto[0]))

            cursor.close()
            connection.close()
            print(f"Datos cargados exitosamente: {len(productos)} productos encontrados")

        except Exception as e:
            print(f"Error al cargar datos de la base de datos: {e}")
            for item in self.tabla.get_children():
                self.tabla.delete(item)

    def on_click_tabla(self, event=None):
        """Maneja el clic en la tabla para la columna de acciones."""
        item_id = self.tabla.identify_row(event.y)
        column = self.tabla.identify_column(event.x)
        if not item_id or column != '#7':
            return

        bbox = self.tabla.bbox(item_id, 'acciones')
        if not bbox:
            return

        x_relative = event.x - bbox[0]
        if x_relative < bbox[2] / 2:
            self.editar_producto(int(item_id))
            return

        if messagebox.askyesno("Eliminar producto", "¿Desea eliminar este producto? Esta acción no se puede deshacer."):
            self._delete_producto(int(item_id))

    def editar_producto(self, producto_id):
        for producto in self.datos_originales:
            if producto[0] == producto_id:
                self.on_agregar_producto(producto)
                return

    def _delete_producto(self, id_producto):
        connection = get_connection()
        if not connection:
            messagebox.showerror("Error", "No se pudo establecer conexión con la base de datos.")
            return

        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Resultados_Modelos WHERE id_producto=%s", (id_producto,))
            cursor.execute("DELETE FROM Parametros WHERE id_producto=%s", (id_producto,))
            cursor.execute("DELETE FROM Productos WHERE id_producto=%s", (id_producto,))
            connection.commit()
            self.cargar_datos()
            messagebox.showinfo("Producto eliminado", "El producto fue eliminado correctamente.")
        except Exception as e:
            if connection:
                connection.rollback()
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def on_agregar_producto(self, producto=None):
        """Abre un formulario flotante moderno usando CTkToplevel."""
        if hasattr(self, 'ventana_agregar') and self.ventana_agregar.winfo_exists():
            self.ventana_agregar.destroy()

        self.editar_producto_id = producto[0] if producto else None
        
        # Ventana flotante moderna
        self.ventana_agregar = ctk.CTkToplevel(self)
        self.ventana_agregar.title("Editar Producto" if producto else "Agregar Producto")
        self.ventana_agregar.configure(fg_color=self.color_tarjetas)
        self.ventana_agregar.geometry("460x650")
        self.ventana_agregar.transient(self)
        self.ventana_agregar.grab_set()
        self.ventana_agregar.resizable(False, False)

        # Forzar que la ventana pase al frente en algunos sistemas operativos
        self.ventana_agregar.attributes("-topmost", True)

        # Contenedor scrollable moderno para el formulario
        scroll_container = ctk.CTkScrollableFrame(
            self.ventana_agregar, 
            fg_color=self.color_tarjetas,
            corner_radius=0
        )
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tarjeta interna del formulario
        form_card = ctk.CTkFrame(scroll_container, fg_color=self.color_tarjetas, border_width=0)
        form_card.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Título decorativo superior
        titulo_label = ctk.CTkLabel(
            form_card,
            text="Editar Producto" if producto else "Agregar Producto",
            text_color=self.color_panel,
            font=('Segoe UI', 16, 'bold'),
            anchor='w'
        )
        titulo_label.pack(fill=tk.X, pady=(10, 15))

        # Registro de funciones de validación nativas
        vcmd_entero = (self.ventana_agregar.register(self._validate_int_entry), '%P')
        vcmd_decimal = (self.ventana_agregar.register(self._validate_float_entry), '%P')

        campos_producto = [
            ("Nombre del Producto", "nombre", None),
            ("Categoría", "categoria", None),
            ("Stock Actual", "stock_actual", vcmd_entero),
            ("Costo Unitario", "costo_unitario", vcmd_decimal),
            ("Proveedor", "proveedor", None),
        ]
        
        self.entradas_producto = {}
        for texto, campo, vcmd in campos_producto:
            row = ctk.CTkFrame(form_card, fg_color="transparent")
            row.pack(fill=tk.X, pady=6)

            label = ctk.CTkLabel(
                row,
                text=texto,
                text_color="#475569",
                font=('Segoe UI', 11, 'bold'),
                anchor='w'
            )
            label.pack(fill=tk.X, pady=(0, 2))

            entry = ctk.CTkEntry(
                row,
                font=('Segoe UI', 12),
                fg_color="#F8FAFC",
                border_color="#CBD5E1",
                corner_radius=6,
                height=36
            )
            entry.pack(fill=tk.X)
            self.entradas_producto[campo] = entry

        # Separador visual moderno
        separador = ctk.CTkFrame(form_card, height=2, fg_color="#E2E8F0")
        separador.pack(fill=tk.X, pady=20)

        label_parametros = ctk.CTkLabel(
            form_card,
            text="Parámetros de Inventario",
            text_color=self.color_panel,
            font=('Segoe UI', 13, 'bold'),
            anchor='w'
        )
        label_parametros.pack(fill=tk.X, pady=(0, 10))

        campos_parametros = [
            ("Demanda Anual", "demanda_anual", vcmd_entero),
            ("Costo de Pedido", "costo_pedido", vcmd_decimal),
            ("Costo de Mantenimiento", "costo_mantenimiento", vcmd_decimal),
            ("Tiempo de Entrega (días)", "tiempo_entrega", vcmd_entero),
        ]
        
        self.entradas_parametros = {}
        for texto, campo, vcmd in campos_parametros:
            row = ctk.CTkFrame(form_card, fg_color="transparent")
            row.pack(fill=tk.X, pady=6)

            label = ctk.CTkLabel(
                row,
                text=texto,
                text_color="#475569",
                font=('Segoe UI', 11, 'bold'),
                anchor='w'
            )
            label.pack(fill=tk.X, pady=(0, 2))

            entry = ctk.CTkEntry(
                row,
                font=('Segoe UI', 12),
                fg_color="#F8FAFC",
                border_color="#CBD5E1",
                corner_radius=6,
                height=36
            )
            entry.pack(fill=tk.X)
            self.entradas_parametros[campo] = entry

        # Botonera inferior estilizada
        botones_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        botones_frame.pack(fill=tk.X, pady=(25, 10))

        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#475569",
            font=('Segoe UI', 12, 'bold'),
            height=38,
            corner_radius=6,
            command=self.ventana_agregar.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=(10, 0), expand=True, fill=tk.X)

        btn_guardar = ctk.CTkButton(
            botones_frame,
            text="Guardar Cambios",
            fg_color=self.color_panel,
            hover_color=self.color_hover,
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            height=38,
            corner_radius=6,
            command=self.guardar_producto
        )
        btn_guardar.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Rellenar inputs si es edición
        if producto:
            self.entradas_producto['nombre'].insert(0, producto[2])
            self.entradas_producto['categoria'].insert(0, producto[3] or "")
            self.entradas_producto['stock_actual'].insert(0, str(producto[4]))
            self.entradas_producto['costo_unitario'].insert(0, str(producto[5] if producto[5] is not None else ""))
            self.entradas_producto['proveedor'].insert(0, producto[6] or "")

            parametros = self._load_parametros(producto[0])
            if parametros:
                self.entradas_parametros['demanda_anual'].insert(0, str(parametros[0] if parametros[0] is not None else ""))
                self.entradas_parametros['costo_pedido'].insert(0, str(parametros[1] if parametros[1] is not None else ""))
                self.entradas_parametros['costo_mantenimiento'].insert(0, str(parametros[2] if parametros[2] is not None else ""))
                self.entradas_parametros['tiempo_entrega'].insert(0, str(parametros[3] if parametros[3] is not None else ""))

    def guardar_producto(self):
        """Valida los datos del formulario y guarda el producto en la base de datos."""
        nombre = self.entradas_producto['nombre'].get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El nombre del producto es obligatorio.")
            return

        categoria = self.entradas_producto['categoria'].get().strip() or None
        proveedor = self.entradas_producto['proveedor'].get().strip() or None

        try:
            stock_actual = int(self.entradas_producto['stock_actual'].get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Validación", "El stock debe ser un número entero.")
            return

        try:
            costo_unitario = float(self.entradas_producto['costo_unitario'].get().strip())
        except ValueError:
            messagebox.showwarning("Validación", "El costo unitario debe ser un número válido.")
            return

        demanda_anual = self._parse_int(self.entradas_parametros['demanda_anual'].get().strip())
        costo_pedido = self._parse_float(self.entradas_parametros['costo_pedido'].get().strip())
        costo_mantenimiento = self._parse_float(self.entradas_parametros['costo_mantenimiento'].get().strip())
        tiempo_entrega = self._parse_int(self.entradas_parametros['tiempo_entrega'].get().strip())
        variabilidad_demanda = round(5 + random.random() * 35, 2)

        if self.editar_producto_id:
            try:
                self._update_producto(
                    id_producto=self.editar_producto_id,
                    nombre=nombre,
                    categoria=categoria,
                    stock_actual=stock_actual,
                    costo_unitario=costo_unitario,
                    proveedor=proveedor,
                    demanda_anual=demanda_anual,
                    costo_pedido=costo_pedido,
                    costo_mantenimiento=costo_mantenimiento,
                    tiempo_entrega=tiempo_entrega,
                    variabilidad_demanda=variabilidad_demanda
                )
                
                # 1. Liberar y destruir la ventana PRIMERO
                if self.ventana_agregar.winfo_exists():
                    self.ventana_agregar.grab_release()
                    self.ventana_agregar.destroy()
                
                self.editar_producto_id = None
                self.cargar_datos()
                
                # 2. Mostrar el mensaje DESPUÉS de cerrar el formulario
                messagebox.showinfo("Producto actualizado", "El producto se actualizó correctamente.")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")
        else:
            try:
                # _insert_producto ahora solo gestiona BD y retorna el código
                codigo_final = self._insert_producto(
                    nombre=nombre,
                    categoria=categoria,
                    stock_actual=stock_actual,
                    costo_unitario=costo_unitario,
                    proveedor=proveedor,
                    demanda_anual=demanda_anual,
                    costo_pedido=costo_pedido,
                    costo_mantenimiento=costo_mantenimiento,
                    tiempo_entrega=tiempo_entrega,
                    variabilidad_demanda=variabilidad_demanda
                )
                
                # 1. Liberar y destruir la ventana PRIMERO
                if self.ventana_agregar.winfo_exists():
                    self.ventana_agregar.grab_release()
                    self.ventana_agregar.destroy()
                    
                self.cargar_datos()
                
                # 2. Mostrar el mensaje DESPUÉS de cerrar el formulario
                messagebox.showinfo("Producto agregado", f"Producto agregado con código {codigo_final}.")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el producto: {e}")
                return

    def _parse_int(self, valor):
        if not valor:
            return None
        return int(valor)

    def _parse_float(self, valor):
        if not valor:
            return None
        return float(valor)

    def _validate_int_entry(self, valor):
        if valor == "":
            return True
        return valor.isdigit()

    def _validate_float_entry(self, valor):
        if valor == "":
            return True
        if valor.count('.') > 1:
            return False
        for caracter in valor:
            if caracter not in '0123456789.':
                return False
        return True

    def _insert_producto(self, nombre, categoria, stock_actual, costo_unitario, proveedor,
                         demanda_anual, costo_pedido,
                         costo_mantenimiento, tiempo_entrega, variabilidad_demanda):
        connection = get_connection()
        if not connection:
            raise Exception("No se pudo establecer la conexión con la base de datos.")

        cursor = None
        try:
            cursor = connection.cursor()
            codigo_temporal = f"_TEMP_{uuid.uuid4().hex[:12]}"

            insert_producto = (
                "INSERT INTO Productos (codigo, nombre, categoria, stock_actual, costo_unitario, proveedor) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(insert_producto, (
                codigo_temporal, nombre, categoria, stock_actual, costo_unitario, proveedor
            ))

            id_producto = cursor.lastrowid
            codigo_final = f"FER{id_producto}"
            cursor.execute(
                "UPDATE Productos SET codigo=%s WHERE id_producto=%s",
                (codigo_final, id_producto)
            )

            insert_parametros = (
                "INSERT INTO Parametros (id_producto, demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega, variabilidad_demanda) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(insert_parametros, (
                id_producto, demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega, variabilidad_demanda
            ))

            connection.commit()
            
            # Retornamos el código hacia guardar_producto en lugar de usar la interfaz gráfica aquí
            return codigo_final  

        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _load_parametros(self, id_producto):
        connection = get_connection()
        if not connection:
            return None
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega FROM Parametros WHERE id_producto=%s",
                (id_producto,)
            )
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def _update_producto(self, id_producto, nombre, categoria, stock_actual, costo_unitario, proveedor,
                         demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega, variabilidad_demanda):
        connection = get_connection()
        if not connection:
            raise Exception("No se pudo establecer la conexión con la base de datos.")

        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE Productos SET nombre=%s, categoria=%s, stock_actual=%s, costo_unitario=%s, proveedor=%s WHERE id_producto=%s",
                (nombre, categoria, stock_actual, costo_unitario, proveedor, id_producto)
            )
            cursor.execute(
                "UPDATE Parametros SET demanda_anual=%s, costo_pedido=%s, costo_mantenimiento=%s, tiempo_entrega=%s, variabilidad_demanda=%s WHERE id_producto=%s",
                (demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega, variabilidad_demanda, id_producto)
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO Parametros (id_producto, demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega, variabilidad_demanda) VALUES (%s, %s, %s, %s, %s, %s)",
                    (id_producto, demanda_anual, costo_pedido, costo_mantenimiento, tiempo_entrega, variabilidad_demanda)
                )
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def on_buscar_tiempo_real(self, event=None):
        """Realiza búsqueda en tiempo real."""
        termino_busqueda = self.entry_busqueda.get().strip().lower()
        
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        if not termino_busqueda:
            datos_filtrados = self.datos_originales
        else:
            datos_filtrados = []
            for producto in self.datos_originales:
                if (termino_busqueda in str(producto[1]).lower() or
                    termino_busqueda in str(producto[2]).lower() or
                    termino_busqueda in str(producto[3]).lower() or
                    termino_busqueda in str(producto[6] if producto[6] else "").lower()):
                    datos_filtrados.append(producto)
        
        for i, producto in enumerate(datos_filtrados):
            costo_formateado = f"₡{producto[5]:,.2f}" if producto[5] else "₡0.00"
            valores = (
                producto[1],
                producto[2],
                producto[3],
                str(producto[4]),
                costo_formateado,
                producto[6] if producto[6] else "N/A",
                '✏️ 🗑️'
            )
            tag = 'oddrow' if i % 2 else 'evenrow'
            self.tabla.insert('', tk.END, values=valores, tags=(tag,), iid=str(producto[0]))


def main():
    """Función para probar el módulo de forma independiente con un contenedor CTk."""
    root = ctk.CTk()
    root.title("Gestión de Inventarios - Prueba")
    root.geometry("1050x650")
    root.configure(fg_color="#EDF2F7")  # Forzamos fondo de la app principal

    frame_gestion = GestionInventariosFrame(root)
    frame_gestion.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()