from abc import ABC, abstractmethod
import datetime
import os


# Excepciones personalizadas para controlar los errores del sistema
class ErrorSistemaFJ(Exception):
  """Clase base para errores propios del sistema."""


class ClienteInvalidoError(ErrorSistemaFJ):
  """Error cuando los datos del cliente no son válidos."""


class ServicioInvalidoError(ErrorSistemaFJ):
  """Error cuando un servicio o sus parámetros fallan."""


class ReservaError(ErrorSistemaFJ):
  """Error al crear, procesar o cancelar una reserva."""


# Guarda eventos y errores en un archivo de texto sin usar base de datos
def registrar_log(mensaje):
  fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  linea = f"[{fecha_hora}] {mensaje}\n"
  try:
    with open("sistema_errores.log", "a", encoding="utf-8") as archivo:
      archivo.write(linea)
  except OSError as err:
    print(f"No se pudo guardar en el log: {err}")


# Clase abstracta general para las entidades del sistema
class EntidadSistema(ABC):

  def __init__(self, identificador):
    if not identificador or not str(identificador).strip():
      raise ErrorSistemaFJ("El identificador es obligatorio.")
    self._identificador = str(identificador).strip()

  @property
  def identificador(self):
    return self._identificador

  @abstractmethod
  def describir(self):
    pass


# Clase Cliente con encapsulación y validaciones
class Cliente(EntidadSistema):

  def __init__(self, nombre, identificacion, correo):
    super().__init__(identificacion)
    if not nombre or not str(nombre).strip():
      raise ClienteInvalidoError("El nombre del cliente no puede estar vacío.")
    if not correo or "@" not in str(correo) or "." not in str(correo):
      raise ClienteInvalidoError("El correo electrónico no es válido.")

    # Atributos privados para encapsular los datos personales
    self.__nombre = str(nombre).strip()
    self.__correo = str(correo).strip()

  @property
  def nombre(self):
    return self.__nombre

  @property
  def correo(self):
    return self.__correo

  def describir(self):
    return (
        f"Cliente [{self._identificador}]: {self.__nombre} - {self.__correo}"
    )


# Clase abstracta Servicio
class Servicio(EntidadSistema, ABC):

  def __init__(self, codigo_servicio, nombre_servicio, precio_base):
    super().__init__(codigo_servicio)
    if not nombre_servicio or not str(nombre_servicio).strip():
      raise ServicioInvalidoError("El nombre del servicio es obligatorio.")
    if precio_base is None or float(precio_base) <= 0:
      raise ServicioInvalidoError("El precio base debe ser mayor a cero.")

    self._nombre_servicio = str(nombre_servicio).strip()
    self._precio_base = float(precio_base)

  @property
  def nombre_servicio(self):
    return self._nombre_servicio

  @property
  def precio_base(self):
    return self._precio_base

  def validar_parametros(self, unidades, descuento, impuesto):
    if unidades is None or unidades <= 0:
      raise ServicioInvalidoError("La cantidad o duración debe ser mayor a cero.")
    if descuento < 0 or impuesto < 0:
      raise ServicioInvalidoError(
          "El descuento y el impuesto no pueden ser negativos."
      )

  @abstractmethod
  def calcular_costo(self, unidades=1, descuento=0.0, impuesto=0.19):
    pass

  def describir(self):
    return (
        f"Servicio [{self._identificador}]: {self._nombre_servicio} | Base:"
        f" ${self._precio_base:.2f}"
    )


# Servicio 1: Reserva de salas
class ReservaSala(Servicio):

  def __init__(
      self, codigo_servicio, nombre_servicio, precio_base, capacidad_personas
  ):
    super().__init__(codigo_servicio, nombre_servicio, precio_base)
    if capacidad_personas is None or int(capacidad_personas) <= 0:
      raise ServicioInvalidoError("La capacidad de la sala debe ser positiva.")
    self.capacidad_personas = int(capacidad_personas)

  # Método con parámetros opcionales (descuento e impuesto)
  def calcular_costo(self, unidades=1, descuento=0.0, impuesto=0.19):
    self.validar_parametros(unidades, descuento, impuesto)
    subtotal = self._precio_base * unidades
    if descuento > subtotal:
      raise ServicioInvalidoError(
          "El descuento no puede superar el subtotal de la sala."
      )
    total = (subtotal - descuento) * (1 + impuesto)
    return round(total, 2)

  def describir(self):
    return (
        f"Sala [{self._identificador}] {self._nombre_servicio} (Capacidad:"
        f" {self.capacidad_personas}) - Base: ${self._precio_base:.2f}"
    )


# Servicio 2: Alquiler de equipos
class AlquilerEquipo(Servicio):

  def __init__(
      self, codigo_servicio, nombre_servicio, precio_base, tipo_equipo
  ):
    super().__init__(codigo_servicio, nombre_servicio, precio_base)
    if not tipo_equipo or not str(tipo_equipo).strip():
      raise ServicioInvalidoError("Debe indicar el tipo de equipo.")
    self.tipo_equipo = str(tipo_equipo).strip()

  def calcular_costo(self, unidades=1, descuento=0.0, impuesto=0.19):
    self.validar_parametros(unidades, descuento, impuesto)
    subtotal = self._precio_base * unidades
    if descuento > subtotal:
      raise ServicioInvalidoError(
          "El descuento no puede superar el subtotal del alquiler."
      )
    total = (subtotal - descuento) * (1 + impuesto)
    return round(total, 2)

  def describir(self):
    return (
        f"Equipo [{self._identificador}] {self._nombre_servicio} (Tipo:"
        f" {self.tipo_equipo}) - Base: ${self._precio_base:.2f}"
    )


# Servicio 3: Asesorías especializadas
class AsesoriaEspecializada(Servicio):

  FACTORES = {"Baja": 1.0, "Media": 1.25, "Alta": 1.5}

  def __init__(
      self, codigo_servicio, nombre_servicio, precio_base, complejidad="Media"
  ):
    super().__init__(codigo_servicio, nombre_servicio, precio_base)
    if complejidad not in self.FACTORES:
      raise ServicioInvalidoError(
          f"Complejidad inválida '{complejidad}'. Use Baja, Media o Alta."
      )
    self.complejidad = complejidad

  def calcular_costo(self, unidades=1, descuento=0.0, impuesto=0.19):
    self.validar_parametros(unidades, descuento, impuesto)
    factor = self.FACTORES[self.complejidad]
    subtotal = self._precio_base * unidades * factor
    if descuento > subtotal:
      raise ServicioInvalidoError(
          "El descuento no puede superar el subtotal de la asesoría."
      )
    total = (subtotal - descuento) * (1 + impuesto)
    return round(total, 2)

  def describir(self):
    return (
        f"Asesoría [{self._identificador}] {self._nombre_servicio}"
        f" (Complejidad: {self.complejidad}) - Base: ${self._precio_base:.2f}"
    )


# Clase Reserva para manejar estados y excepciones
class Reserva:

  def __init__(self, codigo_reserva, cliente, servicio, duracion):
    if not codigo_reserva or not str(codigo_reserva).strip():
      raise ReservaError("El código de reserva es obligatorio.")
    if not isinstance(cliente, Cliente):
      raise ReservaError("El cliente no es válido.")
    if not isinstance(servicio, Servicio):
      raise ReservaError("El servicio no es válido.")
    if duracion is None or duracion <= 0:
      raise ReservaError("La duración debe ser mayor a cero.")

    self.codigo_reserva = str(codigo_reserva).strip()
    self.cliente = cliente
    self.servicio = servicio
    self.duracion = duracion
    self.estado = "Pendiente"
    self.costo_total = 0.0

  def procesar_reserva(self, descuento=0.0, impuesto=0.19):
    print(f"   Procesando {self.codigo_reserva} ({self.servicio.describir()})...")
    try:
      if self.estado == "Cancelada":
        raise ReservaError("No se puede procesar una reserva cancelada.")

      costo = self.servicio.calcular_costo(
          unidades=self.duracion, descuento=descuento, impuesto=impuesto
      )
    except ServicioInvalidoError as err_srv:
      self.estado = "Fallida"
      registrar_log(f"Error de servicio en {self.codigo_reserva}: {err_srv}")
      raise ReservaError(
          f"Fallo en el servicio de {self.codigo_reserva}."
      ) from err_srv
    except Exception as err_gral:
      self.estado = "Fallida"
      registrar_log(f"Error inesperado en {self.codigo_reserva}: {err_gral}")
      raise ReservaError(
          f"No se pudo procesar {self.codigo_reserva}."
      ) from err_gral
    else:
      self.costo_total = costo
      self.estado = "Confirmada"
      registrar_log(
          f"Reserva {self.codigo_reserva} confirmada para cliente"
          f" {self.cliente.identificador}. Total: ${self.costo_total:.2f}"
      )
      print(
          f"   Confirmada para {self.cliente.nombre} | Total:"
          f" ${self.costo_total:.2f}"
      )
    finally:
      print(
          f"   Fin del proceso de {self.codigo_reserva} (Estado:"
          f" {self.estado})"
      )

  def cancelar_reserva(self):
    if self.estado == "Confirmada":
      self.estado = "Cancelada"
      registrar_log(f"Reserva {self.codigo_reserva} cancelada.")
      print(f"   Reserva {self.codigo_reserva} cancelada.")
    else:
      raise ReservaError(
          f"No se puede cancelar {self.codigo_reserva} en estado"
          f" '{self.estado}'."
      )


# Maneja listas internas en memoria sin base de datos
class GestorSoftwareFJ:

  def __init__(self):
    self.clientes = []
    self.servicios = []
    self.reservas = []

  def registrar_cliente(self, cliente):
    if not isinstance(cliente, Cliente):
      raise ClienteInvalidoError("Dato de cliente no válido.")
    if any(c.identificador == cliente.identificador for c in self.clientes):
      raise ClienteInvalidoError(
          f"Ya existe un cliente con ID {cliente.identificador}."
      )
    self.clientes.append(cliente)
    registrar_log(
        f"Cliente registrado: {cliente.identificador} - {cliente.nombre}"
    )
    return cliente

  def registrar_servicio(self, servicio):
    if not isinstance(servicio, Servicio):
      raise ServicioInvalidoError("Dato de servicio no válido.")
    self.servicios.append(servicio)
    registrar_log(
        f"Servicio registrado: {servicio.identificador} -"
        f" {servicio.nombre_servicio}"
    )
    return servicio

  def crear_y_procesar_reserva(
      self, codigo, cliente, servicio, duracion, descuento=0.0, impuesto=0.19
  ):
    reserva = Reserva(codigo, cliente, servicio, duracion)
    self.reservas.append(reserva)
    reserva.procesar_reserva(descuento=descuento, impuesto=impuesto)
    return reserva


# Simulación de 10 operaciones (válidas y con error)
def ejecutar_simulacion():
  if os.path.exists("sistema_errores.log"):
    os.remove("sistema_errores.log")

  gestor = GestorSoftwareFJ()
  sala_ejecutiva = ReservaSala("SRV-SALA-1", "Sala Ejecutiva", 100.0, 10)
  portatil_dev = AlquilerEquipo(
      "SRV-EQ-1", "Portátil Desarrollo", 40.0, "Laptop"
  )
  asesoria_cloud = AsesoriaEspecializada(
      "SRV-ASE-1", "Asesoría Cloud", 180.0, "Alta"
  )

  operaciones = [
      # 1. Reserva válida de sala con descuento
      lambda: gestor.crear_y_procesar_reserva(
          "RES-001",
          gestor.registrar_cliente(
              Cliente("Valentina Díaz", "1001", "valentina@softwarefj.com")
          ),
          gestor.registrar_servicio(sala_ejecutiva),
          2,
          descuento=20.0,
      ),
      # 2. Cliente inválido por correo
      lambda: gestor.registrar_cliente(
          Cliente("Camilo Ortiz", "1002", "correo_invalido.com")
      ),
      # 3. Alquiler de equipo válido
      lambda: gestor.crear_y_procesar_reserva(
          "RES-002",
          gestor.registrar_cliente(
              Cliente("Mariana López", "1003", "mariana@softwarefj.com")
          ),
          gestor.registrar_servicio(portatil_dev),
          3,
      ),
      # 4. Reserva con duración cero
      lambda: gestor.crear_y_procesar_reserva(
          "RES-003",
          Cliente("Juan Torres", "1004", "juan@softwarefj.com"),
          portatil_dev,
          0,
      ),
      # 5. Asesoría especializada válida
      lambda: gestor.crear_y_procesar_reserva(
          "RES-004",
          gestor.registrar_cliente(
              Cliente("Sofía Navarro", "1005", "sofia@softwarefj.com")
          ),
          gestor.registrar_servicio(asesoria_cloud),
          2,
      ),
      # 6. Servicio con precio negativo
      lambda: gestor.registrar_servicio(
          AlquilerEquipo("SRV-ERR-1", "Proyector HD", -35.0, "Proyector")
      ),
      # 7. Cliente con identificación duplicada
      lambda: gestor.registrar_cliente(
          Cliente("Valentina Duplicada", "1001", "dup@softwarefj.com")
      ),
      # 8. Descuento mayor al subtotal
      lambda: gestor.crear_y_procesar_reserva(
          "RES-005",
          Cliente("Andrés Mejía", "1006", "andres@softwarefj.com"),
          sala_ejecutiva,
          1,
          descuento=500.0,
      ),
      # 9. Reserva válida de asesoría
      lambda: gestor.crear_y_procesar_reserva(
          "RES-006",
          gestor.registrar_cliente(
              Cliente("Daniela Vega", "1007", "daniela@softwarefj.com")
          ),
          asesoria_cloud,
          1,
      ),
      # 10. Cancelar reserva que no está confirmada
      lambda: Reserva(
          "RES-007",
          Cliente("Luis Castro", "1008", "luis@softwarefj.com"),
          sala_ejecutiva,
          1,
      ).cancelar_reserva(),
  ]

  print("=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")
  for numero, operacion in enumerate(operaciones, start=1):
    print(f"\nOperación {numero}/10:")
    try:
      operacion()
    except ErrorSistemaFJ as err_controlado:
      registrar_log(f"Operación {numero} controlada: {err_controlado}")
      print(f"   Error controlado: {err_controlado}")
    except Exception as err_inesperado:
      registrar_log(f"Operación {numero} error no previsto: {err_inesperado}")
      print(f"   Error no previsto: {err_inesperado}")

  print(
      "\nSimulación terminada. Revisa 'sistema_errores.log' para ver los"
      " registros."
  )


if __name__ == "__main__":
  ejecutar_simulacion()