import os
import tkinter as tk
from tkinter import ttk
from tkinter import font
from gestion_inventarios import GestionInventariosFrame
from evaluar_inventarios import EvaluarInventariosFrame
from inventario_seguridad import InventarioSeguridadFrame
from reportes import ReportesFrame


class InventarioApp(tk.Tk):
    """
    Clase principal para la aplicación de gestión de inventarios de la Ferretería Simkin.
    Hereda de tk.Tk para crear la ventana principal.
    """
    
    def __init__(self):
        """Inicializa la aplicación y configura la ventana principal."""
        super().__init__()
        
        # Configurar ventana principal
        self.title("Sistema de Inventarios - Ferretería Simkin")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        # Definir colores
        self.color_fondo = "#FFFFFF"
        self.color_panel = "#0A1F44"
        self.color_hover = "#123D6B"
        
        # Variables para gestión de frames
        self.frame_actual = None
        self.area_principal = None
        self.logo_image = None
        
        # Aplicar estilos
        self.aplicar_estilos()
        
        # Crear la interfaz
        self.crear_estructura_principal()
        
    def aplicar_estilos(self):
        """Define los estilos personalizados para la aplicación usando ttk.Style()."""
        self.style = ttk.Style()
        
        # Configurar tema
        self.style.theme_use('clam')
        
        # Estilo para botones del panel lateral
        self.style.configure(
            'NavButton.TButton',
            background=self.color_panel,
            foreground='white',
            font=('Segoe UI', 11),
            relief='flat',
            padding=10,
            borderwidth=0
        )
        
        # Estilo para labels
        self.style.configure(
            'Welcome.TLabel',
            background=self.color_fondo,
            foreground=self.color_panel,
            font=('Helvetica', 14)
        )
        
    def crear_estructura_principal(self):
        """Crea la estructura principal de la aplicación (panel lateral + área principal)."""
        # Configurar el grid para la ventana principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Crear panel lateral
        self.crear_panel_lateral()
        
        # Crear área principal
        self.crear_area_principal()
        
    def crear_panel_lateral(self):
        """
        Crea el panel de navegación lateral izquierdo.
        - Ancho fijo de 200 píxeles
        - Color de fondo azul oscuro
        - Contiene botones verticales elegantes
        """
        # Frame del panel lateral
        panel_lateral = tk.Frame(
            self,
            width=200,
            bg=self.color_panel,
            relief=tk.FLAT,
            bd=0
        )
        panel_lateral.grid(row=0, column=0, sticky='nswe')
        panel_lateral.grid_propagate(False)
        
        # Configurar grid del panel
        panel_lateral.grid_rowconfigure(0, minsize=20)  # Espacio superior
        
        # Definir botones
        botones = [
            "Gestionar Inventarios",
            "Evaluar Inventarios",
            "Inventario de Seguridad",
            "Dashboard"
        ]
        
        # Crear botones
        for idx, nombre_boton in enumerate(botones, start=1):
            btn = tk.Button(
                panel_lateral,
                text=nombre_boton,
                bg=self.color_panel,
                fg='white',
                font=('Segoe UI', 11),
                relief=tk.FLAT,
                cursor='hand2',
                padx=15,
                pady=15,
                command=lambda nb=nombre_boton: self.on_boton_click(nb)
            )
            btn.grid(row=idx, column=0, sticky='ew', padx=10, pady=8)
            
            # Agregar efecto hover
            btn.bind("<Enter>", lambda e, b=btn: self.on_hover_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_hover_leave(b))
        
    def crear_area_principal(self):
        """
        Crea el área principal de la aplicación.
        - Frame blanco que ocupa el resto de la ventana
        - Contiene la vista de Reportes inicialmente
        """
        # Frame principal
        self.area_principal = tk.Frame(
            self,
            bg=self.color_fondo,
            relief=tk.FLAT,
            bd=0
        )
        self.area_principal.grid(row=0, column=1, sticky='nswe')
        self.area_principal.grid_rowconfigure(0, weight=1)
        self.area_principal.grid_columnconfigure(0, weight=1)
        
        # Mostrar vista inicial de bienvenida con logo
        self.mostrar_vista_bienvenida()
        
    def mostrar_vista_bienvenida(self):
        """Muestra la vista inicial con el mensaje de bienvenida y el logo centrado."""
        # Limpiar frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()

        bienvenida_frame = tk.Frame(self.area_principal, bg=self.color_fondo)
        bienvenida_frame.grid(row=0, column=0, sticky='nsew')
        bienvenida_frame.grid_rowconfigure(0, weight=1)
        bienvenida_frame.grid_rowconfigure(1, weight=0)
        bienvenida_frame.grid_rowconfigure(2, weight=1)
        bienvenida_frame.grid_columnconfigure(0, weight=1)

        # Cargar logo
        logo_path = os.path.join(os.path.dirname(__file__), 'Misc', 'logo ferreteria.png')
        try:
            self.logo_image = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(
                bienvenida_frame,
                image=self.logo_image,
                bg=self.color_fondo
            )
            logo_label.grid(row=1, column=0, pady=(0, 10))
        except Exception as e:
            print(f"No se pudo cargar el logo de bienvenida: {e}")

        

        self.frame_actual = bienvenida_frame
    
    def cambiar_frame(self, nuevo_frame_clase):
        """
        Cambia el contenido del área principal por un nuevo frame.
        
        Args:
            nuevo_frame_clase: Clase del frame a mostrar (ej. GestionInventariosFrame)
        """
        # Limpiar frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        
        # Crear nuevo frame
        self.frame_actual = nuevo_frame_clase(self.area_principal)
        self.frame_actual.grid(row=0, column=0, sticky='nswe')
    
    def on_boton_click(self, nombre_boton):
        """Maneja el evento de clic en un botón del panel lateral."""
        print(f"Botón presionado: {nombre_boton}")
        
        # Manejar diferentes secciones
        if nombre_boton == "Evaluar Inventarios":
            self.cambiar_frame(EvaluarInventariosFrame)
        elif nombre_boton == "Gestionar Inventarios":
            self.cambiar_frame(GestionInventariosFrame)
        elif nombre_boton == "Inventario de Seguridad":
            self.cambiar_frame(InventarioSeguridadFrame)
        elif nombre_boton == "Dashboard":
            self.cambiar_frame(ReportesFrame)
    
    def on_hover_enter(self, button):
        """Cambia el color del botón al pasar el mouse (hover)."""
        button.config(bg=self.color_hover)
        
    def on_hover_leave(self, button):
        """Restaura el color original del botón al salir el mouse."""
        button.config(bg=self.color_panel)


def main():
    app = InventarioApp()
    app.mainloop()


if __name__ == "__main__":
    main()
