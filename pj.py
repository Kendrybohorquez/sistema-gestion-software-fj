import datetime
import os


# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS Y SISTEMA DE LOGS
# ==========================================
class ErrorSistemaFJ(Exception):
  """Excepción base para los errores del sistema."""

  pass


class ClienteInvalidoError(ErrorSistemaFJ):
  """Se lanza cuando los datos del cliente no son válidos."""

  pass


class ReservaError(ErrorSistemaFJ):
  """Se lanza cuando ocurre un fallo al procesar una reserva."""

  pass


def registrar_log(mensaje):
  """Registra eventos y errores en un archivo de texto (logs)."""
  fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  log_entry = f"[{fecha_hora}] {mensaje}\n"
  with open("sistema_errores.log", "a", encoding="utf-8") as archivo:
    archivo.write(log_entry)


# ==========================================
# 2. CLASE CLIENTE (Encapsulación y Validaciones)
# ==========================================
class Cliente:

  def __init__(self, nombre, identificacion, email):
    if not nombre or not identificacion:
      raise ClienteInvalidoError(
          "Error: Nombre e identificación no pueden estar vacíos."
      )
    self.__nombre = nombre
    self.__identificacion = identificacion
    self.__email = email

  @property
  def nombre(self):
    return self.__nombre

  @property
  def identificacion(self):
    return self.__identificacion

  def obtener_info(self):
    return (
        f"Client: {self.__nombre} | ID: {self.__identificacion} | Email:"
        f" {self.__email}"
    )


# ==========================================
# 3. CLASE ABSTRACTA SERVICIO Y CLASES HIJAS (Polimorfismo)
# ==========================================
class Servicio:

  def __init__(self, nombre_servicio, precio_base):
    self._nombre_servicio = nombre_servicio
    self._precio_base = precio_base

  def calcular_costo(self):
    raise NotImplementedError("Este método debe ser implementado por la subclase.")

  def descripcion(self):
    return f"Service: {self._nombre_servicio} | Base Price: ${self._precio_base}"


# Servicio 1: Reserva de Salas (Sobrecarga de métodos para costos)
class ReservaSala(Servicio):

  def __init__(self, nombre_servicio, precio_base, capacidad):
    super().__init__(nombre_servicio, precio_base)
    self.capacidad = capacidad

  def calcular_costo(self, descuento=0, impuesto=1.19):
    """Método sobrecargado con parámetros opcionales de descuento e impuesto."""
    try:
      if descuento < 0:
        raise ValueError("El descuento no puede ser negativo.")
      costo_final = (self._precio_base - descuento) * impuesto
      return max(0.0, costo_final)
    except Exception as e:
      registrar_log(f"Error calculando costo en ReservaSala: {e}")
      raise


# Servicio 2: Alquiler de Equipos
class AlquilerEquipo(Servicio):

  def __init__(self, nombre_servicio, precio_base, horas):
    super().__init__(nombre_servicio, precio_base)
    self.horas = horas

  def calcular_costo(self):
    return self._precio_base * self.horas


# Servicio 3: Asesoría Especializada
class AsesoriaEspecializada(Servicio):

  def __init__(self, nombre_servicio, precio_base, nivel_complejidad):
    super().__init__(nombre_servicio, precio_base)
    self.nivel_complejidad = nivel_complejidad

  def calcular_costo(self):
    multiplicador = 1.5 if self.nivel_complejidad == "Alta" else 1.0
    return self._precio_base * multiplicador


# ==========================================
# 4. CLASE RESERVA (Manejo de excepciones try/except/else/finally)
# ==========================================
class Reserva:

  def __init__(self, cliente, servicio, duracion_horas):
    self.cliente = cliente
    self.servicio = servicio
    self.duracion_horas = duracion_horas
    self.estado = "Pendiente"

  def procesar_reserva(self):
    print(f"\n--- Procesando reserva para {self.cliente.nombre} ---")
    try:
      # Validación estricta
      if self.duracion_horas <= 0:
        raise ReservaError("La duración de la reserva debe ser mayor a cero.")

      # Cálculo del costo usando polimorfismo
      if isinstance(self.servicio, ReservaSala):
        costo = self.servicio.calcular_costo(
            descuento=10
        )  # Usando sobrecarga
      else:
        costo = self.servicio.calcular_costo()

    except ReservaError as re:
      registrar_log(f"Fallo en la reserva: {re}")
      self.estado = "Fallida"
      raise
    except Exception as e:
      # Encadenamiento de excepciones
      registrar_log(f"Error crítico en reserva: {e}")
      self.estado = "Fallida"
      raise ReservaError(
          "No se pudo completar la reserva debido a un error interno."
      ) from e
    else:
      # Se ejecuta si todo sale bien
      self.estado = "Confirmada"
      print(f"¡Éxito! Reserva confirmada. Costo total: ${costo:.2f}")
      registrar_log(
          f"Reserva exitosa para el cliente {self.cliente.identificacion}"
      )
    finally:
      # Se ejecuta siempre, ocurra o no error
      print(f"Estado final de la operación: {self.estado}")


# ==========================================
# 5. SIMULACIÓN DE 10 OPERACIONES (Válidas e Inválidas)
# ==========================================
if __name__ == "__main__":
  print("=== INICIANDO SIMULACIÓN DEL SISTEMA SOFTWARE FJ ==\n")

  # Limpiar log anterior si existe para pruebas limpias
  if os.path.exists("sistema_errores.log"):
    os.remove("sistema_errores.log")

  operaciones = [
      # 1. Cliente y Reserva Válida (Sala)
      lambda: Reserva(
          Cliente("Ana Gómez", "1010", "ana@mail.com"),
          ReservaSala("Sala Ejecutiva", 100.0, 5),
          2,
      ).procesar_reserva(),
      # 2. Cliente Inválido (Nombre vacío - Lanzará Excepción)
      lambda: Reserva(
          Cliente("", "", ""), ReservaSala("Sala B", 80.0, 3), 2
      ).procesar_reserva(),
      # 3. Reserva con duración inválida (0 o negativa - Lanzará Excepción)
      lambda: Reserva(
          Cliente("Carlos Pérez", "2020", "carlos@mail.com"),
          AlquilerEquipo("Laptop Gamer", 50.0, 2),
          0,
      ).procesar_reserva(),
      # 4. Alquiler de Equipo Válido
      lambda: Reserva(
          Cliente("Lucía Torres", "3030", "lucia@mail.com"),
          AlquilerEquipo("Proyector 4K", 30.0, 4),
          3,
      ).procesar_reserva(),
      # 5. Asesoría Especializada Válida
      lambda: Reserva(
          Cliente("Mateo Ruiz", "4040", "mateo@mail.com"),
          AsesoriaEspecializada("Arquitectura Cloud", 200.0, "Alta"),
          5,
      ).procesar_reserva(),
      # 6. Descuento inválido en Sala (generará excepción capturada en log)
      lambda: ReservaSala("Sala Conferencia", 150.0, 10).calcular_costo(
          descuento=-50
      ),
      # 7. Operación adicional válida
      lambda: Reserva(
          Cliente("Sofía Castro", "5050", "sofia@mail.com"),
          AlquilerEquipo("Tablet Gráfica", 40.0, 2),
          2,
      ).procesar_reserva(),
      # 8. Operación adicional válida
      lambda: Reserva(
          Cliente("David Morales", "6060", "david@mail.com"),
          AsesoriaEspecializada("Ciberseguridad", 180.0, "Media"),
          3,
      ).procesar_reserva(),
      # 9. Intento de cliente con datos nulos
      lambda: Cliente("", "9999", "error@mail.com"),
      # 10. Reserva con servicio y duración correcta
      lambda: Reserva(
          Cliente("Valeria Vargas", "7070", "valeria@mail.com"),
          ReservaSala("Auditorio Principal", 300.0, 50),
          4,
      ).procesar_reserva(),
  ]

  # Ejecutando secuencialmente las 10 operaciones probando la estabilidad del sistema
  for i, op in enumerate(operaciones, 1):
    print(f"\n--- Operación #{i} ---")
    try:
      op()
    except Exception as ex:
      print(
          f"[CONTROLADOR PRINCIPAL] Error capturado y registrado con éxito: {ex}"
      )

  print(
      "\n=== SIMULACIÓN FINALIZADA. Revise el archivo 'sistema_errores.log' ==="
  )