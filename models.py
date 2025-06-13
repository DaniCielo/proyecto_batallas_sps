import db
from sqlalchemy import (Column, Integer, String, Boolean, ForeignKey, DateTime, LargeBinary, UniqueConstraint,
                        PrimaryKeyConstraint)


class Carta(db.Base):
    """Tabla que guarda todas las cartas del juego y sus datos asociados"""

    __tablename__ = "carta"

    id_card = Column(Integer, primary_key=True, autoincrement=True)   # ID generado para DB, autoincrement de SQLAlchemy
    id_game = Column(Integer, nullable=False)      # Las cartas en el juego son identificadas mediante este ID
    nivel = Column(Integer, nullable=False)        # Es el nivel que tiene la carta, máximo 10 según tipo
    nombre = Column(String(50))                    # El nombre que tiene cada carta
    grupo = Column(String(10))                     # Hay varios: reward, dice, promo, soulbond, etc (para imagen)
    imagen = Column(LargeBinary)                   # Imagen de la carta que se usará para mostrar en pantalla
    extra = Column(String)                         # Campo extra por las dudas

    # Resticción de carta y nivel único
    __table_args__ = (UniqueConstraint("id_game", "nivel", name="card_and_lv"),)

    def __init__(self, id_game, nivel, nombre=None,     # Cada carta podrá grabarse con los datos básicos del ID del
                 grupo=None, imagen=None, extra=None):  # juego y su nivel pudiendo completarse el resto luego
        self.id_game = id_game
        self.nivel = nivel
        self.nombre = nombre
        self.grupo = grupo
        self.imagen = imagen
        self.extra = extra

    def __str__(self):
        return "Carta {}, ID juego Nº {}, nombre: -{}-. Nivel {}.".format(self.id_card, self.id_game, self.nombre,
                                                                          self.nivel)


class Regla(db.Base):
    """La tabla Regla contiene las distintas reglas que existen, son principalmente sus nombres, explicación e
        imágenes"""

    __tablename__ = "regla"
    __table_args__ = {'sqlite_autoincrement': True}

    id_regla = Column(Integer, primary_key=True)                     # ID generado para nuestra DB
    nombre = Column(String(25), nullable=False, unique=True)         # Con el nombre el juego identifica las reglas
    descripcion = Column(String(100))                                # Explicación de la regla
    imagen = Column(LargeBinary)                                     # Es un icono o logo que representa la regla
    extra = Column(String)                                           # Campo extra por las dudas

    def __init__(self, nombre, descripcion=None, imagen=None, extra=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.extra = extra

    def __str__(self):
        return "Regla almacenada bajo ID Nº {}, nombre: -{}-. Descripción: {}.".format(self.id_regla, self.nombre,
                                                                                       self.descripcion)


class Batalla(db.Base):
    """Batallas tiene la información de todas las partidas que se hayan grabado y constituirá la fuente de información
    para hacer estadísticas del éxito que hubo en jugadas anteriores y de esa manera sugerir o informar qué jugar"""

    __tablename__ = "batalla"
    __table_args__ = {'sqlite_autoincrement': True}

    id_batalla = Column(Integer, primary_key=True)  # ID generado para nuestra DB

    seed_ingame = Column(String(32))                # Código interno que se genera para la batalla

    mana_max = Column(Integer)                      # Es una regla, las cartas jugadas no pueden sumar más de este valor

    mazo_red = Column(Boolean)                      # Al iniciar una batalla algunos mazos estarán habilitados y otros
    mazo_blue = Column(Boolean)                     # no, guardaremos True cuando sí esté activado cada mazo...
    mazo_green = Column(Boolean)                    # por defecto las cartas neutrales siempre están activadas
    mazo_white = Column(Boolean)
    mazo_black = Column(Boolean)
    mazo_gold = Column(Boolean)

    regla1 = Column(String(20))      # Cada regla debe ser grabada en un campo para ello, si hay
    regla2 = Column(String(20))      # menos de 3, el/los vacíos quedarán con None/Null... se
    regla3 = Column(String(20))      # registran con el nombre porque así viene la info

    tipo_combate = Column(String)  # En este campo viene si la batalla es 'Ranked' o un torneo u otras

    formato = Column(String)       # En la modalidad 'Ranked' hay dos tipos: Wild y Modern

    jugador = Column(String(15))   # Nombre dentro del juego

    ganada = Column(Boolean)       # Se graba un True al haberse ganado, False si es pérdida o empate

    fecha = Column(DateTime)       # La fecha que se graba como DateTime aprovechando que así viene

    settings = Column(String)      # Diccionario con varios datos, se guarda completo (para diferenciar torneos)

    rating_level = Column(Integer)  # Es un nivel de liga, 0 para Novice (inicial), 1 para Bronze, 2 para Silver y así

    card0_id = Column(Integer)  # Cada carta y su nivel se guardará según su id_game
    card0_lv = Column(Integer)  # y nivel en dos campos por separado...
    card1_id = Column(Integer)  # siempre debe haber al menos un summoner y una carta,
    card1_lv = Column(Integer)  # cuando no haya otras cartas se grabarán como None/Null
    card2_id = Column(Integer)
    card2_lv = Column(Integer)
    card3_id = Column(Integer)
    card3_lv = Column(Integer)
    card4_id = Column(Integer)
    card4_lv = Column(Integer)
    card5_id = Column(Integer)
    card5_lv = Column(Integer)
    card6_id = Column(Integer)
    card6_lv = Column(Integer)

    extra = Column(String)

    def __init__(self, datos, extra=None):       # El constructor recibe un diccionario con todos los datos
        self.seed_ingame = datos["seed_ingame"]
        self.mana_max = datos["mana_max"]
        self.mazo_red = datos["mazo_red"]
        self.mazo_blue = datos["mazo_blue"]
        self.mazo_green = datos["mazo_green"]
        self.mazo_white = datos["mazo_white"]
        self.mazo_black = datos["mazo_black"]
        self.mazo_gold = datos["mazo_gold"]

        self.regla1 = datos["regla1"]
        try:                                     # Se realiza un try porque el diccionario puede no tener las
            self.regla2 = datos["regla2"]        # reglas 2 y/o 3 cuando se trata de batallas con menor
        except KeyError:                         # cantidad de reglas
            self.regla2 = None
        try:
            self.regla3 = datos["regla3"]
        except KeyError:
            self.regla3 = None

        self.tipo_combate = datos["tipo_combate"]
        self.formato = datos["formato"]
        self.jugador = datos["jugador"]
        self.ganada = datos["ganada"]
        self.fecha = datos["fecha"]
        self.settings = datos["settings"]
        self.rating_level = datos["rating_level"]

        self.card0_id = datos["card0_id"]
        self.card0_lv = datos["card0_lv"]
        self.card1_id = datos["card1_id"]
        self.card1_lv = datos["card1_lv"]
        try:
            self.card2_id = datos["card2_id"]  # Las únicas cartas que seguro hay en una batalla son el summoner y la
            self.card2_lv = datos["card2_lv"]  # primera carta, el resto pueden no estar y se grabarán como None/Null
        except KeyError:
            self.card2_id = None
            self.card2_lv = None
        try:
            self.card3_id = datos["card3_id"]
            self.card3_lv = datos["card3_lv"]
        except KeyError:
            self.card3_id = None
            self.card3_lv = None
        try:
            self.card4_id = datos["card4_id"]
            self.card4_lv = datos["card4_lv"]
        except KeyError:
            self.card4_id = None
            self.card4_lv = None
        try:
            self.card5_id = datos["card5_id"]
            self.card5_lv = datos["card5_lv"]
        except KeyError:
            self.card5_id = None
            self.card5_lv = None
        try:
            self.card6_id = datos["card6_id"]
            self.card6_lv = datos["card6_lv"]
        except KeyError:
            self.card6_id = None
            self.card6_lv = None

        self.extra = extra

    def __str__(self):
        if self.ganada:
            resultado = "ganada"
        else:
            resultado = "perdida"

        if self.regla2 is None:
            reglas = self.regla1
        else:
            if self.regla3 is None:
                reglas = self.regla1 + " - " + self.regla2
            else:
                reglas = self.regla1 + " - " + self.regla2 + " - " + self.regla3

        fecha_string = self.fecha.strftime("%d/%m/%Y")

        return "Batalla {} del {}. Tipo: {} {}. Resultado: {}. Mana máx: {}, reglas: {}".format(
                self.id_batalla, fecha_string, self.tipo_combate, self.formato, resultado, self.mana_max, reglas)


class Usuario(db.Base):
    """Usuario es una tabla que tiene información sobre el perfil con el que se quiera jugar"""

    __tablename__ = "usuario"
    __table_args__ = {'sqlite_autoincrement': True}  # Autoincremento explícito: se verá en la config de la DB

    id_usuario = Column(Integer, primary_key=True)
    nombre_de_usuario = Column(String(20), unique=True)
    contrasenia = Column(String(60))
    usuario_juego = Column(String(50))
    contrasenia_juego = Column(String(60))
    deleted = Column(Boolean)
    extra = Column(String)

    def __init__(self, nombre_usuario, contrasenia, usuario_juego=None, contrasenia_juego=None,
                 deleted=False, extra=None):
        self.nombre_de_usuario = nombre_usuario
        self.contrasenia = contrasenia
        self.usuario_juego = usuario_juego
        self.contrasenia_juego = contrasenia_juego
        self.deleted = deleted
        self.extra = extra

    def __str__(self):
        return "Objeto de clase Usuario. Nombre de usuario: {}".format(self.nombre_de_usuario)


class CartasUsuario(db.Base):
    """Esta tabla tiene el objetivo de almacenar información sobre las cartas que posee un usuario creado, ya que puede
    no disponer de todas. Al momento de sugerir o mostrar debe hacerlo teniendo en cuenta estas cartas"""

    __tablename__ = "cartas_usuario"

    name_user = Column(Integer, ForeignKey("usuario.nombre_de_usuario", ondelete="cascade"))
    id_card = Column(Integer, ForeignKey("carta.id_card", ondelete="cascade"))
    activa = Column(Boolean)

    # Restricción para asignar clave primaria a una combinación de valores, que, por cierto, no pueden estar repetidos
    __table_args__ = (PrimaryKeyConstraint("name_user", "id_card", name="card_lv_and_user"),)

    def __init__(self, usuario, id_card, activa=True):
        self.name_user = usuario
        self.id_card = id_card
        self.activa = activa

    def __str__(self):
        if self.activa:
            texto = "posee"
        else:
            texto = "NO posee"
        return "El usuario {} {} la carta código {}".format(self.name_user, texto, self.id_card)

# SQL
# CREATE TABLE carta (
# 	id_card INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 	id_game INTEGER NOT NULL,
# 	nivel INTEGER NOT NULL,
# 	nombre VARCHAR(50),
# 	grupo VARCHAR(10),
# 	imagen BLOB,
# 	extra VARCHAR,
# 	CONSTRAINT card_and_lv UNIQUE (id_game, nivel)
# )
#
# CREATE TABLE regla (
# 	id_regla INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 	nombre VARCHAR(25) NOT NULL,
# 	descripcion VARCHAR(100),
# 	imagen BLOB,
# 	extra VARCHAR,
# 	UNIQUE (nombre)
# )
#
# CREATE TABLE batalla (
# 	id_batalla INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 	seed_ingame VARCHAR(32),
# 	mana_max INTEGER,
# 	mazo_red BOOLEAN,
# 	mazo_blue BOOLEAN,
# 	mazo_green BOOLEAN,
# 	mazo_white BOOLEAN,
# 	mazo_black BOOLEAN,
# 	mazo_gold BOOLEAN,
# 	regla1 VARCHAR(20),
# 	regla2 VARCHAR(20),
# 	regla3 VARCHAR(20),
# 	tipo_combate VARCHAR,
# 	formato VARCHAR,
# 	jugador VARCHAR(15),
# 	ganada BOOLEAN,
# 	fecha DATETIME,
# 	settings VARCHAR,
# 	rating_level INTEGER,
# 	card0_id INTEGER,
# 	card0_lv INTEGER,
# 	card1_id INTEGER,
# 	card1_lv INTEGER,
# 	card2_id INTEGER,
# 	card2_lv INTEGER,
# 	card3_id INTEGER,
# 	card3_lv INTEGER,
# 	card4_id INTEGER,
# 	card4_lv INTEGER,
# 	card5_id INTEGER,
# 	card5_lv INTEGER,
# 	card6_id INTEGER,
# 	card6_lv INTEGER,
# 	extra VARCHAR
# )
#
# CREATE TABLE usuario (
# 	id_usuario INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# 	nombre_de_usuario VARCHAR(20) UNIQUE,
# 	contrasenia VARCHAR(60),
# 	usuario_juego VARCHAR(50),
# 	contrasenia_juego VARCHAR(60),
# 	deleted BOOLEAN,
# 	extra VARCHAR
# )
#
# CREATE TABLE cartas_usuario (
# 	name_user INTEGER NOT NULL,
# 	id_card INTEGER NOT NULL,
# 	activa BOOLEAN,
# 	CONSTRAINT card_lv_and_user PRIMARY KEY (name_user, id_card),
# 	FOREIGN KEY(name_user) REFERENCES usuario (nombre_de_usuario),
# 	FOREIGN KEY(id_card) REFERENCES carta (id_card) ON DELETE CASCADE
# )
