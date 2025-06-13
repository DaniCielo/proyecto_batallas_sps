import db
import bcrypt
import base64
import os
import json
import io
import requests
from tkinter import ttk, filedialog, Canvas, Radiobutton, Checkbutton
from models import Usuario, Batalla, Carta, Regla, CartasUsuario
from sqlalchemy import func, and_, or_, desc, text, tuple_, select
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image, ImageTk, UnidentifiedImageError, PngImagePlugin
from datetime import datetime, timedelta


#-----------------------------------------------------------------------------------------------------------------------
#                                   FUNCIONES COMUNES
#-----------------------------------------------------------------------------------------------------------------------
def seleccionar_archivo(stringvar_ruta):
    """Función que abre la interfaz de búsqueda de un archivo en windows y coloca la ruta en un stringvar que tiene
    que ser enviado al llamar a la función"""

    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo")

    if ruta_archivo:
        stringvar_ruta.set(ruta_archivo)


def imagen_pillow_ruta(ruta):
    """Función que, utilizando la librería Pillow, crea un objeto imagen-pillow y lo devuelve a quien lo llama. Debe
    recibir la ruta en la que se encuentra el archivo. Devolverá un string con un mensaje de error en caso de
    problemas."""

    try:
        imagen_pillow = Image.open(fp=ruta)  # Abrimos con Pillow
        return imagen_pillow                 # Devolvemos el objeto imagen

    except FileNotFoundError as e:
        print("Error al intentar cargar imagen:", e)
        return "No se ha podido encontrar el archivo"

    except UnidentifiedImageError as e:
        print("Error al intentar cargar imagen:", e)
        return "El formato de archivo no es válido"


def imagen_pillow_web(grupo, carta_nombre, nivel):
    """Función que a partir de los datos de una carta: -nombre-, -nivel- y -grupo-, crea un objeto imagen-pillow y lo
    devuelve a quien lo llama. Devolverá un string con un mensaje de error en caso de problemas."""

    nombre_adaptado = carta_nombre.replace(" ", "%20")
    ruta_web = f"https://d36mxiodymuqjm.cloudfront.net/cards_by_level/{grupo}/{nombre_adaptado}_lv{nivel}.png"
    imagen_recibida = requests.get(ruta_web)

    try:
        imagen_pillow = Image.open(io.BytesIO(imagen_recibida.content))
        return imagen_pillow

    except UnidentifiedImageError as e:
        print("Error imagen no encontrada:", e)
        return "Imagen no encontrada en la web"


def colocar_img_en_widget(imagen_a_colocar, widget, alto, imagen_on=None):
    """Función que calcula el ratio de ancho-alto de una imagen, ajusta su tamaño y luego la carga en 2 tipos de
    widgets: Canvas o Label. También crea el vínculo al widget para que permanezca la imagen."""

    # Llamamos a la función para obtener el ancho manteniendo las proporciones de la imagen original
    ancho = ancho_segun_ratio_imagen(imagen=imagen_a_colocar, nvo_alto=alto)

    # Llamamos a la función que aplica tamaño y genera un formato para tkinter
    imagen_tk = convertir_imagen_tk(imagen_convertir=imagen_a_colocar, ancho_nvo=ancho, alto_nvo=alto)

    # Colocamos la imagen en el widget
    if isinstance(widget, Canvas):
        widget.config(width=ancho, height=alto)  # Le damos tamaño al widget
        widget.create_image(0, 0, anchor="nw", image=imagen_tk)  # Cargamos imagen al Canvas en la esquina

    elif isinstance(widget, ttk.Label):
        widget.config(image=imagen_tk, relief="solid")  # No le damos tamaño, el widget se ajusta al tamaño de la imagen

    elif isinstance(widget, Radiobutton):
        widget.config(image=imagen_tk)

    elif isinstance(widget, Checkbutton):
        widget.config(image=imagen_tk)
        if imagen_on:
            imagen_tk2 = convertir_imagen_tk(imagen_convertir=imagen_on, ancho_nvo=ancho, alto_nvo=alto)
            widget.config(selectimage=imagen_tk2)
            widget.imagen2 = imagen_tk2

    widget.imagen = imagen_tk  # Generamos referencia para que no se borre la imagen


def ancho_segun_ratio_imagen(imagen, nvo_alto):
    """Función que calcula según las proporciones de la imagen el nuevo valor de ancho para un nuevo alto deseado.
    Devuelve un integer para que pueda ser utilizado en widget que requieren este tipo de valor."""

    # Tomamos el alto y el ancho actual de la imagen
    alto_actual = imagen.height  # Sin paréntesis
    ancho_actual = imagen.width

    # Calculamos el ratio entre alto y ancho
    ratio = alto_actual / ancho_actual

    # Calculamos el nuevo ancho para el alto que tendrá la imagen en el widget, que respete la proporción original
    nvo_ancho = int(round(nvo_alto / ratio))

    return nvo_ancho


def convertir_imagen_tk(imagen_convertir, ancho_nvo, alto_nvo):
    """Función para convertir una imagen con formato pillow a una para widgets de tkinter de un tamaño indicado"""

    # Se convierte a tamaño más pequeño
    nueva_imagen = imagen_convertir.resize((ancho_nvo, alto_nvo), Image.Resampling.LANCZOS)

    # Pasamos la imagen a un formato conocido para Tkinter
    imagen_final = ImageTk.PhotoImage(nueva_imagen)

    return imagen_final


def check_imagen_cambiada(switch, imagen):
    """Función para controlar que se ha cargado una imagen nueva momentos antes de enviar la grabación a la DB. En caso (es cierto que se produce una reducción de calidad antes de grabar)
    de que se encuentre una nueva, recupera la imagen de la vinculación del widget"""

    imagen_para_db = None

    # Chequeamos la imagen: si se ha cargado y dejado una imagen nueva el switch será: "con imagen"
    if switch == "con imagen":
        # Guardamos la imagen en memoria para recuperar los datos binarios que irán a la DB
        imagen_temporal = io.BytesIO()
        imagen.save(imagen_temporal, format="PNG")
        imagen_para_db = imagen_temporal.getvalue()

    return imagen_para_db


def check_objeto_db_y_colocacion_frame(objeto_db, frame, tipo, alto, sugerencia=None):
    """Función que luego de realizada una consulta a la DB, chequea si ha dado resultado, si tiene imagen, y, en caso
    de tener la imagen, llama a la función correspondiente para colocarla en un widget dentro del frame"""

    texto = None  # Usado para cuando es regla

    # Chequeamos si la búsqueda en la DB dio resultado, si no es que no había carta o regla
    if objeto_db:
        try:
            imagen = objeto_db.imagen  # Intentamos acceder a la imagen

            # Creamos el label en el que irá la imagen
            label_objeto = ttk.Label(frame, relief="solid", anchor="center")

        except KeyError as e:
            imagen = None

        if imagen:
            # Obtenemos la imagen desde objeto extraído de la DB
            imagen_pillow = Image.open(io.BytesIO(objeto_db.imagen))

            # Llamamos a la función que coloca una imagen en un widget
            colocar_img_en_widget(imagen_a_colocar=imagen_pillow, widget=label_objeto, alto=alto)

            label_objeto.pack(side="left")  # Mostramos el label junto a los demás

        else:
            if isinstance(objeto_db, Carta):  # Cuando la carta no tenga imagen grabada en la DB
                texto = "No\ndisponib."
            elif isinstance(objeto_db, str):  # Cuando la carta no tenga imagen grabada en la DB
                texto = "No\ndisponib."

    else:
        if tipo == "carta":  # En caso de que sea carta queremos mostrar un label que diga que no se jugó carta allí
            texto = "No\ncarta"

    if texto:
        # Label con un texto en reemplazo de la imagen
        label_carta = ttk.Label(frame, text=texto, width=7, relief="solid", anchor="center", justify="center")
        if sugerencia:
            label_carta.pack(side="left", padx=1, ipadx=12, ipady=30)
        else:
            label_carta.pack(side="left", padx=1, ipady=15)


def obtener_ultima_row(frame):
    """Función que busca en todos los widgets existentes dentro de un Frame para obtener la última row que ocupan"""

    # Obtenemos la última fila con widgets del Frame Acciones
    widgets = frame.winfo_children()
    max_fila = 0
    for widget in widgets:
        grid_info = widget.grid_info()
        if grid_info:
            fila = grid_info["row"]
            if fila > max_fila:
                max_fila = fila

    return max_fila


def activa_desactiva_botones(padre, nvo_estado):
    """Función que desactiva todos los botones que estén dentro de un widget"""

    for hijo in padre.winfo_children():
        if isinstance(hijo, ttk.Button):
            hijo.config(state=nvo_estado)


#----------------------------------------------------------------------------------------------------------------------#
#                                   FUNCIONES PARA CARTAS
#----------------------------------------------------------------------------------------------------------------------#
# CREATE
def nueva_carta_db(carta_id, carta_nivel, carta_nombre=None, carta_grupo=None, carta_imagen=None):
    """Función que graba en la DB una Nueva Carta. Controla que previamente no exista una con el mismo nombre.
    Genera los mensajes y se los envía a la función que los llama."""

    if carta_nombre == "":  # Si no hacemos esto no se grabarán los campos como Null en la base de datos
        carta_nombre = None
    if carta_grupo == "":
        carta_grupo = None

    # Consultamos en la DB si existe la carta con base en su ID del juego y su nivel
    carta = carta_datos_db(id_game_card=carta_id, nivel_card=carta_nivel)

    if carta:
        return "Número de carta y nivel existente en DB"

    else:
        # Creamos el objeto invocando al constructor de la clase
        rtdo_nva_carta = None
        c1 = Carta(id_game=carta_id, nivel=carta_nivel, nombre=carta_nombre, grupo=carta_grupo, imagen=carta_imagen)
        db.session.add(c1)
        try:  # Grabado en DB bajo un try por si da error
            db.session.commit()
            rtdo_nva_carta = "Carta ID:-{}- Nivel:-{}- creada con éxito.".format(carta_id, carta_nivel)
        except Exception as e:
            db.session.rollback()
            rtdo_nva_carta = "Error al crear la carta en la DB"
            print("Error al crear la carta:", str(e))
        finally:
            db.session.close()
            return rtdo_nva_carta


# READ
def carta_datos_db(id_card=None, id_game_card=None, nivel_card=None, nombre_card=None, grupo_card=None, todos=None):
    """Función que accede a los datos en la DB correspondientes a la tabla Carta. Puede consultarse por diversos
    campos y solicitarse uno o varios resultados"""

    # Iniciamos la consulta base
    query = db.session.query(Carta)

    # Agregamos los filtros según si se proporciona el valor correspondiente
    if id_card is not None:
        query = query.filter(Carta.id_card == id_card)

    if id_game_card is not None:
        query = query.filter(Carta.id_game == id_game_card)

    if nivel_card is not None:
        query = query.filter(Carta.nivel == nivel_card)

    if nombre_card is not None and nombre_card != "Nulls":
        query = query.filter(Carta.nombre.ilike(f"%{nombre_card}%"))  # En el nombre no diferenciará mayúsc y minúsc
    elif nombre_card == "Nulls":
        query = query.filter(Carta.nombre.is_(None))

    if grupo_card is not None:
        query = query.filter(Carta.grupo == grupo_card)

    # Indicamos si buscamos un solo valor o todos de acuerdo al parámetro
    if not todos:
        carta_db = query.first()
    else:
        carta_db = query.all()

    return carta_db


# UPDATE
def modificar_carta_db(carta_id, carta_id_game_nvo, carta_nivel_nvo, carta_nombre_nvo, carta_grupo_nvo, carta_img_nva):
    """Función que modifica una Carta en la DB. Requiere el ID de la Carta como dato principal más cada dato de los
    que componen un registro de una Carta, aunque estos pueden ser None"""

    # Llamamos a la función que trae los datos de la DB
    carta_db = carta_datos_db(carta_id)

    if carta_id_game_nvo:              # Chequeamos si hay nombre nuevo
        carta_db.id_game = carta_id_game_nvo

    if carta_nivel_nvo:                # Chequeamos si hay descripción nueva
        carta_db.nivel = carta_nivel_nvo

    if carta_nombre_nvo:               # Chequeamos si hay descripción nueva
        carta_db.nombre = carta_nombre_nvo

    if carta_grupo_nvo:                # Chequeamos si hay descripción nueva
        carta_db.grupo = carta_grupo_nvo

    if carta_img_nva:                  # Chequeamos si hay imagen nueva
        if carta_img_nva == "Borrar":
            carta_db.imagen = None
        else:
            carta_db.imagen = carta_img_nva

    resultado = None  # Variable con el resultado
    try:
        db.session.commit()  # Acción de grabar en la DB
        resultado = "Carta modificada correctamente"
    except Exception as e:
        db.session.rollback()
        print("Ha ocurrido un problema al intentar grabar en la DB:", str(e))
        resultado = "Error al modificar la carta en la Base de Datos"
    finally:
        db.session.close()
        return resultado


# DELETE
def eliminar_carta_db(carta_eliminar_id):
    """Función que elimina una Carta de la DB y devuelve un mensaje sobre el resultado"""

    # Hacemos consulta rápida a la DB para buscar la carta
    carta = db.session.get(Carta, carta_eliminar_id)

    # Damos el comando para eliminar
    db.session.delete(carta)

    # Intentamos grabar cambios a la DB y generamos el resultado de si hubo cambios o no
    rtdo_eliminar_carta = "Error"
    try:
        db.session.commit()
        rtdo_eliminar_carta = "Carta eliminada con éxito"
    except Exception as e:
        print("Entrando a except")
        db.session.rollback()
        rtdo_eliminar_carta = "La Carta no pudo ser eliminada de la Base de Datos"
        print("Ha ocurrido un error al intentar eliminar la carta:", e)
    finally:
        db.session.close()
        return rtdo_eliminar_carta


#-----------------------------------------------------------------------------------------------------------------------
def cartas_masivo_hilo_secund(cola_queue, detener_proceso):
    """Función que carga en la DB todas las cartas nuevas de acuerdo a un link que contiene la información de las
    cartas de juego. La carga se hace completa con nombre, grupo e imagen si está disponible."""

    cola_queue.put("Inicio del proceso carga de cartas masivo...\n\n")

    # Dirección web con la información de las cartas del juego
    ruta_web = "https://api.splinterlands.io/cards/get_details"

    # Enviamos una solicitud para descargar la información y luego convertimos a JSON
    cartas_descarga = requests.get(ruta_web)
    cartas_recibidas = cartas_descarga.json()

    total = 0
    for x in cartas_recibidas:
        if x["id"] < 10000:
            total += 1
    cola_queue.put(f"{total} cartas descargadas...\n")

    # Diccionario con el nombre del -grupo- según el dato de -edition-
    edition = {"1": "beta",
               "2": "promo",
               "3": "reward",
               "4": "untamed",
               "5": "dice",
               "6": "gladius",
               "7": "chaos",
               "8": "rift",
               "10": "soulbound",
               "12": "rebellion",
               "13": "soulboundrb"}

    # Diccionario con cantidad de niveles según tipo de carta o -rarity-
    rarity = {1: 11,  # Cartas common: hasta nivel 10
              2: 9,   # Cartas rare: hasta nivel 8
              3: 7,   # Cartas epic: Hasta nivel 6
              4: 5}   # Cartas legendary: hasta nivel 4

    cola_queue.put("Registrando en DB...\n")

    # Recorremos todas las cartas recibidas de principio a fin
    for n, carta_info in enumerate(cartas_recibidas):                         # BORRAR ENUMERATE

        # Extraemos los datos que nos interesan
        carta_id = carta_info["id"]
        carta_nombre = carta_info["name"]
        carta_rarity = carta_info["rarity"]
        carta_edition = carta_info["editions"]
        carta_grupo = None

        # Por arriba de 10.000 hay cosas que no son cartas
        if carta_id < 10000:

            # Determinamos el grupo en texto de acuerdo al diccionario y teniendo en cuenta que puede aparecer -0,1-
            if carta_edition == "0,1":
                carta_grupo = "beta"
            elif carta_edition in edition:
                carta_grupo = edition[carta_edition]
            else:
                print("Edición no reconocida:", carta_edition)

            # Determinamos la cantidad de cartas a través del range que usaremos
            if carta_rarity:
                cant_range = rarity[carta_rarity]
            else:
                print("Rarity no detectado")
                cant_range = 0

            # Hacemos un bucle para crear tantas cartas como niveles tenga
            for i in range(1, cant_range):

                # Buscamos la imagen en la web
                carta_imagen = imagen_pillow_web(grupo=carta_grupo, carta_nombre=carta_nombre, nivel=i)

                # Si se pudo descargar la imagen se grabará con imagen, de lo contrario será None
                if isinstance(carta_imagen, PngImagePlugin.PngImageFile):
                    carta_imagen = check_imagen_cambiada(switch="con imagen", imagen=carta_imagen)
                else:
                    carta_imagen = None

                rtdo_nva_carta = nueva_carta_db(carta_id=carta_id,
                                                carta_nivel=i,
                                                carta_nombre=carta_nombre,
                                                carta_grupo=carta_grupo,
                                                carta_imagen=carta_imagen)

                # Al haber recorrido todos los niveles de una carta, ponemos un mensaje en la queue
                if i == cant_range - 1:
                    if "creada con éxito" in rtdo_nva_carta:
                        mensaje = f"Grabada carta {carta_id}, {carta_nombre}, {i} niveles"
                    elif "existente" in rtdo_nva_carta:
                        mensaje = f"Carta {carta_nombre} ya existente en DB"
                    else:
                        mensaje = f"Error al grabar carta {carta_nombre}"
                    cola_queue.put(f"\n{mensaje}...")

        if detener_proceso.is_set():  # Control para detener y proceso y cancelarlo
            break

        # if n == 2:
        #     exit()

    cola_queue.put("\n\nPROCESO FINALIZADO")


#-----------------------------------------------------------------------------------------------------------------------
#                                   FUNCIONES PARA REGLAS
#-----------------------------------------------------------------------------------------------------------------------
# CREATE
def nueva_regla_db(nombre_regla, descrip_regla=None, imagen_regla=None):
    """Función que graba en la DB una Nueva Regla. Controla que previamente no exista una con el mismo nombre.
    Genera los mensajes y se los envía a la función que los llama."""

    if descrip_regla == "":
        descrip_regla = None

    # Consultamos en la DB si existe la regla
    regla = regla_datos_db(nombre_regla=nombre_regla)

    if regla:
        return "Nombre de Regla existente en DB"

    else:
        # Creamos el objeto invocando al constructor de la clase
        rtdo_nva_regla = None
        r1 = Regla(nombre=nombre_regla, descripcion=descrip_regla, imagen=imagen_regla)
        db.session.add(r1)
        try:  # Grabado en DB bajo un try por si da error
            db.session.commit()
            rtdo_nva_regla = "Regla -{}- creada con éxito.".format(nombre_regla)
        except Exception as e:
            db.session.rollback()
            rtdo_nva_regla = "Error al crear la regla en la DB"
            print("Error al crear la regla:", str(e))
        finally:
            db.session.close()
            return rtdo_nva_regla


# READ
def regla_datos_db(id_regla=None, nombre_regla=None, descripcion_regla=None, todos=None):
    """Función que busca los datos de una Regla en la DB partiendo de la información que se prefiera"""

    # Iniciamos la consulta base
    query = db.session.query(Regla)

    # Agregamos los filtros según si se proporciona el valor correspondiente
    if id_regla is not None:
        query = query.filter(Regla.id_regla == id_regla)

    if nombre_regla is not None:
        query = query.filter(Regla.nombre == nombre_regla)

    if descripcion_regla is not None:
        query = query.filter(Carta.descripcion == descripcion_regla)

    # Indicamos si buscamos un solo valor o todos de acuerdo al parámetro
    if not todos:
        regla_db = query.first()
    else:
        regla_db = query.all()

    return regla_db


# UPDATE
def modificar_regla_db(id_regla, regla_nombre_nvo, regla_descrip_nva, regla_imagen_nva):
    """Función que modifica una Regla en la DB. Requiere el ID de la Regla como dato principal más cada dato de los
    que componen un registro de una Regla, aunque estos pueden ser None"""

    # Llamamos a la función que trae los datos de la DB
    regla_db = regla_datos_db(id_regla=id_regla)

    if regla_nombre_nvo:                # Chequeamos si hay nombre nuevo
        regla_db.nombre = regla_nombre_nvo

    if regla_descrip_nva:               # Chequeamos si hay descripción nueva
        regla_db.descripcion = regla_descrip_nva

    if regla_imagen_nva:                  # Chequeamos si hay imagen nueva
        if regla_imagen_nva == "Borrar":
            regla_db.imagen = None
        else:
            regla_db.imagen = regla_imagen_nva

    resultado = None
    try:
        db.session.commit()
        resultado = "Regla modificada correctamente"
    except Exception as e:
        db.session.rollback()
        print("Ha ocurrido un problema al intentar grabar en la DB:", str(e))
        resultado = "Error al modificar la regla en la Base de Datos"
    finally:
        db.session.close()
        return resultado


# DELETE
def eliminar_regla_db(id_regla):
    """Función que elimina una Regla de la DB y devuelve un mensaje sobre el resultado"""

    # Hacemos una consulta rápida a la DB usando la primary key (id regla)
    regla = db.session.get(Regla, id_regla)

    db.session.delete(regla)
    rtdo_eliminar_regla = "Error"
    try:
        db.session.commit()
        rtdo_eliminar_regla = "Regla eliminada con éxito"
    except Exception as e:
        db.session.rollback()
        rtdo_eliminar_regla = "La Regla no pudo ser eliminada de la Base de Datos"
        print("Ha ocurrido un error al intentar eliminar la regla:", e)
    finally:
        db.session.close()
        return rtdo_eliminar_regla


#----------------------------------------------------------------------------------------------------------------------#
#                                   FUNCIONES PARA BATALLAS
#----------------------------------------------------------------------------------------------------------------------#
# READ
def batalla_datos_db(id_bat=None, seed=None, mana=None, red=None, blue=None, green=None, white=None, black=None,
                     gold=None, regla1=None, regla2=None, regla3=None, tipo=None, formato=None, jugador=None,
                     ganada=None, fecha=None, rating=None, card0=None, card1=None, card2=None, card3=None, card4=None,
                     card5=None, card6=None, todos=None):
    """Función que busca los datos de una Batalla en la DB partiendo de la información que se prefiera"""

    # Iniciamos la consulta base
    query = db.session.query(Batalla)

    # Agregamos los filtros según si se proporciona el valor correspondiente
    if id_bat is not None:
        query = query.filter(Batalla.id_batalla == id_bat)

    if seed is not None:
        query = query.filter(Batalla.nombre == seed)

    if mana is not None:
        query = query.filter(Batalla.mana_max == mana)

    if red is not None:
        query = query.filter(Batalla.mazo_red == red)
    if blue is not None:
        query = query.filter(Batalla.mazo_blue == blue)
    if green is not None:
        query = query.filter(Batalla.mazo_green == green)
    if white is not None:
        query = query.filter(Batalla.mazo_white == white)
    if black is not None:
        query = query.filter(Batalla.mazo_black == black)
    if gold is not None:
        query = query.filter(Batalla.mazo_gold == gold)

    if regla1 is not None:
        query = query.filter(Batalla.regla1 == regla1)
    if regla2 is not None:
        query = query.filter(Batalla.regla2 == regla2)
    if regla3 is not None:
        query = query.filter(Batalla.regla3 == regla3)

    if tipo is not None:
        query = query.filter(Batalla.tipo_combate == tipo)

    if formato is not None:
        query = query.filter(Batalla.formato == formato)

    if jugador is not None:
        query = query.filter(Batalla.jugador == jugador)

    if ganada is not None:
        query = query.filter(Batalla.ganada == ganada)

    if fecha is not None:
        dia_siguiente = fecha + timedelta(days=1)
        query = query.filter(and_(Batalla.fecha > fecha, Batalla.fecha < dia_siguiente))

    if rating is not None:
        query = query.filter(Batalla.rating_level == rating)

    if card0 is not None:
        query = query.filter(Batalla.card0_id == card0)
    if card1 is not None:
        query = query.filter(Batalla.card0_id == card1)
    if card2 is not None:
        query = query.filter(Batalla.card0_id == card2)
    if card3 is not None:
        query = query.filter(Batalla.card0_id == card3)
    if card4 is not None:
        query = query.filter(Batalla.card0_id == card4)
    if card5 is not None:
        query = query.filter(Batalla.card0_id == card5)
    if card6 is not None:
        query = query.filter(Batalla.card0_id == card6)

    # Indicamos si buscamos un solo valor o todos de acuerdo al parámetro
    if not todos:
        regla_db = query.first()
    else:
        regla_db = query.all()

    return regla_db


# DELETE
def eliminar_batalla_db(id_batalla_eliminar):
    """Función que elimina una Batalla de la DB. Solo se permite de a una Batalla"""

    batalla = db.session.get(Batalla, id_batalla_eliminar)

    db.session.delete(batalla)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Ha ocurrido un error al intentar eliminar la batalla:", e)
    finally:
        db.session.close()


#-----------------------------------------------------------------------------------------------------------------------
def consulta_batalla_explicita(query):
    """Función que realiza una consulta a la DB para buscar Batallas de acuerdo a una query definida por el usuario"""

    resultados = db.session.query(Batalla).from_statement(text(query)).all()

    return resultados


def consulta_batallas_grabadas(batallas_jugador):
    """Función para obtener un listado de -seed- de la DB de una sola vez y para todas las batallas de un jugador, y
        así evitar 50 consultas a la DB"""

    # Se obtienen todos los seed de todas las batallas de la lista que recibe la función
    lista_seeds = set()
    for b in batallas_jugador:
        una_batalla = json.loads(b["details"])
        if una_batalla.get("seed") is not None:
            lista_seeds.add(una_batalla["seed"])

    # Se obtienen todos los seed de la DB buscando con la lista anterior (seeds del jugador)
    lista_grabadas = db.session.query(Batalla.seed_ingame.distinct()).where(Batalla.seed_ingame.in_(lista_seeds)).all()

    # Se convierte en lista (porque viene un objeto sqlalchemy sobre el que se puede iterar, pero no es lista)
    control_grabadas = set()
    for item in lista_grabadas:
        control_grabadas.add(item[0])

    return control_grabadas


#----------------------------------------------------------------------------------------------------------------------#
#                                   FUNCIONES PARA ACCESO DE USUARIOS
#----------------------------------------------------------------------------------------------------------------------#
# CREATE
def nuevo_usuario_db(usuario, contras_usuario):
    """Función que se ejecuta luego de superar los controles del formulario para crear un Usuario Nuevo en la DB. Se
    incluye la reactivación de perfiles. Acá se conecta con la DB para verificar si el nombre de usuario ya existe.
    Graba al nuevo usuario solo en los campos nombre_de_usuario y el hash de la contraseña."""

    # Buscamos en la DB si el nombre de usuario elegido no se encuentra ya registrado.
    user_previo = usuarios_datos_db(nombre_usuario=usuario)

    # Si la consulta anterior no está vacía (o sea, lo encontró) y se encuentra activa la función finalizará acá
    if user_previo and user_previo.deleted is False:
        return "existente"

    else:
        # Llamamos a la función para crear el hash de la contraseña
        contras_usuario_hash = hash_contrasenia(contras_usuario)

        # Chequeamos si encuentra el usuario, pero está inactivo
        if user_previo and user_previo.deleted:
            user_previo.contrasenia = contras_usuario_hash  # Se reemplaza lo que hubiera por la nueva contraseña
            user_previo.deleted = False  # Se cambia el estado a no borrada
            texto_rtdo = "reactivado"

        else:  # Cuando el usuario es completamente nuevo
            # Creamos el objeto utilizando las clases de SQLAlchemy
            u1 = Usuario(nombre_usuario=usuario, contrasenia=contras_usuario_hash)
            db.session.add(u1)
            texto_rtdo = "ok"

        try:
            db.session.commit()  # Comit para que grabe en la DB
        except Exception as e:
            db.session.rollback()
            texto_rtdo = "error DB"
            print("Error:", e)
        finally:
            db.session.close()  # Cierre DB
            return texto_rtdo   # Devolución de una cadena para que la función anterior emita un mensaje acorde


# READ
def usuarios_datos_db(id_usuario=None, nombre_usuario=None, todos=None):
    """Función que accede a los datos en la DB correspondientes a la tabla Usuario. Puede consultarse por diversos
    campos y solicitarse uno o varios resultados"""

    # Iniciamos la consulta base
    query = db.session.query(Usuario)

    # Agregamos los filtros según si se proporciona el valor correspondiente
    if id_usuario is not None:
        query = query.filter(Usuario.id_usuario == id_usuario)

    if nombre_usuario is not None:  # El nombre de usuario se busca sin distinguir entre mayúsculas y minúsculas
        query = query.filter(Usuario.nombre_de_usuario.ilike(nombre_usuario))

    # Indicamos si buscamos un solo valor o todos de acuerdo al parámetro
    if not todos:
        usuario_db = query.first()
    else:
        usuario_db = query.all()

    return usuario_db


# UPDATE
def modificar_usuario_db(nombre_usuario, contras_usuario,
                         usuario_game=None, contras_game=None, usuario_nvo=None, contras_nva=None):
    """Función que modifica un usuario existente, permitiendo cambiar nombre_de_usuario, usuario en el juego y
    contraseña del juego. En la creación de un usuario nuevo también se utiliza esta función para grabar los datos
    del juego."""

    # Los StringVar vacíos vienen con "" en lugar de como None, con esto nos aseguramos que se graben correctamente
    if usuario_game == "":
        usuario_game = None
    if contras_game == "":
        contras_game = None
    if usuario_nvo == "":
        usuario_nvo = None

    # Buscamos en la DB el usuario para aplicarle la modificación.
    user_previo = usuarios_datos_db(nombre_usuario=nombre_usuario)

    # Llamamos a esta función para que cifre la contraseña del juego y se guarde de forma segura si hay una nueva
    if contras_game:
        cadena_cifrada = cifrado_contras_game(password=contras_usuario, texto_a_cifrar=contras_game)
        user_previo.contrasenia_juego = cadena_cifrada  # Asignamos la nueva contraseña game

    if usuario_game:
        user_previo.usuario_juego = usuario_game  # Actualizamos el usuario game, creándolo si no existiera

    if usuario_nvo:
        user_previo.nombre_de_usuario = usuario_nvo  # En caso de cambio de nombre de usuario de la cuenta

    if contras_nva:
        # Generamos hash para la contraseña
        nva_contras_hash = hash_contrasenia(contras_nva)

        # Almacenamos ese hash en la DB
        user_previo.contrasenia = nva_contras_hash  # Se reemplaza lo que hubiera por la nueva contraseña

        if user_previo.contrasenia_juego:
            # Recuperamos la contraseña anterior y la ciframos utilizando la nueva contraseña
            contras_volver_cifrar = descifrado_contras_game(password=contras_usuario,
                                                            texto_a_descifrar_db=user_previo.contrasenia_juego)

            nvo_cifrado = cifrado_contras_game(password=contras_nva, texto_a_cifrar=contras_volver_cifrar)

            user_previo.contrasenia_juego = nvo_cifrado

    texto_rtdo = ""
    try:
        db.session.commit()  # Comit para que grabe en la DB
        texto_rtdo = "ok"  # Definimos lo que devuelve el return

    except Exception as e:
        db.session.rollback()
        texto_rtdo = "error DB"  # Caso de error
        print("Error al intentar grabar datos de cuenta game en usuario en DB:", e)

    finally:
        db.session.close()  # Cierre DB
        return texto_rtdo  # Devolución de una cadena para que la función anterior emita un mensaje acorde


# DELETE
def eliminar_usuario_db(usuario_db):
    """Función que elimina una cuenta de usuario. Se realiza mediante la modificación del campo 'deleted'"""

    usuario_db.deleted = True

    texto_rtdo = None
    try:
        db.session.commit()                         # Comit para que grabe en la DB
        texto_rtdo = True                           # Definimos lo que devuelve el return

    except Exception as e:
        texto_rtdo = False                          # Caso de error
        print("Error al intentar grabar datos de cuenta usuario en DB:", e)
        db.session.rollback()

    finally:
        db.session.close()                          # Cierre DB
        return texto_rtdo                           # Devolución del resultado


#-----------------------------------------------------------------------------------------------------------------------
def acceder_usuario_db(usuario, contras_usuario):
    """Función que accede a la DB para corroborar si el usuario que se está queriendo loguear existe y para comprobar
    que la contraseña ingresada sea correcta. Devuelve una cadena con el resultado según lo encontrado."""

    # Buscamos el usuario en la DB invocando a la función
    usuario_db = usuarios_datos_db(nombre_usuario=usuario)

    # Si la busqueda da un resultado vacío, no hay usuario y devolvemos una cadena como mensaje del resultado
    if not usuario_db or (usuario_db and usuario_db.deleted):
        return "El usuario no existe en la Base de Datos"

    else:
        # Llamamos función para comparar si las contraseñas son iguales y si devuelve True
        if check_hash_contrasenia(contras_usuario, usuario_db.contrasenia):

            if usuario_db.usuario_juego and usuario_db.contrasenia_juego:
                return "ok con cuenta game"

            else:
                return "ok"
        else:
            return "La contraseña ingresada no es correcta"


def hash_contrasenia(cadena):
    """Función para crear el hash de una cadena de caracteres UTF8 y devolverlo"""

    # Convertimos la cadena a formato bytes, utilizando UTF8 para que admita más caracteres
    cadena_en_bytes = cadena.encode("utf8")

    sal = bcrypt.gensalt()  # Generamos la sal que necesita en el paso siguiente
    cadena_hash = bcrypt.hashpw(password=cadena_en_bytes, salt=sal)  # Creamos en hash que luego devuelve la función

    return cadena_hash


def check_hash_contrasenia(cadena, hash_db):
    """Función que verifica la coincidencia de las contraseñas de un usuario con el hash guardado en DB usando BCRYPT.
     Devuelve True o False"""

    cadena_bytes = cadena.encode("utf8")

    return bcrypt.checkpw(cadena_bytes, hash_db)


def cifrado_contras_game(password, texto_a_cifrar):
    """Función que cifra un texto (la contraseña del juego), utilizando como clave de descifrado la propia contraseña
    del usuario en nuestro programa"""

    # Convertimos a bytes el password y el texto a cifrar
    pass_bytes = password.encode("utf8")
    texto_a_cifrar_bytes = texto_a_cifrar.encode("utf8")

    # Creamos la sal específica para el proceso
    sal = os.urandom(16)

    # Instanciamos un objeto PBKDF2HMAC que se usará para derivar una clave a partir de una contraseña (la del login)
    objeto_kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=480000)

    # Generamos la clave con la que se realiza el cifrado
    clave = base64.urlsafe_b64encode(objeto_kdf.derive(pass_bytes))

    # Instanciamos un objeto de la librería Fernet basándonos en la clave anterior
    objeto_fernet = Fernet(clave)

    # Ciframos el texto
    texto_cifrado = objeto_fernet.encrypt(texto_a_cifrar_bytes)

    # Convertimos a hexadecimal para guardar
    sal_hexadecimal = sal.hex()
    texto_cifrado_hexadecimal = texto_cifrado.hex()

    # Necesitamos guardar tanto el texto cifrado como la sal para después poder recuperar su contenido
    a_guardar = f"{sal_hexadecimal}|{texto_cifrado_hexadecimal}"

    return a_guardar


def descifrado_contras_game(password, texto_a_descifrar_db):
    """Función que utilizando la contraseña de la cuenta recupera la contraseña del juego para que después sea
        utilizada para realizar el log in"""

    # Obtenemos la sal almacenada que viene como cadena string hexadecimal
    m = texto_a_descifrar_db.find("|")
    sal_db = texto_a_descifrar_db[:m]
    sal_bytes = bytes.fromhex(sal_db)

    # Y también el fragmento de la cadena que corresponde a lo que se quiere desencriptar
    contras_game_encriptada = texto_a_descifrar_db[m+1:]
    contras_game_encriptada_bytes = bytes.fromhex(contras_game_encriptada)

    # Generamos el objeto kdf con los mismos datos que se usaron cuando se encriptó
    objeto_kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal_bytes, iterations=480000)

    # El password lo pasamos a bytes
    password_bytes = password.encode("utf8")

    # Generamos la clave con la que se realiza el cifrado
    clave = base64.urlsafe_b64encode(objeto_kdf.derive(password_bytes))

    # Instanciamos un objeto fernet basándonos en la clave anterior
    objeto_fernet = Fernet(clave)

    # Desciframos la contraseña para poder utilizarla
    contras_game_desencriptada_bytes = objeto_fernet.decrypt(contras_game_encriptada_bytes)

    # Convertimos a UTF8
    contras_game_desencriptada = contras_game_desencriptada_bytes.decode("utf8")

    return contras_game_desencriptada


#----------------------------------------------------------------------------------------------------------------------#
#                                   FUNCIONES PARA CARTAS USUARIO
#----------------------------------------------------------------------------------------------------------------------#
# CREATE
def cargar_carta_a_usuario_db(nombre_usuario, id_carta_db):
    """Función para dar de alta una carta a un usuario o para volver a poner esa carta como activa para el usuario"""

    carta_usuario = cartas_usuario_db(usuario=nombre_usuario, carta=id_carta_db)

    rtdo_carga_carta = ""
    if carta_usuario:

        if carta_usuario.activa:
            return "Carta ya activa para el usuario"

        else:
            carta_usuario.activa = True

    else:
        c1 = CartasUsuario(usuario=nombre_usuario, id_card=id_carta_db, activa=True)
        db.session.add(c1)

    try:  # Grabado en DB bajo un try por si da error
        db.session.commit()
        rtdo_carga_carta = f"La carta ID: {id_carta_db} ha sido activada con éxito."
    except Exception as e:
        db.session.rollback()
        rtdo_carga_carta = "Error al crear la carta usuario en la DB"
        print("Error al crear la carta:", str(e))
    finally:
        db.session.close()
        return rtdo_carga_carta


# READ
def cartas_usuario_db(usuario=None, carta=None, activa=None, todos=None, solo_info_cartas=None, max_lv=None):
    """Función para obtener la información de las cartas de un usuario, sea solo de la tabla CartasUsuario, o sea de la
    tabla Cartas pero aplicando filtros de un usuario en particular."""

    # Iniciamos la consulta base
    if solo_info_cartas:
        query = db.session.query(Carta).join(CartasUsuario, and_(CartasUsuario.id_card == Carta.id_card))
    else:
        query = db.session.query(CartasUsuario)

    # Agregamos los filtros según si se proporciona el valor correspondiente
    if usuario:
        query = query.filter(CartasUsuario.name_user == usuario.lower())

    if carta:
        query = query.filter(CartasUsuario.id_card == carta)

    if activa:
        query = query.filter(CartasUsuario.activa == True)

    # Agregamos ordenamiento en caso de que solo solicitemos las cartas
    if solo_info_cartas:
        query = query.order_by(Carta.id_game, Carta.nivel)

    # Ejecutamos la consulta, buscando todos o la primera coincidencia
    if todos:
        cartas_usuario = query.all()
    else:
        cartas_usuario = query.first()

    if max_lv:
        # A través de este bucle nos quedamos solo con la carta de más alto nivel
        cartas_usu_max_lv = {}
        for carta in cartas_usuario:
            if carta.id_game not in cartas_usu_max_lv:
                cartas_usu_max_lv[carta.id_game] = carta
            elif carta.nivel > cartas_usu_max_lv[carta.id_game].nivel:
                cartas_usu_max_lv[carta.id_game] = carta

        # Convertimos en lista
        lista_cartas_max_lv = list(cartas_usu_max_lv.values())

        return lista_cartas_max_lv

    else:
        return cartas_usuario


# UPDATE
def dar_de_baja_carta_usuario_db(nombre_usuario, id_card):
    """Función que modifica la tabla CartasUsuario en su único valor posible que es -activa- porque el resto de los
    valores son claves foráneas de otras tablas."""

    carta_usuario = cartas_usuario_db(usuario=nombre_usuario, carta=id_card)

    carta_usuario.activa = False

    rtdo_carga_carta = ""
    try:  # Grabado en DB bajo un try por si da error
        db.session.commit()
        rtdo_carga_carta = f"Carta ID:-{id_card}- ha sido desactivada con éxito para el usuario."
    except Exception as e:
        db.session.rollback()
        rtdo_carga_carta = "Error al cargar la carta usuario en la DB"
        print("Error al crear la carta:", str(e))
    finally:
        db.session.close()
        return rtdo_carga_carta


#-----------------------------------------------------------------------------------------------------------------------
def id_cartas_usuario_con_lv_inferior(usuario):
    """Función que trae todas las cartas de usuario, extrae sus ID de la DB y completa con los ID de las cartas de
    niveles inferiores"""

    lista_cartas = cartas_usuario_db(usuario=usuario, activa=True, todos=True, solo_info_cartas=True, max_lv=True)

    id_cartas_usuario = []

    for carta in lista_cartas:
        id_cartas_usuario.append(carta.id_card)
        if carta.nivel > 0:
            for x in range(1, carta.nivel):
                carta_nivel_inferior = carta_datos_db(id_game_card=carta.id_game, nivel_card=x)
                id_cartas_usuario.append(carta_nivel_inferior.id_card)

    return id_cartas_usuario


#-----------------------------------------------------------------------------------------------------------------------
#                                   FUNCIONES PARA EL GRABADO DE BATALLAS
#-----------------------------------------------------------------------------------------------------------------------
def usuarios_carga_batallas(cola_queue):
    """Función que genera un listado de usuario filtrando la DB con algunos criterios y ordenando de acuerdo a sus
        batallas. El listado es el que se usará para cargar el Treeview de Grabar Batallas"""

    # Cantidad de batallas en la DB
    # SELECT count(*) as total
    # FROM Batalla
    total_batallas_db = db.session.query(func.count(Batalla.id_batalla)).scalar()

    if total_batallas_db < 20000:
        fecha_buscar = datetime(year=2024, month=1, day=1)
        cant_bat_jugador = 0
        cant_ult_mes = 0
    else:
        # Consultamos las fechas de batallas de la base de datos y tomamos la más reciente
        # SELECT Batalla.fecha
        # FROM Batalla
        # ORDER BY Batalla.fecha DESC LIMIT 1
        ultima_fecha = db.session.query(Batalla.fecha).order_by(desc(Batalla.fecha)).first()

        # Definimos un rango de 30 días antes de esa fecha. Jugadores que no tengan batallas posteriores se eliminarán
        fecha_buscar = ultima_fecha[0] - timedelta(days=30)

        cant_bat_jugador = 20
        cant_ult_mes = 8

    # Consulta SQL
    # SELECT jugador, AVG(ganada) as Victorias, Count(*) as Batallas
    # FROM Batalla
    # WHERE jugador IN(SELECT jugador
    #                  FROM Batalla
    #                  WHERE fecha > "fecha_buscar"
    #                  GROUP BY jugador
    #                  HAVING COUNT(*) > 8)
    # GROUP BY jugador
    # HAVING COUNT(*) > 20
    # ORDER BY Victorias DESC, Batallas DESC, jugador
    usuarios_db = (db.session.query(Batalla.jugador,
                                    func.round(func.avg(Batalla.ganada) * 100, 2).label("Victorias"),
                                    func.count("*").label("Batallas"))
                   .filter(Batalla.jugador.in_(
                        db.session.query(Batalla.jugador)
                        .filter(Batalla.fecha > fecha_buscar)
                        .group_by(Batalla.jugador)
                        .having(func.count("*") > cant_ult_mes)))
                   .group_by(Batalla.jugador)
                   .having(func.count("*") > cant_bat_jugador)
                   .order_by(func.avg(Batalla.ganada).desc(), func.count("*").desc(), Batalla.jugador)
                   .all())

    cola_queue.put(usuarios_db)


def grabar_batallas(cola_queue, datos_recibidos):
    """Función que procesa todos los datos recibidos de un jugador (las 50 batallas descargadas). Chequea requisitos
        para su grabación (liga, rendición, brawl, existente en DB). Extrae los datos necesarios para llamar al
        constructor de Batalla y grabar en DB. Y genera un reporte string que devuelva esta función."""

    # Para estadísticas
    bat_grabadas = 0
    bat_con_rendicion = 0
    bat_ya_grabadas = 0
    bat_otras_ligas = 0
    bat_rendidas_otras = 0
    bat_brawls = 0
    bat_novice_modern_rank = bat_novice_wild_rank = bat_novice_modern_tournam = bat_novice_wild_tournam = 0
    bat_bronze_modern_rank = bat_bronze_wild_rank = bat_bronze_modern_tournam = bat_bronze_wild_tournam = 0
    bat_silver_modern_rank = bat_silver_wild_rank = bat_silver_modern_tournam = bat_silver_wild_tournam = 0
    bat_gold_modern_rank = bat_gold_wild_rank = bat_gold_modern_tournam = bat_gold_wild_tournam = 0
    bat_practice_challenge = 0

    # Obtenemos desde la DB las batallas que ya han sido grabadas de las de cada descarga web recibida
    control_grabadas = consulta_batallas_grabadas(datos_recibidos["battles"])

    # Bucle para iterar sobre las 50 batallas que se descargan, reversed para que tenga un orden igual al cronológico
    for n, batalla in enumerate(reversed(datos_recibidos["battles"])):

        dicc_detalle_una_batalla = json.loads(batalla["details"])  # Estos 2 datos, si bien se ven como un diccionario,
        dicc_settings = json.loads(batalla["settings"])            # son un STR, por lo que debemos convertirlos

        datos = {}  # Para que en cada iteración se resetee el diccionario que vamos creando

        try:                                 # Este try es porque puede no aparecer esta clave cuando uno se rinde
            datos["rating_level"] = dicc_settings["rating_level"]
            if datos["rating_level"] == 0 or datos["rating_level"] == 1 or datos["rating_level"] == 2:
                batalla_nivel_ok = True
            else:
                batalla_nivel_ok = False     # De momento nos interesa grabar las batallas de rating level
        except IndexError:                   # 0, 1 y 2 que se corresponden con las ligas Novice, Bronze y Silver
            batalla_nivel_ok = False         # también grabaremos el valor para tener la forma de diferenciarlas

        try:
            var = dicc_detalle_una_batalla["type"]
            batalla_peleada = False          # Cuando uno de los jugadores se rinde sin pelear aparece este
        except KeyError:                     # campo. En estos casos no grabaremos nada
            batalla_peleada = True

        try:                                 # Check para BRAWL no nos interesa porque tiene condiciones especiales
            datos["settings"] = batalla["settings"]
            if "BRAWL" in datos["settings"]:
                batalla_no_brawl = False
            else:
                batalla_no_brawl = True
        except KeyError:
            batalla_no_brawl = False

        # Se verifica que la batalla sea del nivel, que esté pelado y no sea brawl, si no, salteará el proceso
        if batalla_nivel_ok and batalla_peleada and batalla_no_brawl:

            # Cuando el seed está en la consulta realizada al comienzo es porque está grabada
            if dicc_detalle_una_batalla["seed"] in control_grabadas:
                batalla_grabable = False
            else:
                batalla_grabable = True

        else:
            batalla_grabable = False

        # Arranca el proceso
        if batalla_grabable:

            # Sobre el diccionario creado se irán cargando todos los valores para enviar al constructor
            datos["seed_ingame"] = dicc_detalle_una_batalla["seed"]
            datos["mana_max"] = batalla["mana_cap"]
            datos["tipo_combate"] = batalla["match_type"]

            if batalla["format"] is None:           # Hay 2 formatos: Modern y Wild (pero los Wild vienen como "None")
                datos["formato"] = "wild"
            else:
                datos["formato"] = batalla["format"]

            # La fecha viene como string, la guardaremos como datetime para poder aplicar filtros
            datos["fecha"] = datetime.strptime(batalla["created_date"], "%Y-%m-%dT%H:%M:%S.%fZ")

            reglas = batalla["ruleset"].split("|")  # Cuando hay más de una regla en campo tiene un formato:
            cant_reglas = len(reglas)               # "Fog of War|Weak Magic|Aim True". Lo dividimos y chequeamos,
            datos["regla1"] = reglas[0]             # excepto para el primero porque al menos un valor hay.

            if cant_reglas > 1:
                datos["regla2"] = reglas[1]

            if cant_reglas > 2:                     # No hay batallas con más de 3 reglas
                datos["regla3"] = reglas[2]

            if "Red" in batalla["inactive"]:        # En "inactive" nos vienen los mazos con los que no se puede jugar.
                datos["mazo_red"] = False           # Para cada partida guardaremos con los que sí se puede como un TRUE
            else:
                datos["mazo_red"] = True            # Red = Fuego/Fire
            if "Blue" in batalla["inactive"]:
                datos["mazo_blue"] = False          # Blue = Agua/Water
            else:
                datos["mazo_blue"] = True
            if "Green" in batalla["inactive"]:
                datos["mazo_green"] = False         # Green = Tierra/Earth
            else:
                datos["mazo_green"] = True
            if "White" in batalla["inactive"]:
                datos["mazo_white"] = False         # White = Vida/Life
            else:
                datos["mazo_white"] = True
            if "Black" in batalla["inactive"]:
                datos["mazo_black"] = False         # Black = Muerte/Death
            else:
                datos["mazo_black"] = True
            if "Gold" in batalla["inactive"]:
                datos["mazo_gold"] = False          # Gold = Dragon
            else:
                datos["mazo_gold"] = True

            # Bucle dentro de la batalla porque hay 2 equipos y se graban los dos por separado (victoria y derrota)
            for i in range(2):

                # Reseteamos los valores. Necesario para el 2do equipo
                for x in range(7):
                    datos[f"card{x}_id"] = None
                    datos[f"card{x}_lv"] = None

                team = i + 1                        # En la descarga son team1 y team2 (en bucle son 0 y 1)
                datos["jugador"] = dicc_detalle_una_batalla[f"team{team}"]["player"]

                if dicc_detalle_una_batalla[f"team{team}"]["player"] == dicc_detalle_una_batalla["winner"]:
                    datos["ganada"] = True          # Para determinar si la ganó o no... los empates son no ganadas
                else:
                    datos["ganada"] = False

                datos["card0_id"] = dicc_detalle_una_batalla[f"team{team}"]["summoner"]["card_detail_id"]
                datos["card0_lv"] = dicc_detalle_una_batalla[f"team{team}"]["summoner"]["level"]

                # Las cartas de monsters están dentro de una lista que no siempre tiene 7 elementos
                # En las cartas la numeración la guardamos del 0 hasta el 5 igual que como viene en el diccionario
                for m, y in enumerate(dicc_detalle_una_batalla[f"team{team}"]["monsters"], start=1):
                    datos[f"card{m}_id"] = y["card_detail_id"]
                    datos[f"card{m}_lv"] = y["level"]

                batalla_a_grabar = Batalla(datos)   # Llamado al constructor para crear el objeto Batalla
                db.session.add(batalla_a_grabar)    # Se agrega a la pila

            # Estadísticas. Contando tipos de batallas grabadas.
            if datos["rating_level"] == 0 and datos["formato"] == "modern" and datos["tipo_combate"] == "Ranked":
                bat_novice_modern_rank += 1
            elif datos["rating_level"] == 0 and datos["formato"] == "wild" and datos["tipo_combate"] == "Ranked":
                bat_novice_wild_rank += 1
            elif datos["rating_level"] == 0 and datos["formato"] == "modern" and datos["tipo_combate"] == "Tournament":
                bat_novice_modern_tournam += 1
            elif datos["rating_level"] == 0 and datos["formato"] == "wild" and datos["tipo_combate"] == "Tournament":
                bat_novice_wild_tournam += 1
            elif datos["rating_level"] == 1 and datos["formato"] == "modern" and datos["tipo_combate"] == "Ranked":
                bat_bronze_modern_rank += 1
            elif datos["rating_level"] == 1 and datos["formato"] == "wild" and datos["tipo_combate"] == "Ranked":
                bat_bronze_wild_rank += 1
            elif datos["rating_level"] == 1 and datos["formato"] == "modern" and datos["tipo_combate"] == "Tournament":
                bat_bronze_modern_tournam += 1
            elif datos["rating_level"] == 1 and datos["formato"] == "wild" and datos["tipo_combate"] == "Tournament":
                bat_bronze_wild_tournam += 1
            elif datos["rating_level"] == 2 and datos["formato"] == "modern" and datos["tipo_combate"] == "Ranked":
                bat_silver_modern_rank += 1
            elif datos["rating_level"] == 2 and datos["formato"] == "wild" and datos["tipo_combate"] == "Ranked":
                bat_silver_wild_rank += 1
            elif datos["rating_level"] == 2 and datos["formato"] == "modern" and datos["tipo_combate"] == "Tournament":
                bat_silver_modern_tournam += 1
            elif datos["rating_level"] == 2 and datos["formato"] == "wild" and datos["tipo_combate"] == "Tournament":
                bat_silver_wild_tournam += 1
            elif datos["rating_level"] == 3 and datos["formato"] == "modern" and datos["tipo_combate"] == "Ranked":
                bat_gold_modern_rank += 1
            elif datos["rating_level"] == 3 and datos["formato"] == "wild" and datos["tipo_combate"] == "Ranked":
                bat_gold_wild_rank += 1
            elif datos["rating_level"] == 3 and datos["formato"] == "modern" and datos["tipo_combate"] == "Tournament":
                bat_gold_modern_tournam += 1
            elif datos["rating_level"] == 3 and datos["formato"] == "wild" and datos["tipo_combate"] == "Tournament":
                bat_gold_wild_tournam += 1
            elif datos["formato"] == "Practice" or "Challenge":
                bat_practice_challenge += 1
            else:
                # SELECT Batalla.id_batalla
                # FROM Batalla
                # ORDER BY Batalla.id_batalla
                # LIMIT 1
                ultima_batalla = db.session.query(Batalla).order_by(desc(Batalla.id_batalla)).first()
                print("Batalla grabada pero no clasificada:")
                print(ultima_batalla)

            bat_grabadas += 1

        # Sección que acumula cantidades no grabadas del jugador
        elif batalla_no_brawl is False:
            bat_brawls += 1
        elif batalla_nivel_ok and batalla_peleada is False:
            bat_con_rendicion += 1
        elif batalla_nivel_ok is False and batalla_peleada:
            bat_otras_ligas += 1
        elif batalla_nivel_ok is False and batalla_peleada is False:
            bat_rendidas_otras += 1
        elif batalla_grabable is False:
            bat_ya_grabadas += 1
        else:
            pass
            #print(f"No se ha grabado la batalla {n}. Razón desconocida")

    # Grabación en DB. Por jugador, todas las batallas
    db.session.commit()
    db.session.close()

    # Generación del mensaje sobre la base de las estadísticas.
    rtdo_grabacion = ("\n\nProceso de grabado de batallas de {} finalizado."
                      "\nBatallas grabadas: {}").format(datos_recibidos["player"].upper(), bat_grabadas)
    if bat_novice_modern_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Novice Modern Ranked: {bat_novice_modern_rank}"
    if bat_novice_wild_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Novice Wild Ranked: {bat_novice_wild_rank}"
    if bat_novice_modern_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Novice Modern Torneos: {bat_novice_modern_tournam}"
    if bat_novice_wild_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Novice Wild Torneos: {bat_novice_wild_tournam}"
    if bat_bronze_modern_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Bronze Modern Ranked: {bat_bronze_modern_rank}"
    if bat_bronze_wild_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Bronze Wild Ranked: {bat_bronze_wild_rank}"
    if bat_bronze_modern_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Bronze Modern Torneos: {bat_bronze_modern_tournam}"
    if bat_bronze_wild_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Bronze Wild Torneos: {bat_bronze_wild_tournam}"
    if bat_silver_modern_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Silver Modern Ranked: {bat_silver_modern_rank}"
    if bat_silver_wild_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Silver Wild Ranked: {bat_silver_wild_rank}"
    if bat_silver_modern_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Silver Modern Torneos: {bat_silver_modern_tournam}"
    if bat_silver_wild_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Silver Wild Torneos: {bat_silver_wild_tournam}"
    if bat_gold_modern_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Gold Modern Ranked: {bat_gold_modern_rank}"
    if bat_gold_wild_rank > 0:
        rtdo_grabacion += f"\n >>> Liga Gold Wild Ranked: {bat_gold_wild_rank}"
    if bat_gold_modern_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Gold Modern Torneos: {bat_gold_modern_tournam}"
    if bat_gold_wild_tournam > 0:
        rtdo_grabacion += f"\n >>> Liga Gold Wild Torneos: {bat_gold_wild_tournam}"
    if bat_practice_challenge > 0:
        rtdo_grabacion += f"\n >>> Prácticas o Challenges: {bat_practice_challenge}"

    if bat_con_rendicion > 0:
        rtdo_grabacion += "\nBatallas no grabadas porque hubo rendición: {}".format(bat_con_rendicion)
    if bat_otras_ligas > 0:
        rtdo_grabacion += ("\nBatallas no grabadas porque se jugaron en algún tipo de liga superior a las "
                           "registrables: {}").format(bat_otras_ligas)
    if bat_rendidas_otras > 0:
        rtdo_grabacion += "\nBatallas no grabadas por la liga y por rendición: {}".format(bat_rendidas_otras)
    if bat_brawls > 0:
        rtdo_grabacion += "\nBatallas no grabadas por ser Brawls: {}".format(bat_brawls)
    if bat_ya_grabadas > 0:
        rtdo_grabacion += "\nBatallas no grabadas por ya estar en la DB: {}".format(bat_ya_grabadas)

    cola_queue.put(rtdo_grabacion)


def carga_reglas_desde_batallas(cola_queue):
    """Función que en la DB recorre todas las reglas de la Tabla Batalla (3 campos) y verifica que hayan sido cargadas
    en la Tabla Regla. Cuando alguna no esté cargada, se disparará la creación de una nueva Regla"""

    cola_queue.put("\n\nVerificando reglas en la DB...")

    # SELECT DISTINCT batalla.regla1
    # FROM batalla
    # WHERE batalla.regla1 NOT IN (SELECT regla.nombre
    #                              FROM regla)
    for i in range(1, 4):
        regla = f"regla{i}"
        reglas_nvas_batallas = (db.session.query(getattr(Batalla, regla).distinct())
                                .filter(~getattr(Batalla, regla).in_(db.session.query(Regla.nombre)))
                                .all())
        if reglas_nvas_batallas:
            for regla_nva in reglas_nvas_batallas:
                nueva_regla_db(nombre_regla=regla_nva[0])
                cola_queue.put(f"\nCargada en DB regla {regla_nva[0]}")

    cola_queue.put("\nTodas las reglas están grabadas.")


def verificar_cartas_nuevas_desde_batallas(cola_queue):
    """Función que en la DB recorre todas las cartas de la Tabla Batalla (7 campos) y verifica que hayan sido cargadas
    en la Tabla Carta. Cuando alguna no esté cargada, se disparará la creación de una nueva Carta"""

    cola_queue.put("\n\nVerificando cartas nuevas en la DB...")

    nuevas = []  # Acumulador de cartas nuevas

    # SELECT DISTINCT (batalla.card{i}_id, batalla.card_lv)
    # FROM batalla
    # WHERE (batalla.card{i}_id, batalla.card_lv) NOT IN (SELECT carta.id_game, carta.nivel
    #                                                     FROM carta);
    for i in range(7):
        card_id = f"card{i}_id"
        card_lv = f"card{i}_lv"
        cartas_nvas_batallas = (db.session.query(getattr(Batalla, card_id), getattr(Batalla, card_lv)).distinct()
                                .filter(
                                    ~tuple_(
                                        getattr(Batalla, card_id),
                                        getattr(Batalla, card_lv)
                                    ).in_(select(Carta.id_game, Carta.nivel)))
                                .all())

        for carta in cartas_nvas_batallas:
            if carta not in nuevas:
                nuevas.append(carta)  # Vamos agregando cada carta nueva a una lista

    if len(nuevas) > 0:  # Mensaje en caso de encontrar cartas nuevas
        cola_queue.put(f"\nSe han encontrado {len(nuevas)} cartas nuevas en las batallas descargadas no grabadas en la "
                       f"DB. Se recomienda realizar una carga masiva o manual.")

    else:  # Mensaje en caso de no encontrar nada nuevo
        cola_queue.put("\nRevisión cartas finalizada sin cartas nuevas.")


#-----------------------------------------------------------------------------------------------------------------------
#                                   FUNCIONES PARA SUGERENCIA DE BATALLAS
#-----------------------------------------------------------------------------------------------------------------------
def batallas_sugerir_batallas_db(mana, fire, water, earth, life, death, dragon, combate, formato, liga, regla1, regla2,
                                 regla3, veces_buscadas):

    # Filtro a aplicar en la búsqueda en la DB, estos de acá abajo y luego las reglas se agregan con append
    filtros_busqueda_db = [
        and_(Batalla.mana_max <= mana,
             Batalla.mana_max >= mana - veces_buscadas),  # Por cada vez que se vuelva a buscar reducimos en uno el maná
        Batalla.mazo_red == fire,
        Batalla.mazo_blue == water,
        Batalla.mazo_green == earth,
        Batalla.mazo_white == life,
        Batalla.mazo_black == death,
        Batalla.mazo_gold == dragon,
        Batalla.tipo_combate == combate,
        Batalla.formato == formato,
        Batalla.rating_level <= liga  # Cualquier liga inferior también será incluida
    ]

    if regla3 is None:
        if regla2 is None:  # En los filtros de reglas usamos IN para que busque todos los casos que le pasamos
            filtros_busqueda_db.append(Batalla.regla1.in_([regla1]))
            filtros_busqueda_db.append(Batalla.regla2 == None)
            filtros_busqueda_db.append(Batalla.regla3 == None)
        else:
            filtros_busqueda_db.append(Batalla.regla1.in_([regla1, regla2]))
            filtros_busqueda_db.append(Batalla.regla2.in_([regla1, regla2]))
            filtros_busqueda_db.append(Batalla.regla3 == None)
    else:
        filtros_busqueda_db.append(Batalla.regla1.in_([regla1, regla2, regla3]))
        filtros_busqueda_db.append(Batalla.regla2.in_([regla1, regla2, regla3]))
        filtros_busqueda_db.append(Batalla.regla3.in_([regla1, regla2, regla3]))

    # Consulta en SQL
    # SELECT card0_id, card0_lv, card1_id, card1_lv, card2_id, card2_lv, card3_id, card3_lv, card4_id, card4_lv,
    #        card5_id, card5_lv, card6_id, card6_lv, AVG(ganada) as ratio, COUNT(*) as cantidad
    # FROM batalla
    # WHERE [filtros_busqueda_db]
    # GROUP BY card0_id, card0_lv, card1_id, card1_lv, card2_id, card2_lv, card3_id, card3_lv, card4_id, card4_lv,
    #          card5_id, card5_lv, card6_id, card6_lv
    # ORDER BY ratio, cantidad, card0_lv

    # Query de SqlAlchemy para buscar en la DB
    lista_de_batallas = (db.session.query(Batalla.card0_id, Batalla.card0_lv,
                                          Batalla.card1_id, Batalla.card1_lv,
                                          Batalla.card2_id, Batalla.card2_lv,
                                          Batalla.card3_id, Batalla.card3_lv,
                                          Batalla.card4_id, Batalla.card4_lv,
                                          Batalla.card5_id, Batalla.card5_lv,
                                          Batalla.card6_id, Batalla.card6_lv,
                                          func.avg(Batalla.ganada).label("ratio"),
                                          func.count(Batalla.ganada).label("cantidad"))
                         .filter(and_(*filtros_busqueda_db))
                         .group_by(Batalla.card0_id, Batalla.card0_lv,
                                   Batalla.card1_id, Batalla.card1_lv,
                                   Batalla.card2_id, Batalla.card2_lv,
                                   Batalla.card3_id, Batalla.card3_lv,
                                   Batalla.card4_id, Batalla.card4_lv,
                                   Batalla.card5_id, Batalla.card5_lv,
                                   Batalla.card6_id, Batalla.card6_lv)
                         .order_by(desc("ratio"), desc("cantidad"), desc(Batalla.fecha))
                         .all())

    return lista_de_batallas


def contador_jugadas_posibles_usuario(lista_batallas, usuario):
    """Función que debe acumular la cantidad de batallas que un usuario puede hacer con sus cartas, analizando un
    listado de batallas obtenido de la tabla Batallas cuando se busca desde Sugerir Batallas."""

    cant_bat_usu = 0  # Contador para la cantidad de jugadas del usuario
    bat_ganadas = 0  # Contador de batallas ganadas para el usuario

    for batalla in lista_batallas:
        # Obtenemos de cada batalla el conjunto de los siete pares de id_game y nivel
        lista_cartas_id_y_nivel = lista_cartas_para_buscar(batalla=batalla)

        # Buscamos en la DB las cartas con los datos necesarios para luego colocarlos en frame ya creado
        cartas_db = cartas_listado_db(listado_cartas_id_game_y_nivel=lista_cartas_id_y_nivel, usuario=usuario)

        # Ordenamos el listado porque la consulta devuelve sin orden y quitando los None
        jugada_db = ordenar_cartas_jugada(listado_en_orden=lista_cartas_id_y_nivel, cartas=cartas_db)

        # Llamamos a función que revisa si las cartas de la jugada las tiene el usuario (devuelve True o False)
        jugada_usuario = check_jugada_para_jugador(jugada=jugada_db)

        if jugada_usuario:
            cant_bat_usu += 1
            if batalla.ratio > 0:
                bat_ganadas += 1

    return cant_bat_usu, bat_ganadas


def esquema_mostrar_batallas(frame_a_cargar):
    """Función que genera la interfaz de cómo quedarían 5 jugadas distribuidas en pantallas, con su nombre de jugada y
    seis espacios para las cartas. Se usan al iniciar la ventana sugerir batallas."""

    for i in range(1, 6):  # Se crean 5 frame, o sea para 5 jugadas
        frame_cada_jugada = ttk.Frame(frame_a_cargar)
        frame_cada_jugada.pack(side="top", pady=1)

        etiqueta_cada_jugada = ttk.Label(frame_cada_jugada, text=f"Jugada {i}", width=8)  # En su interior un label
        etiqueta_cada_jugada.pack(side="left")

        for j in range(7):  # Se agregan 7 cartas al igual que cualquier jugada, desde card0 a card6
            card = ttk.Label(frame_cada_jugada, text=f"Carta {j}", width=9, relief="solid", anchor="center")
            card.pack(side="left", padx=1, ipadx=4, ipady=38)


def lista_cartas_para_buscar(batalla):
    """Función para obtener de una jugada obtenida desde la DB de la tabla Batalla, una lista con todas las tuplas de
    pares de id_game y nivel de las cartas jugadas"""

    conj_id_game_nivel_jugada = []  # Listado de pares de id_game y nivel como vienen en cada batalla
    # Buscamos ID (de la DB) de las cartas con el fin de saber si son todas cartas que el usuario tiene
    for j in range(7):
        carta_atributo_check = f"card{j}_id"  # Las cartas están grabadas desde card0 hasta card6
        nivel_atributo_check = f"card{j}_lv"
        carta_check = getattr(batalla, carta_atributo_check)  # Desde batalla obtenemos id_game y nivel
        nivel_check = getattr(batalla, nivel_atributo_check)  # en forma dinámica

        # Buscamos ID (de la DB) de las cartas
        conj_id_game_nivel_jugada.append((carta_check, nivel_check))

    return conj_id_game_nivel_jugada


def cartas_listado_db(listado_cartas_id_game_y_nivel, usuario):
    """Función que busca en la DB los datos de las cartas de una jugada desde sus pares de valores id_game y nivel.
    Requiere un listado de tuplas de esos valores. Es una consulta específica que se necesita cuando se parte de jugadas
    obtenidas de la tabla Batalla. También une la tabla CartasUsuario para saber si el usuario la tiene activa"""

    # SELECT Cartas.nombre, Cartas.imagen, CartasUsuario.activa
    # FROM Carta LEFT JOIN CartasUsuario ON CartasUsuario.id_card = Carta.id_card AND CartasUsuario.name_user = usuario
    # WHERE *[(Carta.id_game == id_game) & (Carta.nivel == nivel)
    #          for id_game, nivel in listado_cartas_id_game_y_nivel]))

    lista_de_cartas = (db.session.query(Carta, CartasUsuario.activa)  # El resultado es varias tuplas, con los datos
                       .join(CartasUsuario,                           # completos de la carta y un True, False o None
                             and_(                                    # por cada una
                                 CartasUsuario.id_card == Carta.id_card,
                                 CartasUsuario.name_user == usuario  # Deben ser las cartas del usuario conectado
                             ),
                             isouter=True)  # LEFT JOIN
                       .filter(
                            or_(
                                *[and_(Carta.id_game == id_game, Carta.nivel == nivel)  # Se genera un listado
                                  for id_game, nivel in listado_cartas_id_game_y_nivel]),
                            )
                       .all())

    return lista_de_cartas


def ordenar_cartas_jugada(listado_en_orden, cartas):
    """Función que ordena un listado de cartas que se recibe en -cartas-, con base al orden que viene en
    -listado_en_orden-. Este último es un listado de tuplas (455, 1), el desordenado es (objeto_db, Boolean)"""

    cartas_en_orden = []
    for elemento in listado_en_orden:
        if elemento == (None, None):  # Los None son espacios en los que no se jugaron cartas
            cartas_en_orden.append((None, None))
        else:
            for x in cartas:  # x[0] es un objeto de sqlalchemy con formato de la tabla Carta
                if x[0].id_game == elemento[0] and x[0].nivel == elemento[1]:  # Elemento[0] es el id_game, [1] es nivel
                    cartas_en_orden.append(x)

    return cartas_en_orden


def check_jugada_para_jugador(jugada):
    """Función que revisa dentro de la misma consulta hecha a la DB para traer las cartas de una jugada, si todas están
    en posesión del jugador."""

    jugada_usuario = True  # Básicamente, será True, si todas las cartas son True
    for x in jugada:
        if x[0] and not x[1]:  # Pero hay que excluir las cartas que son (None, None), si no daría un Falso incorrecto
            jugada_usuario = False

    return jugada_usuario
