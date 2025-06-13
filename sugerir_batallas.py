import os
import io
import funciones
from tkinter import ttk, Toplevel, Button, Checkbutton, Radiobutton, Spinbox, Canvas, StringVar, IntVar
from PIL import Image


class SugerenciaBatalla:
    """Clase perteneciente a la ventana que sugiere a un jugador las jugadas de cartas posibles ante un conjunto de
    reglas indicado. Es el objetivo principal del programa, poder dar está información en función de la DB y las cartas
    en posesión según el usuario."""

    def __init__(self, master, usuario):
        """Constructor de la clase. Carga la venta por encima de la pantalla inicial con toda su configuración de
        widgets, para permitir la selección de las reglas de batalla. También muestra en forma de presentación cómo se
        mostrarán los resultados en las columnas 2 y 3."""

        # Ventana completa
        self.ventana = Toplevel()
        self.ventana.title("Juego Batalla")
        self.ventana.wm_iconbitmap("imagenes/img_icon_splinterlands.ico")

        # Frame izquierdo para las reglas, muchas widgets hacia abajo estarán aquí
        self.frame_reglas = ttk.LabelFrame(self.ventana, text="Reglas de la batalla", borderwidth=3)
        self.frame_reglas.grid(row=0, column=0, sticky="nsew", padx=(3, 1), pady=10, ipadx=3, ipady=5)

        # Etiqueta para el usuario con el que se está jugando
        self.usuario = ttk.Label(self.frame_reglas, text=usuario.upper())
        self.usuario.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Botón para generar la búsqueda
        Button(self.frame_reglas, text="Buscar jugadas", command=self.mostrar_jugadas, bg="#EE9025").grid(
            row=0, column=0, padx=2, pady=5, ipadx=2, ipady=2, sticky="e")

        # Frame para la segunda fila en la que se selecciona la liga (etiqueta y 5 radiobutton)
        self.frame_liga = ttk.Frame(self.frame_reglas)
        self.frame_liga.grid(row=2, column=0, padx=3, pady=5)

        ttk.Label(self.frame_liga, text="LIGA:", width=6).grid(row=1, column=0)

        self.liga = StringVar()  # Variable para la liga vinculado a 4 botones
        self.btn_liga = {}
        for x in range(5):
            imagen_carga = funciones.imagen_pillow_ruta(ruta=f"imagenes/img_event-level_{x}.png")
            self.btn_liga[f"liga{x}"] = Radiobutton(self.frame_liga, indicatoron=False, variable=self.liga, value=x)
            funciones.colocar_img_en_widget(imagen_a_colocar=imagen_carga, widget=self.btn_liga[f"liga{x}"], alto=45)
            if x >= 3:
                self.btn_liga[f"liga{x}"].config(state="disabled")
            self.btn_liga[f"liga{x}"].grid(row=1, column=x+1)

        # Frame en el que se selecciona el formato de batalla: Modern o Wild (etiqueta y 2 radiobutton)
        self.frame_formato = ttk.Frame(self.frame_reglas)
        self.frame_formato.grid(row=3, column=0, padx=3, pady=5)

        ttk.Label(self.frame_formato, text="FORMATO:", anchor="w").grid(row=1, column=0)

        self.formato = StringVar()  # Variable para el formato vinculado a 2 botones

        imagen_modern = funciones.imagen_pillow_ruta(ruta="imagenes/modern.png")
        self.boton_modern = Radiobutton(self.frame_formato, indicatoron=False, variable=self.formato, value="modern")
        funciones.colocar_img_en_widget(imagen_a_colocar=imagen_modern, widget=self.boton_modern, alto=36)
        self.boton_modern.grid(row=1, column=1)

        imagen_wild = funciones.imagen_pillow_ruta(ruta="imagenes/wild.png")
        self.boton_wild = Radiobutton(self.frame_formato, indicatoron=False, variable=self.formato, value="wild")
        funciones.colocar_img_en_widget(imagen_a_colocar=imagen_wild, widget=self.boton_wild, alto=36)
        self.boton_wild.grid(row=1, column=2)

        # Frame para el tipo de batalla entre Ranked y Torneo (etiqueta y 2 radiobutton)
        self.frame_tipo_batalla = ttk.Frame(self.frame_reglas)
        self.frame_tipo_batalla.grid(row=4, column=0, padx=3, pady=5)

        ttk.Label(self.frame_tipo_batalla, text="TIPO DE BATALLA:").grid(row=1, column=0)

        self.combate = StringVar()
        self.combate.set("")  # Para que al iniciarse el formulario no aparezca ningún botón seleccionado

        self.boton_ranked = Radiobutton(self.frame_tipo_batalla, text="RANKED", indicatoron=False,
                                        variable=self.combate, value="Ranked")
        self.boton_ranked.grid(row=1, column=1)
        self.boton_ranked.bind("<Button-1>", lambda event: self.habilitar_opciones())  # Habilita radiobutton inferiores

        self.boton_tournament = Radiobutton(self.frame_tipo_batalla, text="TOURNAMENT", indicatoron=False,
                                            variable=self.combate, value="Tournament")
        self.boton_tournament.grid(row=1, column=2)
        self.boton_tournament.bind("<Button-1>", lambda event: self.habilitar_opciones())  # Hab. radiobutton inferiores

        # Frame para torneos en los que ciertas cartas legendarias no son permitidas
        self.frame_torneos = ttk.Frame(self.frame_reglas)
        self.frame_torneos.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.etiqueta_opciones_tournament = ttk.Label(self.frame_torneos, text="OPCIONES\nTORNEOS", state="disabled")
        self.etiqueta_opciones_tournament.grid(row=1, column=0, rowspan=2)

        self.cartas_torneo = StringVar()
        self.boton_no_leg_card = Radiobutton(self.frame_torneos, text="NO LEGENDARY\nCARDS", state="disabled",
                                             indicatoron=False, variable=self.cartas_torneo,
                                             value="sin ninguna carta legendaria")
        self.boton_no_leg_card.grid(row=1, column=1)

        self.boton_no_leg_summ = Radiobutton(self.frame_torneos, text="NO LEGENDARY\nSUMMONERS", state="disabled",
                                             indicatoron=False, variable=self.cartas_torneo,
                                             value="sin summoners legendarios")
        self.boton_no_leg_summ.grid(row=1, column=2)

        # Frame para ingresar el mana (etiqueta, Spinbox con fondo)
        self.frame_mana = ttk.Frame(self.frame_reglas)
        self.frame_mana.grid(row=6, column=0, padx=3, pady=5)

        ttk.Label(self.frame_mana, text="MANA:").grid(row=1, column=0)

        self.mana = StringVar()
        fondo_mana = funciones.imagen_pillow_ruta(ruta="imagenes/bg_mana.png")
        self.etiqueta_fondo = ttk.Label(self.frame_mana)
        funciones.colocar_img_en_widget(imagen_a_colocar=fondo_mana, widget=self.etiqueta_fondo, alto=60)
        self.etiqueta_fondo.config(relief="flat")
        self.etiqueta_fondo.grid(row=1, column=1, sticky="nsew")
        Spinbox(self.etiqueta_fondo, from_=12, to=99, width=2, font=('Arial', 14), textvariable=self.mana,
                insertbackground='black', bd=0, background="#00C5CD").grid(row=0, column=0, pady=20, padx=20)

        # Frame para seleccionar los elementos habilitados en cada batalla (etiqueta y 6 checkbutton)
        self.frame_elements = ttk.Frame(self.frame_reglas)
        self.frame_elements.grid(row=7, column=0, padx=3, pady=3)

        ttk.Label(self.frame_elements, text="ELEMENTOS:").grid(row=1, column=0, rowspan=2)

        elementos = ["fire", "water", "earth", "life", "death", "dragon"]
        btn_elem = {}
        self.vble_elem = {}
        for e in range(6):
            self.vble_elem[f"{elementos[e]}_cards"] = IntVar()
            imagen_on = funciones.imagen_pillow_ruta(ruta=f"imagenes/icon_splinter_{elementos[e]}.png")
            imagen_off = funciones.imagen_pillow_ruta(ruta=f"imagenes/icon_splinter_{elementos[e]}_inactive.png")
            btn_elem[f"boton_{elementos[e]}"] = Checkbutton(self.frame_elements, indicatoron=False, onvalue=1,
                                                            variable=self.vble_elem[f"{elementos[e]}_cards"])
            funciones.colocar_img_en_widget(imagen_a_colocar=imagen_off, widget=btn_elem[f"boton_{elementos[e]}"],
                                            alto=30, imagen_on=imagen_on)
            btn_elem[f"boton_{elementos[e]}"].grid(row=1, column=1+e)

        # Frame en el que se seleccionan las REGLAS sobre cartas que pueden jugarse o no
        # De momento el código no tiene límites de selección, aunque solo considera las 3 primeras cuando haya más
        self.frame_rules = ttk.Frame(self.frame_reglas)
        self.frame_rules.grid(row=8, column=0, padx=5, pady=(1, 3))

        ttk.Label(self.frame_rules, text="REGLAS:").grid(row=1, column=0)

        # Etiqueta para mostrar el nombre de cada regla al pasar el mouse encima
        self.etiqueta_detalle = ttk.Label(self.frame_rules, text="")
        self.etiqueta_detalle.grid(row=1, column=1, columnspan=8)
        self.frame_rules.grid_columnconfigure(1, minsize=200)

        # Agregamos un botón para que deseleccione todas las reglas
        self.boton_borrar = Button(self.frame_rules, text="X", command=self.borrar_seleccion_reglas)
        self.boton_borrar.grid(row=1, column=1, sticky="e", pady=(3, 1))

        self.frame_btn_reg = ttk.Frame(self.frame_rules)
        self.frame_btn_reg.grid(row=2, column=0, columnspan=2, padx=(5, 0))

        self.d_rules = {}

        # Consulta a la DB para buscar las reglas existentes llamando a la función correspondiente
        lista_de_reglas = funciones.regla_datos_db(todos=True)

        if not lista_de_reglas:  # Mensaje en caso de no encontrar ninguna regla
            self.etiqueta_detalle.configure(text="No se han encontrado reglas en la Base de Datos")
        else:
            self.ch_btns_reg = {}  # Diccionario para poner cada checkbutton

            fila_regla = 2  # Variables de ubicación
            columna_regla = 1
            # Creamos los botones para cada una de las reglas encontradas en la DB
            for regla in lista_de_reglas:
                nombre_regla = regla.nombre.replace("?", "")
                self.d_rules[nombre_regla] = StringVar()

                if not regla.imagen:  # Si no está en la DB, revisamos si no está en la carpeta /imagenes
                    ruta_imagen = f"imagenes/img_rule_{nombre_regla}.png"
                    ruta_imagen_modif = ruta_imagen.lower().replace(" ", "_")

                    if os.path.isfile(ruta_imagen_modif):
                        imag_reg_pillow = funciones.imagen_pillow_ruta(ruta=ruta_imagen_modif)
                    else:
                        imag_reg_pillow = funciones.imagen_pillow_ruta(ruta="imagenes/Imagen-no-disponible-282x300.png")

                else:  # Carga desde la DB
                    imag_reg_pillow = Image.open(io.BytesIO(regla.imagen))

                # Creamos los botones de cada regla con su nombre y su propia variable. Luego colocamos la imagen
                self.ch_btns_reg[nombre_regla] = Checkbutton(self.frame_btn_reg, onvalue=regla.nombre, indicatoron=False,
                                                             variable=self.d_rules[nombre_regla])
                funciones.colocar_img_en_widget(imagen_a_colocar=imag_reg_pillow, widget=self.ch_btns_reg[nombre_regla],
                                                alto=32)

                # Ubicación de los checkbutton incrementando filas y columnas (8 columnas)
                self.ch_btns_reg[nombre_regla].grid(row=fila_regla, column=columna_regla)
                columna_regla += 1
                if columna_regla > 9:
                    fila_regla += 1
                    columna_regla = 1

                # Eventos para que nos muestren el nombre de la regla en uns etiqueta que hay arriba de ellas
                self.ch_btns_reg[nombre_regla].bind("<Enter>", self.entra_cursor_boton_regla(nombre_regla))
                self.ch_btns_reg[nombre_regla].bind("<Leave>", self.sale_cursor_boton_regla())

        # Algunos valores predeterminados al iniciar
        self.liga.set("2")
        self.formato.set("modern")
        self.combate.set("Ranked")
        self.mana.set("17")

        #---------------------------------------------------------------------------------------------------------------
        # Definimos los widgets que se usarán para mostrar los resultados de acuerdo a las cartas que tenga el jugador
        self.frame_resultados_usu = ttk.LabelFrame(self.ventana)
        self.etiqueta_mensaje_usu = ttk.Label(self.frame_resultados_usu)
        self.frame_jugadas_completo_usu = ttk.Frame(self.frame_resultados_usu)
        self.canvas_scroll_usu = Canvas(self.frame_jugadas_completo_usu)
        self.scroll_jugadas_usu = ttk.Scrollbar(self.frame_jugadas_completo_usu)
        self.frame_jugadas_usu = ttk.Frame(self.canvas_scroll_usu)

        # Mediante este método colocamos todos los widgets y los configuramos adecuadamente
        self.colocar_frame_y_sus_widgets(columna=1)

        # Con esta función colocamos una muestra de como serían las batallas
        funciones.esquema_mostrar_batallas(frame_a_cargar=self.frame_jugadas_usu)

        # Llamamos al método para reajustar el scroll (aunque al comenzar no haría falta)
        self.configurar_scroll(columna=1)

        self.dicc_jugadas_usu = {}  # Para grabar cada jugada que puede hacer el usuario

        #---------------------------------------------------------------------------------------------------------------
        # Definimos los widgets que se usarán para mostrar todos los resultados encontrados en la DB para las reglas
        self.frame_resultados = ttk.LabelFrame(self.ventana)
        self.etiqueta_mensaje = ttk.Label(self.frame_resultados)
        self.frame_jugadas_completo = ttk.Frame(self.frame_resultados)
        self.canvas_scroll = Canvas(self.frame_jugadas_completo)
        self.scroll_jugadas = ttk.Scrollbar(self.frame_jugadas_completo)
        self.frame_jugadas = ttk.Frame(self.canvas_scroll)

        # Mediante este método colocamos todos los widgets y los configuramos adecuadamente
        self.colocar_frame_y_sus_widgets(columna=2)

        # Con esta función colocamos una muestra de como serían las batallas
        funciones.esquema_mostrar_batallas(frame_a_cargar=self.frame_jugadas)

        # Llamamos al método para reajustar el scroll (aunque al comenzar no haría falta)
        self.configurar_scroll(columna=2)

        self.dicc_jugadas = {}  # Acá quedará grabada cada jugada con sus cartas, será un dicc y dentro otros dicc

    def habilitar_opciones(self, *args):
        """Método que añade un tiempo de espera antes de ejecutar el método actualizar_opciones dado que si se procesa
        demasiado rápido, no se toman los cambios hechos."""

        self.ventana.after(300, self.actualizar_opciones)

    def actualizar_opciones(self):
        """Método que habilita o deshabilita los botones de torneos."""

        if self.combate.get() == "Tournament":
            self.etiqueta_opciones_tournament.configure(state="active")
            self.boton_no_leg_summ.configure(state="active")
            self.boton_no_leg_card.configure(state="active")
        else:
            self.etiqueta_opciones_tournament.configure(state="disabled")
            self.boton_no_leg_summ.configure(state="disabled")
            self.boton_no_leg_card.configure(state="disabled")

    def entra_cursor_boton_regla(self, regla):
        """Método que se ejecuta ante el evento de entrar con el puntero del mouse en un botón de una regla. La acción
        que realiza es mostrar el nombre de la regla en una etiqueta."""

        return lambda event: self.etiqueta_detalle.config(text=self.ch_btns_reg[regla]["onvalue"])

    def sale_cursor_boton_regla(self):
        """Este método se ejecuta ante el evento de salir con el puntero del mouse de un botón de una regla. Dejará
        vacío el texto de la etiqueta."""

        return lambda event: self.etiqueta_detalle.config(text="")

    def borrar_seleccion_reglas(self):
        """Método que le da funcionalidad a un pequeño botón con un 'X' al final de las reglas. Le quita la selección a
        todas."""

        for valor in self.d_rules:
            if valor:
                self.d_rules[valor].set("")

    def mostrar_jugadas(self):
        """Método que se encarga de procesar las reglas ingresadas, buscar en la DB las posibles jugadas, tanto de todas
        las cartas disponibles como con las que posee el jugador, y luego mostrarlas en la ventana."""

        # Borramos los widgets del frame que tiene las jugadas de cartas
        for widget in self.frame_jugadas.winfo_children():
            widget.destroy()
        for widget in self.frame_jugadas_usu.winfo_children():
            widget.destroy()

        regla_1 = regla_2 = regla_3 = None  # Se ponen en None para darles valor por si no existen tres
        n = 0  # Contador para que tome hasta tres reglas y las asigne
        for x in self.d_rules:  # Se recorren todas las reglas buscando las que estén seleccionadas
            if len(self.d_rules[x].get()) > 1:
                if n == 0:
                    regla_1 = self.d_rules[x].get()
                    n += 1
                elif n == 1:
                    regla_2 = self.d_rules[x].get()
                    n += 1
                elif n == 2:
                    regla_3 = self.d_rules[x].get()
                    n += 1
                else:  # Después de la 3 regla, no se graban más (podría agregarse un control o límite de selección)
                    pass

        buscar_db = True
        repeticion = 0
        lista_de_batallas = []
        while buscar_db:
            # Buscamos la lista de batallas que cumpla las condiciones en la DB llamando a la función específica
            lista_de_batallas = funciones.batallas_sugerir_batallas_db(mana=int(self.mana.get()),
                                                                       fire=self.vble_elem["fire_cards"].get(),
                                                                       water=self.vble_elem["water_cards"].get(),
                                                                       earth=self.vble_elem["earth_cards"].get(),
                                                                       life=self.vble_elem["life_cards"].get(),
                                                                       death=self.vble_elem["death_cards"].get(),
                                                                       dragon=self.vble_elem["dragon_cards"].get(),
                                                                       combate=self.combate.get(),
                                                                       formato=self.formato.get(),
                                                                       liga=self.liga.get(),
                                                                       regla1=regla_1,
                                                                       regla2=regla_2,
                                                                       regla3=regla_3,
                                                                       veces_buscadas=repeticion)

            contador_busqueda = funciones.contador_jugadas_posibles_usuario(lista_batallas=lista_de_batallas,
                                                                            usuario=self.usuario.cget("text").lower())

            print(f"Cantidad de jugadas encontradas rep {repeticion}:", len(lista_de_batallas))
            print(f"Cant de jugadas usuario encontradas rep {repeticion}:", contador_busqueda[0])
            print(f"Cant de ganadas usuario encontradas rep {repeticion}:", contador_busqueda[1])

            repeticion += 1

            if contador_busqueda[1] > 0 or repeticion == 5:
                buscar_db = False

        # Si no encontró batallas, lista_de_batallas viene vacía, en ese caso solo mostramos un mensaje en la etiqueta
        if not lista_de_batallas:
            self.etiqueta_mensaje.config(text="No se encontraron batallas")
            self.etiqueta_mensaje_usu.config(text="Ampliando la búsqueda para encontrar más batallas")
            self.ventana.update_idletasks()

        else:  # Si hay batallas para mostrar, ejecutará desde acá
            # En la etiqueta mostramos la cantidad de jugadas encontradas
            self.etiqueta_mensaje.config(text=f"Cantidad de batallas: {len(lista_de_batallas)}")

            cant_bat_usu = 0  # Contador para la cantidad de jugadas del usuario

            for i, batalla in enumerate(lista_de_batallas):  # Recorremos cada batalla encontrada en la DB

                codigo_jugada = f"jugada_{i}"  # Código de diccionario específico de esta jugada

                # Llamamos al método que generará la interfaz para una jugada (frame contenedor y label en interior)
                self.jugada_indiv_frame(batalla=batalla, jugada=codigo_jugada)  # El frame estará en self.dicc_jugadas

                # Obtenemos de cada batalla el conjunto de los siete pares de id_game y nivel
                lista_cartas_id_y_nivel = funciones.lista_cartas_para_buscar(batalla=batalla)

                # Buscamos en la DB las cartas con los datos necesarios para luego colocarlos en frame ya creado
                cartas_db = funciones.cartas_listado_db(listado_cartas_id_game_y_nivel=lista_cartas_id_y_nivel,
                                                        usuario=self.usuario.cget("text").lower())

                # Ordenamos el listado porque la consulta devuelve sin orden y quitando los None
                jugada_db = funciones.ordenar_cartas_jugada(listado_en_orden=lista_cartas_id_y_nivel, cartas=cartas_db)

                # Para cada posición de la lista de la jugada ordenada, llamamos a la función que coloca label e imagen
                for j in range(7):
                    funciones.check_objeto_db_y_colocacion_frame(objeto_db=jugada_db[j][0],
                                                                 frame=self.dicc_jugadas[codigo_jugada],
                                                                 tipo="carta",
                                                                 alto=90,
                                                                 sugerencia=True)

                # Llamamos a función que revisa si las cartas de la jugada las tiene el usuario (devuelve True o False)
                jugada_usuario = funciones.check_jugada_para_jugador(jugada=jugada_db)

                if jugada_usuario:  # Si son cartas del usuario, hacemos lo mismo que antes pero en la sección del medio
                    cant_bat_usu += 1

                    # Método para crear la misma interfaz en el Frame del usuario. Con 'caso' se adapta el sitio
                    self.jugada_indiv_frame(batalla=batalla, jugada=f"jug_{cant_bat_usu}", caso="jugada_jugador")

                    # Llamamos a la función que coloca label e imagen, ahora cambiando el Frame
                    for j in range(7):
                        funciones.check_objeto_db_y_colocacion_frame(objeto_db=jugada_db[j][0],
                                                                     frame=self.dicc_jugadas_usu[f"jug_{cant_bat_usu}"],
                                                                     tipo="carta",
                                                                     alto=90,
                                                                     sugerencia=True)

            # Cantidad de jugadas para el jugador (podría incluirse algún otro mensaje)
            self.etiqueta_mensaje_usu.configure(text=f"Cantidad de batallas: {cant_bat_usu}")

            # Configuración del Canvas para hacer scroll y para que tome el ancho del frame
            self.configurar_scroll(columna=2)
            self.configurar_scroll(columna=1)

    def colocar_frame_y_sus_widgets(self, columna):
        """Método para colocar los widgets en los apartados que muestran las jugadas. Se trata de la estructura, los
        frames, label, canvas y scroll, los cuales están definidos previamente en el _init_."""

        if columna == 1:  # Esta columna es para el frame del centro donde están los resultados del usuario
            label_frame = self.frame_resultados_usu
            label_frame_txt = "Jugadas con las reglas seleccionadas para el jugador"
            etiqueta = self.etiqueta_mensaje_usu
            etiqueta_txt = "Jugadas que puede hacer el usuario"
            frame_contenedor = self.frame_jugadas_completo_usu
            canvas_interno = self.canvas_scroll_usu
            scroll = self.scroll_jugadas_usu
            frame_jug = self.frame_jugadas_usu

        else:  # El único otro caso que enviaremos es columna = 2, todos los resultados posibles
            label_frame = self.frame_resultados
            label_frame_txt = "Jugadas con las reglas seleccionadas"
            etiqueta = self.etiqueta_mensaje
            etiqueta_txt = "Todas las jugadas que se han realizado"
            frame_contenedor = self.frame_jugadas_completo
            canvas_interno = self.canvas_scroll
            scroll = self.scroll_jugadas
            frame_jug = self.frame_jugadas

        # Label Frame que conforma la columna del medio o de la derecha de la ventana
        label_frame.config(borderwidth=3, text=label_frame_txt)
        label_frame.grid(row=0, column=columna, sticky="nsew", padx=1, pady=10, ipadx=2, ipady=2)

        # Etiqueta informando que se trata de resultados
        ttk.Label(label_frame, text="Resultados:").grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # En esta etiqueta se mostrará información adicional
        etiqueta.config(text=etiqueta_txt)
        etiqueta.grid(row=1, column=0, padx=40)

        # Frame debajo de las etiquetas, irá acompañado de un canvas. En tamaño este frame = canvas
        frame_contenedor.grid(row=2, column=0, sticky="nsew", padx=1, pady=3)

        # Canvas que irá en el interior, su razón de ser es para poder colocar un scroll
        canvas_interno.config(width=800, height=600)  # Se límita la altura
        canvas_interno.grid(row=0, column=0, rowspan=5, sticky="nsew")

        # Configuración del scroll
        scroll.config(orient="vertical", command=canvas_interno.yview)
        scroll.grid(row=0, column=1, rowspan=5, sticky="ns")
        canvas_interno.config(yscrollcommand=scroll.set)

        frame_jug.config(width=800)

        # Configuramos el frame de jugadas dentro del canvas en la esq sup izq.
        canvas_interno.create_window((0, 0), window=frame_jug, anchor="nw")

    def configurar_scroll(self, columna):
        """Método para reconfigurar el scroll ajustando el área desplazable"""

        if columna == 1:  # Esta columna es para el frame del centro donde están los resultados del usuario
            frame_jug = self.frame_jugadas_usu
            canv_scroll = self.canvas_scroll_usu

        else:  # El else es para el caso del frame de todas las jugadas
            frame_jug = self.frame_jugadas
            canv_scroll = self.canvas_scroll

        frame_jug.update_idletasks()
        canv_scroll.config(scrollregion=canv_scroll.bbox("all"))
        canv_scroll.config(width=frame_jug.winfo_reqwidth())

    def jugada_indiv_frame(self, batalla, jugada, caso=None):
        """Método que genera un frame para una sola jugada. Puede ser jugada general o del usuario, lo que se indicará
        con el atributo 'caso'. Además del frame coloca un label en su interior con un par de datos. Para colocar cada
        carta al final de este método se llama a una función."""

        if caso == "jugada_jugador":
            # Frame donde irá una jugada, tendrá una etiqueta y siete cartas
            self.dicc_jugadas_usu[jugada] = ttk.Frame(self.frame_jugadas_usu)
            self.dicc_jugadas_usu[jugada].pack(side="top", pady=1)

            # Etiqueta para el texto o valor a la izquierda (porcentaje de victorias)
            etiqueta_cada_jugada = ttk.Label(self.dicc_jugadas_usu[jugada], width=6,
                                             text=f"V: {int(batalla.ratio * 100)}\nC: {batalla.cantidad}")
            etiqueta_cada_jugada.pack(side="left")

        else:
            # Frame donde irá una jugada, tendrá una etiqueta y siete cartas
            self.dicc_jugadas[jugada] = ttk.Frame(self.frame_jugadas)
            self.dicc_jugadas[jugada].pack(side="top", pady=1)

            # Etiqueta para el texto o valor a la izquierda (porcentaje de victorias)
            etiqueta_cada_jugada = ttk.Label(self.dicc_jugadas[jugada], width=6,
                                             text=f"V: {int(batalla.ratio * 100)}\nC: {batalla.cantidad}")
            etiqueta_cada_jugada.pack(side="left")
