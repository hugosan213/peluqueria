import mysql.connector
from mysql.connector import Error
from datetime import datetime

class Database:
    def __init__(self):
        self.config = {
            'host': '127.0.0.1',
            'user': 'root', 
            'password': '17032003Hsanti', 
            'database': 'peluqueria'
        }

    def conectar(self):
        try:
            conexion = mysql.connector.connect(**self.config)
            if conexion.is_connected():
                return conexion
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

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

    def usuario_existe(self, nombre_usuario):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT idusuario FROM usuario WHERE nombre_usuario = %s", (nombre_usuario,))
            existe = cursor.fetchone() is not None
            cursor.close(); conexion.close()
            return existe
        return False

    def actualizar_credenciales_usuario(self, id_usuario, nuevo_usuario=None, nueva_password=None):
        if not id_usuario:
            return False

        updates = []
        params = []
        if nuevo_usuario:
            updates.append("nombre_usuario = %s")
            params.append(nuevo_usuario)
        if nueva_password:
            updates.append("password = %s")
            params.append(nueva_password)

        if not updates:
            return False

        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                if nuevo_usuario:
                    cursor.execute("SELECT idusuario FROM usuario WHERE nombre_usuario = %s AND idusuario <> %s", (nuevo_usuario, id_usuario))
                    if cursor.fetchone():
                        return False
                sql = f"UPDATE usuario SET {', '.join(updates)} WHERE idusuario = %s"
                params.append(id_usuario)
                cursor.execute(sql, tuple(params))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al actualizar credenciales: {e}")
                return False
            finally:
                cursor.close(); conexion.close()
        return False

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

    def obtener_metodos_pago(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT idmetodopago, tipoPago FROM metodo_pago")
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []

    def finalizar_y_cobrar(self, id_reserva, monto, id_metodo):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("UPDATE reserva SET estado = 'finalizada', monto_total = %s WHERE idreserva = %s", (monto, id_reserva))
                cursor.execute("INSERT INTO pago (monto, fecha, metodo_pago_idmetodopago, reserva_idreserva) VALUES (%s, NOW(), %s, %s)", (monto, id_metodo, id_reserva))
                conexion.commit()
                return True
            finally: cursor.close(); conexion.close()
        return False

    def obtener_caja_diaria(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT mp.tipoPago, SUM(p.monto) as total FROM pago p JOIN metodo_pago mp ON p.metodo_pago_idmetodopago = mp.idmetodopago WHERE DATE(p.fecha) = CURDATE() GROUP BY mp.tipoPago")
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []

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

    # --- EMPLEADOS ---
    def obtener_empleados(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                # Usamos LEFT JOIN por si algún dato en 'persona' falta, 
                # aunque lo ideal es que siempre existan ambos.
                sql = """SELECT e.idempleado, p.nombre, p.apellido 
                        FROM empleado e 
                        JOIN persona p ON e.persona_idpersona = p.idpersona 
                        ORDER BY p.apellido ASC"""
                cursor.execute(sql)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener empleados: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    def agregar_empleado_completo(self, nombre, apellido, mail, dni, password):
        conexion = self.conectar()
        if not conexion:
            return False
            
        cursor = conexion.cursor()
        try:
            # Iniciamos transacción
            conexion.start_transaction()

            # 1. Insertar en PERSONA
            sql_p = "INSERT INTO persona (nombre, apellido, mail, dni) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_p, (nombre, apellido, mail, dni))
            id_persona = cursor.lastrowid

            # 2. Insertar en EMPLEADO vinculado a la persona
            sql_e = "INSERT INTO empleado (persona_idpersona) VALUES (%s)"
            cursor.execute(sql_e, (id_persona,))
            id_empleado = cursor.lastrowid

            # 3. Insertar en USUARIO vinculado al empleado (DNI como nombre de usuario)
            # El rol es 'empleado' por defecto
            sql_u = "INSERT INTO usuario (nombre_usuario, password, rol, empleado_idempleado) VALUES (%s, %s, 'empleado', %s)"
            cursor.execute(sql_u, (dni, password, id_empleado))

            # Si todo salió bien, confirmamos
            conexion.commit()
            return True
        except Exception as e:
            # Si falla cualquier paso, revertimos todo para no dejar datos huérfanos
            print(f"Error al registrar empleado completo: {e}")
            conexion.rollback()
            return False
        finally:
            cursor.close()
            conexion.close()

    def crear_usuario_para_empleado_por_dni(self, dni, password):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute("SELECT idusuario FROM usuario WHERE nombre_usuario = %s", (dni,))
                if cursor.fetchone():
                    return True

                sql = "INSERT INTO usuario (nombre_usuario, password, rol) VALUES (%s, %s, 'empleado')"
                cursor.execute(sql, (dni, password))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al crear usuario: {e}")
                return False
            finally:
                cursor.close(); conexion.close()
        return False

    def crear_usuario_para_empleado(self, id_empleado, password):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                sql = "SELECT p.dni FROM empleado e JOIN persona p ON e.persona_idpersona = p.idpersona WHERE e.idempleado = %s"
                cursor.execute(sql, (id_empleado,))
                row = cursor.fetchone()
                if not row or not row.get('dni'):
                    return False
                dni = row['dni']
                return self.crear_usuario_para_empleado_por_dni(dni, password)
            finally:
                cursor.close(); conexion.close()
        return False

    def obtener_id_empleado_por_dni(self, dni):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                sql = "SELECT e.idempleado FROM empleado e JOIN persona p ON e.persona_idpersona = p.idpersona WHERE p.dni = %s"
                cursor.execute(sql, (dni,))
                row = cursor.fetchone()
                return row['idempleado'] if row and row.get('idempleado') else None
            except Exception as e:
                print(f"Error al obtener idempleado por DNI: {e}")
                return None
            finally:
                cursor.close(); conexion.close()
        return None

    def registrar_egreso(self, monto, descripcion):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql = "INSERT INTO egreso (monto, descripcion) VALUES (%s, %s)"
                cursor.execute(sql, (monto, descripcion))
                conexion.commit()
                return True
            finally: cursor.close(); conexion.close()
        return False

    def obtener_total_egresos_hoy(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Sumamos todos los gastos del día actual
            cursor.execute("SELECT SUM(monto) as total FROM egreso WHERE DATE(fecha) = CURDATE()")
            res = cursor.fetchone()
            cursor.close(); conexion.close()
            return res['total'] if res['total'] else 0
        return 0

    def obtener_estadisticas_ingresos(self, periodo):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Usamos 'fechaPago' que es el nombre real en tu DB[cite: 11]
            
            if periodo == "Semanal":
                # Agrupa por día de la semana usando expresiones completas para evitar ONLY_FULL_GROUP_BY
                sql = """SELECT DAYOFWEEK(fecha) AS orden, DAYNAME(fecha) AS etiqueta, SUM(monto) AS total
                        FROM pago
                        WHERE YEARWEEK(fecha) = YEARWEEK(NOW())
                        GROUP BY DAYOFWEEK(fecha), DAYNAME(fecha)
                        ORDER BY orden"""

            elif periodo == "Mensual":
                # Agrupa por día del mes con la fecha formateada y el número del día para ordenar
                sql = """SELECT DAY(fecha) AS dia_num, DATE_FORMAT(fecha, '%d/%m') AS etiqueta, SUM(monto) AS total
                        FROM pago
                        WHERE MONTH(fecha) = MONTH(NOW()) AND YEAR(fecha) = YEAR(NOW())
                        GROUP BY dia_num, DATE_FORMAT(fecha, '%d/%m')
                        ORDER BY dia_num"""

            else: # Anual
                # Agrupa por mes asegurando orden correcto
                sql = """SELECT MONTH(fecha) AS mes_num, MONTHNAME(fecha) AS etiqueta, SUM(monto) AS total
                        FROM pago
                        WHERE YEAR(fecha) = YEAR(NOW())
                        GROUP BY mes_num, MONTHNAME(fecha)
                        ORDER BY mes_num"""
            
            try:
                cursor.execute(sql)
                res = cursor.fetchall()
                return res
            except Exception as e:
                print(f"Error en SQL: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    def validar_usuario(self, usuario, password):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                # Usamos la relación directa empleado_idempleado de la tabla usuario
                sql = """SELECT u.idusuario, u.nombre_usuario, u.rol, u.empleado_idempleado as idempleado,
                                 p.nombre, p.apellido, p.dni
                         FROM usuario u
                         LEFT JOIN empleado e ON u.empleado_idempleado = e.idempleado
                         LEFT JOIN persona p ON e.persona_idpersona = p.idpersona
                         WHERE u.nombre_usuario = %s AND u.password = %s"""
                cursor.execute(sql, (usuario, password))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error en validación: {e}")
                return None
            finally:
                cursor.close(); conexion.close()
        return None
        
    def obtener_pagos_para_exportar(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                # Traemos el detalle de todos los cobros realizados
                sql = """SELECT p.idpago, p.fecha, p.monto, mp.tipoPago, s.nombre as servicio
                         FROM pago p
                         JOIN metodo_pago mp ON p.metodo_pago_idmetodopago = mp.idmetodopago
                         JOIN reserva r ON p.reserva_idreserva = r.idreserva
                         JOIN servicio s ON r.servicio_idservicio = s.idservicio
                         ORDER BY p.fecha DESC"""
                cursor.execute(sql)
                return cursor.fetchall()
            finally:
                cursor.close(); conexion.close()
        return []
    

def eliminar_empleado(self, id_empleado):
        conexion = self.conectar()
        if not conexion:
            return False
        
        cursor = conexion.cursor()
        try:
            conexion.start_transaction()
            # 1. Borramos el usuario asociado primero (por la clave foránea)
            sql_u = "DELETE FROM usuario WHERE empleado_idempleado = %s"
            cursor.execute(sql_u, (id_empleado,))
            
            # 2. Borramos el registro de la tabla empleado
            sql_e = "DELETE FROM empleado WHERE idempleado = %s"
            cursor.execute(sql_e, (id_empleado,))
            
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar empleado: {e}")
            conexion.rollback()
            return False
        finally:
            cursor.close()
            conexion.close()

def actualizar_credenciales_propio(self, id_empleado, nuevo_usuario, nueva_pass):
        conexion = self.conectar()
        if not conexion: return False
        cursor = conexion.cursor()
        try:
            # Actualizamos el nombre de usuario y la contraseña 
            # solo para el empleado que tiene la sesión iniciada
            sql = "UPDATE usuario SET nombre_usuario = %s, password = %s WHERE empleado_idempleado = %s"
            cursor.execute(sql, (nuevo_usuario, nueva_pass, id_empleado))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar perfil: {e}")
            return False
        finally:
            cursor.close(); conexion.close()