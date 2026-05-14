import customtkinter as ctk
from database.db_finanzas import FinanzasDB
from datetime import datetime
from tkinter import filedialog, messagebox

class StatsTab:
    def __init__(self, master, parent):
        self.master = master  # El tab físico
        self.parent = parent  # MainWindow
        self.db = FinanzasDB()
        self.setup_ui()

    def setup_ui(self):
        """Interfaz con reportes, selector de periodos y ranking lateral."""
        panel = ctk.CTkFrame(self.master, fg_color="transparent")
        panel.pack(fill="both", expand=True, padx=30, pady=20)

        # --- HEADER ---
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(header, text="REPORTES DE INGRESOS", font=("Inter", 24, "bold"), text_color="#5C4033").pack(side="left")

        right_controls = ctk.CTkFrame(header, fg_color="transparent")
        right_controls.pack(side="right")

        self.selector_periodo = ctk.CTkComboBox(right_controls, values=["Semanal", "Mensual", "Anual"],
                                                width=150, height=32, corner_radius=10,
                                                fg_color="#F2F0EB", button_color="#D2B48C",
                                                text_color="#5C4033", dropdown_fg_color="#FFFFFF",
                                                command=lambda _: self.actualizar_todo())
        self.selector_periodo.set("Mensual")
        self.selector_periodo.pack(side="right", padx=(0, 10))

        ctk.CTkButton(right_controls, text="📊 Exportar Excel", fg_color="#8B4513", hover_color="#A0522D", corner_radius=10,
                      font=("Inter", 12, "bold"), width=180,
                      command=self.exportar_estadisticas_excel).pack(side="right")

        # --- RESUMEN DE FACTURACIÓN ---
        self.resumen_frame = ctk.CTkFrame(panel, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.resumen_frame.pack(fill="x", pady=(0, 20))

        self.lbl_resumen = ctk.CTkLabel(self.resumen_frame, text="Cargando datos...", font=("Inter", 12), text_color="#5C4033", anchor="w")
        self.lbl_resumen.pack(fill="x", padx=20, pady=18)

        # --- CONTENEDOR DE GRÁFICO Y RANKING ---
        self.contenedor_data = ctk.CTkFrame(panel, fg_color="transparent")
        self.contenedor_data.pack(fill="both", expand=True)

        # Lado Izquierdo: Gráfico de Barras
        self.frame_grafico = ctk.CTkScrollableFrame(self.contenedor_data, fg_color="#F2F0EB", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.frame_grafico.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Lado Derecho: Ranking de Empleados
        self.frame_ranking = ctk.CTkFrame(self.contenedor_data, width=300, fg_color="#F2F0EB", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.frame_ranking.pack(side="right", fill="y")
        self.frame_ranking.pack_propagate(False)

        ctk.CTkLabel(self.frame_ranking, text="🏆 TOP PELUQUEROS", font=("Inter", 15, "bold"), text_color="#5C4033").pack(pady=20)

        self.actualizar_todo()

    def actualizar_todo(self):
        """Actualiza el gráfico y el ranking simultáneamente."""
        self.actualizar_grafico()
        self.cargar_ranking()


    def actualizar_grafico(self):
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        periodo = self.selector_periodo.get()
        datos = self.db.obtener_estadisticas_ingresos(periodo)

        if not datos:
            ctk.CTkLabel(self.frame_grafico, text=f"No hay datos suficientes para el reporte {periodo.lower()}.", font=("Inter", 14), text_color="#5C4033").pack(pady=120)
            self.lbl_resumen.configure(text=f"Periodo seleccionado: {periodo}. No hay información disponible.")
            return

        total_general = sum(float(d['total']) for d in datos)
        self.lbl_resumen.configure(text=f"Periodo: {periodo}   ·   Total facturado: $ {total_general:,.2f}   ·   {len(datos)} registros")

        max_valor = max(float(d['total']) for d in datos) if datos else 1

        for d in datos:
            fila = ctk.CTkFrame(self.frame_grafico, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E3D6C4")
            fila.pack(fill="x", padx=20, pady=10)

            datos_row = ctk.CTkFrame(fila, fg_color="transparent")
            datos_row.pack(fill="x", padx=20, pady=16)

            ctk.CTkLabel(datos_row, text=str(d['etiqueta']).upper(), font=("Inter", 13, "bold"), text_color="#5C4033", anchor="w", width=160).pack(side="left")
            ctk.CTkLabel(datos_row, text=f"$ {float(d['total']):,.2f}", font=("Inter", 13, "bold"), text_color="#5C4033").pack(side="right")

            barra_contenedor = ctk.CTkFrame(fila, fg_color="#F7E8D9", corner_radius=10)
            barra_contenedor.pack(fill="x", padx=20, pady=(0, 18))

            ancho_barra = max(40, int((float(d['total']) / max_valor) * 680))
            barra = ctk.CTkFrame(barra_contenedor, width=ancho_barra, height=20, fg_color="#D2B48C", corner_radius=10)
            barra.pack(anchor="w", padx=4, pady=4)

    def exportar_estadisticas_excel(self):
        from tkinter import filedialog, messagebox
        import pandas as pd

        datos = self.db.obtener_pagos_para_exportar()

        if not datos:
            messagebox.showinfo("Exportar", "No hay datos de ventas para exportar.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=f"Reporte_Ventas_{datetime.now().strftime('%d_%m_%Y')}.xlsx"
        )

        if path:
            try:
                df = pd.DataFrame(datos)
                df.columns = ['ID Pago', 'Fecha y Hora', 'Monto ($)', 'Método de Pago', 'Servicio']

                with pd.ExcelWriter(path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Ventas')
                    worksheet = writer.sheets['Ventas']
                    for idx, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.column_dimensions[chr(65 + idx)].width = max_len

                messagebox.showinfo("Éxito", f"Reporte profesional generado en:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el Excel: {e}")

    def cargar_ranking(self):
        """Muestra el ranking de ventas por empleado del mes actual."""
        for widget in self.frame_ranking.winfo_children():
            if isinstance(widget, ctk.CTkFrame): widget.destroy()

        ranking = self.db.obtener_ranking_empleados()
        if not ranking:
            ctk.CTkLabel(self.frame_ranking, text="Sin ventas registradas.", font=("Inter", 12, "italic")).pack(pady=40)
            return

        for idx, item in enumerate(ranking):
            fila = ctk.CTkFrame(self.frame_ranking, fg_color="#FFFFFF", corner_radius=12)
            fila.pack(fill="x", padx=15, pady=6)
            
            medalla = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "👤"
            ctk.CTkLabel(fila, text=f"{medalla} {item['empleado']}", font=("Inter", 12, "bold"), anchor="w").pack(side="left", padx=10, pady=12)
            ctk.CTkLabel(fila, text=f"$ {float(item['total']):,.2f}", font=("Inter", 11, "bold"), text_color="#8B4513").pack(side="right", padx=10)