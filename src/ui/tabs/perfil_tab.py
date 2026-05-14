import customtkinter as ctk
from database.db_usuarios import UsuariosDB

class PerfilTab:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        self.db = UsuariosDB()
        self.setup_ui()

    def setup_ui(self):
        # Contenedor principal con scroll para consistencia
        self.container = ctk.CTkScrollableFrame(self.master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- HEADER ---
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="MI CUENTA", font=("Inter", 24, "bold"), text_color="#5C4033").pack(anchor="w")
        ctk.CTkLabel(header, text="Gestioná tu acceso personal al sistema de forma segura.", 
                     font=("Inter", 13), text_color="#8B735B").pack(anchor="w")

        # --- TARJETA DE INFORMACIÓN ACTUAL ---
        # Sacamos los datos del parent (MainWindow)
        current_username = self.parent.usuario_actual.get('nombre_usuario', '')
        current_rol = self.parent.usuario_actual.get('rol', 'empleado')
        nombre_real = f"{self.parent.usuario_actual.get('nombre', '')} {self.parent.usuario_actual.get('apellido', '')}"

        info_card = ctk.CTkFrame(self.container, fg_color="#F2F0EB", corner_radius=15, border_width=1, border_color="#E3D6C4")
        info_card.pack(fill="x", pady=10)

        inner_info = ctk.CTkFrame(info_card, fg_color="transparent")
        inner_info.pack(padx=25, pady=20, fill="x")

        ctk.CTkLabel(inner_info, text=f"👤 {nombre_real.upper()}", font=("Inter", 18, "bold"), text_color="#5C4033", anchor="w").pack(fill="x")
        ctk.CTkLabel(inner_info, text=f"Rol: {current_rol.capitalize()}  |  Usuario: {current_username}", 
                     font=("Inter", 12, "italic"), text_color="#8B735B", anchor="w").pack(fill="x")

        # --- TARJETA DE EDICIÓN ---
        edit_card = ctk.CTkFrame(self.container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E1DA")
        edit_card.pack(fill="x", pady=10)

        form_frame = ctk.CTkFrame(edit_card, fg_color="transparent")
        form_frame.pack(pady=25, padx=25, fill="x")

        ctk.CTkLabel(form_frame, text="ACTUALIZAR CREDENCIALES", font=("Inter", 14, "bold"), text_color="#5C4033").pack(pady=(0, 15))

        self.en_usuario = ctk.CTkEntry(form_frame, placeholder_text="Nuevo nombre de usuario", height=40, corner_radius=10)
        self.en_usuario.pack(fill="x", pady=5)
        self.en_usuario.insert(0, current_username) # Ya lo dejamos cargado para que sea más fácil editar

        self.en_password = ctk.CTkEntry(form_frame, placeholder_text="Nueva contraseña", height=40, corner_radius=10, show="*")
        self.en_password.pack(fill="x", pady=5)

        self.en_password_confirm = ctk.CTkEntry(form_frame, placeholder_text="Confirmar nueva contraseña", height=40, corner_radius=10, show="*")
        self.en_password_confirm.pack(fill="x", pady=5)

        self.lbl_feedback = ctk.CTkLabel(form_frame, text="", font=("Inter", 12, "bold"))
        self.lbl_feedback.pack(pady=10)

        ctk.CTkButton(form_frame, text="💾 GUARDAR CAMBIOS", fg_color="#8B4513", hover_color="#A0522D", 
                      height=45, corner_radius=12, font=("Inter", 13, "bold"), 
                      command=self.actualizar_credenciales).pack(pady=(10, 0), fill="x")

    def actualizar_credenciales(self):
        nuevo_usuario = self.en_usuario.get().strip()
        nueva_contrasena = self.en_password.get().strip()
        confirmar = self.en_password_confirm.get().strip()

        if not nuevo_usuario and not nueva_contrasena:
            self.lbl_feedback.configure(text="Ingresá un nuevo usuario o nueva contraseña.", text_color="#9D2B2B")
            return

        if nueva_contrasena and nueva_contrasena != confirmar:
            self.lbl_feedback.configure(text="Las contraseñas no coinciden.", text_color="#9D2B2B")
            return

        usuario_actual = self.parent.usuario_actual.get('nombre_usuario', '')
        id_usuario = self.parent.usuario_actual.get('idusuario')

        if nuevo_usuario and nuevo_usuario != usuario_actual:
            if self.db.usuario_existe(nuevo_usuario):
                self.lbl_feedback.configure(text="Ese usuario ya está en uso. Elegí otro.", text_color="#9D2B2B")
                return

        if not nueva_contrasena:
            nueva_contrasena = None

        if not nuevo_usuario:
            nuevo_usuario = usuario_actual

        if self.db.actualizar_credenciales_usuario(id_usuario, nuevo_usuario, nueva_contrasena):
            self.lbl_feedback.configure(text="Credenciales actualizadas correctamente.", text_color="#27632a")
            self.parent.usuario_actual['nombre_usuario'] = nuevo_usuario
            if nueva_contrasena:
                self.parent.usuario_actual['password'] = nueva_contrasena
            self.en_usuario.delete(0, 'end')
            self.en_password.delete(0, 'end')
            self.en_password_confirm.delete(0, 'end')
        else:
            self.lbl_feedback.configure(text="No se pudieron actualizar las credenciales.", text_color="#9D2B2B")
