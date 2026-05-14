import customtkinter as ctk
from database.db_usuarios import UsuariosDB
from tkinter import messagebox
class ConfigTab:
    def __init__(self, master, main_window):
        self.master = master
        self.main_window = main_window
        self.db = UsuariosDB()
        self.setup_tab_gestion()

    def setup_tab_gestion(self):
        # Contenedor principal con scroll por si hay muchos empleados
        self.main_container = ctk.CTkScrollableFrame(self.master, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # --- SECCIÓN: REGISTRO ---
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(header_frame, text="GESTIÓN DE PERSONAL", font=("Inter", 24, "bold"), text_color="#5C4033").pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Registra nuevos peluqueros y administra sus accesos al sistema.", 
                     font=("Inter", 13), text_color="#8B735B").pack(anchor="w")

        # Tarjeta del Formulario
        form_card = ctk.CTkFrame(self.main_container, fg_color="#F2F0EB", corner_radius=15, border_width=1, border_color="#E3D6C4")
        form_card.pack(fill="x", pady=10)

        grid_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        grid_frame.pack(pady=20, padx=20, fill="x")

        # Entradas organizadas (Simulando columnas)
        # Fila 1: Nombre y Apellido
        f1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f1.pack(fill="x", pady=5)
        self.en_nom = ctk.CTkEntry(f1, placeholder_text="Nombre", height=40, corner_radius=10); self.en_nom.pack(side="left", expand=True, fill="x", padx=(0,10))
        self.en_ape = ctk.CTkEntry(f1, placeholder_text="Apellido", height=40, corner_radius=10); self.en_ape.pack(side="left", expand=True, fill="x")

        # Fila 2: DNI e Email
        f2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f2.pack(fill="x", pady=5)
        self.en_dni = ctk.CTkEntry(f2, placeholder_text="DNI (Será el usuario)", height=40, corner_radius=10); self.en_dni.pack(side="left", expand=True, fill="x", padx=(0,10))
        self.en_mai = ctk.CTkEntry(f2, placeholder_text="Email (Opcional)", height=40, corner_radius=10); self.en_mai.pack(side="left", expand=True, fill="x")

        # Fila 3: Contraseña
        self.en_pass = ctk.CTkEntry(grid_frame, placeholder_text="Contraseña de acceso", height=40, corner_radius=10, show="*")
        self.en_pass.pack(fill="x", pady=5)

        self.lbl_feedback = ctk.CTkLabel(grid_frame, text="", font=("Inter", 12, "bold"))
        self.lbl_feedback.pack(pady=5)

        ctk.CTkButton(form_card, text="➕ REGISTRAR EMPLEADO", fg_color="#8B4513", hover_color="#A0522D", 
                      height=45, corner_radius=12, font=("Inter", 13, "bold"), 
                      command=self.guardar_empleado).pack(pady=(0, 25), padx=40, fill="x")

        # --- SECCIÓN: LISTADO ---
        ctk.CTkLabel(self.main_container, text="EQUIPO DE TRABAJO", font=("Inter", 18, "bold"), text_color="#5C4033").pack(anchor="w", pady=(20, 10))
        
        self.lista_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.lista_container.pack(fill="x", expand=True)

        self.cargar_empleados()

    def validar_campos(self):
        vals = [self.en_nom.get(), self.en_ape.get(), self.en_dni.get(), self.en_pass.get()]
        if not all(v.strip() for v in vals):
            self.lbl_feedback.configure(text="⚠ Todos los campos (excepto email) son obligatorios", text_color="#9D2B2B")
            return False
        return True

    def guardar_empleado(self):
        if not self.validar_campos(): return

        nom, ape, dni, mai, pas = [e.get().strip() for e in [self.en_nom, self.en_ape, self.en_dni, self.en_mai, self.en_pass]]

        if self.db.agregar_empleado_completo(nom, ape, mai, dni, pas):
            self.lbl_feedback.configure(text=f"✅ {nom} registrado correctamente", text_color="#27632a")
            for e in [self.en_nom, self.en_ape, self.en_dni, self.en_mai, self.en_pass]: e.delete(0, 'end')
            self.cargar_empleados()
        else:
            self.lbl_feedback.configure(text="❌ Error: El DNI ya existe", text_color="#9D2B2B")

    def cargar_empleados(self):
        """Muestra la lista de empleados con el botón de Reset Password."""
        # Limpiamos la lista actual
        for widget in self.lista_container.winfo_children():
            widget.destroy()

        # Obtenemos los empleados de la base de datos
        empleados = self.db.obtener_empleados()

        if not empleados:
            ctk.CTkLabel(self.lista_container, text="No hay personal registrado.", 
                         font=("Inter", 13, "italic")).pack(pady=20)
            return

        for emp in empleados:
            # Tarjeta de empleado
            card = ctk.CTkFrame(self.lista_container, fg_color="#FFFFFF", corner_radius=12, 
                                border_width=1, border_color="#E5E1DA")
            card.pack(fill="x", pady=5, padx=5)

            # Contenedor de texto (Nombre)
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=20, pady=15, fill="x", expand=True)

            ctk.CTkLabel(info_frame, text=f"👤 {emp['nombre']} {emp['apellido']}".upper(), 
                         font=("Inter", 14, "bold"), text_color="#5C4033", anchor="w").pack(fill="x")

            # --- CONTENEDOR DE BOTONES (A la derecha) ---
            actions_frame = ctk.CTkFrame(card, fg_color="transparent")
            actions_frame.pack(side="right", padx=10)

            # NUEVO: Botón Reset Password (La llave)
            btn_reset = ctk.CTkButton(actions_frame, text="🔑", width=40, height=40,
                                      fg_color="#E3D6C4", text_color="#5C4033", hover_color="#D3C5B4",
                                      command=lambda e=emp: self.abrir_modal_reset_password(e))
            btn_reset.pack(side="left", padx=5)

            # Botón Eliminar (el que ya tenías)
            def confirmar_borrado(id_e=emp['idempleado'], nombre=emp['nombre']):
                if messagebox.askyesno("Confirmar Baja", f"¿Estás seguro de eliminar a {nombre}?"):
                    if self.db.eliminar_empleado(id_e):
                        self.cargar_empleados()
            
            btn_del = ctk.CTkButton(actions_frame, text="🗑", width=40, height=40, 
                                    fg_color="#FADBD8", hover_color="#F1948A", text_color="#943126",
                                    command=confirmar_borrado)
            btn_del.pack(side="left", padx=5)

    def abrir_crear_usuario(self, empleado):
        v = ctk.CTkToplevel(self.master)
        v.title("Crear usuario para empleado")
        v.geometry("420x260")
        v.attributes("-topmost", True)
        v.configure(fg_color="#FAF9F6")

        ctk.CTkLabel(v, text=f"Crear acceso para {empleado.get('nombre', '')} {empleado.get('apellido', '')}", font=("Inter", 14, "bold"), text_color="#5C4033").pack(pady=(20, 10), padx=20)
        ctk.CTkLabel(v, text=f"Usuario: {empleado.get('dni', '')}", font=("Inter", 12), text_color="#5C4033").pack(padx=20)

        self.en_pass_crear = ctk.CTkEntry(v, placeholder_text="Contraseña", width=360, show="*")
        self.en_pass_crear.pack(pady=20)

        lbl_error = ctk.CTkLabel(v, text="", font=("Inter", 11), text_color="#9D2B2B")
        lbl_error.pack(pady=(0, 10))

        def guardar_usuario():
            password = self.en_pass_crear.get().strip()
            if not password:
                lbl_error.configure(text="Debe ingresar una contraseña.")
                return
            if self.db.crear_usuario_para_empleado(empleado['idempleado'], password):
                v.destroy()
                self.lbl_feedback.configure(text=f"Usuario creado para {empleado.get('nombre', '')}.", text_color="#27632a")
                self.cargar_empleados()
            else:
                lbl_error.configure(text="No se pudo crear el usuario. Revisa la conexión.")

        ctk.CTkButton(v, text="Crear usuario", fg_color="#8B4513", hover_color="#A0522D", width=180, height=44, corner_radius=12,
                      font=("Inter", 12, "bold"), command=guardar_usuario).pack(pady=10)
        
    # --- DENTRO DE ConfigTab ---

    def actualizar_lista_empleados(self):
        for widget in self.scroll_empleados.winfo_children():
            widget.destroy()

        empleados = self.db.obtener_empleados_completos()
        
        for emp in empleados:
            card = ctk.CTkFrame(self.scroll_empleados, fg_color="#F2F0EB", corner_radius=10)
            card.pack(fill="x", pady=5)

            # Info del empleado
            info = f"{emp['nombre']} {emp['apellido']} | DNI: {emp['dni']} | Rol: {emp.get('rol', 'Sin Usuario')}"
            ctk.CTkLabel(card, text=info, font=("Inter", 13)).pack(side="left", padx=15, pady=10)

            # BOTÓN RESET PASSWORD (🔑)
            btn_reset = ctk.CTkButton(card, text="🔑 Reset Pass", width=100, height=28,
                                      fg_color="#E3D6C4", text_color="#5C4033", hover_color="#D3C5B4",
                                      command=lambda e=emp: self.abrir_modal_reset_password(e))
            btn_reset.pack(side="right", padx=10)

    def abrir_modal_reset_password(self, empleado):
        """Ventana para que el admin cambie la pass de un empleado."""
        v = ctk.CTkToplevel(self.master)
        v.title(f"Resetear acceso - {empleado['nombre']}")
        v.geometry("400x320")
        v.attributes("-topmost", True)
        v.grab_set()

        ctk.CTkLabel(v, text="RESTABLECER CONTRASEÑA", font=("Inter", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(v, text=f"Empleado: {empleado['nombre']} {empleado['apellido']}", font=("Inter", 12)).pack()

        en_nueva_pass = ctk.CTkEntry(v, placeholder_text="Nueva contraseña temporal", width=300, show="*")
        en_nueva_pass.pack(pady=20)

        def confirmar():
            nueva_p = en_nueva_pass.get().strip()
            if not nueva_p:
                messagebox.showwarning("Atención", "Ingrese la nueva contraseña.")
                return
            
            # Aquí usamos self.db que definimos en el __init__
            if self.db.forzar_cambio_password(empleado['idempleado'], nueva_p):
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
                v.destroy()
                self.actualizar_lista_empleados() # Refrescamos por si cambió el rol
            else:
                messagebox.showerror("Error", "No se pudo actualizar. Verifique si el empleado tiene un usuario creado.")

        ctk.CTkButton(v, text="Guardar Cambios", fg_color="#5C4033", command=confirmar).pack(pady=10)