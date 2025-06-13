import sugerir_batallas
import funciones
import navegador
import db
import threading
import queue
import io
import textwrap
from tkinter import Tk, ttk, Label, LabelFrame, Frame, Text, PhotoImage, StringVar, IntVar, Spinbox, Canvas
from playwright.sync_api import Error as PlaywrightError
from PIL import Image, PngImagePlugin
from time import sleep
from datetime import datetime


class PantallaInicial:
    """Clase asociada a la pantalla que se inicia cuando se ejecuta el programa. Contiene los botones que activa las
        principales funciones y algunas etiquetas de mensajes"""

    def __init__(self, root_inicio):
        """Constructor de la clase PantallaInicial. Incluye las configuraciones para cada uno de los elementos que se
            visualizan"""

        # Ventana completa
        self.ventana_inicial = root_inicio
        self.ventana_inicial.title("Menú del Sistema de Gestión para Sugerir Batallas en Splinterlands")
        self.ventana_inicial.wm_iconbitmap("imagenes/img_icon_splinterlands.ico")
        self.ventana_inicial.geometry("1000x600+400+240")  # Tamaño inicial
        self.ventana_inicial.resizable(0, 0)  # Tamaño máximo

        # Formato de filas y columnas para la ventana principal
        self.ventana_inicial.grid_rowconfigure(0, weight=5)
        self.ventana_inicial.grid_rowconfigure(1, weight=0)
        self.ventana_inicial.grid_rowconfigure(2, weight=0)
        self.ventana_inicial.grid_rowconfigure(3, weight=0)
        self.ventana_inicial.grid_columnconfigure(0, weight=0)
        self.ventana_inicial.grid_columnconfigure(1, weight=0)
        self.ventana_inicial.grid_columnconfigure(2, weight=1)

        # ESTILOS
        self.dic_style = {}
        self.carga_estilos()  # Función con la definición de cada estilo

        # ETIQUETA PRINCIPAL
        self.etiq_mensajes_principal = ttk.Label(self.ventana_inicial, anchor="center")
        self.etiq_mensajes_principal.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 2), sticky="NSEW")

        # FRAME en el que van los Botones de CARTAS
        self.fr_botones_cartas = LabelFrame(self.ventana_inicial, text="Cartas")
        self.fr_botones_cartas.grid(row=1, column=0, padx=10, pady=5, ipadx=2, ipady=5, sticky="NSEW")

        # BOTONES CARTAS
        self.botones_cartas()  # Función que define cada botón y lo coloca en pantalla

        # FRAME en el que van los Botones de REGLAS
        self.fr_botones_reglas = ttk.LabelFrame(self.ventana_inicial, text="Reglas")
        self.fr_botones_reglas.grid(row=2, column=0, padx=10, pady=5, ipadx=2, ipady=5, sticky="NSEW")

        # BOTONES REGLAS
        self.botones_reglas()  # Función que define cada botón y lo coloca en pantalla

        # FRAME en el que van los Botones de BATALLAS
        self.fr_botones_batallas = ttk.LabelFrame(self.ventana_inicial, text="Batallas")
        self.fr_botones_batallas.grid(row=3, column=0, padx=10, pady=(5, 10), ipadx=2, ipady=5, sticky="NSEW")

        # BOTONES BATALLAS
        self.botones_batallas()  # Función que define cada botón y lo coloca en pantalla

        # FRAME para los botones de ACCESO USUARIO
        self.fr_acceso_usuario = ttk.LabelFrame(self.ventana_inicial, text="Acceso Usuarios")
        self.fr_acceso_usuario.grid(row=1, column=1, padx=(2, 10), pady=5, ipadx=2, ipady=5, sticky="NSEW")

        # ETIQUETA STATUS
        self.etiq_usuario_logueado = ttk.Label(self.fr_acceso_usuario, text="No se ha logueado", style="red.TLabel",
                                               anchor="center")
        self.etiq_usuario_logueado.grid(row=0, column=0, padx=10, pady=5, sticky="NSEW")

        # BOTONES PARA ACCESO USUARIOS
        self.dic_acc_usu = {}
        self.botones_acceso_usu()  # Función que define cada botón y lo coloca en pantalla

        # Frame para las FUNCIONES DEL USUARIO (una vez logueado)
        self.fr_funciones_usuario = LabelFrame(self.ventana_inicial, text="Funciones de Usuario")
        self.fr_funciones_usuario.grid(row=2, column=1, rowspan=2, padx=(2, 10), pady=(5, 10), ipadx=2, ipady=5,
                                       sticky="NSEW")

        # BOTONES PARA ACCESO A FUNCIONES DE USUARIOS
        self.dic_fun_usu = {}
        self.botones_funciones_usu()

        # Espacio o frame para acciones
        self.fr_acciones = Frame(self.ventana_inicial)  # Creado para que la función lo pueda borrar
        self.etiqueta_acciones = ttk.Label(self.fr_acciones)

        # Imágen de fondo
        imagen_fondo = PhotoImage(file="imagenes/fondo.png")
        self.label_imagen_fondo = Label(self.ventana_inicial, image=imagen_fondo)
        self.label_imagen_fondo.imagen = imagen_fondo
        self.label_imagen_fondo.grid(row=0, column=0, rowspan=5, columnspan=3, sticky="NSEW")
        self.label_imagen_fondo.lower()

        # Declaración de variables y widgets para el FRAME Acciones
        self.d_stv = {}
        self.d_ent = {}
        self.d_btn = {}
        self.d_lbl = {}
        self.d_frm = {}
        self.imagen = None
        self.treeview = ttk.Treeview(self.fr_acciones)
        self.scrollbar = ttk.Scrollbar(self.fr_acciones)
        self.cuadro_texto = Text(self.fr_acciones)
        self.progress_bar = ttk.Progressbar(self.fr_acciones)
        self.canvas = Canvas(self.fr_acciones)
        self.cadena_seg = bytearray()

        # Variables para abrir un navegador web
        self.navegador = navegador.Navegador()

        # Variable para recibir resultados procesos en hilos secundarios
        self.queue = queue.Queue()
        self.control_cola = True
        self.continuar_hilo = threading.Event()
        self.detener_hilo = threading.Event()

        # Vinculamos el cierre de la ventana con el cierre de un navegador, si es que está en ejecución
        self.ventana_inicial.protocol("wm_delete_window", self.al_cerrar)

        # Llamamos a la función que sobre el frame_acciones crea widgets
        self.elementos_como_inicio()  # Función en la que primero borra el frame y luego crea la pantalla básica

        # Mensaje de bienvenida (luego de elemento_como_inicio porque en ella se borra el mensaje)
        self.texto_etiqueta_principal(texto="Bienvenido")

    def al_cerrar(self):
        """Método para que al cerrarse el programa desde la 'x' se detengan el navegador y los hilos secundarios"""

        self.navegador.cerrar()
        self.detener_revision_queue()

# ----------------------------------------------------------------------------------------------------------------------
#                                   FUNCIONES DE INICIO
# ----------------------------------------------------------------------------------------------------------------------
    def carga_estilos(self):
        """Definición de los estilos en diccionario y carga en variable -dic_style-"""

        estilos = {
            "red.TLabel": {"foreground": "red", "anchor": "center", "justify": "center"},
            "blue.TLabel": {"foreground": "blue", "anchor": "center", "justify": "center"},
            "green.TLabel": {"foreground": "#47CF22", "anchor": "center", "justify": "center"},
            "yellow.TLabel": {"foreground": "#DECD25", "anchor": "center", "justify": "center"},
            "tit_bold.TLabel": {"font": ("Segoe UI", 10, "bold")},
            "cursiva.TLabel": {"font": ("Segoe UI", 8, "italic")},
            "cursiva_red.TLabel": {"font": ("Segoe UI", 8, "italic"), "foreground": "red", "anchor": "center",
                                   "justify": "center"},
            "cursiva_green.TLabel": {"font": ("Segoe UI", 8, "italic"), "foreground": "green", "anchor": "center",
                                     "justify": "center"},
            "cursiva_yellow.TLabel": {"font": ("Segoe UI", 8, "italic"), "foreground": "#B2A44E", "anchor": "center",
                                      "justify": "center"},
            "alto_fila_con_img.Treeview": {"rowheight": 55},
            "alto_fila_sin_img.Treeview": {"rowheight": 30},
            "alto_fila_lista.Treeview": {"rowheight": 22},
            "orange.TButton": {"background": "#EE9025"}
        }

        for nombre, definicion in estilos.items():
            self.dic_style[nombre] = ttk.Style()
            self.dic_style[nombre].configure(nombre, **definicion)  # Los ** pasan como parámetros los valores

    def botones_cartas(self):
        """Función que coloca y configura los botones para acceder a las acciones sobre las CARTAS. Se ejecuta en el
            inicio solamente. Estos botones quedarán siempre fijos durante la ejecución del programa."""

        ttk.Button(self.fr_botones_cartas, text="Crear Nueva Carta", name="nueva_carta",
                   command=self.crear_nueva_carta).grid(row=0, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_cartas, text="Modificar Carta", name="modificar_carta",
                   command=self.modificar_carta).grid(row=1, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_cartas, text="Eliminar Carta", name="eliminar_carta",
                   command=self.eliminar_carta).grid(row=2, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_cartas, text="Consultar Cartas", name="consultar_cartas",
                   command=self.consultar_carta).grid(row=3, column=0, padx=10, pady=5, sticky="NSEW")

        # Para EXPANDIR los botones al Frame
        self.fr_botones_cartas.grid_rowconfigure(0, weight=1)
        self.fr_botones_cartas.grid_rowconfigure(1, weight=1)
        self.fr_botones_cartas.grid_rowconfigure(2, weight=1)
        self.fr_botones_cartas.grid_rowconfigure(3, weight=1)
        self.fr_botones_cartas.grid_columnconfigure(0, weight=1)

    def botones_reglas(self):
        """Función que coloca y configura los botones para acceder a las acciones sobre las REGLAS. Se ejecuta en el
                inicio solamente. Estos botones quedarán siempre fijos durante la ejecución del programa."""

        ttk.Button(self.fr_botones_reglas, text="Crear Nueva Regla", name="nueva_regla",
                   command=self.crear_nueva_regla).grid(row=0, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_reglas, text="Modificar Regla", name="modificar_regla",
                   command=self.modificar_regla).grid(row=1, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_reglas, text="Eliminar Regla", name="eliminar_regla",
                   command=self.eliminar_regla).grid(row=2, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_reglas, text="Consultar Reglas", name="consultar_reglas",
                   command=self.consultar_reglas).grid(row=3, column=0, padx=10, pady=5, sticky="NSEW")

        # Para EXPANDIR los botones al Frame
        self.fr_botones_reglas.grid_rowconfigure(0, weight=1)
        self.fr_botones_reglas.grid_rowconfigure(1, weight=1)
        self.fr_botones_reglas.grid_rowconfigure(2, weight=1)
        self.fr_botones_reglas.grid_rowconfigure(3, weight=1)
        self.fr_botones_reglas.grid_columnconfigure(0, weight=1)

    def botones_batallas(self):
        """Función que coloca y configura los botones para acceder a las acciones sobre las BATALLAS. Se ejecuta en el
                inicio solamente. Estos botones quedarán siempre fijos durante la ejecución del programa."""

        ttk.Button(self.fr_botones_batallas, text="Consultar Batallas por fecha", name="batallas_fecha",
                   command=self.batallas_por_fecha).grid(row=0, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_batallas, text="Consultar Batallas SQL", name="batallas_id",
                   command=self.consultar_batallas_sql).grid(row=1, column=0, padx=10, pady=5, sticky="NSEW")
        ttk.Button(self.fr_botones_batallas, text="Eliminar Batalla", name="eliminar_batalla",
                   command=self.eliminar_batalla).grid(row=2, column=0, padx=10, pady=5, sticky="NSEW")

        # Para EXPANDIR los botones al Frame
        self.fr_botones_batallas.grid_rowconfigure(0, weight=1)
        self.fr_botones_batallas.grid_rowconfigure(1, weight=1)
        self.fr_botones_batallas.grid_rowconfigure(2, weight=1)
        self.fr_botones_batallas.grid_rowconfigure(3, weight=1)
        self.fr_botones_batallas.grid_columnconfigure(0, weight=1)

    def botones_acceso_usu(self):
        """Función que coloca y configura los botones para acceder a las acciones sobre ACCESO USUARIOS. Se ejecuta en
            el inicio solamente. Estos botones se activarán o no durante la ejecución del programa."""

        # Creación de los 3 widgets dentro del diccionario definido
        for x in range(3):
            boton = f"boton{x}"
            self.dic_acc_usu[boton] = ttk.Button(self.fr_acceso_usuario)

        # Configuración de cada botón
        self.dic_acc_usu["boton0"].config(text="Acceder con Usuario y Contraseña", command=self.acceder_usuario)
        self.dic_acc_usu["boton0"].grid(row=1, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_acc_usu["boton1"].config(text="Desloguearse", state="disabled", command=self.desloguear)
        self.dic_acc_usu["boton1"].grid(row=2, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_acc_usu["boton2"].config(text="Crear Nuevo Usuario", command=self.nuevo_usuario)
        self.dic_acc_usu["boton2"].grid(row=3, column=0, padx=10, pady=5, sticky="NSEW")

        # Para EXPANDIR los botones de ACCESO
        self.fr_acceso_usuario.grid_rowconfigure(0, weight=1)
        self.fr_acceso_usuario.grid_rowconfigure(1, weight=1)
        self.fr_acceso_usuario.grid_rowconfigure(2, weight=1)
        self.fr_acceso_usuario.grid_rowconfigure(3, weight=1)
        self.fr_acceso_usuario.grid_columnconfigure(0, weight=1)

    def botones_funciones_usu(self):
        """Función que coloca y configura los botones para acceder a las acciones sobre las FUNCIONES de USUARIOS. Se
            ejecuta en el inicio solamente. Estos botones se activarán o no durante la ejecución del programa."""

        # Creación de los 3 widgets dentro del diccionario definido
        for x in range(8):
            boton = f"boton{x}"
            self.dic_fun_usu[boton] = ttk.Button(self.fr_funciones_usuario)

        # Configuración de cada botón
        self.dic_fun_usu["boton0"].config(text="Modificar Usuario", state="disabled",
                                          command=self.modificar_usuario)
        self.dic_fun_usu["boton0"].grid(row=0, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton1"].config(text="Cambiar Contraseña", state="disabled",
                                          command=self.cambiar_contras_usu)
        self.dic_fun_usu["boton1"].grid(row=1, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton2"].config(text="Eliminar Usuario", state="disabled", command=self.eliminar_usuario)
        self.dic_fun_usu["boton2"].grid(row=2, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton3"].config(text="Consultar Cartas del Usuario", state="disabled",
                                          command=self.consultar_cartas_usuario)
        self.dic_fun_usu["boton3"].grid(row=3, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton4"].config(text="Cargar Cartas al Usuario", state="disabled",
                                          command=self.cargar_cartas_usuario)
        self.dic_fun_usu["boton4"].grid(row=4, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton5"].config(text="Dar de Baja Cartas al Usuario", state="disabled",
                                          command=self.dar_de_baja_cartas_usuario)
        self.dic_fun_usu["boton5"].grid(row=5, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton6"].config(text="Grabar Batallas", state="disabled", command=self.grabar_batallas)
        self.dic_fun_usu["boton6"].grid(row=6, column=0, padx=10, pady=5, sticky="NSEW")

        self.dic_fun_usu["boton7"].config(text="Ventana de Sugerir Batallas", state="disabled",
                                          style="orange.TButton", command=self.abrir_sugerencia_batallas)
        self.dic_fun_usu["boton7"].grid(row=8, column=0, padx=10, pady=5, sticky="NSEW")

        # Para EXPANDIR los botones al Frame
        self.fr_funciones_usuario.grid_rowconfigure(0, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(1, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(2, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(3, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(4, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(5, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(6, weight=1)
        self.fr_funciones_usuario.grid_rowconfigure(8, weight=1)
        self.fr_funciones_usuario.grid_columnconfigure(0, weight=1)

    def elementos_como_inicio(self):
        """Método para configurar los elementos en el frame de la derecha. Se ejecuta al cargarse la Pantalla Inicial y
        luego, cada vez que se sale o termina una acción que se haya seleccionado (se vuelve al inicio la pantalla)"""

        # Borramos o eliminamos todos los diccionarios y widgets
        self.d_stv.clear()
        self.d_ent.clear()
        self.d_btn.clear()
        self.d_lbl.clear()
        self.d_frm.clear()
        self.imagen = None
        self.control_cola = True

        for widget in self.fr_acciones.winfo_children():
            widget.destroy()

        # Los volvemos a definir o crear
        for x in range(15):
            nombre = f"stv{x}"
            self.d_stv[nombre] = StringVar()
        for x in range(2):
            nombre = f"ent{x}"
            self.d_ent[nombre] = ttk.Entry(self.fr_acciones)
        for x in range(6):
            nombre = f"btn{x}"
            self.d_btn[nombre] = ttk.Button(self.fr_acciones)
        for x in range(25):
            nombre = f"lbl{x}"
            self.d_lbl[nombre] = ttk.Label(self.fr_acciones)
        for x in range(2):
            nombre = f"frm{x}"
            self.d_frm[nombre] = ttk.Frame(self.fr_acciones)
        self.treeview = ttk.Treeview(self.fr_acciones)
        self.scrollbar = ttk.Scrollbar(self.fr_acciones)
        self.cuadro_texto = Text(self.fr_acciones)
        self.progress_bar = ttk.Progressbar(self.fr_acciones)
        self.canvas = Canvas(self.fr_acciones)

        # Volvemos el color de la letra a negro para la etiqueta principal. "TLabel" es el estilo original
        self.etiq_mensajes_principal.config(text="", style="TLabel", anchor="center", justify="center")

        # Activamos los textos de los botones
        self.activar_textos()

        # Cargamos el frame para acciones en la 3era columna
        self.frame_accion_inicio()

    def activar_textos(self):
        """Método para que se activen los mensajes de ayuda cuando se pasa el mouse por encima de ellos"""
        # Descripción para cada botón. Cada clave es botón atributo name + "_texto"
        textos_mensaje = {
            "Crear Nueva Carta_texto": "Agregue Cartas a la Base de Datos",
            "Modificar Carta_texto": "Modifique los datos de una Carta existente en la Base de Datos",
            "Eliminar Carta_texto": "Elimine una Carta de la Base de Datos",
            "Consultar Cartas_texto": "Consulte las Cartas existentes en la Base de Datos filtrando por nombre",
            "Crear Nueva Regla_texto": "Agregue una Regla nueva a la Base de Datos",
            "Modificar Regla_texto": "Modifique los datos de una Regla existente en la Base de Datos",
            "Eliminar Regla_texto": "Elimine una Regla de la Base de Datos",
            "Consultar Reglas_texto": "Consulte las Reglas existentes en la Base de Datos",
            "Consultar Batallas por fecha_texto": "Ingrese una Fecha para obtener un listado de Batallas",
            "Consultar Batallas SQL_texto": "Realice una consulta personalizada a la DB utilizando SQL",
            "Eliminar Batalla_texto": "Elimine una Batalla de la Base de Datos usando su nro de identificación (ID)",
            "Acceder con Usuario y Contraseña_texto": "Acceda para habilitar las Funciones de Usuario como Sugerir "
                                                      "Batallas",
            "Desloguearse_texto": "Cierre la actual cesión para el usuario que se encuentre logueado",
            "Crear Nuevo Usuario_texto": "Cree un Nuevo Usuario definiendo un usuario y datos de acceso al juego",
            "Modificar Usuario_texto": "Modifique los datos de su cuenta, como su usuario o su correo de\nacceso al "
                                       "juego",
            "Cambiar Contraseña_texto": "Modifique la contraseña de su cuenta",
            "Eliminar Usuario_texto": "Elimine su cuenta",
            "Consultar Cartas del Usuario_texto": "Consulte y obtenga un listado de las cartas en posesión del "
                                                  "usuario.",
            "Cargar Cartas al Usuario_texto": "Indique qué cartas se encuentran en posesión del usuario. Las cartas "
                                              "deben\nestar previamente cargadas en -Crear Nueva Carta-.",
            "Dar de Baja Cartas al Usuario_texto": "Indique qué cartas ya no se encuentran en posesión del usuario",
            "Grabar Batallas_texto": "Permite grabar batallas descargándolas de la consulta API en la web",
            "Ventana de Sugerir Batallas_texto": "Abre la ventana para ingresar un conjunto de Reglas y sugerir "
                                                 "batallas\nsegún las partidas grabadas en la Base de Datos"
        }

        # Recorremos cada Label Frame en el que hay botones y en cada uno sus elementos
        for frame in [self.fr_botones_cartas, self.fr_botones_reglas, self.fr_botones_batallas, self.fr_acceso_usuario,
                      self.fr_funciones_usuario]:
            for widget in frame.winfo_children():
                if isinstance(widget, ttk.Button):  # Preguntamos si es botón (solo es uno hay una etiqueta)
                    texto_widget = widget.cget("text")  # Obtenemos el texto de cada widget
                    dicc_msj = f"{texto_widget}_texto"  # Al nombre le agregamos _texto para formar la clave de arriba

                    # Activamos el mensaje cuando el mouse entra y sale, texto=self.textos_mensaje[dicc_msj] para que
                    # cada widget tenga su descripción, si no el bucle no aplica bien
                    widget.bind("<Enter>", lambda evento, texto_definido=textos_mensaje[dicc_msj]:
                                self.texto_etiqueta_principal(texto=texto_definido))
                    widget.bind("<Leave>", lambda evento, texto_definido="":
                                self.texto_etiqueta_principal(texto=texto_definido))

    def desactivar_textos(self):
        """Método para desactivar los mensajes de ayuda. En general se llamará cuando se selecciona una acción. Los
            mensajes no se mostrarán hasta tanto se llame activar_textos()"""
        for frame in [self.fr_botones_cartas, self.fr_botones_reglas, self.fr_botones_batallas, self.fr_acceso_usuario,
                      self.fr_funciones_usuario]:
            for widget in frame.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.unbind("<Enter>")  # Con .unbind + evento se desactiva la acción
                    widget.unbind("<Leave>")

    def texto_etiqueta_principal(self, texto, estilo="TLabel"):
        """Método para cambiar el texto y el estilo de la etiqueta que está al inicio de la ventana principal"""

        self.etiq_mensajes_principal.config(text=texto, style=estilo)

    def texto_etiqueta_login(self, texto, estilo):
        """Método para cambiar el texto y el estilo de la etiqueta para el login en el frame Acceso Usuario"""

        self.etiq_usuario_logueado.config(text=texto, style=estilo)

#-----------------------------------------------------------------------------------------------------------------------
#                               FUNCIONES COMUNES PARA ACCIONES
#-----------------------------------------------------------------------------------------------------------------------
    def frame_accion_inicio(self):
        """Método que carga el Frame Acciones (3.ª columna de la ventana principal) en su estado básico: configura
            y carga una etiqueta con un mensaje"""

        # Configura el Frame
        self.fr_acciones.grid(row=0, column=2, rowspan=1, padx=10, pady=10, sticky="NSEW")
        self.fr_acciones.grid_rowconfigure(0, minsize=40)

        # Al inicio solo habrá una etiqueta
        self.etiqueta_acciones = ttk.Label(self.fr_acciones, text="Seleccione la acción que desee realizar",
                                           justify="center")
        self.etiqueta_acciones.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="NSEW")

    def reiniciando_frame_acciones(self, text_etiqueta, alto_filas):
        """Método que realiza la configuración inicial del frame acciones según cada botón presionado"""

        # Se vuelve el Frame a su estado inicial (por si viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Durante la ejecución se desactivan los textos y el mensaje que se muestra es que se está dentro de esta acción
        self.desactivar_textos()
        self.texto_etiqueta_principal(texto=text_etiqueta, estilo="blue.TLabel")

        # Tamaño del Frame ajustado a la acción (previamente borramos cualquier tamaño que pueda haber dado una acción)
        for i in range(8):
            self.fr_acciones.grid_columnconfigure(i, minsize=0)  # Resetamos el tamaño usando cero
        for i in range(25):
            self.fr_acciones.grid_rowconfigure(i, minsize=0)  # Resetamos el tamaño usando cero

        self.fr_acciones.grid_configure(rowspan=alto_filas)  # Definimos filas visibles
        self.fr_acciones.grid_rowconfigure(0, minsize=40)  # A la fila-etiqueta le asignamos un mínimo

        # Borramos el contenido de la etiqueta, que luego se usará para mensajes de errores o de completado de la acción
        self.etiqueta_acciones.configure(text="")

    def borrar_variables(self):
        """Método para borrar los valores de los StringVar y de las imágenes sin reiniciar la interfaz de acciones."""

        self.imagen = None

        for x in range(15):
            nombre = f"stv{x}"
            self.d_stv[nombre].set("")

    def cargar_imagen(self, alto_img, ruta_imagen=None, nombre_carta=None, nivel_carta=None, grupo_carta=None):
        """Método que busca una imagen en una ruta de la pc o en la web (cuando no recibe ruta) y la carga en el único
            canvas -self.canvas- de la aplicación. Necesita también el alto de destino para definir el tamaño (puede ser
             llamado por métodos de cartas y de reglas)"""

        if ruta_imagen:  # Cuando se trate de la carga desde archivo o un caso sin imagen, habrá valor aquí

            # Función que busca e intenta su carga. Puede venir con error, en cuyo caso devolverá un string.
            self.imagen = funciones.imagen_pillow_ruta(ruta_imagen)

            # Switch de control de imagen nueva
            if ruta_imagen == "imagenes/sin_imagen.png":
                self.d_stv["stv10"].set("sin imagen")
            else:
                self.d_stv["stv10"].set("con imagen")

        elif ruta_imagen == "" and nombre_carta == ">regla<":
            pass  # No queremos que haga nada. Es que se aprieta el botón sin cargar previamente la ruta

        # En caso de que se llame a la función sin el parámetro ruta_imagen será una búsqueda web
        else:
            # Borramos la variable para chequear si en la búsqueda se encontró imagen (no quitará imagen del widget)
            self.imagen = None
            # Chequeamos si tenemos valores en los 3 campos necesarios para buscar en la web, cuando no hay: msje error
            if nombre_carta == "" or nivel_carta == "" or grupo_carta == "":
                self.etiqueta_acciones.configure(text="Debe completar todos los campos", style="cursiva_red.TLabel")

            else:
                # Llamado a la función que busca e intenta carga. Puede venir con error y devolverá string.
                self.imagen = funciones.imagen_pillow_web(grupo=grupo_carta,
                                                          carta_nombre=nombre_carta,
                                                          nivel=nivel_carta)

                self.d_stv["stv10"].set("con imagen")  # Switch de control

        # Chequeamos lo que nos han devuelto las funciones
        if isinstance(self.imagen, PngImagePlugin.PngImageFile):

            # Colocamos la imagen en el widget, para estas cargas se usará el canvas
            funciones.colocar_img_en_widget(imagen_a_colocar=self.imagen, widget=self.canvas, alto=alto_img)

            self.etiqueta_acciones.config(text="")  # Borramos la etiqueta por si había errores anteriores

        # Si hubo errores, la variable tendrá un string con la descripción del error
        elif isinstance(self.imagen, str):
            self.etiqueta_acciones.config(text=self.imagen, style="cursiva_red.TLabel")

    def configurar_treeview(self, columnas, nombres, anchos):
        """Método para configurar un Treeview, pero sin colocarlo en la ventana. Requiere recibir la cantidad de
            columnas, una lista con los nombres de las columnas y otra lista con el ancho de cada una. El último
            elemento de las listas será el dato del encabezado y columna especial -#0-"""

        # Creamos una lista de columnas que dependerá de la cantidad numérica recibida como parámetro
        l_col = []
        for i in range(columnas):
            l_col.append(str(i))

        # Configuramos Treeview usando la lista anterior
        self.treeview.config(height=7, columns=l_col, style="alto_fila_con_img.Treeview")

        # Encabezado y columna especial -#0- la definimos por separado aquí
        self.treeview.heading("#0", text=nombres[-1], anchor="center")
        self.treeview.column("#0", width=anchos[-1], anchor="center")

        # Definimos cada columna
        for n, col in enumerate(l_col):
            self.treeview.heading(col, text=nombres[n], anchor="center")
            self.treeview.column(col, width=anchos[n], anchor="center")

        self.treeview["displaycolumns"] = l_col

        # Definimos el Scroll
        self.scrollbar.config(orient="vertical", command=self.treeview.yview)
        self.treeview.config(yscrollcommand=self.scrollbar.set)

    def cargar_treeview(self, tipo_datos, lista_datos_db):
        """Método que carga los elementos de una lista de datos obtenidos de una consulta a la DB en un Treeview."""

        alto_img = 10  # El alto de la imagen se define según el tipo de datos
        if tipo_datos == "carta":
            alto_img = 50
        elif tipo_datos == "regla":
            alto_img = 40

        lista_imagenes = []
        for i, elemento_db in enumerate(lista_datos_db):  # Recorremos cada carta recibida de la DB

            # Chequeamos si tiene imagen en la DB y si no, usamos una ilustración de que no está disponible
            if elemento_db.imagen:
                imagen_pillow = Image.open(io.BytesIO(elemento_db.imagen))
                alto_img_tree = alto_img
            else:
                imagen_pillow = Image.open(fp="imagenes/Imagen-no-disponible-282x300.png")
                alto_img_tree = 38

            # Teniendo las proporciones de la imagen, la convertimos a un nuevo tamaño y la pasamos a formato tk
            ancho_img = funciones.ancho_segun_ratio_imagen(imagen=imagen_pillow, nvo_alto=alto_img_tree)
            imagen_tk = funciones.convertir_imagen_tk(imagen_convertir=imagen_pillow,
                                                      ancho_nvo=ancho_img,
                                                      alto_nvo=alto_img_tree)

            # Creamos una lista de imagen que tendrá el mismo orden que la lista de cartas
            lista_imagenes.append(imagen_tk)

            # Creamos una lista para los values
            lista_valores = []
            for n in range(len(lista_datos_db)):
                lista_valores.append("")

            # Completamos el Treeview con los datos de la DB
            fila = self.treeview.insert("", "end",
                                        image=lista_imagenes[i],
                                        values=lista_valores,  # Los valores los dejamos vacíos en este punto
                                        tags="imagen")
            self.treeview.tag_configure("imagen", image=imagen_tk)
            Label(self.fr_acciones).imagen = imagen_tk

            # Colores alternados a cada fila (efecto visual)
            if i % 2 == 0:
                self.treeview.item(fila, tags=("evenrow",))
            else:
                self.treeview.item(fila, tags=("oddrow",))
            self.treeview.tag_configure("oddrow", background="#fcf6ed")
            self.treeview.tag_configure("evenrow", background="#eff2df")

            # Carga de datos para cuando se trata de una CARTA
            if tipo_datos == "carta":
                # Verificamos que haya nombre y si es demasiado largo hacemos que se muestre en 2 líneas
                nombre = elemento_db.nombre
                if nombre:
                    if len(nombre) > 42:
                        nombre = "\n".join(textwrap.wrap(nombre, 42))
                else:
                    nombre = ""

                self.treeview.item(fila, values=(elemento_db.id_card,
                                                 elemento_db.id_game,
                                                 elemento_db.nivel,
                                                 nombre,
                                                 elemento_db.grupo))

            # Carga de datos cuando se trata de una REGLA
            elif tipo_datos == "regla":
                # Verificamos que haya descripción y si es demasiado larga hacemos que se muestre en 2 líneas
                descripcion = elemento_db.descripcion
                if descripcion:
                    if len(descripcion) > 42:
                        descripcion = "\n".join(textwrap.wrap(descripcion, 42))
                else:
                    descripcion = ""

                self.treeview.item(fila, values=(elemento_db.id_regla,
                                                 elemento_db.nombre,
                                                 descripcion))

    def desactivar_botones_todos(self):
        """Método que recorre todos los frame y desactiva los botones"""

        funciones.activa_desactiva_botones(self.fr_acciones, "disabled")
        funciones.activa_desactiva_botones(self.fr_botones_cartas, "disabled")
        funciones.activa_desactiva_botones(self.fr_botones_reglas, "disabled")
        funciones.activa_desactiva_botones(self.fr_botones_batallas, "disabled")
        funciones.activa_desactiva_botones(self.fr_acceso_usuario, "disabled")
        funciones.activa_desactiva_botones(self.fr_funciones_usuario, "disabled")

    def activar_botones_todos(self):
        """Método que recorre todos los frame y activa los botones"""

        funciones.activa_desactiva_botones(self.fr_acciones, "active")
        funciones.activa_desactiva_botones(self.fr_botones_cartas, "active")
        funciones.activa_desactiva_botones(self.fr_botones_reglas, "active")
        funciones.activa_desactiva_botones(self.fr_botones_batallas, "active")
        funciones.activa_desactiva_botones(self.fr_acceso_usuario, "active")
        if self.etiq_usuario_logueado.cget("text") != "No se ha logueado":
            self.dic_acc_usu["boton0"].config(state="disabled")
            funciones.activa_desactiva_botones(self.fr_funciones_usuario, "active")
        else:
            self.dic_acc_usu["boton1"].config(state="disabled")

    @staticmethod
    def proceso_hilo_secundario(proceso, argumentos):
        """Método para que ejecutar una acción en un hilo secundario"""

        hilo = threading.Thread(target=proceso, args=argumentos)
        hilo.start()

    def revision_queue(self, caso):
        """Método para revisar periódicamente la queue de los procesos que se están ejecutando en un hilo secundario"""

        if self.control_cola:  # La variable será utilizada luego para detener el proceso
            try:
                while True:
                    recibido = self.queue.get_nowait()  # Lectura de la queue

                    # Cuando hay datos en la queue, según el caso ejecutamos una función para tratar esa información
                    if caso == "grabar_batallas":
                        self.tratar_grabar_bat(recibido)
                    elif caso == "cartas_masivo":
                        self.tratar_cartas(recibido)
                    elif caso == "tabla_grab_bat":
                        self.cargar_usu_tree_grab_bat(recibido)

            except queue.Empty:
                pass
            finally:  # El proceso se reiniciará pasado 1 segundo
                self.ventana_inicial.after(100, lambda: self.revision_queue(caso=caso))

    def detener_revision_queue(self):
        """Método que cambia el valor de variable que mantiene activo el método de revision_queue"""

        self.control_cola = False

#-----------------------------------------------------------------------------------------------------------------------
#                                      CARTAS
#-----------------------------------------------------------------------------------------------------------------------
    def crear_nueva_carta(self):
        """Método que carga la interfaz en el Frame Acciones para crear una Carta nueva"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Creando Nueva Carta", alto_filas=3)

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Crear una Nueva Carta en la Base de Datos", style="tit_bold.TLabel").grid(
            row=1, column=0, columnspan=2, padx=(10, 15), pady=(0, 6), sticky="W")

        # Etiqueta y Entry NOMBRE CARTA
        ttk.Label(self.fr_acciones, text="Ingrese el nombre de la Carta:").grid(
            row=2, column=0, columnspan=2, padx=10, pady=(10, 3), sticky="W")
        self.d_ent["ent0"].config(textvariable=self.d_stv["stv0"], font=("TkDefaultFont", 11), width=30)
        self.d_ent["ent0"].grid(row=3, column=0, columnspan=2, padx=10, pady=(4, 8), sticky="W")
        self.d_ent["ent0"].focus()

        # Botón carga masiva web
        self.d_btn["btn0"].config(text="Carga masiva web", command=self.inicio_cartas_masivo, width=20)
        self.d_btn["btn0"].grid(row=2, column=2, padx=10, pady=(6, 3), ipadx=1, ipady=2)

        # Etiqueta y Entry ID_GAME
        ttk.Label(self.fr_acciones, text="ID de la carta en el Juego (*):", width=33).grid(
            row=4, column=0, padx=10, pady=10, sticky="W")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv1"], font=("TkDefaultFont", 11), width=4,
                  justify="center").grid(row=4, column=0, padx=10, pady=10, sticky="E")

        # Etiqueta y Entry NIVEL
        ttk.Label(self.fr_acciones, text="Nivel de la carta (*):", width=23).grid(
            row=4, column=1, padx=10, pady=10, sticky="W")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv2"], font=("TkDefaultFont", 11), width=3,
                  justify="center").grid(row=4, column=1, padx=10, pady=10, sticky="E")

        # Etiqueta, Entry y Botón para GRUPO
        ttk.Label(self.fr_acciones, text="Grupo de cartas a la que pertenece:").grid(
            row=6, column=0, columnspan=2, padx=10, pady=(8, 2), sticky="W")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv3"], font=("TkDefaultFont", 11), width=18).grid(
            row=7, column=0, columnspan=2, padx=10, pady=(4, 8), sticky="W")

        ttk.Button(self.fr_acciones, text="Carga web", command=lambda: self.cargar_imagen(
                                                                                nombre_carta=self.d_stv["stv0"].get(),
                                                                                nivel_carta=self.d_stv["stv2"].get(),
                                                                                grupo_carta=self.d_stv["stv3"].get(),
                                                                                alto_img=140),
                   width=10).grid(row=7, column=1, padx=2, pady=(4, 8), sticky="E")

        # Cuadro para la imagen
        self.canvas.grid(row=7, column=2, rowspan=6, padx=(10, 5), pady=4, sticky="N")

        # Etiqueta, Entry y Botón para Ruta IMAGEN
        ttk.Label(self.fr_acciones, text="Ingrese la ruta completa con nombre y extensión de la imagen:").grid(
            row=8, column=0, columnspan=2, padx=(10, 10), pady=(8, 2), sticky="W")
        ttk.Entry(self.fr_acciones, font=("TkDefaultFont", 9), width=42, textvariable=self.d_stv["stv4"]).grid(
            row=9, column=0, columnspan=2, padx=(10, 2), pady=(4, 2), sticky="W")
        ttk.Button(self.fr_acciones, text="Buscar", command=lambda: funciones.seleccionar_archivo(self.d_stv["stv4"]),
                   width=10).grid(row=9, column=1, padx=2, pady=(4, 2), sticky="E")
        ttk.Button(self.fr_acciones, text="Cargar", command=lambda: self.cargar_imagen(
            ruta_imagen=self.d_stv["stv4"].get(), alto_img=140), width=10).grid(
            row=10, column=1, padx=2, pady=(4, 8), sticky="E")
        ttk.Button(self.fr_acciones, text="Quitar", command=lambda: self.cargar_imagen(
            ruta_imagen="imagenes/sin_imagen.png", alto_img=100), width=10).grid(
            row=11, column=1, padx=2, pady=(4, 8), sticky="E")

        # Detalle de lo obligatorio, ya que se puede crear sin completar todas las casillas
        ttk.Label(self.fr_acciones, text="(*) campos obligatorios para crear la carta", justify="left",
                  font=("Segoe UI", 7)).grid(row=11, column=0, padx=10, pady=4, sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=12, column=1, padx=10, pady=(8, 5), ipadx=10, ipady=2, sticky="E")

        ttk.Button(self.fr_acciones, text="Aceptar", command=self.nueva_carta_aceptado).grid(
            row=12, column=2, padx=10, pady=(8, 5), ipadx=10, ipady=2, sticky="W")

        # Carga de imagen inicial
        self.cargar_imagen(ruta_imagen="imagenes/sin_imagen.png", alto_img=100)  # Ilustración -sin imagen-

    def nueva_carta_aceptado(self):
        """Método que se ejecuta al aceptar la creación de una Carta. Muestra mensajes de completado o de error. Llama
            a la función que graba en la DB"""

        # Verificamos que se hayan completado los campos mínimos necesarios
        if not self.d_stv["stv1"].get() or not self.d_stv["stv2"].get():
            self.etiqueta_acciones.config(text="Los campos mínimos no pueden estar vacíos", style="cursiva_red.TLabel")

        else:
            # Llamamos función para saber si hay imagen nueva que se desee grabar en la DB
            imagen_para_db = funciones.check_imagen_cambiada(switch=self.d_stv["stv10"].get(), imagen=self.imagen)

            rtdo_crear_carta = funciones.nueva_carta_db(carta_id=self.d_stv["stv1"].get(),
                                                        carta_nivel=self.d_stv["stv2"].get(),
                                                        carta_nombre=self.d_stv["stv0"].get(),
                                                        carta_grupo=self.d_stv["stv3"].get(),
                                                        carta_imagen=imagen_para_db)

            if rtdo_crear_carta[0] == "C":  # Mensaje y acciones en caso de Creación Correcta

                self.borrar_variables()  # Cuando se grabó en DB borramos todos los widgets

                self.cargar_imagen(ruta_imagen="imagenes/sin_imagen.png", alto_img=100)  # Ilustración

                self.etiqueta_acciones.config(style="cursiva_green.TLabel")  # Color de Ok

            else:  # Mensaje en caso de Error
                self.etiqueta_acciones.config(style="cursiva_red.TLabel")  # Color de error

            self.etiqueta_acciones.config(text=rtdo_crear_carta)  # Mensaje

    def inicio_cartas_masivo(self):
        """Método que inicia la ejecución de la carga masiva en un hilo secundario y la revisión de la queue. También
        carga en la interfaz una barra de avance y un cuadro de texto informativo."""

        if self.fr_acciones.grid_info().get("rowspan") != 4:

            self.fr_acciones.grid_configure(rowspan=4)  # Agrandamos la interfaz

            # Barra de progreso
            self.progress_bar.config(orient="horizontal", length=120, mode="determinate")

            # Insertamos un CUADRO DE TEXTO para ver mensajes
            self.cuadro_texto.config(width=81, height=8, font=("Yu Gothic UI Semibold", 8), wrap="word",
                                     background="#3c3c3c", foreground="white")
            self.cuadro_texto.grid(row=13, column=0, columnspan=3, padx=14, pady=(20, 7), ipady=2, ipadx=1)

            # Colocamos el SCROLL
            self.scrollbar.grid(row=13, column=2, padx=0, pady=(20, 7), sticky="NSE")
            self.cuadro_texto.config(yscrollcommand=self.scrollbar.set)

        # Desactivamos botones
        self.desactivar_botones_todos()

        # Cambiamos el boton a 'Detener' y modificamos lo que ejecuta
        self.d_btn["btn0"].config(text="Detener Carga", command=self.detener_hilo_secund, state="active")

        # Iniciamos el proceso de grabado de las cartas en un hilo secundario y le pasamos sus argumentos
        self.detener_hilo.clear()
        self.proceso_hilo_secundario(proceso=funciones.cartas_masivo_hilo_secund,
                                     argumentos=(self.queue, self.detener_hilo))

        # A su vez iniciamos la revisión de la cola con caso 'cartas masivo' para que llame al proceso 'tratar cartas'
        self.control_cola = True
        self.revision_queue(caso="cartas_masivo")

    def tratar_cartas(self, resultado):
        """Método que recibe las novedades que genera la cola del proceso cargar cartas masivo para ir mostrando en
        pantalla el avance del mismo"""

        # Colocamos el mensaje recibido en el cuadro de texto y llevamos la vista al final
        self.cuadro_texto.insert("end", resultado)
        self.cuadro_texto.see("end")

        # Cuando se trate de un mensaje relacionado con el tratamiento de cartas, aumentamos el progress bar
        if resultado[:6] == "\nCarta" or resultado[:6] == "\nGraba":
            self.progress_bar["value"] += 1

        # Cuando nos informe la cantidad de cartas, configuramos y colocamos el progress bar
        elif "cartas descargadas" in resultado:
            cartas_descargadas = int(resultado[:3])
            self.progress_bar.config(value=0, maximum=cartas_descargadas)
            self.progress_bar.grid(row=1, column=2)

        # Este 'if' se ejecutará con el mensaje final: "Proceso finalizado"
        elif "..." not in resultado:
            self.d_btn["btn0"].config(text="Carga masiva web", command=self.inicio_cartas_masivo)
            self.etiqueta_acciones.config(text="Grabado masivo finalizado", style="cursiva_green.TLabel")
            self.activar_botones_todos()
            self.detener_revision_queue()

#-----------------------------------------------------------------------------------------------------------------------
    def modificar_carta(self):
        """Método que carga la interfaz en el Frame Acciones para buscar una Carta que se quiere modificar"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Modificando Cartas", alto_filas=2)

        # TITULO
        ttk.Label(self.fr_acciones, text="Modifica o completa los datos de una carta:", style="tit_bold.TLabel",
                  justify="right").grid(row=1, column=0, columnspan=3, padx=(20, 40), pady=(0, 8), sticky="E")

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Número de ID Game y nivel de una Carta:").grid(
            row=2, column=0, columnspan=3, padx=(15, 5), pady=(0, 6), sticky="E")

        # Entry para ID GAME CARTA
        self.d_ent["ent0"].config(width=6, font=("Segoe UI", 10), justify="center", textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=2, column=3, padx=3, pady=(0, 6))
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", self.buscar_carta_a_modif)

        # Entry para NIVEL CARTA
        self.d_ent["ent1"].config(width=4, font=("Segoe UI", 10), justify="center", textvariable=self.d_stv["stv1"])
        self.d_ent["ent1"].grid(row=2, column=4, padx=10, pady=(0, 6))
        self.d_ent["ent1"].bind("<Return>", self.buscar_carta_a_modif)

        # BOTON BUSCAR
        ttk.Button(self.fr_acciones, text="Buscar", command=self.buscar_carta_a_modif).grid(
            row=2, column=5, padx=2, pady=(0, 6), sticky="W")

        # Variable para indicar si debe cargar la interfaz cuando se busque, la primera vez debe hacerlo
        self.d_stv["stv12"].set(True)

    def buscar_carta_a_modif(self, *args):
        """Método que se ejecuta al Buscar una Carta que se quiere Modificar. Colocará los widgets en pantalla con
            los valores de la Carta y/o mostrará errores"""

        self.etiqueta_acciones.configure(text="")  # Borramos mensaje por si había de antes

        carta_db = None
        msje_error = None
        try:  # Try para evitar errores cuando se ingresan valores no numéricos
            id_juego = int(self.d_ent["ent0"].get().strip())
            nivel = int(self.d_ent["ent1"].get().strip())

        except ValueError:
            msje_error = "Error en los datos ingresados. No son numéricos"

        else:
            carta_db = funciones.carta_datos_db(id_game_card=id_juego, nivel_card=nivel)  # Función para ir a la DB
            self.d_stv["stv0"].set("")

        if carta_db:  # Si se pudo asignar valor (o sea si había un valor numérico)

            if self.d_stv["stv12"].get():  # Chequeamos si ya está cargada la interfaz
                self.interfaz_modif_carta()

            # Colocamos valores según DB
            for x in range(5):
                self.d_lbl[f"lbl{x}"].config(text="")
            self.d_lbl["lbl0"].config(text=carta_db.nombre)
            self.d_lbl["lbl1"].config(text=carta_db.id_card)
            self.d_lbl["lbl2"].config(text=carta_db.id_game)
            self.d_lbl["lbl3"].config(text=carta_db.nivel)
            self.d_lbl["lbl4"].config(text=carta_db.grupo)

            # Definimos la imagen: de la DB o una ilustración de que no está disponible
            if carta_db.imagen:
                imagen_pillow = Image.open(io.BytesIO(carta_db.imagen))
                self.d_stv["stv11"].set("con imagen DB")  # Switch para saber que hay imagen en la DB
            else:
                imagen_pillow = Image.open(fp="imagenes/Imagen-no-disponible-282x300.png")

            # Llamamos a la función para colocarla en el widget, label en este caso
            funciones.colocar_img_en_widget(imagen_a_colocar=imagen_pillow, widget=self.d_lbl["lbl5"], alto=140)

        else:
            # Mensaje de error cuando la carta no es encontrada en la DB
            self.etiqueta_acciones.config(style="cursiva_red.TLabel")
            if not msje_error:
                self.etiqueta_acciones.config(text="La carta ingresada no existe en la Base de Datos")
            else:
                self.etiqueta_acciones.config(text=msje_error)

        self.d_ent["ent0"].focus()  # Al buscar posicionamos el cursor debe nuevo en el número de carta para buscar otro

    def interfaz_modif_carta(self):
        """Método para cargar los widgets en el frame acciones cuando se ha buscado una carta a modificar en la DB"""

        self.fr_acciones.grid_configure(rowspan=4)

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=3, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # NOMBRE DE LA CARTA
        ttk.Label(self.fr_acciones, text="Nombre de la carta B.D.", style="cursiva.TLabel").grid(
            row=4, column=0, padx=10, pady=(6, 2), sticky="E")
        self.d_lbl["lbl0"].config(wraplength=120, style="cursiva.TLabel")
        self.d_lbl["lbl0"].grid(row=4, column=1, columnspan=2, padx=10, pady=(6, 2), sticky="W")
        ttk.Label(self.fr_acciones, text="Nombre carta nuevo:").grid(
            row=5, column=0, padx=10, pady=(2, 6), sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv2"], font=("Segoe UI", 9)).grid(
            row=5, column=1, columnspan=3, padx=10, pady=(2, 6), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=6, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # ID DE LA CARTA
        ttk.Label(self.fr_acciones, text="ID de la carta B.D.", style="cursiva.TLabel").grid(
            row=7, column=0, padx=10, pady=6, sticky="E")
        self.d_lbl["lbl1"].config(style="cursiva.TLabel")
        self.d_lbl["lbl1"].grid(row=7, column=1, columnspan=2, padx=10, pady=6, sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=8, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # ID GAME
        ttk.Label(self.fr_acciones, text="ID game de la carta B.D.", style="cursiva.TLabel").grid(
            row=9, column=0, padx=10, pady=6, sticky="E")
        self.d_lbl["lbl2"].config(style="cursiva.TLabel")
        self.d_lbl["lbl2"].grid(row=9, column=1, columnspan=2, padx=10, pady=6, sticky="W")
        ttk.Label(self.fr_acciones, text="Nuevo ID game:").grid(
            row=9, column=2, padx=10, pady=6, sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv3"], font=("Segoe UI", 9), width=6,
                  justify="center").grid(row=9, column=3, padx=6, pady=6, sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=10, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # NIVEL
        ttk.Label(self.fr_acciones, text="Nivel B.D.", style="cursiva.TLabel").grid(
            row=11, column=0, padx=10, pady=6, sticky="E")
        self.d_lbl["lbl3"].config(style="cursiva.TLabel")
        self.d_lbl["lbl3"].grid(row=11, column=1, columnspan=2, padx=10, pady=6, sticky="W")
        ttk.Label(self.fr_acciones, text="Nuevo nivel:").grid(
            row=11, column=2, padx=10, pady=6, sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv4"], font=("Segoe UI", 9), width=4,
                  justify="center").grid(row=11, column=3, padx=6, pady=6, sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=12, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # GRUPO DE LA CARTA
        ttk.Label(self.fr_acciones, text="Grupo carta B.D.", style="cursiva.TLabel").grid(
            row=13, column=0, padx=10, pady=(6, 2), sticky="E")
        self.d_lbl["lbl4"].config(style="cursiva.TLabel")
        self.d_lbl["lbl4"].grid(row=13, column=1, columnspan=2, padx=10, pady=(6, 2), sticky="W")
        ttk.Label(self.fr_acciones, text="Grupo carta nuevo:").grid(
            row=14, column=0, padx=10, pady=(2, 6), sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv5"], font=("Segoe UI", 9), width=15).grid(
            row=14, column=1, columnspan=2, padx=10, pady=(2, 6), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=15, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # IMAGEN CARTAS
        ttk.Label(self.fr_acciones, text="Imagen carta B.D.", style="cursiva.TLabel").grid(
            row=16, column=0, padx=10, pady=(6, 2), sticky="E")
        self.d_lbl["lbl5"].config(relief="solid")
        self.d_lbl["lbl5"].grid(row=16, column=1, columnspan=2, padx=10, pady=1, sticky="W")
        ttk.Label(self.fr_acciones, text="Ruta imagen nueva:").grid(
            row=17, column=0, padx=10, pady=2, sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv6"], font=("Segoe UI", 9), width=23).grid(
            row=17, column=1, columnspan=6, padx=(8, 5), pady=2, sticky="W")
        ttk.Button(self.fr_acciones, text="Archivo", command=lambda: funciones.seleccionar_archivo(
            self.d_stv["stv6"]), width=7).grid(row=17, column=3, padx=0, pady=2, sticky="W")
        ttk.Button(self.fr_acciones, text="Cargar", command=lambda: self.cargar_imagen(
            ruta_imagen=self.d_stv["stv6"].get(), alto_img=140), width=7).grid(
            row=17, column=4, padx=1, pady=2, sticky="W")
        ttk.Button(self.fr_acciones, text="Carga web", command=lambda: self.cargar_imagen(
            nombre_carta=self.d_stv["stv2"].get(),
            nivel_carta=self.d_stv["stv4"].get(),
            grupo_carta=self.d_stv["stv5"].get(),
            alto_img=140),
                   width=10).grid(row=17, column=5, padx=0, pady=2, sticky="W")
        ttk.Checkbutton(self.fr_acciones, text="Quitar/Sin imagen", variable=self.d_stv["stv7"],
                        onvalue="quitar imagen").grid(row=18, column=3, columnspan=3, padx=5, pady=(2, 4))

        self.canvas.config(width=100, height=140)
        self.canvas.grid(row=16, column=4, columnspan=3, padx=5, pady=0, sticky="w")

        self.fr_acciones.grid_rowconfigure(16, minsize=140)  # Configuración para la fila de la imagen

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=19, column=0, columnspan=6, sticky="ew", padx=(20, 4))

        # Detalle aclaratorio
        ttk.Label(self.fr_acciones, justify="left", font=("Segoe UI", 7),
                  text="Los nuevos datos reemplazarán a los existentes en la Base de Datos").grid(
            row=20, column=0, columnspan=4, padx=20, pady=4, sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=21, column=2, columnspan=2, padx=10, pady=4, ipadx=10, ipady=2, sticky="E")
        ttk.Button(self.fr_acciones, text="Aceptar", command=self.modificar_carta_aceptado).grid(
            row=21, column=4, columnspan=2, padx=10, pady=4, ipadx=10, ipady=2, sticky="W")

        # Variable para indicar si debe cargar la interfaz, una vez que la carga la pasamos a False
        self.d_stv["stv12"].set(False)

    def modificar_carta_aceptado(self):
        """Método que se ejecuta al aceptar los cambios en una Carta. Muestra mensajes de completado o de error. Llama
            a la función que graba en la DB"""

        # Chequeamos que se hayan ingresado nuevos valores y una imagen nueva o pedido de quitar la existente
        if ((not self.d_stv["stv2"].get() and not self.d_stv["stv3"].get() and not self.d_stv["stv4"].get() and
            not self.d_stv["stv5"].get()) and
            ((self.d_stv["stv7"].get() == "quitar imagen" and self.d_stv["stv11"].get() != "con imagen DB") or
             (self.d_stv["stv7"].get() != "quitar imagen" and self.d_stv["stv10"].get() == "sin imagen"))):

            self.etiqueta_acciones.config(text="No hay cambios que realizar", style="cursiva_red.TLabel")

        else:
            # Chequeamos si se desea quitar la imagen existente en la DB
            if self.d_stv["stv7"].get() == "quitar imagen":
                imagen_para_db = "Borrar"

            # En caso de que no quieran quitar la imagen, llamamos a una función que devuelve una imagen o un None
            else:
                imagen_para_db = funciones.check_imagen_cambiada(switch=self.d_stv["stv10"].get(), imagen=self.imagen)

            # Función que modifica la DB con los nuevos datos
            rtdo_modif = funciones.modificar_carta_db(carta_id=int(self.d_lbl["lbl1"].cget("text")),
                                                      carta_id_game_nvo=self.d_stv["stv3"].get(),
                                                      carta_nivel_nvo=self.d_stv["stv4"].get(),
                                                      carta_nombre_nvo=self.d_stv["stv2"].get(),
                                                      carta_grupo_nvo=self.d_stv["stv5"].get(),
                                                      carta_img_nva=imagen_para_db)

            # Mostramos el resultado de la modificación realizada
            self.etiqueta_acciones.configure(text=rtdo_modif, style="cursiva_green.TLabel")
            if rtdo_modif[0] == "E":
                self.etiqueta_acciones.configure(style="cursiva_red.TLabel")

            self.borrar_variables()

#-----------------------------------------------------------------------------------------------------------------------
    def eliminar_carta(self):
        """Método que carga la interfaz en el Frame Acciones para Eliminar una Carta de la DB"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Eliminando Cartas", alto_filas=2)
        self.fr_acciones.grid_columnconfigure(0, minsize=282)  # Para formato

        # TITULO
        ttk.Label(self.fr_acciones, text="Elimina cartas existentes en D.B.:", style="tit_bold.TLabel",
                  justify="right").grid(row=1, column=0, padx=10, pady=(0, 12), sticky="E")

        # Nombre de la acción a realizar
        ttk.Label(self.fr_acciones, text="Texto a buscar en una Carta:").grid(
            row=2, column=0, padx=(10, 5), pady=(0, 6), sticky="E")

        # Entry para texto a buscar en el nombre de la carta
        self.d_ent["ent0"].config(width=18, font=("Segoe UI", 9), justify="center", textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=2, column=1, padx=6, pady=(0, 6))
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", self.buscar_eliminar_carta)

        # BOTÓN BUSCAR
        ttk.Button(self.fr_acciones, text="Buscar", command=self.buscar_eliminar_carta, width=7).grid(
            row=2, column=2, padx=(4, 2), pady=(2, 6), sticky="W")

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=2, column=3, padx=(2, 4), pady=(2, 6), sticky="W")

    def buscar_eliminar_carta(self, *args):
        """Método que se ejecuta al Buscar una Carta que se quiere Eliminar. Colocará los widgets en pantalla con
        los valores de la Carta y/o mostrará errores"""

        # Cargamos la misma tabla que se usa en -consultar cartas- adaptando la cantidad de filas mostradas
        self.consultar_carta_ingresado()
        self.treeview.config(height=6)

        # Agregamos un evento para que con cada clic se verifique si hay algún elemento seleccionado
        self.treeview.bind("<ButtonRelease-1>", self.verificar_cantidad)

        # Al haber al menos un elemento seleccionado se habilitará el botón -Eliminar- que es el que iniciará la acción
        self.d_btn["btn0"].config(text="Eliminar", command=lambda: self.eliminar_carta_aceptado(tipo="carta_db"),
                                  state="disabled")
        self.d_btn["btn0"].grid(row=5, column=2, columnspan=2, padx=(2, 4), pady=6, sticky="E")

    def verificar_cantidad(self, evento):
        """Método para chequear si hay elementos seleccionados en el Treeview y activar/desactivar un botón cuando
        ello suceda"""

        # Tomamos la selección del Treeview
        seleccionados = self.treeview.selection()

        # Si hay al menos un elemento, habilitamos el botón -Eliminar-, caso contrario lo desactivamos
        if len(seleccionados) > 0:
            self.d_btn["btn0"].config(state="active")
        else:
            self.d_btn["btn0"].config(state="disabled")

    def eliminar_carta_aceptado(self, tipo):
        """Método que se ejecuta cuando se da clic a Eliminar Carta. Llama a la función que ejecuta los cambios en la
        DB y muestra mensajes del resultado"""

        # La eliminación se manejará de acuerdo a la lista de los seleccionados, empezamos definiéndola vacía
        rtdo_eliminar = []

        # Recorremos toda la selección para que por cada item hacer el pedido de eliminación a la DB
        for carta in self.treeview.selection():

            cada_seleccion = self.treeview.item(carta)  # Nos devuelve el código del Treeview del 1er seleccionado

            carta_id = cada_seleccion["values"][0]  # Sacamos el ID, que está en la primera columna de valores

            if tipo == "carta_db":
                # Llamamos la función para eliminar la carta en la DB y creamos lista de resultados
                rtdo_individual = funciones.eliminar_carta_db(carta_eliminar_id=carta_id)
                rtdo_eliminar.append(rtdo_individual)

            elif tipo == "carta_usuario":
                # Llamamos la función para eliminar la carta en la DB y creamos lista de resultados
                rtdo_individual = funciones.dar_de_baja_carta_usuario_db(
                    nombre_usuario=self.etiq_usuario_logueado.cget("text"), id_card=carta_id)
                rtdo_eliminar.append(rtdo_individual)

            else:
                rtdo_individual = None

            # Los que van siendo eliminados correctamente se borran del Treeview
            try:
                if rtdo_individual[0] == "C":
                    self.treeview.delete(carta)
            except:
                pass

        # En caso de borrado correcto, devuelve un "Carta eliminada..." en cada elemento de la lista
        mensaje = "El borrado ha sido exitoso"
        self.etiqueta_acciones.config(style="cursiva_green.TLabel")

        for resultado in rtdo_eliminar:
            if resultado[0] != "C":
                mensaje = "Ha ocurrido un error en el borrado de al menos una de las cartas"
                self.etiqueta_acciones.config(style="cursiva_red.TLabel")

        self.etiqueta_acciones.config(text=mensaje)

#-----------------------------------------------------------------------------------------------------------------------
    def consultar_carta(self):
        """Método que carga la interfaz en el Frame Acciones para buscar una Carta que se quiere consultar"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Consultando Cartas", alto_filas=2)
        self.fr_acciones.grid_columnconfigure(0, minsize=282)

        # TITULO
        ttk.Label(self.fr_acciones, text="Consulta las cartas existentes en D.B.:", style="tit_bold.TLabel",
                  justify="right").grid(row=1, column=0, padx=10, pady=(0, 12), sticky="E")

        # Nombre de la acción a realizar
        ttk.Label(self.fr_acciones, text="Texto a buscar en una Carta:").grid(
            row=2, column=0, padx=(10, 5), pady=(0, 6), sticky="E")

        # Entry para texto a buscar en el nombre de la carta
        self.d_ent["ent0"].config(width=18, font=("Segoe UI", 9), justify="center", textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=2, column=1, padx=6, pady=(0, 6))
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", self.consultar_carta_ingresado)

        # BOTÓN BUSCAR
        ttk.Button(self.fr_acciones, text="Buscar", command=self.consultar_carta_ingresado, width=7).grid(
            row=2, column=2, padx=(4, 2), pady=(2, 6), sticky="W")

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=2, column=3, padx=(2, 4), pady=(2, 6), sticky="W")

    def consultar_carta_ingresado(self, *args):
        """Método que muestra en pantalla en un Treeview un listado de las Cartas existentes en la DB de ese id_game"""

        self.etiqueta_acciones.configure(text="")  # Borramos mensaje por si había de antes

        for item in self.treeview.get_children():  # Elimina los datos del treeview por si hay una consulta anterior
            self.treeview.delete(item)

        if self.d_stv["stv0"].get() == "":  # Se pueden buscar los que tengan "Null" en la DB
            texto_a_buscar = "Nulls"
            lista_de_cartas = funciones.carta_datos_db(nombre_card=texto_a_buscar, todos=True)

        elif self.d_stv["stv0"].get().isnumeric():
            lista_de_cartas = funciones.carta_datos_db(id_game_card=self.d_stv["stv0"].get(), todos=True)

        else:
            texto_a_buscar = self.d_stv["stv0"].get()
            # Llamamos a la función que busca en la DB las cartas
            lista_de_cartas = funciones.carta_datos_db(nombre_card=texto_a_buscar, todos=True)

        if not lista_de_cartas:
            self.etiqueta_acciones.config(text="No se han encontrado Cartas en la Base de Datos",
                                          style="cursiva_red.TLabel")

        else:
            # Tamaño del Frame ajustado a la acción
            self.fr_acciones.grid_configure(rowspan=4)

            # Borramos el contenido de la etiqueta, por si había algún mensaje de error anterior
            self.etiqueta_acciones.config(text="")

            # TITULO
            ttk.Label(self.fr_acciones, text="Resultado de la consulta:", style="tit_bold.TLabel",
                      justify="right").grid(row=3, column=0, columnspan=2, padx=10, pady=(8, 4), sticky="W")

            # Configuramos el Treeview
            nombres_col = ["ID Carta", "ID Game", "Nivel", "Nombre Carta", "Grupo", "Imagen"]
            anchos_col = [54, 54, 54, 190, 90, 70]  # Las últimas corresponden a -#0-

            # Llamamos a la función que lo crea
            self.configurar_treeview(columnas=5, nombres=nombres_col, anchos=anchos_col)

            # Lo colocamos en la posición deseada
            self.treeview.grid(row=4, column=0, columnspan=4, padx=(10, 0), pady=8, sticky="EW")
            self.treeview.column("#0", anchor="w")
            self.treeview.column("3", anchor="w")

            # SCROLL de la Tabla
            self.scrollbar.grid(row=4, column=4, padx=0, pady=8, sticky="NSE")

            # Cargamos el Treeview con los datos
            self.cargar_treeview(tipo_datos="carta", lista_datos_db=lista_de_cartas)

            # Posicionamos la vista en la primera fila
            self.treeview.see(self.treeview.get_children()[0])

            # Borramos el entry con el texto que se buscó y dejamos el cursor allí por si se quiere buscar otro
            self.d_stv["stv0"].set("")
            self.d_ent["ent0"].focus()

#-----------------------------------------------------------------------------------------------------------------------
#                                      REGLAS
#-----------------------------------------------------------------------------------------------------------------------
    def crear_nueva_regla(self):
        """Método que carga la interfaz en el Frame Acciones para crear una Nueva Regla en la DB"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Creando Nueva Regla", alto_filas=3)
        #self.fr_acciones.grid_columnconfigure(0, minsize=282)

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Crear una Nueva Regla en la Base de Datos", style="tit_bold.TLabel").grid(
            row=1, column=0, padx=(10, 15), pady=(0, 6), sticky="W")

        # Etiqueta y Entry NOMBRE REGLA
        ttk.Label(self.fr_acciones, text="Ingrese el nombre de la regla tal como está en el juego (*):").grid(
            row=2, column=0, padx=10, pady=(10, 3), sticky="W")
        self.d_ent["ent0"].grid(row=3, column=0, padx=10, pady=(4, 8), sticky="W")
        self.d_ent["ent0"].config(width=40, textvariable=self.d_stv["stv0"], font=("Segoe UI", 10))
        self.d_ent["ent0"].focus()

        # Etiqueta y Entry DESCRIPCIÓN REGLA
        ttk.Label(self.fr_acciones, text="Ingrese la descripción de la regla:").grid(
            row=4, column=0, padx=10, pady=(8, 2), sticky="W")
        ttk.Entry(self.fr_acciones, font=("Segoe UI", 10), width=56, textvariable=self.d_stv["stv1"]).grid(
            row=5, column=0, columnspan=2, padx=10, pady=(4, 8), sticky="W")

        # Etiqueta y Entry Ruta IMAGEN REGLA
        ttk.Label(self.fr_acciones,
                  text="Ingrese la ruta completa con nombre y extensión de la imagen de la regla:").grid(
            row=6, column=0, columnspan=2, padx=10, pady=(8, 2), sticky="W")
        ttk.Entry(self.fr_acciones, font=("Segoe UI", 10), width=45, textvariable=self.d_stv["stv2"]).grid(
            row=7, column=0, columnspan=2, padx=(10, 0), pady=(4, 2), sticky="W")

        # Botón para IMAGEN
        ttk.Button(self.fr_acciones, text="Buscar", command=lambda: funciones.seleccionar_archivo(self.d_stv["stv2"]),
                   width=10).grid(row=7, column=1, padx=2, pady=(4, 2))
        ttk.Button(self.fr_acciones, text="Cargar", command=lambda: self.cargar_imagen(
            ruta_imagen=self.d_stv["stv2"].get(), nombre_carta=">regla<", alto_img=80), width=10).grid(
            row=8, column=1, padx=2, pady=(4, 2))
        ttk.Button(self.fr_acciones, text="Quitar", command=lambda: self.cargar_imagen(
            ruta_imagen="imagenes/sin_imagen.png", alto_img=80), width=10).grid(
            row=9, column=1, padx=2, pady=(4, 8))

        # CANVAS para la IMAGEN
        self.canvas.grid(row=7, column=2, rowspan=3, padx=2, pady=(4, 8), sticky="N")

        # Detalle de lo obligatorio, ya que se puede crear sin completar todas las casillas
        ttk.Label(self.fr_acciones, text="(*) campos obligatorios para crear la regla", justify="left",
                  font=("Segoe UI", 7)).grid(row=9, column=0, padx=8, pady=(4, 8), sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=10, column=0, padx=15, pady=(20, 5), ipadx=5, ipady=2, sticky="E")

        ttk.Button(self.fr_acciones, text="Aceptar", command=self.nueva_regla_aceptado).grid(
            row=10, column=1, padx=0, pady=(20, 5), ipadx=5, ipady=2, sticky="W")

        # Carga de imagen inicial
        self.cargar_imagen(ruta_imagen="imagenes/sin_imagen.png", alto_img=80)  # ilustración -sin imagen-

    def nueva_regla_aceptado(self):
        """Método que se ejecuta una vez que se acepta la creación de una Nueva Regla. Controla los campos y llama
            a la función que graba en la DB. Da mensajes del resultado"""

        # Borramos el contenido del mensaje, por si hay algún error anterior
        self.etiqueta_acciones.configure(text="")

        # Verificamos que se hayan completado los campos mínimos necesarios
        if not self.d_stv["stv0"].get():
            self.etiqueta_acciones.configure(text="El nombre no puede estar vacío", style="cursiva_red.TLabel")

        else:
            # Llamamos función para saber si hay imagen nueva que se desee grabar en la DB
            imagen_para_db = funciones.check_imagen_cambiada(switch=self.d_stv["stv10"].get(), imagen=self.imagen)

            # Llamado a la función que crea la Regla pasándole todos los valores
            rtdo_creacion = funciones.nueva_regla_db(nombre_regla=self.d_stv["stv0"].get().strip(),
                                                     descrip_regla=self.d_stv["stv1"].get().strip(),
                                                     imagen_regla=imagen_para_db)

            if rtdo_creacion[0] == "R":  # Mensaje y acciones en caso de Creación Correcta
                self.borrar_variables()
                self.cargar_imagen(ruta_imagen="imagenes/sin_imagen.png", alto_img=70)  # Ilustración
                self.etiqueta_acciones.configure(text=rtdo_creacion, style="cursiva_green.TLabel")

            else:  # Mensaje en caso de Error
                self.etiqueta_acciones.configure(text=rtdo_creacion, style="cursiva_red.TLabel")

#-----------------------------------------------------------------------------------------------------------------------
    def modificar_regla(self):
        """Método que carga la interfaz en el Frame Acciones para buscar una Regla que se quiere modificar"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Modificando Reglas", alto_filas=2)

        # TITULO
        self.d_lbl["lbl0"].config(text="Modifica o completa los datos de una regla:", style="tit_bold.TLabel",
                                  justify="right")
        self.d_lbl["lbl0"].grid(row=1, column=0, columnspan=2, padx=(55, 10), pady=(0, 8), sticky="E")

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Ingrese un número de ID de una Regla:").grid(
            row=2, column=0, columnspan=2, padx=(15, 5), pady=(0, 6), sticky="E")

        # Entry para ID REGLA
        self.d_ent["ent0"].config(width=6, font=("Segoe UI", 10), justify="center", textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=2, column=2, padx=10, pady=(0, 6))
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", self.buscar_regla_a_modif)

        # BOTON BUSCAR
        self.d_btn["btn0"].config(text="Buscar", command=self.buscar_regla_a_modif)
        self.d_btn["btn0"].grid(row=2, column=3, padx=(5, 10), pady=(0, 6), sticky="W")

        # Variable para indicar si debe cargar la interfaz cuando se busque, la primera vez debe hacerlo
        self.d_stv["stv12"].set(True)

    def buscar_regla_a_modif(self, *args):  # para que funcione el "bind" apretando Enter en el Entry
        """Método que se ejecuta al Buscar una Regla que se quiere Modificar. Colocará los widgets en pantalla con
            los valores de la Regla y/o mostrará errores"""

        self.etiqueta_acciones.configure(text="")  # Borramos mensaje por si había de antes

        regla_db = None
        msje_error = None
        try:  # Try para evitar errores cuando se ingresan valores no numéricos
            id_regla = int(self.d_stv["stv0"].get().strip())

        except ValueError:
            msje_error = "Error en el ID de la regla ingresado"

        else:
            regla_db = funciones.regla_datos_db(id_regla)  # Función para ir a la DB
            self.d_stv["stv0"].set("")  # Borramos todos los datos completados (de una nva consulta o una anterior)

        if regla_db:  # Si se pudo asignar valor (o sea si había un valor numérico)

            if self.d_stv["stv12"].get():  # Chequeamos si ya está cargada la interfaz
                self.interfaz_modif_regla()

            self.datos_regla_mostrar(regla=regla_db)  # Llamamos a un método que carga los datos de la DB

            # Carga de ilustración -sin imagen- cuando se abre por primera vez la acción (en el canvas)
            self.cargar_imagen(ruta_imagen="imagenes/sin_imagen.png", alto_img=70)

        else:
            # Mensaje de error cuando la carta no es encontrada en la DB
            self.etiqueta_acciones.config(style="cursiva_red.TLabel")
            if not msje_error:
                self.etiqueta_acciones.config(text="La regla ingresada no existe en la Base de Datos")
            else:
                self.etiqueta_acciones.config(text=msje_error)

        self.d_ent["ent0"].focus()

    def interfaz_modif_regla(self):
        """Método para cargar los widgets en el frame acciones cuando se ha buscado una regla a modificar en la DB"""

        self.fr_acciones.grid_configure(rowspan=4)

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=3, column=0, columnspan=4, sticky="ew", padx=(15, 0), pady=(4, 0))

        # ID DE LA REGLA
        ttk.Label(self.fr_acciones, text="ID de la regla B.D.", style="cursiva.TLabel").grid(
            row=4, column=0, padx=10, pady=(8, 6), sticky="E")
        self.d_lbl["lbl1"].config(style="cursiva.TLabel")
        self.d_lbl["lbl1"].grid(row=4, column=1, padx=10, pady=(8, 6), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=5, column=0, columnspan=5, sticky="ew", padx=(15, 0))

        # NOMBRE DE LA REGLA
        ttk.Label(self.fr_acciones, text="Nombre de la regla B.D.", style="cursiva.TLabel").grid(
            row=6, column=0, padx=10, pady=(8, 4), sticky="E")
        self.d_lbl["lbl2"].config(wraplength=120, style="cursiva.TLabel")
        self.d_lbl["lbl2"].grid(row=6, column=1, columnspan=2, padx=10, pady=(8, 4), sticky="W")
        ttk.Label(self.fr_acciones, text="Nombre regla nuevo").grid(
            row=7, column=0, padx=10, pady=(2, 6), sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv1"], font=("Segoe UI", 9), width=32).grid(
            row=7, column=1, columnspan=3, padx=(8, 10), pady=(2, 6), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=8, column=0, columnspan=5, sticky="ew", padx=(15, 0))

        # DESCRIPCIÓN DE LA REGLA
        ttk.Label(self.fr_acciones, text="Descripción regla B.D.", style="cursiva.TLabel").grid(
            row=9, column=0, padx=10, pady=(10, 4), sticky="E")
        self.d_lbl["lbl3"].config(wraplength=310, style="cursiva.TLabel")
        self.d_lbl["lbl3"].grid(row=9, column=1, columnspan=4, padx=10, pady=(10, 4), sticky="W")
        ttk.Label(self.fr_acciones, text="Descripción regla nueva").grid(
            row=10, column=0, padx=(25, 10), pady=(2, 6), sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv2"], font=("Segoe UI", 9), width=50).grid(
            row=10, column=1, columnspan=4, padx=(8, 0), pady=(2, 6), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=11, column=0, columnspan=5, sticky="ew", padx=(15, 0))

        # IMAGEN REGLA
        ttk.Label(self.fr_acciones, text="Imagen regla B.D.", style="cursiva.TLabel").grid(
            row=12, column=0, padx=10, pady=(10, 4), sticky="E")
        self.d_lbl["lbl4"].config(relief="solid")
        self.d_lbl["lbl4"].grid(row=12, column=1, padx=10, pady=(10, 4), sticky="W")
        ttk.Label(self.fr_acciones, text="Ruta imagen nueva").grid(
            row=13, column=0, padx=10, pady=2, sticky="E")
        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv3"], font=("Segoe UI", 9), width=24).grid(
            row=13, column=1, padx=(8, 10), pady=2, sticky="W")
        ttk.Button(self.fr_acciones, text="Archivo", command=lambda: funciones.seleccionar_archivo(
            self.d_stv["stv3"]), width=9).grid(row=13, column=2, padx=1, pady=2, sticky="")
        ttk.Button(self.fr_acciones, text="Cargar", command=lambda: self.cargar_imagen(
            ruta_imagen=self.d_stv["stv3"].get(), alto_img=70), width=9).grid(
            row=13, column=3, padx=1, pady=2, sticky="")
        ttk.Checkbutton(self.fr_acciones, text="Quitar/Sin imagen", variable=self.d_stv["stv4"],
                        onvalue="quitar imagen").grid(row=14, column=2, columnspan=2, padx=2, pady=(2, 6))

        self.canvas.grid(row=12, column=2, columnspan=2, padx=2, pady=(10, 4))

        self.fr_acciones.grid_rowconfigure(9, minsize=44)  # Configuración para la fila de la descripción
        self.fr_acciones.grid_rowconfigure(12, minsize=70)  # Configuración para la fila de la imagen

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=15, column=0, columnspan=5, sticky="ew", padx=(15, 0))

        # Detalle aclaratorio
        ttk.Label(self.fr_acciones, justify="left", font=("Segoe UI", 7),
                  text="Los nuevos datos reemplazarán a los existentes en la Base de Datos").grid(
            row=16, column=0, columnspan=2, padx=(20, 10), pady=4)

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=17, column=1, padx=8, pady=15, ipadx=10, ipady=2, sticky="E")
        ttk.Button(self.fr_acciones, text="Aceptar", command=self.modificar_regla_aceptado).grid(
            row=17, column=2, columnspan=2, padx=8, pady=15, ipadx=10, ipady=2, sticky="W")

        # Variable para indicar si debe cargar la interfaz, una vez que la carga la pasamos a False
        self.d_stv["stv12"].set(False)

    def datos_regla_mostrar(self, regla):

        # Colocamos valores según DB borrando primero valores anteriores
        self.d_lbl["lbl1"].config(text="")
        self.d_lbl["lbl2"].config(text="")
        self.d_lbl["lbl3"].config(text="")
        self.d_lbl["lbl1"].config(text=regla.id_regla)
        self.d_lbl["lbl2"].config(text=regla.nombre)
        self.d_lbl["lbl3"].config(text=regla.descripcion)

        # Colocamos la imagen de la DB o una ilustración
        if regla.imagen:
            imagen_pillow = Image.open(io.BytesIO(regla.imagen))
            self.d_stv["stv11"].set("con imagen DB")  # Switch para saber que hay imagen en la DB
        else:
            imagen_pillow = Image.open(fp="imagenes/Imagen-no-disponible-282x300.png")

        # Llamamos a la función para colocarla en el widget, label en este caso
        funciones.colocar_img_en_widget(imagen_a_colocar=imagen_pillow, widget=self.d_lbl["lbl4"], alto=70)

    def modificar_regla_aceptado(self):
        """Método que se ejecuta al aceptar los cambios en una Regla. Muestra mensajes de completado o de error. Llama
            a la función que graba en la DB"""

        if ((not self.d_stv["stv1"].get() and not self.d_stv["stv2"].get()) and
            ((self.d_stv["stv4"].get() == "quitar imagen" and self.d_stv["stv11"].get() != "con imagen DB") or
             (self.d_stv["stv4"].get() != "quitar imagen" and self.d_stv["stv10"].get() == "sin imagen"))):

            self.etiqueta_acciones.configure(text="No hay cambios que realizar", style="cursiva_red.TLabel")

        else:
            # Chequeamos si se desea quitar la imagen existente en la DB
            if self.d_stv["stv4"].get() == "quitar imagen":
                imagen_para_db = "Borrar"

            else:
                imagen_para_db = funciones.check_imagen_cambiada(switch=self.d_stv["stv10"].get(), imagen=self.imagen)

            rtdo_modif = funciones.modificar_regla_db(id_regla=int(self.d_lbl["lbl1"].cget("text")),
                                                      regla_nombre_nvo=self.d_stv["stv1"].get(),
                                                      regla_descrip_nva=self.d_stv["stv2"].get(),
                                                      regla_imagen_nva=imagen_para_db)

            self.etiqueta_acciones.configure(text=rtdo_modif, style="cursiva_green.TLabel")
            if rtdo_modif[0] == "E":
                self.etiqueta_acciones.configure(style="cursiva_red.TLabel")

            self.borrar_variables()

#-----------------------------------------------------------------------------------------------------------------------
    def eliminar_regla(self):
        """Método que carga la interfaz en el Frame Acciones para Eliminar una Regla de la DB"""

        # Utilizamos la misma interfaz que para modificar regla y adaptamos algunos textos y opciones
        self.modificar_regla()

        self.etiq_mensajes_principal.config(text="Eliminando Reglas")

        self.d_lbl["lbl0"].config(text="Elimina una regla de la Base de Datos:")

        self.d_ent["ent0"].bind("<Return>", self.buscar_eliminar_regla)

        self.d_btn["btn0"].config(command=self.buscar_eliminar_regla)

    def buscar_eliminar_regla(self, *args):
        """Método que se ejecuta al Buscar una Regla que se quiere Eliminar. Colocará los widgets en pantalla con
                los valores de la Regla y/o mostrará errores"""

        self.etiqueta_acciones.configure(text="")  # Borramos mensaje por si había de antes

        regla_db = None
        try:
            id_regla = int(self.d_stv["stv0"].get().strip())

        except ValueError:
            self.etiqueta_acciones.configure(text="Error en el ID de la regla ingresado", style="cursiva_red.TLabel")

        else:
            regla_db = funciones.regla_datos_db(id_regla)  # Función para ir a la DB
            self.d_stv["stv0"].set("")  # Borramos todos los datos completados (de una nva consulta o una anterior)

        if regla_db:

            if self.d_stv["stv12"].get():
                self.interfaz_elim_regla()

            self.datos_regla_mostrar(regla=regla_db)  # Llamamos a un método que carga los datos de la DB

        else:
            self.etiqueta_acciones.configure(text="La regla ingresada no existe en la Base de Datos",
                                             style="cursiva_red.TLabel")

        self.d_ent["ent0"].focus()

    def interfaz_elim_regla(self):
        """Método para cargar los widgets en el frame acciones cuando se ha buscado una regla a eliminar en la DB"""

        self.fr_acciones.grid_configure(rowspan=3)

        ttk.Label(self.fr_acciones, text="ID de la regla:").grid(
            row=3, column=0, padx=10, pady=(10, 6), sticky="E")
        self.d_lbl["lbl1"].grid(row=3, column=1, columnspan=2, padx=10, pady=(10, 6), sticky="W")

        # NOMBRE DE LA REGLA
        ttk.Label(self.fr_acciones, text="Nombre de la regla:").grid(
            row=4, column=0, padx=(25, 10), pady=(8, 6), sticky="E")
        self.d_lbl["lbl2"].grid(row=4, column=1, columnspan=3, padx=10, pady=(8, 6), sticky="W")

        # DESCRIPCIÓN DE LA REGLA
        ttk.Label(self.fr_acciones, text="Descripción regla:").grid(
            row=5, column=0, padx=10, pady=4, sticky="E")
        self.d_lbl["lbl3"].config(wraplength=300)
        self.d_lbl["lbl3"].grid(row=5, column=1, columnspan=5, padx=(10, 0), pady=4, sticky="W")

        # IMAGEN REGLA
        ttk.Label(self.fr_acciones, text="Imagen regla:").grid(row=6, column=0, padx=10, pady=4, sticky="E")
        self.d_lbl["lbl4"].config(relief="solid")
        self.d_lbl["lbl4"].grid(row=6, column=1, padx=10, pady=(8, 6), sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=7, column=0, padx=10, pady=20, ipadx=10, ipady=2, sticky="E")
        ttk.Button(self.fr_acciones, text="Eliminar", command=self.eliminar_regla_aceptado).grid(
            row=7, column=1, padx=10, pady=20, ipadx=10, ipady=2, sticky="W")

        self.fr_acciones.grid_rowconfigure(5, minsize=60)

    def eliminar_regla_aceptado(self):
        """Método que se ejecuta cuando se da clic a Eliminar Regla. Llama a la función que ejecuta los cambios en la
            DB y muestra mensajes del resultado"""

        # Buscamos la regla en la DB
        rtdo_eliminar = funciones.eliminar_regla_db(id_regla=int(self.d_lbl["lbl1"].cget("text")))

        # En caso de que haya realizado el borrado (devuelve un "Regla elim...") y se vuelve a cargar la interfaz
        if rtdo_eliminar[0] == "R":
            self.eliminar_regla()

        # Se muestra el mensaje del resultado. Por defecto en rojo, luego si pudo borrar, entonces se cambia a verde
        self.etiqueta_acciones.config(text=rtdo_eliminar, style="cursiva_red.TLabel")
        if rtdo_eliminar[0] == "R":
            self.etiqueta_acciones.config(style="cursiva_green.TLabel")

#-----------------------------------------------------------------------------------------------------------------------
    def consultar_reglas(self):
        """Método que muestra en pantalla en un Treeview un listado de todas las Reglas existentes en la DB"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Consultando Reglas", alto_filas=4)

        # TITULO
        ttk.Label(self.fr_acciones, text="Reglas existentes en la Base de Datos:", style="tit_bold.TLabel",
                  justify="right").grid(row=1, column=0, padx=10, pady=(0, 12), sticky="E")

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=1, column=1, padx=4, pady=(0, 12), sticky="e")

        # Configuramos el Treeview
        nombres_col = ["ID Regla", "Nombre Regla", "Descripción Regla", "Imagen"]
        anchos_col = [52, 140, 250, 70]  # Las últimas corresponden a -#0-

        # Llamamos a la función que lo crea
        self.configurar_treeview(columnas=3, nombres=nombres_col, anchos=anchos_col)

        # Configuración personalizada de este Treeview
        self.treeview.config(height=8)
        self.treeview.column("#0", anchor="w")
        self.treeview.column("2", anchor="w")

        # Se coloca en el frame
        self.treeview.grid(row=2, column=0, columnspan=2, padx=(10, 0), pady=8, sticky="EW")

        # SCROLL de la Tabla
        self.scrollbar.grid(row=2, column=2, padx=0, pady=8, sticky="NSE")

        # Consulta a la DB de las reglas existentes
        lista_de_reglas = funciones.regla_datos_db(todos=True)

        # Verificamos si se han encontrado reglas en la DB
        if not lista_de_reglas:
            self.etiqueta_acciones.config(text="No se han encontrado Reglas en la Base de Datos",
                                          style="cursiva_red.TLabel")

        else:
            # En caso de encontrar en la DB, llamamos a la función que realiza la carga pasándole esa consulta a la DB
            self.cargar_treeview(tipo_datos="regla", lista_datos_db=lista_de_reglas)

#-----------------------------------------------------------------------------------------------------------------------
#                                      BATALLAS
#-----------------------------------------------------------------------------------------------------------------------
    def batallas_por_fecha(self):
        """Método que carga la interfaz en el Frame Acciones para hacer una Consulta a la DB de Batallas para
            un día en particular"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Consultando Batallas por Fecha...", alto_filas=2)

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Ingrese una fecha para ver batallas de ese día:").grid(
            row=1, column=0, columnspan=2, padx=(10, 8), pady=(0, 6), sticky="W")

        # Variables y widgets para FECHA
        fecha_hoy = datetime.today()
        dia_var = IntVar()
        mes_var = IntVar()
        anyo_var = IntVar()

        Spinbox(self.fr_acciones, from_=1, to=31, width=3, font=("Segoe UI", 10), justify="center", state="readonly",
                textvariable=dia_var).grid(row=1, column=2, padx=2, pady=(0, 6))

        Spinbox(self.fr_acciones, from_=1, to=12, width=3, font=("Segoe UI", 10), justify="center", state="readonly",
                textvariable=mes_var).grid(row=1, column=3, padx=2, pady=(0, 6))

        Spinbox(self.fr_acciones, from_=2023, to=2030, width=5, font=("Segoe UI", 10), justify="center",
                state="readonly", textvariable=anyo_var).grid(row=1, column=4, padx=2, pady=(0, 6))

        dia_var.set(fecha_hoy.day)
        mes_var.set(fecha_hoy.month)
        anyo_var.set(fecha_hoy.year)

        # Botón BUSCAR
        ttk.Button(self.fr_acciones, text="Buscar", command=lambda: self.batallas_por_fecha_aceptado(dia_var.get(),
                   mes_var.get(), anyo_var.get())).grid(row=1, column=5, padx=(6, 2), pady=(0, 6))

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=1, column=6, padx=(2, 0), pady=(0, 6))

    def batallas_por_fecha_aceptado(self, dia, mes, anyo):
        """Método que se ejecuta luego aceptar una Consulta a la DB de Batalla para un día. Requiere los campos de
            la fecha y llamará a la Función de consulta a la DB. Muestra mensajes de error y, si hay batallas,
            llama otras Funciones para mostrar los datos"""

        fecha_dt = datetime(year=anyo, month=mes, day=dia)

        lista_de_batallas = None
        msje_error = "No se han encontrado batallas en la DB para esa fecha"
        try:
            lista_de_batallas = funciones.batalla_datos_db(fecha=fecha_dt, todos=True)

        except ValueError:
            msje_error = "La fecha ingresada no es correcta"

        except Exception as e:
            msje_error = "Ha habido un error en la consulta de batallas"
            print("Error busqueda de batallas en DB:", e)

        if lista_de_batallas:

            self.treeview_batallas(lista_batallas=lista_de_batallas)

        else:
            self.etiqueta_acciones.configure(text=msje_error, style="cursiva_red.TLabel")

    def treeview_batallas(self, lista_batallas):
        """Método que configura el Treeview para mostrar las batallas obtenidas de una consulta a la DB"""

        # Mensaje
        self.etiqueta_acciones.configure(text="Batallas encontradas en la DB", style="cursiva_green.TLabel")

        # Agrandamos el espacio
        self.fr_acciones.grid_configure(rowspan=4)

        # Configuramos el Treeview - Las últimas corresponden a -#0-
        nombres_col = ["ID", "Format", "Type", "Rank", "Mana", "Fire", "Water", "Earth", "Life", "Death", "Dragon",
                       "seed", "fecha", "jugador", "ganada", "regla1", "regla2", "regla3", "carta0", "carta0_lv",
                       "carta1", "carta1_lv", "carta2", "carta2_lv", "carta3", "carta3_lv", "carta4", "carta4_lv",
                       "carta5", "carta5_lv", "carta6", "carta6_lv", ""]
        anchos_col = [20, 30, 30, 14, 14, 25, 25, 25, 25, 25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0]

        # Llamamos a la función para que coloque los widgets para ver los datos
        self.configurar_treeview(columnas=32, nombres=nombres_col, anchos=anchos_col)

        # Configuración personalizada de este Treeview
        self.treeview.config(height=9, show="headings", style="alto_fila_sin_img.Treeview")
        self.treeview["displaycolumns"] = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        self.treeview.bind("<<TreeviewSelect>>", self.seleccion_treeview_batallas)

        # Llamamos a la función que nos dice cuantas filas hay ocupadas
        ult_fila = funciones.obtener_ultima_row(frame=self.fr_acciones)

        # Colocamos el Treeview en posición
        self.treeview.grid(row=ult_fila+1, column=0, columnspan=7, padx=(5, 0), pady=10, sticky="ew")

        # SCROLL de la Tabla
        self.scrollbar.grid(row=ult_fila+1, column=7, padx=0, pady=10, sticky="nsw")

        # Cargamos las label de abajo del Treeview llamando a la función
        self.etiquetas_mostrar_batallas(fila=ult_fila+2)

        # Cargamos los datos en el Treeview
        self.cargar_treeview_batallas(lista_batallas=lista_batallas)

    def etiquetas_mostrar_batallas(self, fila):
        """Método qus se ejecuta si al buscar Batallas en la DB se encuentran resultados. Coloca Labels para datos
            adicionales de las batallas"""

        # Textos base para las etiquetas
        textos_labels = ["Seed: ", "Fecha: ", "Jugador: ", "Ganada: "]

        c = 0  # columna a colocarlo
        f = 2  # fila a colocar el label

        for x in range(4):  # Creamos un bucle para colocar los 4 labels con los textos anteriores
            if x == 2:  # Luego de colocar los 2 primeros labels cambiamos la columna y volvemos atrás la fila
                c = 3
                f = 2 - x

            # Usamos los labels definidos al inicio porque los reutilizaremos para el texto + valor de batalla
            self.d_lbl[f"lbl{x}"].config(text=textos_labels[x])
            self.d_lbl[f"lbl{x}"].grid(row=fila + f + x, column=c, columnspan=c + 3, padx=10, pady=3, sticky="w")

        # Buscamos la última fila con widgets
        ult_fila = funciones.obtener_ultima_row(self.fr_acciones)

        # Creamos los labels con textos fijos
        ttk.Label(self.fr_acciones, text="Reglas", anchor="center").grid(
            row=ult_fila+1, column=0, padx=5, pady=3, sticky="ew")
        ttk.Label(self.fr_acciones, text="Cartas", anchor="center").grid(
            row=ult_fila+1, column=1, columnspan=6, padx=5, pady=3, sticky="ew")

        # Definimos los Frames en los que se colocarán las reglas y las cartas
        self.d_frm["frm0"].grid(row=ult_fila+2, column=0, pady=5)
        self.d_frm["frm1"].grid(row=ult_fila+2, column=1, columnspan=6, pady=5)

    def cargar_treeview_batallas(self, lista_batallas):
        """Método que carga los elementos de una lista de batallas obtenidos de una consulta a la DB en un Treeview."""

        for batalla in lista_batallas:
            self.treeview.insert("", "end", text=batalla.id_batalla,
                                 values=(batalla.id_batalla,
                                         batalla.formato,
                                         batalla.tipo_combate,
                                         batalla.rating_level,
                                         batalla.mana_max,
                                         batalla.mazo_red,
                                         batalla.mazo_blue,
                                         batalla.mazo_green,
                                         batalla.mazo_white,
                                         batalla.mazo_black,
                                         batalla.mazo_gold,
                                         batalla.seed_ingame,
                                         batalla.fecha,
                                         batalla.jugador,
                                         batalla.ganada,
                                         batalla.regla1,
                                         batalla.regla2,
                                         batalla.regla3,
                                         batalla.card0_id, batalla.card0_lv,
                                         batalla.card1_id, batalla.card1_lv,
                                         batalla.card2_id, batalla.card2_lv,
                                         batalla.card3_id, batalla.card3_lv,
                                         batalla.card4_id, batalla.card4_lv,
                                         batalla.card5_id, batalla.card5_lv,
                                         batalla.card6_id, batalla.card6_lv))

    def seleccion_treeview_batallas(self, *args):
        """Método que se activa al hacer clic en un elemento de la Tabla de Resultados de la búsqueda. Actualiza el
            texto de los Label con información adicional sobre la Batalla"""

        # Vaciamos los Frames con reglas y cartas que había de una selección anterior
        try:
            for widget in self.d_frm["frm0"].winfo_children():
                widget.destroy()
            for widget in self.d_frm["frm1"].winfo_children():
                widget.destroy()
        except IndexError:
            pass
        except Exception as e:  # El de arriba no captura el error
            pass

        # Textos base para las etiquetas (al texto anterior, les agregamos los valores de la tabla)
        textos_labels = ["Seed: ", "Fecha: ", "Jugador: ", "Ganada: "]

        # Obtenemos los datos desde el Treeview, será una lista (que continúa más allá de los visibles)
        item_lista = self.treeview.selection()[0]  # Se obtiene el item (formato Tkinter)
        datos_item = self.treeview.item(item_lista, "values")  # Lista de valores a partir del item

        # Creamos un bucle para recorrer los datos. La 'x' es para los valores en label y la 'n' la posición en lista
        n = 11  # Es una constante. Los 10 primeros valores se muestran dentro del Treeview, a partir del 11 tomaremos
        for x in range(14):  # Debe recorrer 4 datos + 3 reglas + 7 cartas

            if n <= 14:  # Desde 'n=11' hasta 'n=14' tendremos "Seed", "Fecha", "Jugador", "Ganada"
                contenido_etiqueta = textos_labels[x] + datos_item[n]
                self.d_lbl[f"lbl{x}"].config(text=contenido_etiqueta)

            elif 15 <= n <= 17:  # Entre 'n=15' y 'n=17' tendremos las reglas

                # Buscamos la regla en la DB para obtener la imagen
                regla_db = funciones.regla_datos_db(nombre_regla=datos_item[n])

                # Llamamos a la función que trata el resultado y coloca en frame de ser posible
                funciones.check_objeto_db_y_colocacion_frame(objeto_db=regla_db,
                                                             frame=self.d_frm["frm0"],
                                                             tipo="regla",
                                                             alto=38)

            else:  # A partir de la 18 son cartas, de las que buscamos su nombre (si hay) en la DB y mostraríamos eso

                if datos_item[n] != "None":
                    # Buscamos la carta en la DB para obtener la imagen
                    carta_db = funciones.carta_datos_db(id_game_card=datos_item[n], nivel_card=datos_item[n + 1])
                    if not carta_db:
                        carta_db = "carta no disponible"
                else:
                    carta_db = None

                # Llamamos a la función que trata el resultado y coloca en frame de ser posible
                funciones.check_objeto_db_y_colocacion_frame(objeto_db=carta_db,
                                                             frame=self.d_frm["frm1"],
                                                             tipo="carta",
                                                             alto=60)

                n += 1  # Volvemos a sumar, queremos que sume de a dos (carta + nivel)

            n += 1

#-----------------------------------------------------------------------------------------------------------------------
    def consultar_batallas_sql(self):
        """Método que carga la interfaz en el Frame Acciones para hacer una Consulta a la DB sobre la Tabla Batallas
                en el que el usuario puede definir una consulta SQL"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Consultando de Forma Personalizada...", alto_filas=2)

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Ingrese una consulta en Formato SQL para hacer a la Base de Datos:").grid(
            row=1, column=0, columnspan=4, padx=(10, 15), pady=(0, 6), sticky="W")

        self.cuadro_texto.config(width=55, height=5, font=("Segoe UI", 10))
        self.cuadro_texto.grid(row=2, column=0, columnspan=5, padx=(8, 4), pady=6)
        self.cuadro_texto.focus()

        ttk.Button(self.fr_acciones, text="Buscar", command=self.consultar_batallas_sql_aceptado).grid(
            row=2, column=5, padx=2, pady=6, sticky="N")

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=2, column=6, padx=(2, 0), pady=6, sticky="N")

    def consultar_batallas_sql_aceptado(self):
        """Método que se ejecuta cuando se da la orden de Buscar mediante una Consulta SQL. Muestra errores, o carga
            una Tabla según corresponde"""

        # Tomamos el texto ingresado como query haciendo un ajuste con los \n (si hay)
        texto_ingresado = self.cuadro_texto.get(1.0, "end").strip()
        texto_query = texto_ingresado.replace("\n", " ")

        # Definimos variables para controlar errores y mensajes
        mensaje = None
        estilo = "cursiva_red.TLabel"
        lista_de_batallas = None

        # Intentamos hacer la consulta a la DB y generamos mensaje en caso de error
        try:
            lista_de_batallas = funciones.consulta_batalla_explicita(query=texto_query)

        except Exception as e:
            mensaje = "Ha ocurrido un error al realizar la consulta a la DB"
            print("Error:", e)

        # Si la consulta dio resultado, mostramos en pantalla las batallas y un mensaje
        if lista_de_batallas:
            mensaje = "Batallas encontradas en la DB para la query SQL"
            estilo = "cursiva_green.TLabel"

            # Llamamos a la función para que coloque los widgets para ver los datos
            self.treeview_batallas(lista_batallas=lista_de_batallas)

            self.treeview.config(height=6)  # Achicamos la cantidad de filas a mostrar porque no hay espacio

        # Cuando la variable 'mensaje' sigue siendo None es porque buscó, no encontró resultado y no paso por except
        elif not mensaje:
            mensaje = "No se han encontrado Batallas en la DB"

        # Mostramos el mensaje en la etiqueta
        self.etiqueta_acciones.configure(text=mensaje, style=estilo)

#-----------------------------------------------------------------------------------------------------------------------
    def eliminar_batalla(self):
        """Método que carga la interfaz en el Frame Acciones cuando se desea eliminar una Batalla de la DB"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Eliminando Batalla...", alto_filas=2)

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Ingrese un número de ID de una Batalla:").grid(
            row=1, column=0, columnspan=2, padx=10, pady=(0, 6), sticky="W")

        # Entry para ID BATALLA
        self.d_ent["ent0"].config(width=7, font=("Segoe UI", 10), justify="center", textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=1, column=2, padx=5, pady=(0, 6))
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", self.buscar_eliminar_batalla)

        # BOTÓN BUSCAR
        ttk.Button(self.fr_acciones, text="Buscar", command=self.buscar_eliminar_batalla).grid(
            row=1, column=3, padx=5, pady=(0, 6))

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=1, column=4, padx=5, pady=(0, 6))

    def buscar_eliminar_batalla(self, *args):
        """Método que busca una Batalla por ID en la pantalla de Eliminar Batalla. Carga los datos de la Batalla, o
            muestra los errores según corresponda"""

        # Definimos variables para controlar errores y mensajes
        mensaje = None
        batalla_db = None

        # Llamamos a la función que consulta a la DB
        try:
            batalla_db = funciones.batalla_datos_db(id_bat=int(self.d_stv["stv0"].get().strip()))
            consulta_db = True

        except Exception as e:
            mensaje = "Error al buscar en la DB"
            consulta_db = False
            self.d_btn["btn0"].config(state="disabled")
            print("Error en DB:", e)

        # Se encuentra batalla: vacía el Entry, agranda el Frame, borra mensaje, habilita Eliminar y muestra datos
        if batalla_db:

            self.d_stv["stv0"].set("")

            self.fr_acciones.grid_configure(rowspan=3)

            mensaje = ""

            self.d_btn["btn0"].config(state="active", text="Eliminar", command=self.eliminar_batalla_aceptado)
            self.d_btn["btn0"].grid(row=1, column=5, padx=5, pady=(0, 6))

            self.etiquetas_compl_mostrar_bat(batalla_db=batalla_db)

        # En caso de que la consulta a la DB se haya hecho y no arroje resultados: MENSAJE y DESHABILITAR botón ELIMINAR
        elif consulta_db:
            mensaje = "La batalla indicada no existe"
            self.d_btn["btn0"].config(state="disabled")

        self.etiqueta_acciones.config(text=mensaje, style="cursiva_red.TLabel")

    def etiquetas_compl_mostrar_bat(self, batalla_db):
        """Este método es el que pone los Label y los datos en ellas de la Batalla que se intenta Eliminar"""

        # Colocamos las etiquetas
        for x in range(25):
            nombre_etiq = f"lbl{x}"
            self.d_lbl[nombre_etiq].grid(row=x + 2, column=0, columnspan=3, padx=(12, 5), pady=3, sticky="W")
            if x > 11:
                self.d_lbl[nombre_etiq].grid(row=x - 10, column=3, columnspan=3, padx=(5, 12), pady=3, sticky="E")

        # Damos más margen superior a las 2 primeras
        self.d_lbl["lbl0"].grid(pady=(8, 3))
        self.d_lbl["lbl12"].grid(pady=(8, 3))

        # Definimos el texto de cada una
        textos_etiq = [f"ID_Batalla: {batalla_db.id_batalla}",
                       f"Formato: {batalla_db.formato}",
                       f"Tipo_Combate: {batalla_db.tipo_combate}",
                       f"Rating: {batalla_db.rating_level}",
                       f"Seed_ingame: {batalla_db.seed_ingame}",
                       f"Fecha: {batalla_db.fecha}",
                       f"Jugador: {batalla_db.jugador}",
                       f"Ganada: {batalla_db.ganada}",
                       f"Mana_max: {batalla_db.mana_max}",
                       f"Regla1: {batalla_db.regla1}",
                       f"Regla2: {batalla_db.regla2}",
                       f"Regla3: {batalla_db.regla3}",
                       f"Mazo_red: {batalla_db.mazo_red}",
                       f"Mazo_blue: {batalla_db.mazo_blue}",
                       f"Mazo_green: {batalla_db.mazo_green}",
                       f"Mazo_white: {batalla_db.mazo_white}",
                       f"Mazo_black: {batalla_db.mazo_black}",
                       f"Mazo_gold: {batalla_db.mazo_gold}",
                       f"Carta ID Game: {batalla_db.card0_id} - Lv: {batalla_db.card0_lv}",
                       f"Carta ID Game: {batalla_db.card1_id} - Lv: {batalla_db.card1_lv}",
                       f"Carta ID Game: {batalla_db.card2_id} - Lv: {batalla_db.card2_lv}",
                       f"Carta ID Game: {batalla_db.card3_id} - Lv: {batalla_db.card3_lv}",
                       f"Carta ID Game: {batalla_db.card4_id} - Lv: {batalla_db.card4_lv}",
                       f"Carta ID Game: {batalla_db.card5_id} - Lv: {batalla_db.card5_lv}",
                       f"Carta ID Game: {batalla_db.card6_id} - Lv: {batalla_db.card6_lv}"]

        # Colocamos el TEXTO en las etiquetas
        for x in range(25):
            nombre_etiq = f"lbl{x}"
            self.d_lbl[nombre_etiq].config(text=textos_etiq[x])

    def eliminar_batalla_aceptado(self):
        """Método que elimina la Batalla de la DB y muestra Mensaje"""

        # Tomamos el Número de Batalla de la etiqueta que lo contiene
        split_id_batalla = self.d_lbl["lbl0"].cget("text").split(":")
        numero_batalla = int(split_id_batalla[1].strip())

        # Llamamos a la Función que ELIMINA y MENSAJE
        try:
            funciones.eliminar_batalla_db(id_batalla_eliminar=numero_batalla)
            self.etiqueta_acciones.config(text=f"La batalla {numero_batalla} ha sido eliminada",
                                          style="cursiva_green.TLabel")
            self.d_btn["btn0"].config(state="disabled")

        except Exception as e:
            self.etiqueta_acciones.config(text="La batalla no pudo ser eliminada", style="cursiva_red.TLabel")
            print("Error al eliminar batalla:", e)

#-----------------------------------------------------------------------------------------------------------------------
#                                      ACCEDER CON USUARIO Y CONTRASEÑA
#-----------------------------------------------------------------------------------------------------------------------
    def acceder_usuario(self):
        """Método que carga la interfaz con todos sus elementos en el Frame de la derecha de la Pantalla Inicial cuando
            se selecciona la acción de Acceder con Usuario y Contraseña"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Accediendo a su perfil con usuario y contraseña", alto_filas=2)

        # TÍTULO
        ttk.Label(self.fr_acciones, text="Ingrese su nombre de usuario y contraseña para acceder",
                  style="tit_bold.TLabel").grid(row=1, column=0, padx=10, pady=(0, 6), sticky="W")

        # NOMBRE USUARIO
        ttk.Label(self.fr_acciones, text="Ingrese el nombre de usuario:").grid(
            row=2, column=0, padx=10, pady=(5, 1), sticky="W")

        self.d_ent["ent0"].config(textvariable=self.d_stv["stv0"], font=("Segoe UI", 10))
        self.d_ent["ent0"].grid(row=3, column=0, padx=60, pady=(2, 4), sticky="W")
        self.d_ent["ent0"].focus()

        # CONTRASEÑA
        ttk.Label(self.fr_acciones, text="Ingrese su contraseña:").grid(
            row=4, column=0, padx=10, pady=(5, 1), sticky="W")

        self.d_ent["ent1"].config(textvariable=self.d_stv["stv1"], show="*", font=("Segoe UI", 10))
        self.d_ent["ent1"].grid(row=5, column=0, padx=60, pady=(2, 10), sticky="W")
        self.d_ent["ent1"].bind("<Return>", self.control_campos_acced_usu)

        # Botones CANCELAR e INGRESAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=6, column=0, padx=10, pady=10, ipadx=10, ipady=2, sticky="E")

        self.d_btn["btn0"].config(text="Ingresar", command=self.control_campos_acced_usu)
        self.d_btn["btn0"].grid(row=6, column=1, padx=10, pady=10, ipadx=10, ipady=2, sticky="W")

    def control_campos_acced_usu(self, *args):
        """Método que se ejecuta cuando se acepta en la pantalla para hacer un login. Se hacen controles sobre los
            campos para controlar que todop esté completado y no haya errores así evitar que los datos se graben en la
            DB con parámetros no aceptables."""

        # Borramos el contenido del mensaje, por si hay algún error anterior
        self.etiqueta_acciones.configure(text="")

        # Verificamos que se hayan completado los campos mínimos necesarios
        if not self.d_stv["stv0"].get() or not self.d_stv["stv1"].get():
            rtdo_login = "Los campos usuario y contraseña son obligatorios"

        else:
            # Chequeamos el largo del usuario
            if len(self.d_stv["stv0"].get()) < 3:
                rtdo_login = "El nombre de usuario debe tener más de 2 caracteres"

            # Controlamos la cantidad de caracteres de la contraseña
            elif len(self.d_stv["stv1"].get()) < 8 or len(self.d_stv["stv1"].get()) > 20:
                rtdo_login = "Su contraseña debe tener entre 8 y 20 caracteres"

            else:
                rtdo_login = funciones.acceder_usuario_db(usuario=self.d_stv["stv0"].get().strip(),
                                                          contras_usuario=self.d_stv["stv1"].get())

        # Mensaje a mostrar de acuerdo a las partes del código que se ejecutaron
        self.etiqueta_acciones.config(text=rtdo_login, style="cursiva_red.TLabel")

        # En casos de acceso exitoso llamamos al método que ejecuta las acciones de login
        if rtdo_login[:2] == "ok":
            self.acceso_usu_correcto(rtdo_login)

    def acceso_usu_correcto(self, rtdo_login):
        """Método que concentra las acciones y mensajes cuando el acceso con Usuario y Contraseña es correcto"""

        # Deshabilitamos el boton Ingresar para que no se pueda loguear otra vez
        self.d_btn["btn0"].config(state="disabled")

        # En Acceso Usuarios ponemos en nombre del usuario logueado
        self.texto_etiqueta_login(texto=self.d_stv["stv0"].get().upper(), estilo="green.TLabel")
        self.etiqueta_acciones.config(text="Contraseña correcta", style="cursiva_green.TLabel")

        # Habilitamos los botones que dependen de un usuario
        for x in range(8):
            self.dic_fun_usu[f"boton{x}"].config(state="active")

        # Deshabilitamos el boton de loguearse y habilitamos el de desloguearse
        self.dic_acc_usu["boton0"].config(state="disabled")
        self.dic_acc_usu["boton1"].config(state="active")

        # Si el usuario no tiene los datos de la cuenta completos, el resultado habrá sido 'ok'
        if "ok" in rtdo_login:
            self.etiqueta_acciones.configure(text="Acceso correcto", style="cursiva_green.TLabel")

            if "ok con cuenta game" in rtdo_login:
                self.cadena_seg = bytearray(self.d_stv["stv1"].get(), 'utf-8')
            else:
                self.dic_fun_usu["boton6"].config(state="disabled")

            # Se termina borrando los campos del formulario
            self.d_ent["ent0"].delete(0, "end")
            self.d_ent["ent1"].delete(0, "end")

#-----------------------------------------------------------------------------------------------------------------------
#                                      DESLOGUEARSE
#-----------------------------------------------------------------------------------------------------------------------
    def desloguear(self):
        """Método que carga la interfaz con todos sus elementos en el Frame de la derecha de la Pantalla Inicial cuando
            se selecciona la acción de Acceder con Usuario y Contraseña"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Cerrando su cesión activa", alto_filas=2)

        # Leyenda para mensaje de confirmación
        texto = "Confirma que desea cerrar su cesión: {}?".format(self.etiq_usuario_logueado.cget("text"))
        ttk.Label(self.fr_acciones, text=texto, style="tit_bold.TLabel").grid(
            row=1, column=0, padx=10, pady=(0, 6), sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=12, column=0, padx=10, pady=(20, 5), ipadx=10, ipady=2, sticky="E")

        self.d_btn["btn0"].config(text="Aceptar", command=self.desloguear_aceptado)
        self.d_btn["btn0"].grid(row=12, column=1, padx=10, pady=(20, 5), ipadx=10, ipady=2, sticky="W")

    def desloguear_aceptado(self):
        """Método que se ejecuta cuando se acepta en la pantalla para cerrar cesión. Se actualizan los estados de
            habilitados/deshabilitados de los botones correspondientes."""

        # Salimos de la interfaz de cierre de sesión
        self.elementos_como_inicio()

        # Mostramos mensaje de deslogueado
        self.etiqueta_acciones.configure(text="Cierre de cesión exitoso", style="cursiva_green.TLabel")

        # Cambiamos la etiqueta del status de logueado llamando a la función que lo hace
        self.texto_etiqueta_login(texto="No se ha logueado", estilo="red.TLabel")

        # Deshabilitamos los botones que dependen de un usuario
        for x in range(8):
            self.dic_fun_usu[f"boton{x}"].config(state="disabled")

        # Habilitamos el boton de loguearse y deshabilitamos el de desloguearse
        self.dic_acc_usu["boton0"].config(state="active")
        self.dic_acc_usu["boton1"].config(state="disabled")

        if self.cadena_seg:  # Borramos la cadena guardada temporalmente en esta variable de forma segura
            for i in range(len(self.cadena_seg)):
                self.cadena_seg[i] = 0

#-----------------------------------------------------------------------------------------------------------------------
#                                      USUARIOS: -NUEVOS, MODIFICACIONES, ELIMINACIÓN-
#-----------------------------------------------------------------------------------------------------------------------
    def nuevo_usuario(self):
        """Método que carga la interfaz con todos sus elementos en el Frame de la derecha de la Pantalla Inicial cuando
                se selecciona la acción de Crear Nuevo Usuario"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Creando Nuevo Usuario", alto_filas=3)

        # Elementos que refieren a la cuenta en el programa (subtitulo + 3 cuadros de entrada con sus label)
        ttk.Label(self.fr_acciones, text="Cuenta en el Software de Gestión de Batallas", style="tit_bold.TLabel").grid(
            row=1, column=0, padx=10, pady=(0, 6), sticky="W")

        ttk.Label(self.fr_acciones, text="Ingrese el nombre de usuario (mínimo 3 caracteres) (*):").grid(
            row=2, column=0, padx=10, pady=(5, 1), sticky="W")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv0"], font=("Segoe UI", 10)).grid(
            row=3, column=0, padx=12, pady=(2, 4), sticky="W")

        ttk.Label(self.fr_acciones, text="Ingrese su contraseña (8-20 caracteres) (*):").grid(
            row=4, column=0, padx=10, pady=(5, 1), sticky="W")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv1"], show="*", font=("Segoe UI", 10)).grid(
            row=5, column=0, padx=12, pady=(2, 4), sticky="W")

        ttk.Label(self.fr_acciones, text="Confirme su contraseña (*):").grid(
            row=4, column=1, padx=(0, 10), pady=(5, 1), sticky="W")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv2"], show="*", font=("Segoe UI", 10)).grid(
            row=5, column=1, padx=(2, 10), pady=(2, 4), sticky="W")

        # Elementos que refieren a la cuenta en el juego splinterlands (subtitulo + 3 cuadros de entrada con sus label)
        ttk.Label(self.fr_acciones, text="Cuenta con la que juega en Splinterlands", style="tit_bold.TLabel").grid(
            row=6, column=0, padx=10, pady=(18, 6), sticky="W")

        ttk.Label(self.fr_acciones, text="Ingrese el e-mail de su usuario en el juego:").grid(
            row=7, column=0, padx=10, pady=(5, 1), sticky="W")

        ttk.Entry(self.fr_acciones, width=25, textvariable=self.d_stv["stv3"], font=("Segoe UI", 10)).grid(
            row=8, column=0, padx=12, pady=(2, 4), sticky="W")

        ttk.Label(self.fr_acciones, text="Ingrese su contraseña para acceder en el juego:").grid(
            row=9, column=0, padx=10, pady=(5, 1), sticky="W")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv4"], show="*", font=("Segoe UI", 10)).grid(
            row=10, column=0, padx=12, pady=(2, 4), sticky="W")

        ttk.Label(self.fr_acciones, text="Confirme su contraseña del juego:").grid(
            row=9, column=1, padx=(0, 10), pady=(5, 1), sticky="W")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv5"], show="*", font=("Segoe UI", 10)).grid(
            row=10, column=1, padx=(2, 10), pady=(2, 4), sticky="W")

        # Detalle de lo obligatorio, ya que se puede crear sin completar todas las casillas
        ttk.Label(self.fr_acciones, text="(*) campos obligatorios para crear la cuenta", justify="left",
                  font=("Segoe UI", 7)).grid(row=11, column=0, padx=10, pady=10, sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=12, column=0, padx=10, pady=5, ipadx=10, ipady=2, sticky="E")

        ttk.Button(self.fr_acciones, text="Aceptar", command=self.nuevo_usuario_aceptado).grid(
            row=12, column=1, padx=10, pady=5, ipadx=10, ipady=2, sticky="W")

    def nuevo_usuario_aceptado(self):
        """Método que se llama al aceptar en la interfaz de creación de usuario. Controla que todos los campos
            necesarios estén completados, que no haya errores al confirmar contraseñas, el formato de email y llama al
            método que accede a la DB cuando tódo está correcto. Muestra mensajes del tipo de error o cuando está
            completada la creación."""

        # Borramos el contenido del mensaje, por si hay algún error anterior
        self.etiqueta_acciones.configure(text="")

        # Variables para el manejo de mensajes y llamados a función correspondientes
        rtdo_nvo_usuario = ""
        rtdo_cuenta_game = ""
        mensaje = ""
        estilo = ""
        check_campos_minimos = False
        check_largo_nombre_usu = False
        check_largo_contras_usu = False
        check_contras_usu_iguales = False
        check_campos_cuenta_game = False
        check_email_game_usu = False
        check_contras_game_iguales = False

        # Verificamos que se hayan completado los campos mínimos necesarios
        if self.d_stv["stv0"].get() and self.d_stv["stv1"].get() and self.d_stv["stv2"].get():
            check_campos_minimos = True

        # Chequeamos el largo del usuario (no menor a 3 caracteres)
        if len(self.d_stv["stv0"].get()) >= 3:
            check_largo_nombre_usu = True

        # Controlamos la cantidad de caracteres de la contraseña (el máximo es solo para poner uno)
        if 8 <= len(self.d_stv["stv1"].get()) <= 20:
            check_largo_contras_usu = True

        # Controlamos que las contraseñas sean iguales
        if self.d_stv["stv1"].get() == self.d_stv["stv2"].get():
            check_contras_usu_iguales = True

        # Vemos si se completaron los datos de la cuenta en el juego (los 3, menos será como si no hubiera nada)
        if self.d_stv["stv3"].get() and self.d_stv["stv4"].get() and self.d_stv["stv5"].get():
            check_campos_cuenta_game = True

        # Revisamos el formato del email
        if "@" in self.d_stv["stv3"].get() and ".com" in self.d_stv["stv3"].get():
            check_email_game_usu = True

        # Chequeamos que las contraseñas del game sean iguales entre sí
        if self.d_stv["stv4"].get() == self.d_stv["stv5"].get():
            check_contras_game_iguales = True

        # Controlamos si se están cumpliendo todas las condiciones
        if (check_campos_minimos and check_largo_nombre_usu and check_largo_contras_usu and check_contras_usu_iguales
                and check_campos_cuenta_game and check_email_game_usu and check_contras_game_iguales):

            # Creamos la cuenta con los datos mínimos. El usuario irá en minúscula y quitando espacios antes y después
            rtdo_nvo_usuario = funciones.nuevo_usuario_db(usuario=self.d_stv["stv0"].get().strip(),
                                                          contras_usuario=self.d_stv["stv1"].get())

            # Hacemos un llamado a modificar el mismo usuario para que le agregue el resto de los datos
            if rtdo_nvo_usuario != "existente" or rtdo_nvo_usuario != "error DB":
                rtdo_cuenta_game = funciones.modificar_usuario_db(nombre_usuario=self.d_stv["stv0"].get().strip(),
                                                                  contras_usuario=self.d_stv["stv1"].get(),
                                                                  usuario_game=self.d_stv["stv3"].get(),
                                                                  contras_game=self.d_stv["stv4"].get())

        # Cuando no se cumplen todas vemos si las que están relacionadas con la cuenta están ok y no hay nada más
        elif (check_campos_minimos and check_largo_nombre_usu and check_largo_contras_usu and check_contras_usu_iguales
              and check_campos_cuenta_game is False):

            # Creamos la cuenta con esos datos porque son los mínimos obligatorios
            rtdo_nvo_usuario = funciones.nuevo_usuario_db(usuario=self.d_stv["stv0"].get().strip(),
                                                          contras_usuario=self.d_stv["stv1"].get())

        # Acá van los errores, los casos por los que no se ejecutó la creación del usuario
        else:
            estilo = "cursiva_red.TLabel"
            if check_campos_minimos is False:
                mensaje = "Los campos usuario, contraseña y confirmar contraseña son obligatorios"

            elif check_largo_nombre_usu is False:
                mensaje = "El nombre de usuario no puede ser de menos de 3 caracteres"

            elif check_largo_contras_usu is False:
                mensaje = "Su contraseña de usuario no puede tener menos de 8 caracteres o más de 20"

            elif check_contras_usu_iguales is False:
                mensaje = "Las contraseñas de usuario ingresadas no coinciden, por favor verifique"

            elif check_email_game_usu is False:
                mensaje = "El formato de e-mail ingresado no es válido, revise"

            elif check_contras_game_iguales is False:
                mensaje = "Las contraseñas de juego ingresadas no coinciden, por favor verifique"

        # Analizamos los resultados de la ejecución sobre la DB para mostrar un mensaje de confirmación o error
        if rtdo_nvo_usuario == "ok" and (rtdo_cuenta_game == "ok" or rtdo_cuenta_game == ""):
            mensaje = f"Usuario -{self.d_stv["stv0"].get()}- creado con éxito"
            estilo = "cursiva_green.TLabel"

        elif rtdo_nvo_usuario == "ok" and rtdo_cuenta_game == "error DB":
            mensaje = (f"Usuario -{self.d_stv["stv0"].get()}- creado con éxito pero no se pudieron grabar\nlos datos "
                       f"de su cuenta en el game")
            estilo = "cursiva_yellow.TLabel"

        elif rtdo_nvo_usuario == "reactivado" and (rtdo_cuenta_game == "ok" or rtdo_cuenta_game == ""):
            mensaje = f"Usuario -{self.d_stv["stv0"].get()}- reactivado con éxito"
            estilo = "cursiva_green.TLabel"

        elif rtdo_nvo_usuario == "reactivado" and rtdo_cuenta_game == "error DB":
            mensaje = (f"Usuario -{self.d_stv["stv0"].get()}- reactivado con éxito pero no se pudieron grabar\nlos "
                       f"datos de su cuenta en el game")
            estilo = "cursiva_yellow.TLabel"

        elif rtdo_nvo_usuario == "existente":
            mensaje = "No se pudo grabar en la Base de Datos, ya existe un usuario con ese nombre"
            estilo = "cursiva_red.TLabel"

        elif rtdo_nvo_usuario == "error DB":
            mensaje = "Ha ocurrido un error al intentar grabar en la Base de Datos"
            estilo = "cursiva_red.TLabel"

        self.etiqueta_acciones.configure(text=mensaje, style=estilo)

        # Borramos en contenido de los Entry
        if rtdo_nvo_usuario == "ok" or rtdo_nvo_usuario == "reactivado":
            self.borrar_variables()

#-----------------------------------------------------------------------------------------------------------------------
    def modificar_usuario(self):
        """Método que carga la interfaz con todos sus elementos en el Frame de la derecha de la Pantalla Inicial cuando
                se selecciona la acción de Modificar Usuario"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Modificando Usuario", alto_filas=3)

        # Llamamos a la función que trae los datos de la DB
        usuario_db = funciones.usuarios_datos_db(nombre_usuario=self.etiq_usuario_logueado.cget("text"))

        # Elementos que refieren a la CUENTA EN NUESTRO PROGRAMA (2 Label + Label y Entry)
        ttk.Label(self.fr_acciones, text="Modifica o completa los datos de\ntu usuario:", style="tit_bold.TLabel",
                  justify="right").grid(row=1, column=0, padx=10, pady=(0, 16), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=(50, 0))

        ttk.Label(self.fr_acciones, text="Nombre de usuario B.D.", style="cursiva.TLabel").grid(
            row=3, column=0, padx=10, pady=(8, 3), sticky="E")

        ttk.Label(self.fr_acciones, text=usuario_db.nombre_de_usuario, style="cursiva.TLabel").grid(
            row=3, column=1, padx=10, pady=(8, 3), sticky="W")

        ttk.Label(self.fr_acciones, text="Nombre usuario nuevo").grid(
            row=4, column=0, padx=10, pady=(3, 10), sticky="E")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv0"], font=("Segoe UI", 9)).grid(
            row=4, column=1, padx=10, pady=(3, 10), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=(50, 0))

        # Elementos que refieren al USUARIO EN EL JUEGO, normalmente un email (2 Label + Label y Entry)
        ttk.Label(self.fr_acciones, text="Usuario juego B.D.", style="cursiva.TLabel").grid(
            row=6, column=0, padx=10, pady=(8, 3), sticky="E")

        ttk.Label(self.fr_acciones, text=usuario_db.usuario_juego, style="cursiva.TLabel").grid(
            row=6, column=1, padx=10, pady=(8, 3), sticky="W")

        ttk.Label(self.fr_acciones, text="Usuario juego nuevo").grid(
            row=7, column=0, padx=10, pady=(3, 10), sticky="E")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv1"], font=("Segoe UI", 9), width=25).grid(
            row=7, column=1, padx=10, pady=(3, 10), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=8, column=0, columnspan=2, sticky="ew", padx=(50, 0))

        # Elementos que refieren a la CONTRASEÑA EN EL JUEGO (2 Label + Label y Entry)
        ttk.Label(self.fr_acciones, text="Contraseña Juego B.D.", style="cursiva.TLabel").grid(
            row=9, column=0, padx=10, pady=(8, 3), sticky="E")

        text_contras = ""
        if usuario_db.contrasenia_juego is not None:
            text_contras = "**********"
        ttk.Label(self.fr_acciones, text=text_contras, style="cursiva.TLabel").grid(
            row=9, column=1, padx=10, pady=(8, 3), sticky="W")

        ttk.Label(self.fr_acciones, text="Contraseña juego nueva").grid(
            row=10, column=0, padx=10, pady=(3, 10), sticky="E")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv2"], font=("Segoe UI", 9), show="*").grid(
            row=10, column=1, padx=10, pady=(3, 10), sticky="W")

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=11, column=0, columnspan=2, sticky="ew", padx=(50, 0))

        # Detalle aclaratorio
        ttk.Label(self.fr_acciones, text="Los nuevos datos reemplazarán a los existentes en la Base de Datos",
                  justify="left", font=("Segoe UI", 7)).grid(row=12, column=0, columnspan=2, padx=(18, 10), pady=(8, 5))

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=13, column=0, padx=10, pady=10, ipadx=10, ipady=2, sticky="E")

        ttk.Button(self.fr_acciones, text="Aceptar", command=self.modificar_usuario_aceptado).grid(
            row=13, column=1, padx=10, pady=10, ipadx=10, ipady=2, sticky="W")

    def modificar_usuario_aceptado(self):
        """Método que se ejecuta al aceptar un cambio en los datos de usuario en Modificar Usuario. Controla que haya
            algún dato a modificar y carga la interfaz para solicitar confirmación con la clave de la cuenta."""

        # Controlamos que se haya cargado información a modificar en alguno de los Entry
        if self.d_stv["stv0"].get() != "" or self.d_stv["stv1"].get() != "" or self.d_stv["stv2"].get() != "":

            # Llamamos al método que agrega los widgets para confirmar con la contraseña
            self.widgets_confirmacion(metodo_ejecutar=self.modificar_usuario_confirmado)

        else:
            # Mensaje en caso de no completar campos
            self.etiqueta_acciones.configure(text="Ingrese algún valor para poder realizar cambios",
                                             style="cursiva_red.TLabel")

    def widgets_confirmacion(self, metodo_ejecutar):
        """Método que agrega los widgets necesarios para pedir confirmación ingresando su contraseña de usuario"""

        ult_fila = funciones.obtener_ultima_row(self.fr_acciones)

        ttk.Separator(self.fr_acciones, orient="horizontal").grid(
            row=ult_fila+1, column=0, columnspan=3, sticky="ew", padx=8, pady=(4, 0))

        # Carga elementos de confirmación: ETIQUETA, ENTRY y BOTÓN
        ttk.Label(self.fr_acciones, text="Ingrese su contraseña para confirmar: ").grid(
            row=ult_fila+2, column=0, padx=10, pady=10, sticky="E")

        self.d_ent["ent0"].config(textvariable=self.d_stv["stv8"], font=("Segoe UI", 9), show="*")
        self.d_ent["ent0"].grid(row=ult_fila+2, column=1, padx=10, pady=10, sticky="W")
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", metodo_ejecutar)

        ttk.Button(self.fr_acciones, text="Confirmar", command=metodo_ejecutar).grid(
            row=ult_fila+2, column=2, padx=10, pady=10, ipady=2, sticky="W")

    def modificar_usuario_confirmado(self, *args):
        """Método que se ejecuta una vez confirmada una Modificación de Usuario. Chequea que la contraseña de
            confirmación sea correcta y llama a la función que modifica la DB"""

        # Traemos los datos del usuario logueado desde la DB
        usuario_db = funciones.usuarios_datos_db(nombre_usuario=self.etiq_usuario_logueado.cget("text"))

        # Controlamos la contraseña
        if funciones.check_hash_contrasenia(cadena=self.d_stv["stv8"].get(), hash_db=usuario_db.contrasenia):

            modif = funciones.modificar_usuario_db(nombre_usuario=usuario_db.nombre_de_usuario,
                                                   contras_usuario=self.d_stv["stv8"].get(),
                                                   usuario_game=self.d_stv["stv1"].get().lower().strip(),
                                                   contras_game=self.d_stv["stv2"].get(),
                                                   usuario_nvo=self.d_stv["stv0"].get().lower().strip())

            if modif == "ok":
                if self.d_stv["stv0"].get() != "":  # Si han modificado el usuario, actualizamos el nombre
                    self.etiq_usuario_logueado.config(text=self.d_stv["stv0"].get().upper())

                # Volvemos a cargar el frame de modificar usuario para que se actualicen los campos
                self.modificar_usuario()

                # Mensaje de completada la modificación
                self.etiqueta_acciones.configure(text="Las modificaciones han sido realizadas con éxito",
                                                 style="cursiva_green.TLabel")

        else:
            # Mensaje en caso de no completar campos
            self.etiqueta_acciones.configure(text="La contraseña ingresada no es correcta", style="cursiva_red.TLabel")

#-----------------------------------------------------------------------------------------------------------------------
    def cambiar_contras_usu(self):
        """Método que carga la interfaz con todos sus elementos en el Frame de la derecha de la Pantalla Inicial cuando
                se selecciona la acción de Cambiar Contraseña"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Modificando Contraseña de Usuario", alto_filas=2)

        # Elementos que refieren al nombre de la cuenta en el programa (2 Label + Label y Entry)
        ttk.Label(self.fr_acciones, text="     Cambia la contraseña de tu usuario:", font=("Segoe UI", 10, "bold"),
                  justify="right").grid(row=1, column=0, padx=10, pady=(0, 12), sticky="W")

        ttk.Label(self.fr_acciones, text="Ingrese su nueva contraseña:").grid(
            row=2, column=0, padx=10, pady=(2, 6), sticky="E")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv0"], font=("Segoe UI", 9), show="*").grid(
            row=2, column=1, padx=10, pady=(2, 6), sticky="W")

        ttk.Label(self.fr_acciones, text="Confirme su nueva contraseña:").grid(
            row=3, column=0, padx=10, pady=4, sticky="E")

        ttk.Entry(self.fr_acciones, textvariable=self.d_stv["stv1"], font=("Segoe UI", 9), show="*").grid(
            row=3, column=1, padx=10, pady=4, sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=4, column=0, padx=10, pady=10, ipadx=10, ipady=2, sticky="E")

        ttk.Button(self.fr_acciones, text="Aceptar", command=self.cambiar_contras_aceptada).grid(
            row=4, column=1, padx=10, pady=10, ipadx=10, ipady=2, sticky="W")

    def cambiar_contras_aceptada(self):
        """Método que se ejecuta al aceptar un cambio en la contraseña de usuario en Cambiar Contraseña. Controla que
            se hayan completado los campos y que la contraseña y su confirmación coincidan. Luego carga la interfaz para
            solicitar confirmación con la clave de la cuenta."""

        # Controlamos que estén completadas ambas contraseñas
        if self.d_stv["stv0"].get() and self.d_stv["stv1"].get():

            # Check de que sean iguales
            if self.d_stv["stv0"].get() == self.d_stv["stv1"].get():

                self.widgets_confirmacion(metodo_ejecutar=self.cambiar_contras_confirmado)

            else:
                self.etiqueta_acciones.configure(text="Error de confirmación de contraseña", style="cursiva_red.TLabel")

        else:
            self.etiqueta_acciones.configure(text="Ingrese su nueva contraseña para realizar el cambio",
                                             style="cursiva_red.TLabel")

    def cambiar_contras_confirmado(self, *args):
        """Método que se ejecuta una vez confirmado un Cambio de Contraseña. Chequea que la contraseña de confirmación
                sea correcta y llama a la función que modifica la DB"""

        # Trae los datos del usuario desde la DB a través de esta función
        usuario_db = funciones.usuarios_datos_db(nombre_usuario=self.etiq_usuario_logueado.cget("text"))

        # Check de contraseña
        if funciones.check_hash_contrasenia(cadena=self.d_stv["stv8"].get(), hash_db=usuario_db.contrasenia):

            # Llamado a la función que accede a la DB para grabar los cambios
            rtdo_cambio = funciones.modificar_usuario_db(nombre_usuario=self.etiq_usuario_logueado.cget("text"),
                                                         contras_usuario=self.d_stv["stv8"].get(),
                                                         contras_nva=self.d_stv["stv0"].get())

            if rtdo_cambio:
                # Llevamos el frame como al inicio
                self.cambiar_contras_usu()

                # Mostramos mensaje en la etiqueta superior
                self.etiqueta_acciones.configure(text="La contraseña ha sido modificada correctamente",
                                                 style="cursiva_green.TLabel")
            else:
                self.etiqueta_acciones.configure(text="El cambio no pudo ser grabado en la DB",
                                                 style="cursiva_red.TLabel")
        else:
            self.etiqueta_acciones.configure(text="La contraseña de confirmación es incorrecta",
                                             style="cursiva_red.TLabel")

#-----------------------------------------------------------------------------------------------------------------------
    def eliminar_usuario(self):
        """Método que carga la interfaz con todos sus elementos en el Frame de la derecha de la Pantalla Inicial cuando
                se selecciona la acción de Eliminar Usuario"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Eliminando Usuario", alto_filas=2)

        # Elementos que refieren al nombre de la cuenta en el programa (2 Label + Label y Entry)
        ttk.Label(self.fr_acciones, text="¿Está seguro de que desea eliminar el usuario?", justify="right",
                  font=("Segoe UI", 10, "bold")).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 12), sticky="W")

        ttk.Label(self.fr_acciones, text="Se borrará su usuario: ").grid(
            row=2, column=0, padx=(140, 10), pady=(2, 4), sticky="E")

        ttk.Label(self.fr_acciones, text=self.etiq_usuario_logueado.cget("text"), font=("Segoe UI", 9)).grid(
            row=2, column=1, padx=10, pady=(2, 4), sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Button(self.fr_acciones, text="Cancelar", command=self.elementos_como_inicio).grid(
            row=3, column=0, padx=10, pady=20, ipadx=10, ipady=2, sticky="E")

        ttk.Button(self.fr_acciones, text="Aceptar", command=lambda: self.widgets_confirmacion(
            self.eliminar_usuario_confirmado)).grid(row=3, column=1, padx=10, pady=20, ipadx=10, ipady=2, sticky="W")

    def eliminar_usuario_confirmado(self, *args):
        """Método que se ejecuta una vez confirmada la Eliminación de Usuario. Chequea que la contraseña de confirmación
                    sea correcta y llama a la función que modifica la DB"""

        # Accedemos a la DB para traer los datos del usuario
        usuario_db = funciones.usuarios_datos_db(nombre_usuario=self.etiq_usuario_logueado.cget("text"))

        # Check contraseña Correcta
        if funciones.check_hash_contrasenia(cadena=self.d_stv["stv8"].get(), hash_db=usuario_db.contrasenia):

            nombre = usuario_db.nombre_de_usuario.upper()
            rtdo_cambio = funciones.eliminar_usuario_db(usuario_db)

            if rtdo_cambio:
                # Llevamos la ventana como al inicio
                self.desloguear_aceptado()
                self.elementos_como_inicio()

                # Mensajes en etiqueta
                self.etiqueta_acciones.configure(text=f"El usuario {nombre} ha sido eliminado",
                                                 style="cursiva_green.TLabel")
            else:
                self.etiqueta_acciones.configure(text="La eliminación no pudo ser grabada en la DB",
                                                 style="cursiva_red.TLabel")
        else:
            self.etiqueta_acciones.configure(text="La contraseña de confirmación es incorrecta",
                                             style="cursiva_red.TLabel")

#-----------------------------------------------------------------------------------------------------------------------
#                                      CARTAS USUARIO
#-----------------------------------------------------------------------------------------------------------------------
    def consultar_cartas_usuario(self):
        """Método que carga la interfaz en el Frame Acciones para mostrar las Cartas del usuario en juego"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Consultando Cartas Usuario", alto_filas=4)

        # TITULO
        ttk.Label(self.fr_acciones, text="Cartas del usuario según la Base de Datos:", style="tit_bold.TLabel",
                  justify="right").grid(row=1, column=0, padx=10, pady=(0, 12), sticky="E")

        # Buscamos en DB todas las cartas del usuario, pero solo tomaremos la del nivel mayor si tiene varias
        listado_cartas = funciones.cartas_usuario_db(usuario=self.etiq_usuario_logueado.cget("text"),
                                                     activa=True,
                                                     todos=True,
                                                     solo_info_cartas=True,
                                                     max_lv=True)

        if not listado_cartas:
            self.etiqueta_acciones.config(text="No se han encontrado Cartas en la Base de Datos",
                                          style="cursiva_red.TLabel")

        else:
            # Llamamos al método que carga los widgets en pantalla
            self.interfaz_ver_y_filtrar_cartas_usu()

            # Colocamos nuestras cartas en el Treeview
            self.cargar_treeview(tipo_datos="carta", lista_datos_db=listado_cartas)

            # Vinculamos el entry a un evento para que automáticamente filtre el listado
            self.d_ent["ent0"].bind("<KeyRelease>", lambda event: self.filtrar_treeview(listado_cartas=listado_cartas))

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=1, column=2, padx=4, pady=(0, 12), sticky="E")

    def interfaz_ver_y_filtrar_cartas_usu(self):
        """Método para cargar un cuadro de texto y un treeview configurado para filtrar y mostrar cartas del usuario"""

        # Label para la acción de filtro
        ttk.Label(self.fr_acciones, text="Filtra por texto de la Carta:").grid(
            row=2, column=0, padx=(15, 5), pady=(0, 6), sticky="E")

        # Entry para ID GAME CARTA
        self.d_ent["ent0"].config(width=12, font=("Segoe UI", 10), justify="center",
                                  textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=2, column=1, padx=6, pady=(0, 6))
        self.d_ent["ent0"].focus()

        # Configuramos el Treeview
        nombres_col = ["ID Carta", "ID Game", "Nivel", "Nombre Carta", "Grupo", "Imagen"]
        anchos_col = [54, 54, 54, 190, 90, 70]  # Las últimas corresponden a -#0-

        # Llamamos a la función que lo crea
        self.configurar_treeview(columnas=5, nombres=nombres_col, anchos=anchos_col)

        # Lo colocamos en la posición deseada
        self.treeview.grid(row=3, column=0, columnspan=3, padx=(10, 0), pady=8, sticky="EW")

        # SCROLL de la Tabla
        self.scrollbar.grid(row=3, column=3, padx=0, pady=8, sticky="NSE")

    def filtrar_treeview(self, listado_cartas, *args):
        """Método para filtrar un Treeview teniendo en cuenta una consulta de cartas previamente realizada a la DB y
        con la que ya se cargó la información en el Treeview. Elimina lo cargado y filtra por un texto indicado en un
        entry según los nombres de las cartas"""

        # Vaciamos el Treeview de los datos anteriores
        for carta in self.treeview.get_children():
            self.treeview.delete(carta)

        # Del entry tomamos el texto que filtraremos y creamos una nueva lista de cartas (son objetos DB)
        texto_buscar = self.d_stv["stv0"].get().lower()
        cartas_filtradas = []
        for item in listado_cartas:
            if texto_buscar in item.nombre.lower():
                cartas_filtradas.append(item)

        # Llamamos a la función para cargar nuevamente el Treeview con la nueva lista de cartas
        self.cargar_treeview(tipo_datos="carta", lista_datos_db=cartas_filtradas)

#-----------------------------------------------------------------------------------------------------------------------
    def cargar_cartas_usuario(self):
        """Método que carga la interfaz en el Frame Acciones para buscar una Carta que se quiere agregar al usuario"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Cargando Cartas al Usuario", alto_filas=2)

        # TITULO
        ttk.Label(self.fr_acciones, text=f"Carga una carta al usuario {self.etiq_usuario_logueado.cget("text")}:",
                  style="tit_bold.TLabel", justify="right").grid(
            row=1, column=0, padx=10, pady=(0, 12), sticky="E")

        # Título para la acción a realizar
        ttk.Label(self.fr_acciones, text="Número de ID Game y nivel de una Carta:").grid(
            row=2, column=0, padx=(15, 5), pady=(0, 6), sticky="E")

        # Entry para ID GAME CARTA
        self.d_ent["ent0"].config(width=6, font=("Segoe UI", 9), justify="center", textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=2, column=1, padx=6, pady=(0, 6), sticky="W")
        self.d_ent["ent0"].focus()
        self.d_ent["ent0"].bind("<Return>", self.buscar_carta_a_cargar_usuario)

        # Entry para NIVEL CARTA
        self.d_ent["ent1"].config(width=4, font=("Segoe UI", 9), justify="center", textvariable=self.d_stv["stv1"])
        self.d_ent["ent1"].grid(row=2, column=2, padx=6, pady=(0, 6), sticky="W")
        self.d_ent["ent1"].bind("<Return>", self.buscar_carta_a_cargar_usuario)

        # BOTON BUSCAR
        ttk.Button(self.fr_acciones, text="Buscar", command=self.buscar_carta_a_cargar_usuario).grid(
            row=2, column=3, padx=5, pady=(2, 6), sticky="W")

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=2, column=4, padx=4, pady=(2, 6), sticky="W")

        # Variable para indicar si debe cargar la interfaz cuando se busque, la primera vez debe hacerlo
        self.d_stv["stv12"].set(True)

    def buscar_carta_a_cargar_usuario(self, *args):
        """Método que se ejecuta al Buscar una Carta que se quiere Cargar a un Usuario. Colocará los widgets en pantalla
            con los valores de la Carta y/o mostrará errores"""

        self.etiqueta_acciones.configure(text="")  # Borramos mensaje por si había de antes

        carta_db = None
        try:  # Try para evitar errores cuando se ingresan valores no numéricos
            id_juego = int(self.d_stv["stv0"].get().strip())
            nivel = int(self.d_stv["stv1"].get().strip())
        except ValueError:
            self.etiqueta_acciones.configure(text="Error en los datos ingresados. No son numéricos",
                                             style="cursiva_red.TLabel")
        else:
            carta_db = funciones.carta_datos_db(id_game_card=id_juego, nivel_card=nivel)
            self.d_stv["stv0"].set("")

        if carta_db:  # Si se pudo asignar valor (o sea si había un valor numérico)

            if self.d_stv["stv12"].get():  # Chequeamos si ya está cargada la interfaz
                self.interfaz_cargar_carta_usuario()

            # Colocamos valores según DB
            self.d_lbl["lbl0"].config(text=carta_db.id_card, style="cursiva.TLabel")
            self.d_lbl["lbl1"].config(text=carta_db.id_game, style="cursiva.TLabel")
            self.d_lbl["lbl2"].config(text=carta_db.nivel, style="cursiva.TLabel")
            self.d_lbl["lbl3"].config(text=carta_db.nombre, style="cursiva.TLabel")
            self.d_lbl["lbl4"].config(text=carta_db.grupo, style="cursiva.TLabel")

            # Definimos la imagen: de la DB o una ilustración de que no está disponible
            if carta_db.imagen:
                imagen_pillow = Image.open(io.BytesIO(carta_db.imagen))
            else:
                imagen_pillow = Image.open(fp="imagenes/Imagen-no-disponible-282x300.png")

            # Llamamos a la función para colocar la imagen en el widget
            funciones.colocar_img_en_widget(imagen_a_colocar=imagen_pillow, widget=self.canvas, alto=140)

        else:
            self.etiqueta_acciones.configure(text="La carta ingresada no existe en la Base de Datos",
                                             style="cursiva_red.TLabel")

        self.d_ent["ent0"].focus()

    def interfaz_cargar_carta_usuario(self):
        """Método para cargar los widgets en el frame acciones cuando se ha buscado una carta a cargar a un usuario
        para luego grabar en la DB"""

        self.fr_acciones.grid_configure(rowspan=4)

        # ID DE LA CARTA
        ttk.Label(self.fr_acciones, text="ID de la carta B.D.").grid(
            row=3, column=0, padx=10, pady=(10, 4), sticky="E")
        self.d_lbl["lbl0"].grid(row=3, column=1, columnspan=3, padx=10, pady=(8, 6), sticky="W")

        # ID GAME
        ttk.Label(self.fr_acciones, text="ID game de la carta B.D.").grid(
            row=4, column=0, padx=10, pady=(10, 4), sticky="E")
        self.d_lbl["lbl1"].grid(row=4, column=1, columnspan=3, padx=10, pady=(8, 6), sticky="W")

        # NIVEL
        ttk.Label(self.fr_acciones, text="Nivel B.D.").grid(
            row=5, column=0, padx=10, pady=(10, 4), sticky="E")
        self.d_lbl["lbl2"].grid(row=5, column=1, columnspan=3, padx=10, pady=(8, 6), sticky="W")

        # NOMBRE DE LA CARTA
        ttk.Label(self.fr_acciones, text="Nombre de la carta B.D.").grid(
            row=6, column=0, padx=10, pady=(10, 4), sticky="E")
        # # self.d_lbl["lbl3"].config(wraplength=120)
        self.d_lbl["lbl3"].grid(row=6, column=1, columnspan=3, padx=10, pady=(10, 4), sticky="W")

        # GRUPO DE LA CARTA
        ttk.Label(self.fr_acciones, text="Grupo carta B.D.").grid(
            row=7, column=0, padx=10, pady=(10, 4), sticky="E")
        self.d_lbl["lbl4"].grid(row=7, column=1, columnspan=3, padx=10, pady=(10, 4), sticky="W")

        # IMAGEN CARTAS (el StringVar de la ruta debe ser el 3 para que se ejecute correctamente la Función)
        ttk.Label(self.fr_acciones, text="Imagen carta B.D.").grid(
            row=8, column=0, padx=10, pady=(10, 4), sticky="E")
        self.canvas.grid(row=8, column=1, columnspan=3, padx=10, pady=(10, 4), sticky="W")

        # Botones CANCELAR y ACEPTAR
        ttk.Label(self.fr_acciones, text="Acepte para agregar la carta al usuario:").grid(
            row=9, column=0, padx=10, pady=20, sticky="E")
        ttk.Button(self.fr_acciones, text="Aceptar", command=self.cargar_carta_usuario_aceptado).grid(
            row=9, column=1, columnspan=4, padx=10, pady=9, ipadx=10, ipady=2, sticky="W")

        # Variable para indicar si debe cargar la interfaz, una vez que la carga la pasamos a False
        self.d_stv["stv12"].set(False)

    def cargar_carta_usuario_aceptado(self):
        """Método que se ejecuta al aceptar Cargar una Carta a un Usuario. Muestra mensajes de completado o de error.
            Llama a la función que graba en la DB"""

        rtdo_carga = funciones.cargar_carta_a_usuario_db(nombre_usuario=self.etiq_usuario_logueado.cget("text").lower(),
                                                         id_carta_db=int(self.d_lbl["lbl0"].cget("text")))

        self.etiqueta_acciones.configure(text=rtdo_carga, style="cursiva_red.TLabel")
        if rtdo_carga[0] == "L":
            self.etiqueta_acciones.configure(style="cursiva_green.TLabel")

        self.d_stv["stv0"].set("")
        self.d_stv["stv1"].set("")

#-----------------------------------------------------------------------------------------------------------------------
    def dar_de_baja_cartas_usuario(self):
        """Método que carga la interfaz en el Frame Acciones para buscar una Carta que se quiere dar de baja al
            usuario"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Dando de Baja Cartas al Usuario", alto_filas=4)

        # TITULO
        ttk.Label(self.fr_acciones, text=f"Da de baja una carta al usuario {self.etiq_usuario_logueado.cget("text")}:",
                  style="tit_bold.TLabel", justify="right").grid(
            row=1, column=0, padx=10, pady=(0, 12), sticky="E")

        # Buscamos en DB todas las cartas del usuario, incluso si tiene de distintos niveles se verán todas
        listado_cartas = funciones.cartas_usuario_db(usuario=self.etiq_usuario_logueado.cget("text"),
                                                     activa=True,
                                                     todos=True,
                                                     solo_info_cartas=True)

        if not listado_cartas:
            self.etiqueta_acciones.config(text="No se han encontrado Cartas en la Base de Datos",
                                          style="cursiva_red.TLabel")

        else:
            # Llamamos al método que carga los widgets en pantalla
            self.interfaz_ver_y_filtrar_cartas_usu()

            # Colocamos nuestras cartas en el Treeview
            self.cargar_treeview(tipo_datos="carta", lista_datos_db=listado_cartas)

            # Agregamos un evento para que con cada clic se verifique si hay algún elemento seleccionado
            self.treeview.bind("<ButtonRelease-1>", self.verificar_cantidad)

            # Vinculamos el entry a un evento para que automáticamente filtre el listado
            self.d_ent["ent0"].bind("<KeyRelease>", lambda event: self.filtrar_treeview(listado_cartas=listado_cartas))

            # BOTÓN ELIMINAR
            self.d_btn["btn0"].config(text="Dar de baja", command=lambda: self.eliminar_carta_aceptado(
                tipo="carta_usuario"))
            self.d_btn["btn0"].grid(row=4, column=2, padx=5, pady=(2, 6), sticky="W")

        # BOTÓN SALIR
        ttk.Button(self.fr_acciones, text="Salir", command=self.elementos_como_inicio, width=7).grid(
            row=1, column=2, padx=4, pady=(0, 12), sticky="E")

#-----------------------------------------------------------------------------------------------------------------------
#                                      GRABAR BATALLAS
#-----------------------------------------------------------------------------------------------------------------------
    def grabar_batallas(self):
        """Método que carga la interfaz de Grabar Batallas en el panel de la derecha. Se puede cargar el propio usuario
        logueado, un usuario que se ingrese dando su nombre en el juego y también carga en un Treeview los usuarios de
        la DB"""

        # Se vuelve el Frame a su estado inicial (por si se viene de otra acción anterior que todavía se está mostrando)
        self.elementos_como_inicio()

        # Inicio del Frame
        self.reiniciando_frame_acciones(text_etiqueta="Grabando Batallas", alto_filas=3)

        # Título
        ttk.Label(self.fr_acciones, text="Grabar últimas 50 batallas:", style="tit_bold.TLabel").grid(
            row=1, column=0, padx=10, pady=(0, 12), sticky="w")

        # Etiqueta y Botón para Batallas del usuario logueado
        texto_etiq = "Usuario logueado: {}".format(self.etiq_usuario_logueado.cget("text"))
        ttk.Label(self.fr_acciones, text=texto_etiq).grid(row=2, column=0, padx=10, pady=(2, 4), sticky="w")

        ttk.Button(self.fr_acciones, command=lambda: self.grabar_batallas_aceptado(tipo="propias"),
                   text="Cargar Batallas").grid(row=2, column=1, padx=10, pady=2, ipadx=2, ipady=3, sticky="nsew")

        # Etiqueta, Entry y Botón para ingresar el nombre de un usuario a cargar
        ttk.Label(self.fr_acciones, text="Ingrese un Usuario:").grid(row=3, column=0, padx=10, pady=(8, 2), sticky="w")

        self.d_ent["ent0"].config(font=("Segoe UI", 9), textvariable=self.d_stv["stv0"])
        self.d_ent["ent0"].grid(row=4, column=0, padx=10, pady=(2, 4))
        self.d_ent["ent0"].bind("<KeyRelease>", self.verificar_entry)

        self.d_btn["btn5"].config(text="Cargar Batallas", command=lambda: self.grabar_batallas_aceptado(tipo="jugador"),
                                  state="disabled")
        self.d_btn["btn5"].grid(row=4, column=1, padx=10, pady=2, ipadx=2, ipady=3, sticky="nsew")

        # Etiqueta para título de Tabla
        ttk.Label(self.fr_acciones, text="Usuarios de Base de Datos").grid(
            row=5, column=0, padx=10, pady=(6, 2), sticky="w")

        # Configuramos el Treeview
        nombres_col = ["Usuario", "Victorias", "Batallas"]
        anchos_col = [120, 60, 60]

        # Llamamos a la función que lo crea
        self.configurar_treeview(columnas=3, nombres=nombres_col, anchos=anchos_col)

        # Configuración particular de este Treeview
        self.treeview.config(height=8, show="headings", style="alto_fila_lista.Treeview")
        self.treeview.state(["disabled"])
        self.treeview.bind("<ButtonRelease-1>", self.verificar_cantidad)

        # Colocamos el Treeview
        self.treeview.grid(row=6, column=0, rowspan=5, columnspan=2, padx=(20, 24), pady=(2, 4), sticky="ew")

        # Colocamos el SCROLL de la Tabla
        self.scrollbar.grid(row=6, column=1, rowspan=5, padx=(2, 8), pady=(2, 5), sticky="NSE")

        # BOTONES para carga desde la TABLA
        self.d_btn["btn0"].config(text="Cargar Selección", command=lambda: self.grabar_batallas_aceptado(
            tipo="seleccion"), state="disabled")
        self.d_btn["btn0"].grid(row=6, column=2, padx=1, pady=3, ipadx=9, ipady=4, sticky="ew")

        self.d_btn["btn1"].config(text="Cargar Todas", command=lambda: self.grabar_batallas_aceptado(tipo="todas"))
        self.d_btn["btn1"].grid(row=7, column=2, padx=1, pady=3, ipady=4, sticky="ew")

        self.d_btn["btn2"].config(text="Quitar de Lista", command=self.quitar_tabla)
        self.d_btn["btn2"].grid(row=8, column=2, padx=1, pady=3, ipady=4, sticky="ew")

        self.d_btn["btn3"].config(text="Pausar grabación", command=self.pausar_hilo_secund, state="disabled")
        self.d_btn["btn3"].grid(row=9, column=2, padx=1, pady=3, ipady=4, sticky="ew")

        self.d_btn["btn4"].config(text="Cancelar", command=self.elementos_como_inicio)
        self.d_btn["btn4"].grid(row=10, column=2, padx=1, pady=3, ipady=4, sticky="ew")

        # Etiqueta para cantidad de usuarios
        self.d_lbl["lbl0"].grid(row=10, column=3, padx=1, pady=3, sticky="W")
        self.total_usuarios_grab_bat()  # Llamamos a la función que coloca cantidad (empezará con cero)

        # Etiqueta informando de que habrá una demora buscando en la DB (luego desaparece)
        self.d_lbl["lbl1"].config(text="Leyendo usuarios en DB...", style="cursiva.TLabel", anchor="center")
        self.d_lbl["lbl1"].grid(row=8, column=0, columnspan=2, padx=5, pady=3, ipady=3)
        self.d_lbl["lbl1"].lift()  # Para que se coloque encima del widget treeview y se pueda ver

        # Llamamos en un hilo secundario la búsqueda en la DB de los usuarios para colocar en el Treeview
        self.proceso_hilo_secundario(proceso=funciones.usuarios_carga_batallas, argumentos=(self.queue,))

        self.revision_queue(caso="tabla_grab_bat")  # Iniciamos la revisión de la queue

    def cargar_usu_tree_grab_bat(self, usuarios_db):
        """Método para cargar en el treeview los resultados de la consulta a la DB con los nombres de usuarios a buscar
        sus batallas para luego grabar. Es ejecutado cuando el proceso que revisa la queue detecta el resultado."""

        self.detener_revision_queue()  # Detenemos la revisión de la queue porque solo llega la información una vez

        if usuarios_db:  # Por si no encuentra nada

            for fila in usuarios_db:  # Ponemos los usuarios en la Tabla
                self.treeview.insert("", "end", text=fila[0], values=(fila[0], fila[1], fila[2]))

        self.total_usuarios_grab_bat()  # Ejecutamos para actualizar la cantidad del Label

        self.d_lbl["lbl1"].destroy()  # Quitamos el Label que informaba la lectura de la DB
        self.treeview.state(["!disabled"])  # Habilitamos el Treeview

    def total_usuarios_grab_bat(self):
        """Método que de acuerdo a la cantidad de elementos listados en un Treeview actualiza esa cantidad en Label"""

        # Se toma la cantidad de filas del Treeview y se le da formato para colocar en la etiqueta
        cant_filas = len(self.treeview.get_children())
        text_cant_users = "Usuarios Tabla: {}".format(cant_filas)
        self.d_lbl["lbl0"].config(text=text_cant_users)

    def verificar_entry(self, event):
        """Método que verifica que se haya escrito texto en el entry de usuarios de grabación de batallas para
        habilitar el botón que permite iniciar la carga de esas batallas."""

        if self.d_stv["stv0"].get().strip() == "":  # Cuando lo escrito esté vacío o sea igual a espacios se desactiva
            self.d_btn["btn5"].config(state="disabled")
        else:
            self.d_btn["btn5"].config(state="active")

    def grabar_batallas_aceptado(self, tipo):
        """Método que modifica la interfaz de grabar batallas, desactivando y activando botones, agregando un cuadro de
        texto y enviando el primer mensaje de inicio, definiendo una progressbar, generando la lista de usuarios a
        grabar, e iniciando los procesos para la ejecución en hilo secundario de la grabación."""

        # Deshabilitamos los botones
        self.desactivar_botones_todos()
        self.d_btn["btn3"].config(state="active")

        # Mensaje de la operación (se va a ver mientras se esté ejecutando)
        self.etiqueta_acciones.configure(text="Grabando Batallas...", style="cursiva_yellow.TLabel")

        self.fr_acciones.grid_configure(rowspan=4)  # Agrandamos el FRAME

        # Colocamos el cuadro de información y el scroll
        self.cuadro_texto.config(width=81, height=10, wrap="word", background="#3c3c3c", foreground="white",
                                 font=("Yu Gothic UI Semibold", 8, "bold"))
        self.cuadro_texto.grid(row=11, column=0, columnspan=4, padx=(10, 15), pady=(20, 7), ipady=2, ipadx=2)
        scroll_cuadro_text = ttk.Scrollbar(self.fr_acciones, orient="vertical", command=self.cuadro_texto.yview)
        scroll_cuadro_text.grid(row=11, column=3, padx=2, pady=(20, 7), sticky="nse")
        self.cuadro_texto.config(yscrollcommand=scroll_cuadro_text.set)

        # Barra de progreso
        self.progress_bar.config(orient="horizontal", length=180, mode="determinate")

        # Mensaje de inicio en el cuadro de texto
        posicion = self.cuadro_texto.index("end")  # Obtenemos la posición final en formato tkinter
        linea, columna = map(int, posicion.split("."))  # map aplica int() a cada elem de la lista resultante de split()
        if linea > 2:
            self.cuadro_texto.insert("end", "\n\n")
        self.cuadro_texto.insert("end", ">>> Iniciando grabación de Batallas de Usuarios <<<\n\n")

        a_grabar = []  # Lista con pares de valores, 1ro nombre: para descargar, 2do ubicación en treeview: para quitar
        if tipo == "propias":  # Usuario logueado
            a_grabar.append((self.etiq_usuario_logueado.cget("text").lower(),))  # No llevan ubicación en treeview

        elif tipo == "jugador":  # Usuario completado en entry
            a_grabar.append((self.d_stv["stv0"].get().lower().strip(),))  # No llevan ubicación en treeview
            self.d_stv["stv0"].set("")

        elif tipo == "seleccion":  # Se pueden seleccionar más de uno
            nombres_a_grabar = self.treeview.selection()
            self.treeview.see(nombres_a_grabar[0])
            for item in nombres_a_grabar:
                a_grabar.append((self.treeview.item(item)["text"], item))

        elif tipo == "todas":  # Se toma el treeview completo
            nombres_a_grabar = self.treeview.get_children()
            self.treeview.see(nombres_a_grabar[0])
            for item in nombres_a_grabar:
                a_grabar.append((self.treeview.item(item)["text"], item))

        # La grabación se hará en hilo secundario, requiere la lista de nombres definida anteriormente
        self.proceso_hilo_secundario(proceso=self.grabar_batallas_hilo_secund, argumentos=(a_grabar,))

        self.control_cola = True  # Si se ejecutó otra grabación antes, habrá quedado en False.

        self.revision_queue(caso="grabar_batallas")  # Se inicia la función que estará leyendo self.queue

    def grabar_batallas_hilo_secund(self, lista_a_grabar):
        """Método que se ejecuta en hilo secundario y va dirigiendo todas las funciones que se ejecutarán para completar
        el proceso de grabado que se ha seleccionado y no tiene que ver con la interfaz."""

        self.continuar_hilo.set()  # Variable para pausar el proceso, comienza sin orden de pausa, o sea continuar = sí
        self.detener_hilo.clear()  # Variable para cancelar el proceso, comienza con un no
        self.progress_bar.grid_forget()  # Borramos un progressbar que puede haber quedado de una grabación anterior

        self.queue.put("Iniciando navegador web...\n")  # Enviamos el primer mensaje

        self.navegador.iniciar()  # Iniciamos el navegador

        self.queue.put("Navegador iniciado.\n\n")  # Segundo mensaje

        # Se ejecuta el proceso que abre la web del juego y se ingresa con usuario y contraseña
        self.navegador.proceso_login_splint(cola_queue=self.queue,
                                            usuario=self.etiq_usuario_logueado.cget("text").lower(),
                                            contras=self.cadena_seg)

        if len(lista_a_grabar) > 1:  # Configuramos el progressbar, solo en casos de más de un jugador seleccionado
            self.progress_bar.config(value=0, maximum=len(lista_a_grabar))
            self.progress_bar.grid(row=1, column=2, columnspan=2)

        for jugador in lista_a_grabar:  # Bucle para recorrer la lista de jugadores y grabar de uno en uno
            rtdo_descarga = None  # Eliminamos los datos de la consulta anterior
            desc_grab_incompl = True
            while desc_grab_incompl:  # Con este while y la variable de control volverá a intentar con el mismo usuario
                try:  # Intentamos la descarga de las batallas llamando a esta función. Suele haber errores de conexión.
                    rtdo_descarga = self.navegador.conexion_descarga_batallas(player=jugador[0])

                    if rtdo_descarga:  # Si encontró el sitio web llamaremos a la función que graba en DB
                        funciones.grabar_batallas(cola_queue=self.queue, datos_recibidos=rtdo_descarga)

                        try:  # El try porque no todos los métodos de grabación tienen un par de valores
                            self.queue.put(jugador[1])  # Este mensaje es para que se quite el nombre del treeview
                        except IndexError:
                            pass  # Simplemente que no haga nada porque no hay nada que quitar del treeview

                        desc_grab_incompl = False  # Cambiamos el valor para que salga del while

                except PlaywrightError:  # Cuando no logra conexión con el sitio web para descargar las batallas
                    self.queue.put("\n\nError de conexión a la web, se volverá a intentar en 2 minutos.")
                    for x in range(120):  # Creamos un bucle con tiempo de espera para que lea si se quiere cancelar
                        sleep(1)
                        if self.detener_hilo.is_set():  # Esta orden le llegará cuando apretamos 'Detener grabación'
                            break  # Sale del bucle de 120 seg
                self.continuar_hilo.wait()  # Chequea en cada iteración si el usuario ha pedido pausar la grabación
                if self.detener_hilo.is_set():  # También se chequea si se ha cancelado
                    break  # Sale del bucle While
            if self.detener_hilo.is_set():
                break  # Sale del bucle For

        # Ejecutamos carga automática de reglas
        funciones.carga_reglas_desde_batallas(cola_queue=self.queue)

        # Revisamos si hay cartas nuevas
        funciones.verificar_cartas_nuevas_desde_batallas(cola_queue=self.queue)

        self.queue.put("Proceso finalizado")  # Mensaje de finalización
        self.navegador.cerrar()  # El navegador siempre se cierra porque también se cierra el hilo secundario

    def tratar_grabar_bat(self, mensaje):
        """Método que va recibiendo y tratando los mensajes que se van generando en el hilo secundario de los procesos
        necesarios para realizar la grabación de batallas. Los mensajes son de todas las funciones involucradas."""

        if "Proceso de grabado de batallas de" in mensaje:  # Es en caso de grabado de un usuario en DB
            self.cuadro_texto.insert("end", mensaje)  # Colocamos el mensaje recibido en el cuadro de texto
            self.cuadro_texto.see("end")  # Llevamos la vista al final

            self.progress_bar["value"] += 1  # Aumentamos el avance del progressbar

            if not self.continuar_hilo.is_set():  # Si se ha pedido pausar la grabación
                self.cuadro_texto.tag_configure("amarillo", foreground="yellow")
                self.cuadro_texto.insert("end", "\n\n - Proceso en pausa -", "amarillo")
                self.cuadro_texto.see("end")

        elif self.treeview.exists(mensaje):  # Un mensaje es el orden en el treeview, se chequea si lo encuentra
            self.treeview.delete(mensaje)    # Borramos el elemento de la tabla
            self.total_usuarios_grab_bat()   # Actualizamos la etiqueta con la cantidad

        elif "se volverá a intentar" in mensaje:  # Es el error cuando no puede descargar las batallas
            self.cuadro_texto.tag_configure("amarillo", foreground="yellow")
            self.cuadro_texto.insert("end", mensaje, "amarillo")
            self.cuadro_texto.see("end")

        elif "al intentar acceder" in mensaje:  # Es el error cuando no puede ingresar con usuario y contraseña
            self.cuadro_texto.insert("end", f"\n{mensaje}")
            self.cuadro_texto.see("end")
            self.fin_grabar_batallas(mensaje1="\n\nACCESO WEB INCORRECTO", mensaje2="Grabado de batallas no concluido")

        elif mensaje == "Proceso finalizado":  # Se cierra la revisión continua de la queue y se coloca un mensaje
            self.detener_revision_queue()
            self.fin_grabar_batallas(mensaje1="\n\nPROCESO FINALIZADO", mensaje2="Grabado de batallas finalizado")

        else:  # El resto de los mensajes se tratan todos por igual, se muestran en el cuadro de texto
            self.cuadro_texto.insert("end", mensaje)  # Colocamos el mensaje recibido en el cuadro de texto
            self.cuadro_texto.see("end")  # Llevamos la vista al final

    def pausar_hilo_secund(self):
        """Método que se inicia cuando se quiere pausar la grabación de batallas en el hilo secundario"""

        self.continuar_hilo.clear()  # Esta variable detendrá el bucle cuando se realice el control
        self.d_btn["btn3"].config(text="Reanudar grabación", command=self.reanudar_hilo_secund)
        self.d_btn["btn4"].config(text="Detener grabación", state="active",
                                  command=lambda: self.detener_hilo_secund(caso="batallas"))

    def reanudar_hilo_secund(self):
        """Método que se inicia cuando se quiere continuar la grabación de batallas en el hilo secundario después de una
        pausa"""

        self.continuar_hilo.set()  # Esta variable reiniciará el bucle cuando se realice el control
        self.d_btn["btn3"].config(text="Pausar grabación", command=self.pausar_hilo_secund)
        self.d_btn["btn4"].config(text="Cancelar", command=self.elementos_como_inicio, state="disabled")

        self.queue.put("\n\n + Proceso reanudado +")

    def detener_hilo_secund(self, caso=None):
        """Método que se inicia cuando se quiere detener completamente la grabación de batallas en el hilo secundario.
        Solo se puede accionar cuando se haya pausado la grabación."""

        self.detener_hilo.set()  # Esta variable es la que detiene el proceso saliendo de los bucles
        if caso == "batallas":
            self.continuar_hilo.set()  # Como solo se puede ejecutar estando en pausa, es importante quitar la pausa
        self.queue.put("\n\nProceso detenido por el usuario")

        self.progress_bar.grid_forget()  # Quitamos el progressbar que estaría incompleto

    def quitar_tabla(self):
        """Método que quita un elemento seleccionado, o varios, del treeview"""

        for item in self.treeview.selection():
            self.treeview.delete(item)

    def fin_grabar_batallas(self, mensaje1, mensaje2):
        """Método que se ejecuta al finalizar la grabación de batalla, ya sea que se completa o cuando se detiene. Deja
        la interfaz como antes de comenzar y muestra un mensaje final en el cuadro y otro en la etiqueta."""

        self.cuadro_texto.tag_configure("green", foreground="#009846")
        self.cuadro_texto.insert("end", mensaje1, "green")  # Mensaje en cuadro de texto
        self.cuadro_texto.see("end")
        self.etiqueta_acciones.configure(text=mensaje2, style="cursiva_green.TLabel")  # Mensaje en etiqueta

        self.d_btn["btn3"].config(text="Pausar grabación", command=self.pausar_hilo_secund)
        self.d_btn["btn4"].config(text="Cancelar", command=self.elementos_como_inicio)

        self.activar_botones_todos()  # Activa todos los botones
        self.d_btn["btn3"].config(state="disabled")

    def abrir_sugerencia_batallas(self):
        """Método que inicia en una nueva ventana la interfaz para sugerir cartas en función de reglas de batalla"""

        nombre_usuario = self.etiq_usuario_logueado.cget("text").lower()
        sug_bat = sugerir_batallas.SugerenciaBatalla(master=self, usuario=nombre_usuario)


if __name__ == "__main__":
    db.Base.metadata.create_all(db.engine)

    root = Tk()
    pant_ini = PantallaInicial(root)
    root.mainloop()
