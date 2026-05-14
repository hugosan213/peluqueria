import customtkinter as ctk
from database.db_finanzas import FinanzasDB
from tkinter import messagebox

class CajaTab:
    def __init__(self, master, parent):
        self.master = master  # El tab físico (ctk.CTkFrame)[cite: 19]
        self.parent = parent  # Instancia de MainWindow[cite: 19]
        self.db = FinanzasDB()
        self.setup_ui()

    def setup_ui(self):
        """Define la estructura de la caja diaria."""
        for widget in self.master.winfo_children(): 
            widget.destroy()
        
        wrapper = ctk.CTkFrame(self.master, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=30, pady=20)
        
        header = ctk.CTkFrame(wrapper, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header, text="CONTROL DE CAJA DIARIA", font=("Inter", 22, "bold"), text_color="#5C4033").pack(side="left")
        ctk.CTkButton(header, text="- Retirar Dinero / Gasto", fg_color="#CD5C5C", hover_color="#A52A2A", corner_radius=12,
                      font=("Inter", 12, "bold"), command=self.abrir_formulario_egreso).pack(side="right")
        
        self.frame_caja_info = ctk.CTkFrame(wrapper, fg_color="#F2F0EB", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.frame_caja_info.pack(pady=10, fill="both", expand=True)
        self.cargar_caja_diaria()

    def cargar_caja_diaria(self):
        """Refresca los ingresos y egresos del día."""
        for widget in self.frame_caja_info.winfo_children(): 
            widget.destroy()
            
        ingresos = self.db.obtener_caja_diaria()
        egresos_total = self.db.obtener_total_egresos_hoy()
        total_ingresos = sum(float(r['total']) for r in ingresos)

        ingresos_card = ctk.CTkFrame(self.frame_caja_info, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E3D6C4")
        ingresos_card.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(ingresos_card, text="INGRESOS", font=("Inter", 16, "bold"), text_color="#5C4033").pack(anchor="w", padx=20, pady=(16, 8))

        if ingresos:
            for r in ingresos:
                row = ctk.CTkFrame(ingresos_card, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=6)
                ctk.CTkLabel(row, text=r['tipoPago'].upper(), font=("Inter", 12, "bold"), anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=f"$ {float(r['total']):,.2f}", font=("Inter", 12), text_color="#5C4033").pack(side="right")
        else:
            ctk.CTkLabel(ingresos_card, text="No se registraron ingresos hoy.", font=("Inter", 12), text_color="#5C4033").pack(padx=20, pady=16)

        totales_card = ctk.CTkFrame(self.frame_caja_info, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E3D6C4")
        totales_card.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(totales_card, text=f"TOTAL EGRESOS: - $ {float(egresos_total):,.2f}", text_color="#CD5C5C", font=("Inter", 16, "bold")).pack(anchor="w", padx=20, pady=(18, 8))
        saldo_neto = total_ingresos - float(egresos_total)
        ctk.CTkLabel(totales_card, text=f"SALDO EN CAJA: $ {saldo_neto:,.2f}", font=("Inter", 24, "bold"), text_color="#2D2424").pack(anchor="w", padx=20, pady=(0, 18))

    def abrir_formulario_egreso(self):
        """Seguridad y formulario de retiro con validación de contraseña y botón de acción."""
        dialogo = ctk.CTkInputDialog(text="Ingrese su contraseña para autorizar el retiro:", title="Seguridad de Caja")
        password_ingresada = dialogo.get_input()

        # 1. Verificamos si el usuario apretó 'Cancelar' o cerró la ventana
        if password_ingresada is None:
            return

        # 2. Verificamos que no haya enviado el campo vacío
        if password_ingresada.strip() == "":
            messagebox.showwarning("Atención", "Debe ingresar una contraseña.")
            return

        # 3. Comparación con la contraseña del usuario actual
        if password_ingresada == self.parent.usuario_actual.get('password'):
            v = ctk.CTkToplevel(self.master)
            v.geometry("350x450") # Un poco más de alto para que entre el botón cómodo
            v.attributes("-topmost", True)
            v.title("Nuevo Egreso")
            
            ctk.CTkLabel(v, text="SALIDA DE DINERO", font=("Inter", 16, "bold")).pack(pady=20)
            
            em = ctk.CTkEntry(v, placeholder_text="Monto (ej: 1500.50)", width=250)
            em.pack(pady=10)
            
            ed = ctk.CTkEntry(v, placeholder_text="Descripción / Motivo", width=250)
            ed.pack(pady=10)
            
            def guardar():
                monto_texto = em.get()
                desc = ed.get()
                
                if not monto_texto or not desc:
                    messagebox.showwarning("Atención", "Complete todos los campos.")
                    return
                
                try:
                    monto_a_retirar = float(monto_texto)
                    
                    # Obtenemos el saldo actual para validar
                    ingresos = self.db.obtener_caja_diaria()
                    total_ingresos = sum(float(r['total']) for r in ingresos)
                    egresos_ya_realizados = float(self.db.obtener_total_egresos_hoy())
                    saldo_disponible = total_ingresos - egresos_ya_realizados

                    # VALIDACIÓN DE SALDO
                    if monto_a_retirar > saldo_disponible:
                        messagebox.showerror("Error de Caja", 
                            f"No hay dinero suficiente.\nSaldo disponible: $ {saldo_disponible:,.2f}")
                        return

                    # Registro en base de datos
                    if self.db.registrar_egreso(monto_a_retirar, desc):
                        messagebox.showinfo("Éxito", "Egreso registrado correctamente.")
                        v.destroy()
                        self.cargar_caja_diaria() # Refresca la vista de la caja
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un monto numérico válido.")

            # --- EL BOTÓN QUE FALTABA ---
            btn_confirmar = ctk.CTkButton(v, 
                                          text="Confirmar Retiro", 
                                          fg_color="#CD5C5C", 
                                          hover_color="#A52A2A",
                                          font=("Inter", 13, "bold"),
                                          height=40,
                                          command=guardar)
            btn_confirmar.pack(pady=30)
            
        else:
            # Si la contraseña no coincide
            messagebox.showerror("Error", "Contraseña incorrecta. Operación cancelada.")