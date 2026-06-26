import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker
import pandas as pd
from db_config import get_connection


class ReportesFrame(ctk.CTkFrame):  # Cambiado a CTkFrame para consistencia
    def __init__(self, master=None, **kwargs):
        # Inicializar con el fondo gris suave moderno del sistema
        super().__init__(master, fg_color="#F8FAFC", **kwargs)
        self.master = master
        self.fecha_seleccionada = None
        self.df_datos = pd.DataFrame()

        # Paleta de colores unificada
        self.color_primario = "#0A1F44"
        self.color_secundario = "#5A7FB8"
        self.color_exito = "#10B981"       # Verde esmeralda moderno
        self.color_alerta = "#EF4444"      # Rojo suave moderno para el Riesgo
        self.color_texto = "#1E293B"

        self.crear_panel_navbar()
        self.crear_panel_kpis()
        self.crear_contenido_principal()

        self.cargar_fechas()
        self.cargar_reportes()

    def crear_panel_navbar(self):
        navbar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        navbar.pack(fill=tk.X, padx=20, pady=(20, 5))
        navbar.pack_propagate(False)

        title_label = ctk.CTkLabel(
            navbar,
            text="Dashboard de Gestión",
            text_color=self.color_primario,
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=5)

        controls = ctk.CTkFrame(navbar, fg_color="transparent")
        controls.pack(side=tk.RIGHT, padx=5)

        lbl_fecha = ctk.CTkLabel(
            controls,
            text="Fecha de Cálculo:",
            text_color=self.color_primario,
            font=("Segoe UI", 11, "bold")
        )
        lbl_fecha.pack(side=tk.LEFT, padx=(0, 8))

        # Reemplazo por un CTkComboBox moderno y estilizado internamente
        # Alternativa con CTkOptionMenu (Menú de opciones plano y moderno)
        self.cb_fechas = ctk.CTkOptionMenu(
            controls,
            width=220,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.color_primario,
            button_color=self.color_primario,
            button_hover_color="#1E3A5F",
            text_color="white",
            
            # Estilo del menú desplegable
            dropdown_fg_color="white",
            dropdown_text_color=self.color_texto,
            dropdown_hover_color="#F1F5F9",
            dropdown_font=("Segoe UI", 11)
        )
        self.cb_fechas.pack(side=tk.LEFT, padx=(0, 15))
        self.cb_fechas.configure(command=self.on_fecha_select)

        btn_exportar = ctk.CTkButton(
            controls,
            text="Exportar a Excel",
            command=self.exportar_reporte,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.color_primario,
            hover_color="#1E3A5F",
            text_color="white",
            corner_radius=8,
            height=32
        )
        btn_exportar.pack(side=tk.LEFT)

    def crear_panel_kpis(self):
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill=tk.X, padx=20, pady=10)

        tarjeta_info = [
            {'titulo': 'Producto Estrella',         'atributo': 'producto_estrella',        'color': self.color_primario, 'icono': '📦'},
            {'titulo': 'Mayor EOQ',                 'atributo': 'mayor_eoq',                'color': self.color_primario, 'icono': '📉'},
            {'titulo': 'Promedio Tiempo de Entrega','atributo': 'promedio_tiempo_entrega', 'color': self.color_primario, 'icono': '⏱️'},
            {'titulo': 'Productos en Riesgo',       'atributo': 'productos_en_riesgo',      'color': '#D97706', 'icono': '⚠️'},
        ]

        self.kpi_labels = {}
        self.kpi_subtitles = {}

        for index, item in enumerate(tarjeta_info):
            # Tarjetas refinadas con bordes suaves y redondeados
            tarjeta = ctk.CTkFrame(
                self.kpi_frame, 
                fg_color="white", 
                corner_radius=12,
                border_width=1,
                border_color="#E2E8F0"
            )
            tarjeta.grid(row=0, column=index, sticky='nsew', padx=6, pady=2)
            self.kpi_frame.grid_columnconfigure(index, weight=1)

            # --- TÍTULOS DE LOS KPIS MÁS GRANDES ---
            ctk.CTkLabel(
                tarjeta,
                text=f"{item['icono']} {item['titulo']}",
                text_color=item['color'],
                font=("Segoe UI", 14, "bold")  # Aumentado de 11 a 14 para mayor jerarquía
            ).pack(anchor='center', padx=12, pady=(18, 2))

            subtitle = None
            if item['atributo'] == 'mayor_eoq':
                subtitle = ctk.CTkLabel(
                    tarjeta,
                    text='',
                    text_color="#64748B",  # Texto gris para mejorar jerarquía visual
                    font=("Segoe UI", 10, "italic") # Ajustado a 10 para balancear con el título
                )
                subtitle.pack(anchor='center', padx=12, pady=(0, 2))
                self.kpi_subtitles[item['atributo']] = subtitle

            valor = ctk.CTkLabel(
                tarjeta, 
                text="-",
                text_color=self.color_primario,
                font=("Segoe UI", 24, "bold")  # Aumentado ligeramente a 24 para que guarde proporción
            )
            valor.pack(anchor='center', padx=12, pady=(0, 18))
            self.kpi_labels[item['atributo']] = valor
    def crear_contenido_principal(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Tarjeta contenedora para los gráficos unificados
        tarjeta_graficos = ctk.CTkFrame(
            self.main_frame,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        tarjeta_graficos.pack(fill=tk.BOTH, expand=True)

        self.fig = plt.Figure(figsize=(14, 4.5), dpi=100)
        self.fig.patch.set_facecolor('white') # El lienzo ahora es blanco puro

        gs = gridspec.GridSpec(
            1, 3,
            figure=self.fig,
            left=0.08, right=0.96, # Ajustado el margen izquierdo para evitar textos recortados
            top=0.88, bottom=0.20,
            wspace=0.38
        )

        self.ax_ventas    = self.fig.add_subplot(gs[0, 0])
        self.ax_abc       = self.fig.add_subplot(gs[0, 1])
        self.ax_seguridad = self.fig.add_subplot(gs[0, 2])

        self.canvas = FigureCanvasTkAgg(self.fig, master=tarjeta_graficos)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _estilo_ax(self, ax, title):
        """Aplica fondo blanco y título uniforme a un eje."""
        ax.set_facecolor('white')
        ax.set_title(title, color=self.color_primario, fontweight='bold', fontsize=11, pad=12)

    def _grafico_pastel(self, ax, sizes, labels, colors, title):
        if not sizes:
            return

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            autopct='%1.1f%%',
            pctdistance=0.70,
            colors=colors,
            startangle=90,
            wedgeprops={'width': 0.45, 'edgecolor': 'white', 'linewidth': 2},
        )

        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
            autotext.set_color('#1E293B')
            autotext.set_bbox(dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8, ec='#E2E8F0', lw=0.5))

        ax.legend(
            wedges, labels,
            loc='lower center',
            bbox_to_anchor=(0.5, -0.22),
            ncol=len(labels),
            fontsize=9,
            frameon=False,
        )

        ax.axis('equal')
        self._estilo_ax(ax, title)

    def cargar_fechas(self):
        try:
            conexion = get_connection()
            if not conexion:
                return
            cursor = conexion.cursor()
            cursor.execute("SELECT DISTINCT fecha_calculo FROM Resultados_Modelos ORDER BY fecha_calculo DESC")
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()

            fechas = [str(fila[0]) for fila in resultados if fila[0] is not None]
            if fechas:
                self.cb_fechas.configure(values=fechas)
                self.cb_fechas.set(fechas[0])
                self.fecha_seleccionada = fechas[0]
        except Exception as e:
            print(f"Error al cargar fechas: {e}")

    def on_fecha_select(self, fecha):
        self.fecha_seleccionada = fecha
        self.cargar_reportes()

    def cargar_parametros(self):
        try:
            conexion = get_connection()
            if not conexion:
                return 0
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT AVG(tiempo_entrega) AS promedio_tiempo_entrega FROM Parametros")
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            if resultado and resultado.get('promedio_tiempo_entrega') is not None:
                return float(resultado['promedio_tiempo_entrega'])
        except Exception as e:
            print(f"Error al cargar parámetros: {e}")
        return 0

    def cargar_reportes(self):
        if not self.fecha_seleccionada:
            return
        try:
            conexion = get_connection()
            if not conexion:
                messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
                return

            cursor = conexion.cursor(dictionary=True)
            query = '''
                SELECT r.id_resultado, r.id_producto,
                       p.nombre AS Producto, p.stock_actual,
                       r.EOQ, r.PRO, r.inventario_seguridad,
                       r.fecha_calculo, r.ventas_anuales,
                       r.porcentaje, r.porcentaje_acumulado,
                       r.costo_anual_ordenar, r.costo_anual_conservacion,
                       r.costo_total, r.punto_reorden, r.clasificacion_ABC
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

            if self.df_datos.empty:
                messagebox.showinfo("Reportes", "No hay datos para la fecha seleccionada.")
                self.limpiar_graficas()
                self.actualizar_kpis('-', 0, 0, 0)
                return

            promedio = self.cargar_parametros()
            producto_estrella, mayor_eoq, riesgo = self.calcular_kpis()
            self.actualizar_kpis(producto_estrella, mayor_eoq, promedio, riesgo)
            self.actualizar_graficas()

        except Exception as e:
            print(f"Error al cargar reportes: {e}")
            messagebox.showerror("Error", f"Ocurrió un error al cargar los reportes:\n{e}")

    def calcular_kpis(self):
        producto_estrella = '-'
        mayor_eoq = 0
        productos_en_riesgo = 0

        if not self.df_datos.empty:
            df = self.df_datos.copy()
            df['ventas_anuales'] = pd.to_numeric(df.get('ventas_anuales', 0), errors='coerce').fillna(0)
            producto_estrella = df.sort_values('ventas_anuales', ascending=False).iloc[0].get('Producto', '-')

            df['EOQ'] = pd.to_numeric(df.get('EOQ', 0), errors='coerce').fillna(0)
            mayor_eoq = int(df['EOQ'].max())

            df['stock_actual'] = pd.to_numeric(df.get('stock_actual', 0), errors='coerce').fillna(0)
            df['inventario_seguridad'] = pd.to_numeric(df.get('inventario_seguridad', 0), errors='coerce').fillna(0)
            productos_en_riesgo = int((df['stock_actual'] < df['inventario_seguridad']).sum())

        return producto_estrella, mayor_eoq, productos_en_riesgo

    def actualizar_kpis(self, producto_estrella, mayor_eoq, promedio_tiempo_entrega, productos_en_riesgo):
        self.kpi_labels['producto_estrella'].configure(text=str(producto_estrella))
        self.kpi_labels['mayor_eoq'].configure(text=f"{mayor_eoq:,}")
        if 'mayor_eoq' in self.kpi_subtitles:
            self.kpi_subtitles['mayor_eoq'].configure(text=f'{producto_estrella}')
        self.kpi_labels['promedio_tiempo_entrega'].configure(text=f"{promedio_tiempo_entrega:.1f} días")
        
        # Color dinámico limpio para el estado crítico
        color = self.color_exito if productos_en_riesgo == 0 else "#DC2626"
        self.kpi_labels['productos_en_riesgo'].configure(text=str(productos_en_riesgo), text_color=color)

    def limpiar_graficas(self):
        for ax in (self.ax_ventas, self.ax_abc, self.ax_seguridad):
            ax.clear()
        self.canvas.draw()

    def actualizar_graficas(self):
        for ax in (self.ax_ventas, self.ax_abc, self.ax_seguridad):
            ax.clear()

        if self.df_datos.empty:
            self.canvas.draw()
            return

        # ── 1. Top 10 Ventas ────────────────────────────────────────────────
        df_v = self.df_datos[['Producto', 'ventas_anuales']].copy()
        df_v['ventas_anuales'] = pd.to_numeric(df_v['ventas_anuales'], errors='coerce').fillna(0)
        df_v = df_v.sort_values('ventas_anuales', ascending=True).tail(10)

        # Usando la paleta secundaria unificada
        bars = self.ax_ventas.barh(
            df_v['Producto'], df_v['ventas_anuales'],
            color=self.color_secundario, edgecolor='white', linewidth=0.5
        )

        max_val = df_v['ventas_anuales'].max()
        self.ax_ventas.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, pos: f"₡{x/1e6:.0f}M")
        )

        self.ax_ventas.tick_params(axis='x', rotation=45, labelsize=8)
        self.ax_ventas.set_xlim(0, max_val * 1.15)
        self.ax_ventas.set_xlabel('Ventas Anuales', color=self.color_primario, fontsize=9, fontweight='bold')
        self.ax_ventas.tick_params(axis='both', labelsize=8, colors=self.color_primario)
        
        # Eliminando bordes innecesarios (Spines) y suavizando las líneas restantes
        self.ax_ventas.spines[['top', 'right']].set_visible(False)
        self.ax_ventas.spines[['left', 'bottom']].set_color('#CBD5E1')
        self.ax_ventas.spines[['left', 'bottom']].set_linewidth(1)

        self._estilo_ax(self.ax_ventas, 'Top 10 Ventas Anuales')

        # ── 2. Clasificación ABC ─────────────────────────────────────────────
        if 'clasificacion_ABC' in self.df_datos.columns:
            abc_counts = self.df_datos['clasificacion_ABC'].fillna('N/A').value_counts()
            sizes, labels = [], []
            for cat in ['A', 'B', 'C']:
                if cat in abc_counts:
                    labels.append(cat)
                    sizes.append(abc_counts[cat])

            self._grafico_pastel(
                self.ax_abc, sizes, labels,
                colors=[self.color_primario, self.color_secundario, self.color_exito],
                title='Clasificación ABC'
            )

        # ── 3. Seguridad de Inventario ───────────────────────────────────────
        df_s = self.df_datos.copy()
        df_s['stock_actual'] = pd.to_numeric(df_s.get('stock_actual', 0), errors='coerce').fillna(0)
        df_s['inventario_seguridad'] = pd.to_numeric(df_s.get('inventario_seguridad', 0), errors='coerce').fillna(0)

        riesgo = int((df_s['stock_actual'] < df_s['inventario_seguridad']).sum())
        seguro = int((df_s['stock_actual'] >= df_s['inventario_seguridad']).sum())

        if riesgo + seguro > 0:
            # Colores del gráfico de dona unificados con el concepto de Riesgo/Éxito
            self._grafico_pastel(
                self.ax_seguridad,
                sizes=[riesgo, seguro],
                labels=[f'En riesgo ({riesgo})', f'Seguro ({seguro})'],
                colors=[self.color_alerta, self.color_exito],
                title='Seguridad de Inventario'
            )

        # Ajuste de layout seguro antes del dibujado en el Canvas
        self.fig.tight_layout()
        self.canvas.draw()

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
                SELECT r.id_resultado, r.id_producto,
                       p.nombre AS Producto, p.stock_actual,
                       r.EOQ, r.PRO, r.inventario_seguridad,
                       r.fecha_calculo, r.ventas_anuales,
                       r.porcentaje, r.porcentaje_acumulado,
                       r.costo_anual_ordenar, r.costo_anual_conservacion,
                       r.costo_total, r.punto_reorden, r.clasificacion_ABC
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

            pd.DataFrame(datos).to_excel(ruta_archivo, index=False)
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente a:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al exportar:\n{e}")


if __name__ == "__main__":
    # Inicialización usando la estética por defecto de customtkinter
    ctk.set_appearance_mode("Light")
    root = ctk.CTk()
    root.title("Prueba de Reportes")
    root.geometry("1300x850")
    app = ReportesFrame(master=root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()