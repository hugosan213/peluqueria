from .base import BaseDatabase
from datetime import datetime
class AgendaDB(BaseDatabase):
    # --- MÉTODOS DE SERVICIOS (ABM) ---
    def obtener_servicios_detallados(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT idservicio, nombre, precio, duracion FROM servicio")
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []
    
    # Método agregado para el ComboBox del formulario de reservas[cite: 10]
    def obtener_servicios(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT idservicio, nombre FROM servicio")
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []
    

    def agregar_servicio_nuevo(self, nombre, precio, duracion):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "INSERT INTO servicio (nombre, precio, duracion) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nombre, precio, duracion))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al agregar servicio: {e}")
                return False
            finally:
                cursor.close(); conexion.close()
        return False
    
    def eliminar_servicio(self, id_servicio):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "DELETE FROM servicio WHERE idservicio = %s"
                cursor.execute(sql, (id_servicio,))
                conexion.commit()
                return True
            except Exception:
                print("Error: No se puede eliminar un servicio que tiene turnos asociados.")
                return False
            finally:
                cursor.close(); conexion.close()
        return False

    def actualizar_servicio(self, id_servicio, precio, duracion):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "UPDATE servicio SET precio = %s, duracion = %s WHERE idservicio = %s"
                cursor.execute(sql, (precio, duracion, id_servicio))
                conexion.commit()
                return True
            finally: cursor.close(); conexion.close()
        return False
    

    # --- MÉTODOS DE AGENDA Y COBRO ---
    def obtener_agenda(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Quitamos el filtro de tiempo estricto y priorizamos el estado
            sql = """SELECT * FROM vista_agenda_completa 
                     WHERE Estado = 'pendiente' 
                     ORDER BY Fecha_Raw ASC"""
            cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []
    
    def obtener_historial_cortes(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Traemos los últimos 50 cortes realizados
            sql = """SELECT * FROM vista_agenda_completa 
                     WHERE Estado = 'finalizada' 
                     ORDER BY Fecha_Raw DESC LIMIT 50"""
            cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []

    def obtener_agenda_por_empleado(self, id_empleado):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            sql = """
            SELECT r.idreserva, r.fecha_inicio as Fecha_Hora, r.estado as Estado,
                   CONCAT(p.nombre, ' ', p.apellido) as Cliente,
                   s.nombre as Servicio, s.precio as Precio_Sugerido,
                   CONCAT(pe.nombre, ' ', pe.apellido) as Peluquero
            FROM reserva r
            JOIN cliente c ON r.cliente_idcliente = c.idcliente
            JOIN persona p ON c.persona_idpersona = p.idpersona
            JOIN servicio s ON r.servicio_idservicio = s.idservicio
            JOIN empleado e ON r.empleado_idempleado = e.idempleado
            JOIN persona pe ON e.persona_idpersona = pe.idpersona
            WHERE r.estado = 'pendiente' AND r.empleado_idempleado = %s
            ORDER BY r.fecha_inicio
            """
            cursor.execute(sql, (id_empleado,))
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []

    def obtener_historial_por_empleado(self, id_empleado):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            sql = """
            SELECT r.fecha_inicio as Fecha_Hora, r.estado as Estado,
                   CONCAT(p.nombre, ' ', p.apellido) as Cliente,
                   s.nombre as Servicio,
                   CONCAT(pe.nombre, ' ', pe.apellido) as Peluquero
            FROM reserva r
            JOIN cliente c ON r.cliente_idcliente = c.idcliente
            JOIN persona p ON c.persona_idpersona = p.idpersona
            JOIN servicio s ON r.servicio_idservicio = s.idservicio
            JOIN empleado e ON r.empleado_idempleado = e.idempleado
            JOIN persona pe ON e.persona_idpersona = pe.idpersona
            WHERE r.estado = 'finalizada' AND r.empleado_idempleado = %s
            ORDER BY r.fecha_inicio DESC LIMIT 50
            """
            cursor.execute(sql, (id_empleado,))
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []
    

    # Lógica de registro implementada[cite: 10]
    def registrar_reserva(self, id_cliente, id_empleado, id_servicio, fecha_sql):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "INSERT INTO reserva (cliente_idcliente, empleado_idempleado, servicio_idservicio, fecha_inicio, estado) VALUES (%s, %s, %s, %s, 'pendiente')"
                cursor.execute(sql, (id_cliente, id_empleado, id_servicio, fecha_sql))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al registrar reserva: {e}")
                return False
            finally: cursor.close(); conexion.close()
        return False
    
    def obtener_o_crear_cliente(self, nombre, apellido, mail):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                # 1. Lógica de búsqueda inteligente
                # Si el mail no es opcional o no está vacío, buscamos por mail
                if mail and str(mail).strip() != "" and mail != "temp@mail.com":
                    sql_busqueda = """SELECT c.idcliente FROM cliente c 
                                      JOIN persona p ON c.persona_idpersona = p.idpersona 
                                      WHERE p.mail = %s"""
                    cursor.execute(sql_busqueda, (mail,))
                else:
                    # Si el mail está vacío, buscamos por nombre y apellido para no duplicar
                    sql_busqueda = """SELECT c.idcliente FROM cliente c 
                                      JOIN persona p ON c.persona_idpersona = p.idpersona 
                                      WHERE p.nombre = %s AND p.apellido = %s"""
                    cursor.execute(sql_busqueda, (nombre, apellido))
                
                resultado = cursor.fetchone()
                if resultado: 
                    return resultado['idcliente']

                # 2. Si no existe, creamos la PERSONA primero
                # Guardamos el mail como NULL si está vacío para que no rompa la vista SQL
                mail_final = mail if (mail and str(mail).strip() != "") else None
                
                sql_p = "INSERT INTO persona (nombre, apellido, mail) VALUES (%s, %s, %s)"
                cursor.execute(sql_p, (nombre, apellido, mail_final))
                id_p = cursor.lastrowid
                conexion.commit() 

                # 3. Creamos el CLIENTE vinculado a esa persona
                sql_c = "INSERT INTO cliente (persona_idpersona) VALUES (%s)"
                cursor.execute(sql_c, (id_p,))
                id_c = cursor.lastrowid
                conexion.commit() 
                
                return id_c
            except Exception as e:
                print(f"Error al procesar cliente: {e}")
                return None
            finally: 
                cursor.close(); conexion.close()
        return None

    def obtener_clientes_lista(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT c.idcliente, p.nombre, p.apellido, p.mail, c.notas_relevantes FROM cliente c JOIN persona p ON c.persona_idpersona = p.idpersona ORDER BY p.apellido ASC")
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []
    
    def obtener_clientes_por_empleado(self, id_empleado):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            sql = """
            SELECT DISTINCT c.idcliente, p.nombre, p.apellido, p.mail, c.notas_relevantes
            FROM cliente c
            JOIN persona p ON c.persona_idpersona = p.idpersona
            JOIN reserva r ON r.cliente_idcliente = c.idcliente
            WHERE r.empleado_idempleado = %s
            ORDER BY p.apellido ASC, p.nombre ASC
            """
            cursor.execute(sql, (id_empleado,))
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []
    

    def actualizar_notas_cliente(self, id_cliente, notas):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "UPDATE cliente SET notas_relevantes = %s WHERE idcliente = %s"
                cursor.execute(sql, (notas, id_cliente))
                conexion.commit()
                return True
            finally: cursor.close(); conexion.close()
        return False