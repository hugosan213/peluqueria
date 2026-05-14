from .base import BaseDatabase

class StockDB(BaseDatabase):
    # --- MÉTODO DE STOCK ---
    def obtener_productos_stock(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM producto")
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []

    def agregar_producto_stock(self, nombre, stock_actual, stock_minimo, unidad):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "INSERT INTO producto (nombre, stock_actual, stock_minimo, unidad) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (nombre, stock_actual, stock_minimo, unidad))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al agregar producto: {e}")
                return False
            finally:
                cursor.close(); conexion.close()
        return False
    
    def eliminar_producto_stock(self, id_producto):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Borramos el producto por su ID
                sql = "DELETE FROM producto WHERE idproducto = %s"
                cursor.execute(sql, (id_producto,))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al eliminar producto: {e}")
                return False
            finally:
                cursor.close(); conexion.close()
        return False
