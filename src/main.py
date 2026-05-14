import customtkinter as ctk
from ui.main_window import MainWindow
from ui.login import LoginWindow
import sys
import os

def inicio():
    # 1. Configuración inicial
    os.system('cls' if os.name == 'nt' else 'clear')
    ctk.set_appearance_mode("Light") 
    ctk.set_default_color_theme("blue")

    # Contenedor para persistir los datos entre ventanas
    datos_finales = {"usuario": None}

    def capturar_exito(usuario):
        datos_finales["usuario"] = usuario
        # Detenemos el bucle pero no destruimos todavía
        login_v.quit()

    # --- FASE 1: LOGIN ---
    login_v = LoginWindow(on_login_success=capturar_exito)
    
    # Truco para Python 3.14: Forzar renderizado antes del loop
    login_v.update() 
    
    # Iniciamos el bucle del login
    login_v.mainloop()
    
    # Cuando salimos del mainloop (por login exitoso), matamos la ventana
    try:
        login_v.destroy()
    except:
        pass

    # --- FASE 2: PRINCIPAL ---
    # Solo si el usuario se logueó correctamente
    if datos_finales["usuario"]:
        # Recién ahora creamos la MainWindow
        app = MainWindow(datos_finales["usuario"])
        
        # Al cerrar la X de la principal, matamos todo el proceso
        app.protocol("WM_DELETE_WINDOW", sys.exit)
        app.mainloop()

if __name__ == "__main__":
    try:
        inicio()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        import traceback
        traceback.print_exc()