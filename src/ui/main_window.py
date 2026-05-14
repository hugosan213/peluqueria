import customtkinter as ctk
from ui.tabs.agenda_admin_tab import AgendaAdminTab
from ui.tabs.agenda_empleado_tab import AgendaEmpleadoTab
from ui.tabs.clientes_tab import ClientesTab
from ui.tabs.servicios_tab import ServiciosTab
from ui.tabs.stock_tab import StockTab
from ui.tabs.caja_tab import CajaTab
from ui.tabs.stats_tab import StatsTab
from ui.tabs.config import ConfigTab
from ui.tabs.perfil_tab import PerfilTab

class MainWindow(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario_actual = usuario
        self.title("Peluquería - Gestión Integral")
        self.geometry("1100x850")
        ctk.set_appearance_mode("Light") 
        self.configure(fg_color="#FAF9F6")

        top_bar = ctk.CTkFrame(self, fg_color="#E7D3B8", corner_radius=18, border_width=1, border_color="#C3AA83")
        top_bar.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(top_bar, text="Peluquería - Gestión Integral", font=("Inter", 16, "bold"), text_color="#5C4033").pack(side="left", padx=20, pady=10)

        self.btn_logout = ctk.CTkButton(top_bar, text="Cerrar Sesión 🔓", 
                                        fg_color="#8B4513", hover_color="#A0522D",
                                        width=150, height=38, corner_radius=14,
                                        font=("Inter", 12, "bold"), command=self.cerrar_sesion)
        self.btn_logout.pack(side="right", padx=16, pady=10)

        self.tabview = ctk.CTkTabview(self, fg_color="#F7E8D9", corner_radius=18,
                                      border_width=1, border_color="#C3AA83",
                                      segmented_button_fg_color="#F1D9B5", 
                                      segmented_button_selected_color="#8B4513", 
                                      text_color="black")
        self.tabview.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # Inicialización de pestañas modularizadas
        if self.usuario_actual['rol'] == 'admin':
            self.tab_agenda = AgendaAdminTab(self.tabview.add("📅 Agenda"), self)
        else:
            self.tab_agenda = AgendaEmpleadoTab(self.tabview.add("📅 Mi Agenda"), self)

        self.tab_clientes = ClientesTab(self.tabview.add("👥 Clientes"), self)
        self.tab_perfil = PerfilTab(self.tabview.add("👤 Mi Cuenta"), self)
        self.tab_servicios = ServiciosTab(self.tabview.add("✂️ Precios"), self)
        self.tab_stock = StockTab(self.tabview.add("📦 Stock"), self)

        if self.usuario_actual['rol'] == 'admin':
            self.tab_caja_obj = CajaTab(self.tabview.add("💰 Caja"), self)
            self.tab_config = ConfigTab(self.tabview.add("⚙️ Config."), self)
            self.tab_stats_obj = StatsTab(self.tabview.add("📊 Estadísticas"), self)

    

    def cerrar_sesion(self):
        from tkinter import messagebox
        import sys
        import os

        # 1. Preguntar al usuario para evitar cierres accidentales
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro que querés salir?"):
            try:
                # 2. Obtener la ruta del ejecutable de Python y del script actual (main.py)
                python = sys.executable
                
                # 3. Destruir la ventana actual y liberar recursos de la interfaz
                self.destroy()
                
                # 4. Reiniciar la aplicación desde cero
                # os.execl reemplaza el proceso actual por uno nuevo,
                # garantizando que el Login aparezca de forma estable.
                os.execl(python, python, *sys.argv)
                
            except Exception as e:
                # En caso de error crítico, al menos cerramos la app
                print(f"Error al reiniciar sesión: {e}")
                sys.exit()
    
