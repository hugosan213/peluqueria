from .base import BaseDatabase

class FinanzasDB(BaseDatabase):

    # En db_finanzas.py
    def obtener_caja_diaria(self):
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Asegúrate de que 'p.fecha' coincida con el nombre en tu tabla 'pago'
            sql = """
                SELECT mp.tipoPago, SUM(p.monto) as total 
                FROM pago p 
                JOIN metodo_pago mp ON p.metodo_pago_idmetodopago = mp.idmetodopago 
                WHERE DATE(p.fecha) = CURDATE() 
                GROUP BY mp.tipoPago
            """
            cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close(); conexion.close()
            return res
        return []

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
    
    def obtener_ranking_empleados(self):
        """Calcula el total generado por cada empleado en el mes actual."""
        conexion = self.conectar()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            sql = """SELECT CONCAT(p.nombre, ' ', p.apellido) AS empleado, SUM(pag.monto) AS total
                     FROM pago pag
                     JOIN reserva r ON pag.reserva_idreserva = r.idreserva
                     JOIN empleado e ON r.empleado_idempleado = e.idempleado
                     JOIN persona p ON e.persona_idpersona = p.idpersona
                     WHERE MONTH(pag.fecha) = MONTH(NOW()) AND YEAR(pag.fecha) = YEAR(NOW())
                     GROUP BY e.idempleado, p.nombre, p.apellido
                     ORDER BY total DESC"""
            try:
                cursor.execute(sql)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error en ranking: {e}")
                return []
            finally:
                cursor.close(); conexion.close()
        return []
    

    
    