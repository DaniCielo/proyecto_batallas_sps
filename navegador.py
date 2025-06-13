import funciones
import random
import json
from playwright.sync_api import sync_playwright
from time import sleep


class Navegador:
    def __init__(self):
        self.playwright = None
        self.navegador = None
        self.page_web = None

    def iniciar(self):
        self.playwright = sync_playwright().start()
        self.navegador = self.playwright.chromium.launch(headless=True)  # headless=False => visible
        self.page_web = self.navegador.new_page()

    def cerrar(self):
        if self.navegador:
            self.navegador.close()
        if self.playwright:
            self.playwright.stop()

    def proceso_login_splint(self, cola_queue, usuario, contras):
        """Método que intenta loguear en la web del juego al usuario que se acaba de loguear en nuestro programa. Abre
        la página web del juego, accede a la sección de 'log in' y coloca usuario y contraseña dando a ingresar. Luego
        busca el nombre de usuario en el html para ver si lo encuentra (no es una búsqueda específica)."""

        cola_queue.put("Comenzando proceso de Log in en Splinterlands...\n")

        # Buscamos el usuario en la DB
        usuario_db = funciones.usuarios_datos_db(nombre_usuario=usuario)

        # Obtenemos el email que está guardado en la db
        email_acceso = usuario_db.usuario_juego

        # Llamamos a la función para obtener la contraseña para loguearnos que está guardada en forma cifrada
        contras_game = funciones.descifrado_contras_game(password=contras.decode('utf-8'),
                                                         texto_a_descifrar_db=usuario_db.contrasenia_juego)

        # Insertamos el primer mensaje en el cuadro de información
        cola_queue.put("Abriendo página web Splinterlands...\n")

        try:
            # Indicamos al navagador en la página que teníamos abierta que acceda al sitio web splinterlands
            self.page_web.goto("https://splinterlands.com/")
            self.page_web.wait_for_load_state()

            # Le pedimos que busque una etiqueta en el código html y luego haga clic
            self.page_web.click("button[data-testid='login']")

            # Esperará 5 seg o hasta que encuentre una etiqueta con el nombre email (en el html)
            self.page_web.wait_for_selector("input[name='email']", timeout=2000)

            cola_queue.put("Ingresando con usuario y contraseña...\n")

            # Completamos los campos de usuario y contraseña con la información de la Base de Datos
            self.page_web.focus("input[name='email']")
            self.page_web.type("input[name='email']", email_acceso, delay=random.randint(35, 80))
            self.page_web.focus("input[name='password']")
            self.page_web.type("input[name='password']", contras_game, delay=random.randint(40, 90))

            # Una vez completado buscará en el html el botón de log in y hará clic
            self.page_web.click('//button[text()="Log In" and contains(@class, "c-drMScW-cOYpNt-color-green")]')

            cola_queue.put("Aguardando respuesta...\n")

            # Damos tiempo a la carga completa y buscamos el usuario en el código html de la web
            self.page_web.wait_for_load_state("domcontentloaded", timeout=3000)
            sleep(2)  # Agregamos tiempo de espera para que realmente cargue el perfil del usuario

            elemento_html = self.page_web.locator("div.c-PJLV > h2")

            # Verificamos si ha encontrado al menos uno
            if elemento_html.count() > 0:
                for i in range(elemento_html.count()):
                    texto_en_html = elemento_html.nth(i).inner_text().strip()
                    if texto_en_html.lower() == usuario.lower():
                        cola_queue.put("El inicio de sesión en Splinterlands.com ha sido exitoso")
                        break

            else:
                cola_queue.put("Error al acceder. Puede haberse ingresado y no detectar una etiqueta con el usuario")

        except TimeoutError or Exception:
            cola_queue.put("Ha ocurrido un error al intentar acceder a Splinterlands.com")

    def conexion_descarga_batallas(self, player):
        """Método que descarga desde la web de Splinterlands las batallas de un jugador accediendo por medio de una api
        disponible"""

        self.page_web.goto(f"https://api.splinterlands.com/battle/history?player={player}")
        self.page_web.wait_for_selector("pre", timeout=5000)

        datos = self.page_web.inner_text("pre")
        datos_recibidos = json.loads(datos)

        return datos_recibidos
