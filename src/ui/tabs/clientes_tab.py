import customtkinter as ctk
from database.db_agenda import AgendaDB

class ClientesTab:
    def __init__(self, master, parent):
        self.master = master  # El tab físico (este es el que hay que usar para Toplevel)
        self.parent = parent  # La MainWindow
        self.db = AgendaDB()
        self.setup_ui()

    def setup_ui(self):
        """Define la interfaz de búsqueda y la lista."""
        wrapper = ctk.CTkFrame(self.master, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(wrapper, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(header, text="CLIENTES", font=("Inter", 24, "bold"), text_color="#5C4033").pack(side="left")
        self.lbl_resultados = ctk.CTkLabel(header, text="", font=("Inter", 12), text_color="#5C4033")
        self.lbl_resultados.pack(side="right")

        f_busqueda = ctk.CTkFrame(wrapper, fg_color="#F2F0EB", corner_radius=16, border_width=1, border_color="#E3D6C4")
        f_busqueda.pack(fill="x", pady=(0, 20))

        self.ent_bus_cli = ctk.CTkEntry(f_busqueda, placeholder_text="Buscar cliente por nombre o apellido...", width=420)
        self.ent_bus_cli.pack(side="left", padx=(20, 10), pady=16)

        ctk.CTkButton(f_busqueda, text="🔍 Buscar", width=120, fg_color="#8B4513", hover_color="#A0522D", text_color="white", corner_radius=12,
                      font=("Inter", 12, "bold"), command=self.cargar_lista_clientes).pack(side="left", padx=(0, 20), pady=16)

        self.frame_lista_clientes = ctk.CTkScrollableFrame(wrapper, fg_color="transparent", corner_radius=16, border_width=1, border_color="#E3D6C4")
        self.frame_lista_clientes.pack(fill="both", expand=True)

        self.cargar_lista_clientes()

    def cargar_lista_clientes(self):
        """Refresca la lista de clientes según la búsqueda."""
        for widget in self.frame_lista_clientes.winfo_children():
            widget.destroy()

        busqueda = self.ent_bus_cli.get().strip().lower()
        if self.parent.usuario_actual['rol'] == 'empleado':
            id_empleado = self.parent.usuario_actual.get('idempleado')
            clientes = self.db.obtener_clientes_por_empleado(id_empleado) if id_empleado else []
        else:
            clientes = self.db.obtener_clientes_lista()

        clientes_filtrados = []
        for c in clientes:
            nombre_completo = f"{c['apellido'] or ''}, {c['nombre'] or ''}".strip()
            if busqueda and busqueda not in nombre_completo.lower():
                continue
            clientes_filtrados.append((c, nombre_completo))

        self.lbl_resultados.configure(text=f"{len(clientes_filtrados)} clientes encontrados")

        if not clientes_filtrados:
            mensaje = "No se encontraron clientes." if busqueda else "No hay clientes registrados todavía."
            ctk.CTkLabel(self.frame_lista_clientes, text=mensaje, font=("Inter", 14), text_color="#5C4033").pack(pady=80)
            return

        for cliente, nombre_completo in clientes_filtrados:
            row = ctk.CTkFrame(self.frame_lista_clientes, fg_color="#FFFFFF", border_width=1, border_color="#E5E1DA", corner_radius=16)
            row.pack(fill="x", pady=8, padx=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(fill="x", padx=18, pady=14)

            ctk.CTkLabel(info, text=nombre_completo.upper(), font=("Inter", 14, "bold"), text_color="#5C4033", anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"Email: {cliente.get('mail', 'sin email')}" if cliente.get('mail') else "Email: sin email", 
                          font=("Inter", 11), text_color="#5C4033", anchor="w").pack(fill="x", pady=(4, 0))

            boton_frame = ctk.CTkFrame(row, fg_color="transparent")
            boton_frame.pack(fill="x", padx=18, pady=(0, 14))

            ctk.CTkButton(boton_frame, text="📋 Ver Notas", width=130, fg_color="#8B4513", hover_color="#A0522D", corner_radius=12,
                          font=("Inter", 11, "bold"), command=lambda cli=cliente: self.abrir_notas_cliente(cli)).pack(side="right")

    def abrir_notas_cliente(self, cliente):
        """Abre la ventana de notas corrigiendo el error de referencia"""
        # CAMBIO CLAVE: Usamos self.master en lugar de self
        v = ctk.CTkToplevel(self.master) 
        v.title(f"Historial: {cliente['nombre']}")
        v.geometry("450x550")
        v.attributes("-topmost", True)
        
        ctk.CTkLabel(v, text=f"NOTAS DE {cliente['nombre'].upper()}", font=("Inter", 14, "bold")).pack(pady=15)
        
        txt_notas = ctk.CTkTextbox(v, width=400, height=350)
        txt_notas.pack(pady=10)
        
        if cliente['notas_relevantes']: 
            txt_notas.insert("1.0", cliente['notas_relevantes'])
        
        def guardar():
            if self.db.actualizar_notas_cliente(cliente['idcliente'], txt_notas.get("1.0", "end-1c")):
                v.destroy()
                self.cargar_lista_clientes()
        
        ctk.CTkButton(v, text="Guardar Cambios", fg_color="#8B4513", hover_color="#A0522D", corner_radius=8, command=guardar).pack(pady=20)