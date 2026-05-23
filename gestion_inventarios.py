import os
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db_config import get_connection
import uuid


class GestionInventariosFrame(tk.Frame):
    """
    Frame para la gestión de inventarios de la Ferretería Simkin.
    Hereda de tk.Frame y se puede integrar en cualquier contenedor padre.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Inicializa el frame de gestión de inventarios.

        Args:
            parent: El contenedor padre (tk.Frame o tk.Tk)
        """
        super().__init__(parent, *args, **kwargs)

        # Definir colores (consistentes con la app principal)
        self.color_fondo = "#FFFFFF"
        self.color_panel = "#0A1F44"
        self.color_hover = "#123D6B"
        self.color_gris_claro = "#F5F5F5"

        # Variable para almacenar datos originales para búsqueda
        self.datos_originales = []

        # Configurar el frame principal
        self.configure(bg=self.color_fondo)

        # Aplicar estilos
        self.aplicar_estilos()

        # Crear la interfaz
        self.crear_panel_acciones()
        self.crear_tabla_inventarios()

        # Cargar datos desde la base de datos
        self.cargar_datos()

    def aplicar_estilos(self):
        """Define los estilos personalizados para la tabla y componentes."""
        self.style = ttk.Style()

        # Configurar tema
        self.style.theme_use('clam')

        # Estilo para botones de acción
        self.style.configure(
            'ActionButton.TButton',
            background=self.color_panel,
            foreground='white',
            font=('Segoe UI', 11),
            relief='flat',
            padding=(15, 8),
            borderwidth=0
        )

        self.style.configure(
            'GuardarButton.TButton',
            background=self.color_panel,
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padding=(12, 8),
            borderwidth=0
        )

        self.style.configure(
            'CancelarButton.TButton',
            background='#DDDDDD',
            foreground='#333333',
            font=('Segoe UI', 10),
            relief='flat',
            padding=(12, 8),
            borderwidth=0
        )

        # Estilo para el campo de búsqueda
        self.style.configure(
            'SearchEntry.TEntry',
            font=('Segoe UI', 11),
            relief='flat',
            borderwidth=1,
            padding=(5, 3)
        )

        # Estilo para la tabla Treeview
        self.style.configure(
            'Treeview',
            background=self.color_fondo,
            foreground=self.color_panel,
            font=('Segoe UI', 10),
            rowheight=25,
            fieldbackground=self.color_fondo
        )

        # Estilo para encabezados de tabla
        self.style.configure(
            'Treeview.Heading',
            background=self.color_panel,
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            borderwidth=0,
            padding=(10, 5)
        )

        # Estilo para filas alternadas
        self.style.map('Treeview',
            background=[('selected', self.color_hover),
                       ('alternate', self.color_gris_claro)])

    def crear_panel_acciones(self):
        """
        Crea el panel superior con botones de acción y campo de búsqueda.
        """
        # Frame del panel de acciones
        panel_acciones = tk.Frame(
            self,
            bg=self.color_fondo,
            relief=tk.FLAT,
            bd=0
        )
        panel_acciones.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Fila 1: Botón "Agregar producto"
        frame_boton = tk.Frame(panel_acciones, bg=self.color_fondo)
        frame_boton.pack(fill=tk.X, pady=(0, 10))

        btn_agregar = tk.Button(
            frame_boton,
            text="Agregar producto",
            bg=self.color_panel,
            fg='white',
            font=('Segoe UI', 11),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8,
            command=self.on_agregar_producto
        )
        btn_agregar.pack(side=tk.LEFT)

        # Agregar efecto hover al botón
        btn_agregar.bind("<Enter>", lambda e: btn_agregar.config(bg=self.color_hover))
        btn_agregar.bind("<Leave>", lambda e: btn_agregar.config(bg=self.color_panel))

        # Fila 2: Barra de búsqueda que abarca todo el ancho
        frame_busqueda = tk.Frame(panel_acciones, bg=self.color_fondo)
        frame_busqueda.pack(fill=tk.X)

        # Etiqueta para búsqueda
        lbl_buscar = tk.Label(
            frame_busqueda,
            text="Buscar:",
            font=('Segoe UI', 11),
            bg=self.color_fondo,
            fg=self.color_panel
        )
        lbl_buscar.pack(side=tk.LEFT, padx=(0, 10))

        # Campo de entrada para búsqueda con colores más oscuros
        self.entry_busqueda = tk.Entry(
            frame_busqueda,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=2,
            bg="#E8E8E8",
            fg=self.color_panel,
            insertbackground=self.color_panel
        )
        self.entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Vincular evento de escritura para búsqueda en tiempo real
        self.entry_busqueda.bind('<KeyRelease>', self.on_buscar_tiempo_real)

    def crear_tabla_inventarios(self):
        """
        Crea la tabla de inventarios usando ttk.Treeview con scrollbar.
        """
        # Frame contenedor para la tabla y scrollbar
        frame_tabla = tk.Frame(self, bg=self.color_fondo)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Crear Treeview con columnas
        columnas = ('codigo', 'nombre', 'categoria', 'stock', 'costo_unitario','proveedor')
        self.tabla = ttk.Treeview(
            frame_tabla,
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
            'proveedor': 'Proveedor'
        }

        for col, texto in encabezados.items():
            self.tabla.heading(col, text=texto, anchor=tk.W)
            # Configurar ancho de columnas
            if col == 'codigo':
                self.tabla.column(col, width=100, anchor=tk.W)
            elif col == 'nombre':
                self.tabla.column(col, width=200, anchor=tk.W)
            elif col == 'categoria':
                self.tabla.column(col, width=150, anchor=tk.W)
            elif col == 'stock':
                self.tabla.column(col, width=80, anchor=tk.CENTER)
            elif col == 'costo_unitario':
                self.tabla.column(col, width=120, anchor=tk.E)
            elif col == 'proveedor':
                self.tabla.column(col, width=200, anchor=tk.W)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Habilitar filas alternadas
        self.tabla.tag_configure('oddrow', background=self.color_gris_claro)
        self.tabla.tag_configure('evenrow', background=self.color_fondo)

    def cargar_datos(self):
        """
        Carga los datos de productos desde la base de datos MySQL.
        Solo muestra datos reales de la tabla Productos.
        """
        try:
            # Obtener conexión a la base de datos
            connection = get_connection()
            if not connection:
                print("Error: No se pudo establecer conexión con la base de datos")
                return

            # Crear cursor
            cursor = connection.cursor()

            # Ejecutar consulta para obtener datos 
            query = "SELECT codigo, nombre, categoria, stock_actual, costo_unitario, proveedor FROM Productos ORDER BY nombre"
            cursor.execute(query)

            # Obtener resultados
            productos = cursor.fetchall()

            # Guardar datos originales para búsqueda
            self.datos_originales = productos

            # Limpiar tabla antes de insertar nuevos datos
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            # Insertar datos en la tabla
            for i, producto in enumerate(productos):
                # Formatear el costo unitario como moneda costarricense
                costo_formateado = f"₡{producto[4]:,.2f}" if producto[4] else "₡0.00"

                # Preparar valores para la tabla
                valores = (
                    producto[0],  # código
                    producto[1],  # nombre
                    producto[2],  # categoria
                    str(producto[3]),  # stock_actual
                    costo_formateado,  # costo_unitario
                    producto[5] if producto[5] else "N/A"  # proveedor
                )

                # Determinar tag para filas alternadas
                tag = 'oddrow' if i % 2 else 'evenrow'
                self.tabla.insert('', tk.END, values=valores, tags=(tag,))

            # Cerrar cursor y conexión
            cursor.close()
            connection.close()

            print(f"Datos cargados exitosamente: {len(productos)} productos encontrados")

        except Exception as e:
            print(f"Error al cargar datos de la base de datos: {e}")
            # Limpiar tabla si hay error
            for item in self.tabla.get_children():
                self.tabla.delete(item)

    def on_agregar_producto(self):
        """Abre el formulario para agregar un nuevo producto."""
        if hasattr(self, 'ventana_agregar') and self.ventana_agregar.winfo_exists():
            self.ventana_agregar.lift()
            return

        self.ventana_agregar = tk.Toplevel(self)
        self.ventana_agregar.title("Agregar Producto")
        self.ventana_agregar.configure(bg=self.color_fondo)
        self.ventana_agregar.geometry("520x620")
        self.ventana_agregar.transient(self)
        self.ventana_agregar.grab_set()
        self.ventana_agregar.resizable(False, False)

        contenedor = tk.Frame(self.ventana_agregar, bg=self.color_fondo)
        contenedor.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        canvas = tk.Canvas(
            contenedor,
            bg=self.color_fondo,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(contenedor, orient='vertical', command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.color_fondo)

        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Form card
        form_card = tk.Frame(
            self.scrollable_frame,
            bg='#FFFFFF',
            highlightbackground='#DDDDDD',
            highlightthickness=1,
            bd=0
        )
        form_card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        header_frame = tk.Frame(form_card, bg='#FFFFFF')
        header_frame.pack(fill=tk.X, padx=12, pady=(12, 6))

        
        titulo_label = tk.Label(
            header_frame,
            text="Agregar Producto",
            bg='#FFFFFF',
            fg='#0A1F44',
            font=('Segoe UI', 14, 'bold')
        )
        titulo_label.pack(side=tk.LEFT, anchor='w')

        # Validaciones numéricas
        vcmd_entero = (self.ventana_agregar.register(self._validate_int_entry), '%P')
        vcmd_decimal = (self.ventana_agregar.register(self._validate_float_entry), '%P')

        campos_producto = [
            ("Nombre", "nombre", None),
            ("Categoría", "categoria", None),
            ("Stock actual", "stock_actual", vcmd_entero),
            ("Costo unitario", "costo_unitario", vcmd_decimal),
            ("Proveedor", "proveedor", None),
        ]
        self.entradas_producto = {}
        for texto, campo, vcmd in campos_producto:
            row = tk.Frame(form_card, bg='#FFFFFF')
            row.pack(fill=tk.X, padx=12, pady=5)

            label = tk.Label(
                row,
                text=f"{texto}:",
                bg='#FFFFFF',
                fg='#333333',
                font=('Segoe UI', 10)
            )
            label.pack(anchor='w')

            entry = tk.Entry(
                row,
                font=('Segoe UI', 10),
                bg='#F7F7F7',
                fg='black',
                bd=0,
                relief=tk.FLAT,
                highlightthickness=1,
                highlightbackground='#DDDDDD',
                highlightcolor='#DDDDDD',
                insertbackground='black',
                validate='key',
                validatecommand=vcmd if vcmd else None
            )
            entry.pack(fill=tk.X, pady=(6, 0), ipady=6)
            self.entradas_producto[campo] = entry

        separator = ttk.Separator(form_card, orient='horizontal')
        separator.pack(fill=tk.X, padx=12, pady=15)

        label_parametros = tk.Label(
            form_card,
            text="Parámetros de inventario",
            bg='#FFFFFF',
            fg='#0A1F44',
            font=('Segoe UI', 11, 'bold')
        )
        label_parametros.pack(anchor='w', padx=12, pady=(0, 8))

        campos_parametros = [
            ("Demanda anual", "demanda_anual", vcmd_entero),
            ("Costo de pedido", "costo_pedido", vcmd_decimal),
            ("Costo de mantenimiento", "costo_mantenimiento", vcmd_decimal),
            ("Tiempo de entrega (días)", "tiempo_entrega", vcmd_entero),
        ]
        self.entradas_parametros = {}
        for texto, campo, vcmd in campos_parametros:
            row = tk.Frame(form_card, bg='#FFFFFF')
            row.pack(fill=tk.X, padx=12, pady=5)

            label = tk.Label(
                row,
                text=f"{texto}:",
                bg='#FFFFFF',
                fg='#333333',
                font=('Segoe UI', 10)
            )
            label.pack(anchor='w')

            entry = tk.Entry(
                row,
                font=('Segoe UI', 10),
                bg='#F7F7F7',
                fg='black',
                bd=0,
                relief=tk.FLAT,
                highlightthickness=1,
                highlightbackground='#DDDDDD',
                highlightcolor='#DDDDDD',
                insertbackground='black',
                validate='key',
                validatecommand=vcmd
            )
            entry.pack(fill=tk.X, pady=(6, 0), ipady=6)
            self.entradas_parametros[campo] = entry

        botones_frame = tk.Frame(form_card, bg='#FFFFFF')
        botones_frame.pack(fill=tk.X, padx=12, pady=20)

        btn_cancelar = ttk.Button(
            botones_frame,
            text="Cancelar",
            style='CancelarButton.TButton',
            command=self.ventana_agregar.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=(10, 0))

        btn_guardar = ttk.Button(
            botones_frame,
            text="Guardar",
            style='GuardarButton.TButton',
            command=self.guardar_producto
        )
        btn_guardar.pack(side=tk.RIGHT)

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

        try:
            self._insert_producto(
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
            messagebox.showerror("Error", "No se pudo establecer la conexión con la base de datos.")
            return

        cursor = None
        try:
            cursor = connection.cursor()
            codigo_temporal = f"_TEMP_{uuid.uuid4().hex[:12]}"

            insert_producto = (
                "INSERT INTO Productos (codigo, nombre, categoria, stock_actual, costo_unitario, proveedor) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(insert_producto, (
                codigo_temporal,
                nombre,
                categoria,
                stock_actual,
                costo_unitario,
                proveedor
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
                id_producto,
                demanda_anual,
                costo_pedido,
                costo_mantenimiento,
                tiempo_entrega,
                variabilidad_demanda
            ))

            connection.commit()
            messagebox.showinfo("Producto agregado", f"Producto agregado con código {codigo_final}.")
            self.ventana_agregar.destroy()
            self.cargar_datos()
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
        """Realiza búsqueda en tiempo real mientras se escribe en el campo."""
        termino_busqueda = self.entry_busqueda.get().strip().lower()
        
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Si no hay término de búsqueda, mostrar todos los datos
        if not termino_busqueda:
            datos_filtrados = self.datos_originales
        else:
            # Filtrar datos que coincidan con el término de búsqueda
            datos_filtrados = []
            for producto in self.datos_originales:
                # Buscar en código, nombre, categoría y proveedor
                if (termino_busqueda in str(producto[0]).lower() or
                    termino_busqueda in str(producto[1]).lower() or
                    termino_busqueda in str(producto[2]).lower() or
                    termino_busqueda in str(producto[5]).lower()):
                    datos_filtrados.append(producto)
        
        # Insertar datos filtrados en la tabla
        for i, producto in enumerate(datos_filtrados):
            # Formatear el costo unitario como moneda costarricense
            costo_formateado = f"₡{producto[4]:,.2f}" if producto[4] else "₡0.00"

            # Preparar valores para la tabla
            valores = (
                producto[0],  # código
                producto[1],  # nombre
                producto[2],  # categoria
                str(producto[3]),  # stock_actual
                costo_formateado,  # costo_unitario
                producto[5] if producto[5] else "N/A"  # proveedor
            )

            # Determinar tag para filas alternadas
            tag = 'oddrow' if i % 2 else 'evenrow'
            self.tabla.insert('', tk.END, values=valores, tags=(tag,))


# Función de prueba para ejecutar el módulo de forma independiente
def main():
    """Función para probar el módulo de forma independiente."""
    root = tk.Tk()
    root.title("Gestión de Inventarios - Prueba")
    root.geometry("1000x600")

    # Crear instancia del frame
    frame_gestion = GestionInventariosFrame(root)
    frame_gestion.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()