import customtkinter as ctk
from database.db_agenda import AgendaDB
from database.db_usuarios import UsuariosDB
from database.db_finanzas import FinanzasDB
from datetime import datetime

class AgendaAdminTab:
    def __init__(self, master, parent):
        self.master = master
        self.parent = parent
        # Asignamos nombres diferentes para no sobrescribirlos
        self.db_usuarios = UsuariosDB() 
        self.db_agenda = AgendaDB()
        self.filtro_actual = "Todos"
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        header = ctk.CTkFrame(self.master, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=20)
        
        ctk.CTkLabel(header, text="AGENDA DE TURNOS", font=("Inter", 24, "bold"), text_color="#5C4033").pack(side="left")

        # --- NUEVO: Filtro por Peluquero ---
        filtro_frame = ctk.CTkFrame(header, fg_color="transparent")
        filtro_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(filtro_frame, text="Filtrar por:", font=("Inter", 12)).pack(side="left", padx=5)
        
        # Obtenemos empleados para el filtro
        empleados = self.db_usuarios.obtener_empleados()
        opciones_filtro = ["Todos"] + [f"{e['nombre']} {e['apellido']}" for e in empleados]
        
        self.cb_filtro = ctk.CTkComboBox(filtro_frame, values=opciones_filtro, command=self.aplicar_filtro, width=200)
        self.cb_filtro.set("Todos")
        self.cb_filtro.pack(side="left")

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

    def aplicar_filtro(self, seleccion):
        self.filtro_actual = seleccion
        self.cargar_datos()

    def cargar_datos(self):
        for widget in self.frame_agenda.winfo_children():
            widget.destroy()
        
        agenda = self.db_agenda.obtener_agenda()
        
        # --- FILTRADO LÓGICO ---
        if self.filtro_actual != "Todos":
            agenda = [t for t in agenda if t.get('Peluquero') == self.filtro_actual]

        if not agenda:
            msg = "No hay turnos pendientes." if self.filtro_actual == "Todos" else f"No hay turnos para {self.filtro_actual}."
            ctk.CTkLabel(self.frame_agenda, text=msg, font=("Inter", 14), text_color="#5C4033").pack(pady=80)
            return

        for t in agenda:
            card = ctk.CTkFrame(self.frame_agenda, fg_color="#FFFFFF", border_width=1, border_color="#E5E1DA", corner_radius=15)
            card.pack(fill="x", pady=8, padx=16)
            
            # (El resto del código de la tarjeta se mantiene igual)
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
            peluquero = t.get('Peluquero', "No asignado")
            ctk.CTkLabel(info_row, text=f"💇 Peluquero: {peluquero}", font=("Inter", 12), text_color="#5C4033").pack(side="right")

            if t.get('Estado') != 'finalizada':
                ctk.CTkButton(card, text="💵 Cobrar", width=100, fg_color="#8B4513", hover_color="#A0522D", corner_radius=12,
                              font=("Inter", 11, "bold"), command=lambda trn=t: self.abrir_ventana_cobro(trn)).pack(padx=18, pady=(0, 16), anchor="e")

    # ... (El resto de métodos abrir_formulario, cargar_historial, etc., se mantienen igual)

    def cargar_historial(self):
        for widget in self.frame_agenda.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.frame_agenda, text="HISTORIAL DE CORTES FINALIZADOS", font=("Inter", 16, "bold")).pack(pady=10)
        
        historial = self.db_agenda.obtener_historial_cortes()
        if not historial:
            ctk.CTkLabel(self.frame_agenda, text="No hay cortes finalizados para mostrar.", font=("Inter", 14), text_color="#5C4033").pack(pady=80)
            return
        
        for t in historial:
            card = ctk.CTkFrame(self.frame_agenda, fg_color="#E5E1DA", corner_radius=12)
            card.pack(fill="x", pady=6, padx=10)
            ctk.CTkLabel(card, text=f"🕒 {t['Fecha_Hora']} | 👤 {t['Cliente']}", font=("Inter", 14)).pack(side="left", padx=20, pady=15)
            ctk.CTkLabel(card, text=f"✅ {t['Servicio']}", text_color="#6B8E23", font=("Inter", 12, "italic")).pack(side="right", padx=20)

    def abrir_formulario(self):
        v = ctk.CTkToplevel(self.master)
        v.title("NUEVA RESERVA")
        v.geometry("500x780")
        v.attributes("-topmost", True)
        v.configure(fg_color="#FAF9F6")

        # Recuperar datos de la base de datos
        empleados = empleados = self.db_usuarios.obtener_empleados()
        servicios = self.db_agenda.obtener_servicios()

        ctk.CTkLabel(v, text="DATOS DEL CLIENTE", font=("Inter", 16, "bold"), text_color="#5C4033").pack(pady=(20, 10))
        en = ctk.CTkEntry(v, placeholder_text="Nombre", width=380); en.pack(pady=5)
        ea = ctk.CTkEntry(v, placeholder_text="Apellido", width=380); ea.pack(pady=5)
        em = ctk.CTkEntry(v, placeholder_text="Email (Opcional)", width=380); em.pack(pady=5)

        ctk.CTkLabel(v, text="DETALLES DEL TURNO", font=("Inter", 16, "bold"), text_color="#5C4033").pack(pady=(30, 10))
        
        # --- Lógica de Empleados ---
        ctk.CTkLabel(v, text="Empleado", font=("Inter", 12), text_color="#5C4033").pack(pady=(0, 2))
        if empleados:
            valores_empleados = [f"{e['nombre']} {e['apellido']}" for e in empleados]
        else:
            valores_empleados = ["No hay empleados registrados"]
            
        cb_e = ctk.CTkComboBox(v, values=valores_empleados, width=380)
        cb_e.pack(pady=5)
        
        if empleados:
            cb_e.set(valores_empleados[0])
        else:
            cb_e.configure(state="disabled")

        # --- Lógica de Servicios ---
        ctk.CTkLabel(v, text="Servicio", font=("Inter", 12), text_color="#5C4033").pack(pady=(10, 2))
        if servicios:
            valores_servicios = [s['nombre'] for s in servicios]
        else:
            valores_servicios = ["No hay servicios disponibles"]
            
        cb_s = ctk.CTkComboBox(v, values=valores_servicios, width=380)
        cb_s.pack(pady=5)
        
        if servicios:
            cb_s.set(valores_servicios[0])
        else:
            cb_s.configure(state="disabled")

        # --- Fecha y Hora ---
        ef = ctk.CTkEntry(v, width=380)
        ef.insert(0, datetime.now().strftime("%d/%m/%Y"))
        ef.pack(pady=5)

        f_h = ctk.CTkFrame(v, fg_color="transparent"); f_h.pack(pady=5)
        cb_h = ctk.CTkComboBox(f_h, values=[f"{i:02d}" for i in range(8, 21)], width=80); cb_h.set("10"); cb_h.pack(side="left", padx=5)
        cb_m = ctk.CTkComboBox(f_h, values=["00", "15", "30", "45"], width=80); cb_m.set("00"); cb_m.pack(side="left", padx=5)

        feedback_label = ctk.CTkLabel(v, text="", font=("Inter", 12), text_color="#9D2B2B")
        feedback_label.pack(pady=(10, 0))

        def guardar():
            try:
                # Validaciones previas
                if not empleados:
                    feedback_label.configure(text="No hay empleados registrados. Agregalos en Configuración.")
                    return
                if not servicios:
                    feedback_label.configure(text="No hay servicios disponibles. Agregalos en Precios.")
                    return
                if not en.get() or not ea.get():
                    feedback_label.configure(text="Nombre y Apellido son obligatorios.")
                    return

                # Procesar datos
                id_c = self.db_agenda.obtener_o_crear_cliente(en.get(), ea.get(), em.get())
                empleado_seleccionado = cb_e.get()
                id_e = next(e['idempleado'] for e in empleados if f"{e['nombre']} {e['apellido']}" == empleado_seleccionado)
                id_s = next(s['idservicio'] for s in servicios if s['nombre'] == cb_s.get())
                
                fecha_str = f"{ef.get()} {cb_h.get()}:{cb_m.get()}"
                fecha_sql = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
                
                if self.db_agenda.registrar_reserva(id_c, id_e, id_s, fecha_sql):
                    v.destroy()
                    self.cargar_datos()
            except Exception as ex:
                print(f"Error al guardar reserva: {ex}")
                feedback_label.configure(text="Error al guardar. Revisá el formato de fecha.")

        btn_confirmar = ctk.CTkButton(v, text="CONFIRMAR TURNO", fg_color="#8B4513", hover_color="#A0522D", font=("Inter", 14, "bold"), 
                                     height=50, width=380, corner_radius=10, command=guardar)
        btn_confirmar.pack(pady=40)

        # Desactivar botón si faltan datos maestros
        if not empleados or not servicios:
            btn_confirmar.configure(state="disabled")
            if not empleados:
                feedback_label.configure(text="No hay empleados registrados. Agregalos en Configuración.")
            elif not servicios:
                feedback_label.configure(text="No hay servicios disponibles. Agregalos en Precios.")

    def abrir_ventana_cobro(self, t):
        v = ctk.CTkToplevel(self.master) 
        v.geometry("350x450")
        v.attributes("-topmost", True)
        v.title("Procesar Pago")
        
        db = FinanzasDB()
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
                    self.cargar_datos() # Esto funciona porque cargar_datos está en esta clase[cite: 14]
                    
                    if hasattr(self.parent, 'cargar_caja_diaria'):
                        self.parent.cargar_caja_diaria()
            except Exception as e:
                print(f"Error al cobrar: {e}")

        ctk.CTkButton(v, text="Confirmar Pago", fg_color="#8B4513", hover_color="#A0522D", height=45, corner_radius=10,
                      font=("Inter", 12, "bold"), command=conf).pack(pady=30)
