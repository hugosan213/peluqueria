import customtkinter as ctk
from database.db_agenda import AgendaDB
from datetime import datetime

class AgendaEmpleadoTab:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        self.db = AgendaDB()
        self.id_empleado = self.parent.usuario_actual.get('idempleado')
        if not self.id_empleado and self.parent.usuario_actual.get('rol') == 'empleado':
            posible_dni = self.parent.usuario_actual.get('dni') or self.parent.usuario_actual.get('nombre_usuario')
            if posible_dni:
                self.id_empleado = self.db.obtener_id_empleado_por_dni(posible_dni)
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=20)
        ctk.CTkLabel(header, text="MI AGENDA", font=("Inter", 24, "bold"), text_color="#5C4033").pack(side="left")

        self.sidebar = ctk.CTkFrame(self.master, width=240, fg_color="#F2F0EB", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.sidebar.pack(side="left", fill="y", padx=(20, 10), pady=10)
        
        ctk.CTkButton(self.sidebar, text="➕ Nueva Reserva", fg_color="#8B4513", hover_color="#A0522D", corner_radius=12,
                      font=("Inter", 12, "bold"), command=self.abrir_formulario).pack(pady=(20, 10), padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="🔄 Actualizar", fg_color="#C49E6F", hover_color="#E0C085", corner_radius=12,
                      font=("Inter", 12, "bold"), command=self.cargar_datos).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="📜 Ver Historial", fg_color="#C49E6F", hover_color="#E0C085", corner_radius=12,
                      font=("Inter", 12, "bold"), command=self.cargar_historial).pack(pady=10, padx=20, fill="x")
        
        self.frame_agenda = ctk.CTkScrollableFrame(self.master, fg_color="#F7E8D9", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.frame_agenda.pack(side="right", fill="both", expand=True, padx=(0,20), pady=10)

    def cargar_datos(self):
        for widget in self.frame_agenda.winfo_children():
            widget.destroy()

        if not self.id_empleado:
            ctk.CTkLabel(self.frame_agenda, text="No se encontró tu empleado. Comunicate con el administrador.", font=("Inter", 14), text_color="#A52A2A").pack(pady=80)
            return

        agenda = self.db.obtener_agenda_por_empleado(self.id_empleado)
        if not agenda:
            ctk.CTkLabel(self.frame_agenda, text="No tenés turnos asignados. Creá un nuevo turno.", font=("Inter", 14), text_color="#5C4033").pack(pady=80)
            return

        for t in agenda:
            card = ctk.CTkFrame(self.frame_agenda, fg_color="#FFFFFF", border_width=1, border_color="#E5E1DA", corner_radius=15)
            card.pack(fill="x", pady=8, padx=16)

            nombre_cliente = t.get('Cliente')
            if not nombre_cliente or str(nombre_cliente).strip() in ["", "None", "NULL"]:
                n = t.get('nombre', t.get('Nombre', ''))
                a = t.get('apellido', t.get('Apellido', ''))
                nombre_cliente = f"{n} {a}".strip() if (n or a) else "Cliente Nuevo"

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=18, pady=(16, 8))
            ctk.CTkLabel(top_row, text=f"🕒 {t['Fecha_Hora']}", font=("Inter", 13, "bold"), text_color="#5C4033").pack(side="left")
            ctk.CTkLabel(top_row, text=f"👤 {nombre_cliente}", font=("Inter", 12), text_color="#5C4033").pack(side="right")

            info_row = ctk.CTkFrame(card, fg_color="transparent")
            info_row.pack(fill="x", padx=18, pady=(0, 8))
            ctk.CTkLabel(info_row, text=f"✂️ Servicio: {t['Servicio']}", font=("Inter", 12), text_color="#5C4033").pack(side="left")
            ctk.CTkLabel(info_row, text=f"💼 Estado: {t.get('Estado', 'Pendiente')}", font=("Inter", 12), text_color="#5C4033").pack(side="right")

            if t.get('Estado') != 'finalizada':
                ctk.CTkButton(card, text="💵 Cobrar", width=100, fg_color="#8B4513", hover_color="#A0522D", corner_radius=12,
                              font=("Inter", 11, "bold"), command=lambda trn=t: self.abrir_ventana_cobro(trn)).pack(padx=18, pady=(0, 16), anchor="e")

    def cargar_historial(self):
        """Muestra el historial de cortes finalizados respetando el filtro de peluquero seleccionado."""
        for widget in self.frame_agenda.winfo_children():
            widget.destroy()
        
        # Título dinámico según el filtro
        titulo = "HISTORIAL GLOBAL DE CORTES" if self.filtro_actual == "Todos" else f"HISTORIAL DE: {self.filtro_actual}"
        ctk.CTkLabel(self.frame_agenda, text=titulo, font=("Inter", 18, "bold"), text_color="#5C4033").pack(pady=20)
        
        # 1. Obtenemos el historial base (los últimos 50 cortes finalizados)
        historial = self.db_agenda.obtener_historial_cortes()
        
        # 2. Aplicamos el filtrado por peluquero si no es "Todos"
        if self.filtro_actual != "Todos":
            historial = [t for t in historial if t.get('Peluquero') == self.filtro_actual]

        if not historial:
            msg = "No hay cortes finalizados registrados." if self.filtro_actual == "Todos" else f"No hay historial para {self.filtro_actual}."
            ctk.CTkLabel(self.frame_agenda, text=msg, font=("Inter", 14), text_color="#5C4033").pack(pady=80)
            return
        
        # 3. Renderizado de las tarjetas de historial
        for t in historial:
            card = ctk.CTkFrame(self.frame_agenda, fg_color="#FFFFFF", border_width=1, border_color="#E5E1DA", corner_radius=15)
            card.pack(fill="x", pady=8, padx=16)
            
            # Fila superior: Fecha y Cliente
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=18, pady=(15, 5))
            ctk.CTkLabel(top_row, text=f"🕒 {t['Fecha_Hora']}", font=("Inter", 13, "bold"), text_color="#5C4033").pack(side="left")
            ctk.CTkLabel(top_row, text=f"👤 {t['Cliente']}", font=("Inter", 13), text_color="#5C4033").pack(side="right")
            
            # Fila inferior: Servicio y Peluquero (para saber quién lo hizo en la vista global)
            info_row = ctk.CTkFrame(card, fg_color="transparent")
            info_row.pack(fill="x", padx=18, pady=(0, 15))
            ctk.CTkLabel(info_row, text=f"✅ {t['Servicio']}", text_color="#6B8E23", font=("Inter", 12, "italic")).pack(side="left")
            
            # Solo mostramos el nombre del peluquero si estamos en vista "Todos"
            if self.filtro_actual == "Todos":
                ctk.CTkLabel(info_row, text=f"💇 {t.get('Peluquero', 'N/A')}", font=("Inter", 11), text_color="#8E8E8E").pack(side="right")

    def abrir_formulario(self):
        v = ctk.CTkToplevel(self.master)
        v.title("NUEVA RESERVA")
        v.geometry("500x700")
        v.attributes("-topmost", True)
        v.configure(fg_color="#FAF9F6")

        if not self.id_empleado:
            ctk.CTkLabel(v, text="No se encontró tu perfil de empleado. Comunicate con el administrador.", font=("Inter", 14), text_color="#A52A2A").pack(pady=80)
            return

        servicios = self.db.obtener_servicios()

        ctk.CTkLabel(v, text="DATOS DEL CLIENTE", font=("Inter", 16, "bold"), text_color="#5C4033").pack(pady=(20, 10))
        en = ctk.CTkEntry(v, placeholder_text="Nombre", width=380); en.pack(pady=5)
        ea = ctk.CTkEntry(v, placeholder_text="Apellido", width=380); ea.pack(pady=5)
        em = ctk.CTkEntry(v, placeholder_text="Email (Opcional)", width=380); em.pack(pady=5)

        ctk.CTkLabel(v, text="DETALLES DEL TURNO", font=("Inter", 16, "bold"), text_color="#5C4033").pack(pady=(30, 10))
        ctk.CTkLabel(v, text=f"Peluquero: {self.parent.usuario_actual.get('nombre', '')} {self.parent.usuario_actual.get('apellido', '')}",
                      font=("Inter", 13), text_color="#5C4033").pack(pady=(0, 10))

        cb_s = ctk.CTkComboBox(v, values=[s['nombre'] for s in servicios], width=380)
        cb_s.pack(pady=5)

        ef = ctk.CTkEntry(v, width=380)
        ef.insert(0, datetime.now().strftime("%d/%m/%Y"))
        ef.pack(pady=5)

        f_h = ctk.CTkFrame(v, fg_color="transparent")
        f_h.pack(pady=5)
        cb_h = ctk.CTkComboBox(f_h, values=[f"{i:02d}" for i in range(8, 21)], width=80); cb_h.set("10"); cb_h.pack(side="left", padx=5)
        cb_m = ctk.CTkComboBox(f_h, values=["00", "15", "30", "45"], width=80); cb_m.set("00"); cb_m.pack(side="left", padx=5)

        def guardar():
            try:
                id_c = self.db.obtener_o_crear_cliente(en.get(), ea.get(), em.get())
                id_s = next(s['idservicio'] for s in servicios if s['nombre'] == cb_s.get())
                fecha_sql = datetime.strptime(f"{ef.get()} {cb_h.get()}:{cb_m.get()}", "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")

                if self.db.registrar_reserva(id_c, self.id_empleado, id_s, fecha_sql):
                    v.destroy()
                    self.cargar_datos()
            except Exception as ex:
                print(f"Error al guardar reserva: {ex}")

        ctk.CTkButton(v, text="CONFIRMAR TURNO", fg_color="#8B4513", hover_color="#A0522D", font=("Inter", 14, "bold"), 
                      height=50, width=380, corner_radius=10, command=guardar).pack(pady=40)

    def abrir_ventana_cobro(self, t):
        v = ctk.CTkToplevel(self.master)
        v.geometry("350x450")
        v.attributes("-topmost", True)
        v.title("Procesar Pago")

        db = Database()
        metodos = db.obtener_metodos_pago()
        id_reserva = t.get('idreserva')
        precio_base = t.get('Precio_Sugerido', 0)

        ctk.CTkLabel(v, text="FINALIZAR Y COBRAR", font=("Inter", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(v, text=f"Servicio: {t['Servicio']}", font=("Inter", 12)).pack()
        ctk.CTkLabel(v, text="Confirmar Monto:", font=("Inter", 12)).pack(pady=(15, 0))
        em = ctk.CTkEntry(v, placeholder_text="Monto", width=200)
        em.insert(0, str(precio_base))
        em.pack(pady=5)
        ctk.CTkLabel(v, text="Método de Pago:", font=("Inter", 12)).pack(pady=(10, 0))
        cb = ctk.CTkComboBox(v, values=[m['tipoPago'] for m in metodos], width=200)
        cb.pack(pady=5)

        def conf():
            try:
                monto = em.get()
                id_m = next(m['idmetodopago'] for m in metodos if m['tipoPago'] == cb.get())
                if db.finalizar_y_cobrar(id_reserva, monto, id_m):
                    v.destroy()
                    self.cargar_datos()
                    if hasattr(self.parent, 'cargar_caja_diaria'):
                        self.parent.cargar_caja_diaria()
            except Exception as e:
                print(f"Error al cobrar: {e}")

        ctk.CTkButton(v, text="Confirmar Pago", fg_color="#8B4513", hover_color="#A0522D", height=45, corner_radius=10,
                      font=("Inter", 12, "bold"), command=conf).pack(pady=30)
