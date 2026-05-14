import customtkinter as ctk
from database.db_usuarios import UsuariosDB
from tkinter import messagebox

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success # Función que lanzará la MainWindow
        
        # Configuración de la ventana
        self.title("Acceso al Sistema - Peluquería")
        self.geometry("400x550")
        self.configure(fg_color="#FAF9F6")
        
        # Centrar ventana en pantalla
        self.eval('tk::PlaceWindow . center')

        # Interfaz de Usuario
        self.setup_ui()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="#F2F0EB", corner_radius=20, border_width=1, border_color="#E3D6C4")
        container.pack(pady=40, padx=30, fill="both", expand=True)

        ctk.CTkLabel(container, text="BIENVENIDO", font=("Inter", 28, "bold"), text_color="#5C4033").pack(pady=(40, 10))
        ctk.CTkLabel(container, text="Gestión de Peluquería", font=("Inter", 14), text_color="#A67B5B").pack(pady=(0, 15))
        ctk.CTkLabel(container, text="Accede con tu usuario y contraseña para continuar.", font=("Inter", 12), text_color="#5C4033").pack(pady=(0, 30))

        self.user_entry = ctk.CTkEntry(container, placeholder_text="Usuario ", width=320, height=45, corner_radius=12)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(container, placeholder_text="Contraseña", show="*", width=320, height=45, corner_radius=12)
        self.pass_entry.pack(pady=10)

        self.btn_login = ctk.CTkButton(container, text="INICIAR SESIÓN", 
                                        command=self.intentar_login,
                                        width=320, height=52, corner_radius=14,
                                        fg_color="#8B4513", hover_color="#A0522D",
                                        font=("Inter", 14, "bold"))
        self.btn_login.pack(pady=30)

        self.bind("<Return>", lambda event: self.intentar_login())

    def intentar_login(self):
        # Desactivamos para evitar ruidos en el proceso
        self.btn_login.configure(state="disabled")
        
        usuario = self.user_entry.get()
        password = self.pass_entry.get()

        db = UsuariosDB()
        datos_usuario = db.validar_usuario(usuario, password)

        if datos_usuario:
            self.on_login_success(datos_usuario) 
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            self.btn_login.configure(state="normal")