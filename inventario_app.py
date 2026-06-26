import os
import tkinter as tk
import customtkinter as ctk
from gestion_inventarios import GestionInventariosFrame
from evaluar_inventarios import EvaluarInventariosFrame
from inventario_seguridad import InventarioSeguridadFrame
from reportes import ReportesFrame


class InventarioApp(ctk.CTk):  # Hereda de CTk para soportar el escalado dinámico y temas
    """
    Clase principal moderna para la aplicación de gestión de inventarios de la Ferretería Simkin.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurar ventana principal
        self.title("Sistema de Inventarios - Ferretería Simkin")
        self.geometry("1200x750")  # Un poco más amplia para dashboards cómodos
        self.resizable(True, True)
        
        # Configurar la estética global (Modo claro por defecto)
        ctk.set_appearance_mode("Light")
        
        # Paleta de colores consistente con ReportesFrame
        self.color_fondo = "#F8FAFC"       # Gris suave moderno para áreas de contenido
        self.color_panel = "#0A1F44"       # Azul oscuro profundo para la barra lateral
        self.color_hover = "#1E3A5F"       # Azul intermedio para el estado hover
        self.color_activo = "#5A7FB8"      # Azul claro/grisáceo para marcar pestaña activa
        
        # Variables para gestión de vistas y tracking de navegación
        self.frame_actual = None
        self.area_principal = None
        self.logo_image = None
        self.botones_menu = {}
        self.boton_activo = None
        
        # Crear la interfaz optimizada
        self.crear_estructura_principal()
        
    def crear_estructura_principal(self):
        """Crea la arquitectura base usando un Grid layout limpio."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Crear panel lateral con el fondo oscuro institucional
        self.crear_panel_lateral()
        
        # Crear área de contenido con el fondo gris suave moderno
        self.crear_area_principal()
        
    def crear_panel_lateral(self):
        """Crea la barra de navegación lateral izquierda usando CTk widgets."""
        panel_lateral = ctk.CTkFrame(
            self,
            width=240,  # Un poco más ancho para evitar que se corten textos como 'Inventario de Seguridad'
            fg_color=self.color_panel,
            corner_radius=0
        )
        panel_lateral.grid(row=0, column=0, sticky='nswe')
        panel_lateral.grid_propagate(False)
        
        # Cabecera / Título de la App en el Sidebar
        lbl_brand = ctk.CTkLabel(
            panel_lateral,
            text="🛠️ Simkin Ferretería",
            text_color="white",
            font=("Segoe UI", 16, "bold")
        )
        lbl_brand.pack(anchor='w', padx=20, pady=(30, 25))
        
        # Configuración de ítems de menú (Separamos el ícono del texto para controlar su alineación)
        opciones_menu = [
            ("Gestionar Inventarios", "📦", GestionInventariosFrame),
            ("Evaluar Inventarios","📊", EvaluarInventariosFrame),
            ("Inventario de Seguridad","🔗", InventarioSeguridadFrame),
            ("Dashboard","📈", ReportesFrame)
        ]
        
        # Contenedor para agrupar los botones verticalmente
        menu_container = ctk.CTkFrame(panel_lateral, fg_color="transparent")
        menu_container.pack(fill=tk.X, padx=10, anchor='n')
        
        for nombre, icono, frame_clase in opciones_menu:
            # Añadimos unos espacios antes del ícono para empujarlo a la derecha y alinearlo de forma uniforme
            texto_formateado = f"   {icono}     {nombre}" 
            
            btn = ctk.CTkButton(
                menu_container,
                text=texto_formateado,
                anchor="w",                      # Forzar alineación a la izquierda
                font=("Segoe UI", 14, "bold"),   
                fg_color="transparent",          
                hover_color=self.color_hover,
                text_color="#E2E8F0",
                height=45,                       # Le da una excelente altura vertical al botón
                corner_radius=8,
                command=lambda name=nombre, f_class=frame_clase: self.navegar_a(name, f_class)
            )
            btn.pack(fill=tk.X, pady=4)
            
            # Guardamos la referencia para poder cambiar su color activo después
            self.botones_menu[nombre] = btn

    def crear_area_principal(self):
        """Crea el contenedor dinámico para las diferentes pantallas."""
        self.area_principal = ctk.CTkFrame(
            self,
            fg_color=self.color_fondo,
            corner_radius=0
        )
        self.area_principal.grid(row=0, column=1, sticky='nswe')
        self.area_principal.grid_rowconfigure(0, weight=1)
        self.area_principal.grid_columnconfigure(0, weight=1)
        
        # Mostrar la pantalla de bienvenida por defecto al iniciar
        self.mostrar_vista_bienvenida()
        
    def mostrar_vista_bienvenida(self):
        """Limpia el visor y monta una tarjeta de bienvenida minimalista."""
        if self.frame_actual:
            self.frame_actual.destroy()

        bienvenida_frame = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        bienvenida_frame.grid(row=0, column=0, sticky='nsew')
        
        # Centrado usando grid interno flexible
        bienvenida_frame.grid_rowconfigure((0, 2), weight=1)
        bienvenida_frame.grid_columnconfigure(0, weight=1)

        # Intento de carga de Logo institucional
        logo_path = os.path.join(os.path.dirname(__file__), 'Misc', 'logo ferreteria.png')
        try:
            # Si usas PIL/Pillow puedes usar ctk.CTkImage para mejor calidad,
            # aquí mantenemos PhotoImage nativo por compatibilidad estructural
            self.logo_image = tk.PhotoImage(file=logo_path)
            logo_label = ctk.CTkLabel(
                bienvenida_frame,
                image=self.logo_image,
                text=""
            )
            logo_label.grid(row=1, column=0, pady=20)
        except Exception as e:
            # Fallback en texto si no localiza la imagen en la ruta
            lbl_fallback = ctk.CTkLabel(
                bienvenida_frame,
                text=" F E R R E T E R Í A   S I M K I N ",
                text_color=self.color_panel,
                font=("Segoe UI", 20, "bold")
            )
            lbl_fallback.grid(row=1, column=0, pady=20)

        self.frame_actual = bienvenida_frame

    def navegar_a(self, nombre_boton, nuevo_frame_clase):
        """
        Controla el switch de pantallas y refresca el estado visual de los botones del menú.
        """
        print(f"Navegando hacia: {nombre_boton}")
        
        # 1. Gestionar el estado visual de los botones (Foco Activo)
        if self.boton_activo:
            # Restaurar el botón anteriormente seleccionado a su estado base plano
            self.boton_activo.configure(fg_color="transparent", text_color="#E2E8F0")
            
        # Resaltar el nuevo botón presionado
        btn_actual = self.botones_menu[nombre_boton]
        btn_actual.configure(fg_color=self.color_activo, text_color="white")
        self.boton_activo = btn_actual
        
        # 2. Destruir el frame anterior e instanciar el seleccionado
        if self.frame_actual:
            self.frame_actual.destroy()
        
        self.frame_actual = nuevo_frame_clase(self.area_principal)
        self.frame_actual.grid(row=0, column=0, sticky='nswe')


def main():
    app = InventarioApp()
    app.mainloop()


if __name__ == "__main__":
    main()