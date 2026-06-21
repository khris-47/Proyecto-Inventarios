import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from db_config import get_connection


class ReportesFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.fecha_seleccionada = None
        self.df_datos = pd.DataFrame()
        self.datos_originales = []

        self.crear_panel_titulo()
        self.crear_panel_filtro()
        self.crear_panel_exportar()
        self.crear_panel_busqueda()

        # Frame central para tabla y graficas
        self.main_content = tk.Frame(self)
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame izquierdo para tabla
        self.left_frame = tk.Frame(self.main_content)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Frame derecho para graficas
        self.right_frame = tk.Frame(self.main_content)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.crear_tabla_reportes()
        self.crear_graficas()

        self.cargar_fechas()
        self.cargar_reportes()

    def crear_panel_titulo(self):
        title_frame = tk.Frame(self, bg="white")
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        title_label = tk.Label(
            title_frame, 
            text="Reportes de Inventarios", 
            bg="white", 
            fg="#0A1F44", 
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=10)

    def crear_panel_filtro(self):
        filtro_frame = tk.Frame(self, bg="white")
        filtro_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        lbl_fecha = tk.Label(
            filtro_frame,
            text="Fecha de Cálculo:",
            bg="white",
            fg="#0A1F44",
            font=("Segoe UI", 10, "bold")
        )
        lbl_fecha.pack(side=tk.LEFT, padx=(0, 5), pady=5)

        self.cb_fechas = ttk.Combobox(
            filtro_frame,
            state="readonly",
            width=30,
            font=("Segoe UI", 10)
        )
        self.cb_fechas.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        self.cb_fechas.bind("<<ComboboxSelected>>", self.on_fecha_select)

    def crear_panel_exportar(self):
        export_frame = tk.Frame(self, bg="white")
        export_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        style = ttk.Style()
        style.configure(
            "Export.TButton",
            background="#0A1F44",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )
        style.map(
            "Export.TButton",
            background=[('active', '#1E3A5F'), ('pressed', '#0A1F44')]
        )

        btn_exportar = ttk.Button(
            export_frame,
            text="Exportar a Excel",
            command=self.exportar_reporte,
            style="Export.TButton"
        )
        btn_exportar.pack(side=tk.RIGHT, pady=5)

    def crear_panel_busqueda(self):
        """Crea el panel de búsqueda en tiempo real."""
        panel_busqueda = tk.Frame(self, bg="white")
        panel_busqueda.pack(fill=tk.X, padx=10, pady=(0, 10))

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

    def crear_tabla_reportes(self):
        # Estilo de encabezados
        style = ttk.Style()
        style.configure("Treeview.Heading", background="#0A1F44", foreground="white", font=("Segoe UI", 10, "bold"))
        
        # Frame para la tabla con scrollbar
        table_frame = tk.Frame(self.left_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ("Producto", "EOQ", "PRO", "Inventario de Seguridad", "Ventas Anuales", "Clasificación ABC")
        self.tree = ttk.Treeview(table_frame, columns=columnas, show="headings", yscrollcommand=scrollbar.set)
        
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
            
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

    def crear_graficas(self):
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_eoq = tk.Frame(self.notebook, bg="white")
        self.tab_ventas = tk.Frame(self.notebook, bg="white")
        self.tab_abc = tk.Frame(self.notebook, bg="white")
        self.tab_seguridad = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab_eoq, text="EOQ")
        self.notebook.add(self.tab_ventas, text="Ventas Anuales")
        self.notebook.add(self.tab_abc, text="Clasificación ABC")
        self.notebook.add(self.tab_seguridad, text="Inventario de Seguridad")

        self.fig_eoq = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_eoq = self.fig_eoq.add_subplot(111)
        self.canvas_eoq = FigureCanvasTkAgg(self.fig_eoq, master=self.tab_eoq)
        self.canvas_eoq.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_ventas = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_ventas = self.fig_ventas.add_subplot(111)
        self.canvas_ventas = FigureCanvasTkAgg(self.fig_ventas, master=self.tab_ventas)
        self.canvas_ventas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_abc = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_abc = self.fig_abc.add_subplot(111)
        self.canvas_abc = FigureCanvasTkAgg(self.fig_abc, master=self.tab_abc)
        self.canvas_abc.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_seguridad = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_seguridad = self.fig_seguridad.add_subplot(111)
        self.canvas_seguridad = FigureCanvasTkAgg(self.fig_seguridad, master=self.tab_seguridad)
        self.canvas_seguridad.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def cargar_fechas(self):
        try:
            conexion = get_connection()
            if not conexion:
                return

            cursor = conexion.cursor()
            query = "SELECT DISTINCT fecha_calculo FROM Resultados_Modelos ORDER BY fecha_calculo DESC"
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()

            fechas = []
            for fila in resultados:
                fecha_valor = fila[0]
                if fecha_valor is not None:
                    fechas.append(str(fecha_valor))

            self.cb_fechas['values'] = fechas
            if fechas:
                self.cb_fechas.current(0)
                self.fecha_seleccionada = fechas[0]
        except Exception as e:
            print(f"Error al cargar fechas: {e}")

    def on_fecha_select(self, event):
        self.fecha_seleccionada = self.cb_fechas.get()
        self.entry_busqueda.delete(0, tk.END)  # Limpiar campo de búsqueda
        self.cargar_reportes()

    def cargar_reportes(self):
        if not self.fecha_seleccionada:
            return

        try:
            conexion = get_connection()
            if not conexion:
                print("Error: No se pudo conectar a la base de datos.")
                return

            cursor = conexion.cursor(dictionary=True)
            query = '''
                SELECT
                    r.id_resultado,
                    r.id_producto,
                    p.nombre AS Producto,
                    p.stock_actual,
                    r.EOQ,
                    r.PRO,
                    r.inventario_seguridad,
                    r.fecha_calculo,
                    r.ventas_anuales,
                    r.porcentaje,
                    r.porcentaje_acumulado,
                    r.costo_anual_ordenar,
                    r.costo_anual_conservacion,
                    r.costo_total,
                    r.punto_reorden,
                    r.clasificacion_ABC
                FROM Resultados_Modelos r
                LEFT JOIN Productos p ON p.id_producto = r.id_producto
                WHERE r.fecha_calculo = %s
                ORDER BY p.nombre
            '''
            cursor.execute(query, (self.fecha_seleccionada,))
            datos = cursor.fetchall()
            cursor.close()
            conexion.close()

            self.df_datos = pd.DataFrame(datos)

            for item in self.tree.get_children():
                self.tree.delete(item)

            if self.df_datos.empty:
                messagebox.showinfo("Reportes", "No hay datos para la fecha seleccionada.")
                self.limpiar_graficas()
                return

            # Guardar datos originales para búsqueda
            self.datos_originales = self.df_datos.to_dict('records')

            for _, row in self.df_datos.iterrows():
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        row.get('Producto', ''),
                        int(row.get('EOQ', 0)) if pd.notnull(row.get('EOQ')) else 0,
                        int(row.get('PRO', 0)) if pd.notnull(row.get('PRO')) else 0,
                        int(row.get('inventario_seguridad', 0)) if pd.notnull(row.get('inventario_seguridad')) else 0,
                        f"₡{row.get('ventas_anuales', 0):,.2f}" if pd.notnull(row.get('ventas_anuales')) else "₡0.00",
                        row.get('clasificacion_ABC', '')
                    )
                )

            self.actualizar_graficas()

        except Exception as e:
            print(f"Error al cargar reportes: {e}")
            messagebox.showerror("Error", f"Ocurrió un error al cargar los reportes:\n{e}")

    def limpiar_graficas(self):
        self.ax_eoq.clear()
        self.ax_ventas.clear()
        self.ax_abc.clear()
        self.ax_seguridad.clear()
        self.canvas_eoq.draw()
        self.canvas_ventas.draw()
        self.canvas_abc.draw()
        self.canvas_seguridad.draw()

    def actualizar_graficas(self):
        if self.df_datos.empty:
            self.limpiar_graficas()
            return

        self.ax_eoq.clear()
        self.ax_ventas.clear()
        self.ax_abc.clear()

        colores = ['#0A1F44', '#5A7FB8', '#8FA6D7', '#C3D1EB']

        df_eoq = self.df_datos[['Producto', 'EOQ']].copy()
        df_eoq['EOQ'] = pd.to_numeric(df_eoq['EOQ'], errors='coerce').fillna(0)
        df_eoq = df_eoq.sort_values('EOQ', ascending=False).head(10)
        self.ax_eoq.bar(df_eoq['Producto'], df_eoq['EOQ'], color=colores[1])
        self.ax_eoq.set_title('EOQ por Producto', color='#0A1F44', fontweight='bold')
        self.ax_eoq.set_ylabel('Cantidad', color='#0A1F44')
        self.ax_eoq.tick_params(axis='x', rotation=45, labelsize=8)

        df_ventas = self.df_datos[['Producto', 'ventas_anuales']].copy()
        df_ventas['ventas_anuales'] = pd.to_numeric(df_ventas['ventas_anuales'], errors='coerce').fillna(0)
        df_ventas = df_ventas.sort_values('ventas_anuales', ascending=False).head(10)
        self.ax_ventas.bar(df_ventas['Producto'], df_ventas['ventas_anuales'], color=colores[2])
        self.ax_ventas.set_title('Ventas Anuales por Producto', color='#0A1F44', fontweight='bold')
        self.ax_ventas.set_ylabel('Ventas Anuales ₡', color='#0A1F44')
        self.ax_ventas.tick_params(axis='x', rotation=45, labelsize=8)

        if 'clasificacion_ABC' in self.df_datos.columns:
            abc_counts = self.df_datos['clasificacion_ABC'].fillna('N/A').value_counts()
            labels = []
            sizes = []
            for cat in ['A', 'B', 'C']:
                if cat in abc_counts:
                    labels.append(cat)
                    sizes.append(abc_counts[cat])

            if sizes:
                def autopct_with_label(pct, all_labels=labels):
                    autopct_with_label.index = getattr(autopct_with_label, 'index', 0)
                    label = all_labels[autopct_with_label.index] if autopct_with_label.index < len(all_labels) else ''
                    text = f"{label} {pct:.1f}%"
                    autopct_with_label.index += 1
                    return text

                self.ax_abc.pie(
                    sizes,
                    labels=labels,
                    autopct=autopct_with_label,
                    colors=['#0A1F44', '#5A7FB8', '#8FA6D7'],
                    textprops={'color': 'white'}
                )
                self.ax_abc.set_title('Clasificación ABC', color='#0A1F44', fontweight='bold')

        # Inventario de seguridad: productos en riesgo vs seguros
        df_seguridad = self.df_datos.copy()
        df_seguridad['stock_actual'] = pd.to_numeric(df_seguridad.get('stock_actual', 0), errors='coerce').fillna(0)
        df_seguridad['inventario_seguridad'] = pd.to_numeric(df_seguridad.get('inventario_seguridad', 0), errors='coerce').fillna(0)
        riesgo = int((df_seguridad['stock_actual'] < df_seguridad['inventario_seguridad']).sum())
        seguro = int((df_seguridad['stock_actual'] >= df_seguridad['inventario_seguridad']).sum())

        if riesgo + seguro > 0:
            self.ax_seguridad.pie(
                [riesgo, seguro],
                labels=['En riesgo', 'Seguro'],
                autopct='%1.1f%%',
                colors=['#E74C3C', '#2ECC71'],
                startangle=90,
                textprops={'color': 'white'}
            )
            self.ax_seguridad.set_title('Cumplimiento Inventario de Seguridad', color='#0A1F44', fontweight='bold')

        self.fig_eoq.tight_layout()
        self.fig_ventas.tight_layout()
        self.fig_abc.tight_layout()
        self.fig_seguridad.tight_layout()
        self.canvas_eoq.draw()
        self.canvas_ventas.draw()
        self.canvas_abc.draw()
        self.canvas_seguridad.draw()

    def exportar_reporte(self):
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar Reporte"
        )

        if not ruta_archivo:
            return

        try:
            conexion = get_connection()
            if not conexion:
                messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
                return

            cursor = conexion.cursor(dictionary=True)
            query = '''
                SELECT
                    r.id_resultado,
                    r.id_producto,
                    p.nombre AS Producto,
                    r.EOQ,
                    r.PRO,
                    r.inventario_seguridad,
                    r.fecha_calculo,
                    r.ventas_anuales,
                    r.porcentaje,
                    r.porcentaje_acumulado,
                    r.costo_anual_ordenar,
                    r.costo_anual_conservacion,
                    r.costo_total,
                    r.punto_reorden,
                    r.clasificacion_ABC
                FROM Resultados_Modelos r
                LEFT JOIN Productos p ON p.id_producto = r.id_producto
                WHERE r.fecha_calculo = %s
                ORDER BY r.id_resultado
            '''
            cursor.execute(query, (self.fecha_seleccionada,))
            datos = cursor.fetchall()
            cursor.close()
            conexion.close()

            if not datos:
                messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                return

            df_export = pd.DataFrame(datos)
            df_export.to_excel(ruta_archivo, index=False)
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al exportar:\n{e}")

    def on_buscar_tiempo_real(self, event=None):
        """Realiza búsqueda en tiempo real mientras se escribe en el campo."""
        if not self.datos_originales:
            return
        
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
                # Buscar en producto
                if termino_busqueda in str(producto.get('Producto', '')).lower():
                    datos_filtrados.append(producto)
        
        # Insertar datos filtrados en la tabla
        for row in datos_filtrados:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row.get('Producto', ''),
                    int(row.get('EOQ', 0)) if pd.notnull(row.get('EOQ')) else 0,
                    int(row.get('PRO', 0)) if pd.notnull(row.get('PRO')) else 0,
                    int(row.get('inventario_seguridad', 0)) if pd.notnull(row.get('inventario_seguridad')) else 0,
                    f"₡{row.get('ventas_anuales', 0):,.2f}" if pd.notnull(row.get('ventas_anuales')) else "₡0.00",
                    row.get('clasificacion_ABC', '')
                )
            )

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba de Reportes")
    root.geometry("1000x800")
    app = ReportesFrame(master=root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
