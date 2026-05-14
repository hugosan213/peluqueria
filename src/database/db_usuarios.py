from .base import BaseDatabase

class UsuariosDB(BaseDatabase):
    

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


    def usuario_existe(self, nombre_usuario):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT idusuario FROM usuario WHERE nombre_usuario = %s", (nombre_usuario,))
            existe = cursor.fetchone() is not None
            cursor.close(); conexion.close()
            return existe
        return False


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

    def validar_usuario(self, usuario, password):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                # Agregamos u.password a la lista de campos seleccionados
                sql = """SELECT u.idusuario, u.nombre_usuario, u.password, u.rol, u.empleado_idempleado as idempleado,
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
    
        # Agregar esto a database/db_usuarios.py
    def forzar_cambio_password(self, id_empleado, nueva_password):
        conexion = self.conectar()
        if not conexion: return False
        cursor = conexion.cursor()
        try:
            sql = "UPDATE usuario SET password = %s WHERE empleado_idempleado = %s"
            cursor.execute(sql, (nueva_password, id_empleado))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close(); conexion.close()