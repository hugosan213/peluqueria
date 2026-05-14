import customtkinter as ctk
from database.db_stock import StockDB

class StockTab:
    def __init__(self, master, parent):
        self.master = master  # El tab físico
        self.parent = parent  # MainWindow
        self.db = StockDB()
        self.setup_ui()

    def setup_ui(self):
        """Estructura de control de insumos."""
        wrapper = ctk.CTkFrame(self.master, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=30, pady=20)
        
        header = ctk.CTkFrame(wrapper, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header, text="CONTROL DE INSUMOS", font=("Inter", 22, "bold"), text_color="#5C4033").pack(side="left")
        
        if self.parent.usuario_actual['rol'] == 'admin':
            ctk.CTkButton(header, text="+ Nuevo Producto", fg_color="#8B4513", hover_color="#A0522D", corner_radius=12,
                          font=("Inter", 12, "bold"), command=self.abrir_formulario_producto).pack(side="right")
            
        self.frame_lista_stock = ctk.CTkScrollableFrame(wrapper, fg_color="transparent", corner_radius=18, border_width=1, border_color="#E3D6C4")
        self.frame_lista_stock.pack(fill="both", expand=True)
        self.cargar_lista_stock()

    def cargar_lista_stock(self):
        """Refresca la lista de productos y marca en rojo los que tienen stock bajo."""
        for widget in self.frame_lista_stock.winfo_children(): 
            widget.destroy()
            
        productos = self.db.obtener_productos_stock()
        if not productos:
            ctk.CTkLabel(self.frame_lista_stock, text="No hay insumos cargados.", font=("Inter", 14), text_color="#5C4033").pack(pady=80)
            return

        for p in productos:
            es_bajo = p['stock_actual'] <= p['stock_minimo']
            row = ctk.CTkFrame(self.frame_lista_stock, 
                               fg_color="#FFEBE9" if es_bajo else "#FFFFFF", 
                               border_width=1, border_color="#E5E1DA", corner_radius=15)
            row.pack(fill="x", pady=8, padx=10)
            
            # Contenedor de información
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(fill="x", padx=18, pady=14)
            
            # Nombre del producto
            ctk.CTkLabel(info, text=p['nombre'].upper(), font=("Inter", 13, "bold"), text_color="#5C4033", anchor="w").pack(side="left")
            
            # BOTÓN ELIMINAR (Solo para Admin)
            if self.parent.usuario_actual['rol'] == 'admin':
                ctk.CTkButton(info, text="🗑️", width=40, fg_color="#CD5C5C", hover_color="#A52A2A", corner_radius=10,
                              font=("Inter", 11, "bold"), 
                              command=lambda i=p['idproducto']: self.borrar_producto(i)).pack(side="right", padx=(10, 0))

            # Stock actual
            ctk.CTkLabel(info, text=f"Stock: {p['stock_actual']} {p['unidad']}", font=("Inter", 12), text_color="#5C4033").pack(side="right")

    def abrir_formulario_producto(self):
        """Ventana para agregar un nuevo insumo[cite: 7]"""
        # CORRECCIÓN: Usamos self.master para evitar el error de Tkinter
        v = ctk.CTkToplevel(self.master)
        v.geometry("400x500")
        v.attributes("-topmost", True)
        v.title("Nuevo Producto")

        ctk.CTkLabel(v, text="NUEVO PRODUCTO", font=("Inter", 16, "bold")).pack(pady=20)
        en = ctk.CTkEntry(v, placeholder_text="Nombre", width=300); en.pack(pady=10)
        es = ctk.CTkEntry(v, placeholder_text="Stock Actual", width=300); es.pack(pady=10)
        em = ctk.CTkEntry(v, placeholder_text="Stock Mínimo", width=300); em.pack(pady=10)
        eu = ctk.CTkEntry(v, placeholder_text="Unidad", width=300); eu.pack(pady=10)

        def add():
            # Usamos self.db para la inserción[cite: 17]
            if self.db.agregar_producto_stock(en.get(), es.get(), em.get(), eu.get()):
                v.destroy()
                self.cargar_lista_stock()

        ctk.CTkButton(v, text="Guardar", fg_color="#8B4513", hover_color="#A0522D", corner_radius=10,
                      font=("Inter", 12, "bold"), command=add).pack(pady=30)
        
    def borrar_producto(self, id_p):
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este insumo?"):
            if self.db.eliminar_producto_stock(id_p):
                self.cargar_lista_stock()