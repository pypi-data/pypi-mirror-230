__author__ = "Gonzalo Fernandez Suarez"

# Utils
import os
import regex as re
import time
import json
import difflib  # Search Better Match
from time import sleep
from enum import Enum
from PIL import Image, ImageDraw  # Captcha resolve dependecies
from .utils import (
    KillAllChromiumProcessOnLinux,
    KillAllChromiumProcessOnWindows,
    Singleton,
    Log,
    Input,
    check_binary_files_istalled,
)

# Selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# Use Chromium
from selenium.webdriver.chromium.service import ChromiumService
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.webdriver import ChromiumDriver

Locator = tuple[By, str]


class Browser(metaclass=Singleton):
    """
    Objeto responsable de interactuar con el navegador.\n
    ``Solo existe una instancia de este objeto.``\n
    Dependencias:
        - La enumeracion de ventanas "browser_windows" : necesario saber el numero de ventanas\n
          que se van a utilizar de antemano. Debe empezar desde 0 e ir ascendiendo de uno en uno\n
        - Variable de entorno ``OS`` : para indicar el sistema operativo, "linux" o "win".\n
    """

    def open(
        self,
        browser_windows: Enum,
        screenshots_path: str = os.path.dirname(
            os.path.abspath(__file__)) + "/screenshots",
        binary_folder: str = os.path.dirname(os.path.abspath(__file__)),
        short_wait_scs: int = 5,
        normal_wait_scs: int = 10,
        long_wait_scs: int = 20,
        disable_logging: bool = True,
        headless: bool = False,
        disable_save_passwords: bool = False,
        incognito: bool = False,
        start_maximize: bool = False,
        start_fullscreen: bool = False,
        configForDocker: bool = False,
        disable_translate: bool = False,
        disable_transitions: bool = False,
        window_position: dict['x':int, 'y':int] | None = None,
        window_size: dict['x':int, 'y':int] | None = None,
    ) -> None:
        BINARY_RELEASE_VERSION = "1.0.9"
        self.OS = os.getenv("OS")  # "linux" | "win"
        if self.OS == "linux":
            chromedriver_path = (
                binary_folder + "/bin-" + BINARY_RELEASE_VERSION + "/linux/chromedriver"
            )
            chromium_path = (
                binary_folder
                + "/bin-"
                + BINARY_RELEASE_VERSION
                + "/linux/chrome/chromium"
            )
            self.log_path = (
                binary_folder + "/bin-" + BINARY_RELEASE_VERSION + "/chromedriver.log"
            )
            check_binary_files_istalled(
                binary_folder, BINARY_RELEASE_VERSION, "/linux/chromedriver"
            )
        else:
            chromedriver_path = (
                binary_folder
                + "\\bin-"
                + BINARY_RELEASE_VERSION
                + "\\win\\chromedriver.exe"
            )
            chromium_path = (
                binary_folder
                + "\\bin-"
                + BINARY_RELEASE_VERSION
                + "\\win\\chrome\\chromium.exe"
            )
            self.log_path = (
                binary_folder + "\\bin-" + BINARY_RELEASE_VERSION + "\\chromedriver.log"
            )
            check_binary_files_istalled(
                binary_folder, BINARY_RELEASE_VERSION, "\\win\\chromedriver.exe"
            )
        self.screenshots_path = screenshots_path
        self.disable_transitions = disable_transitions
        self.log_read_index = 0
        options = ChromiumOptions()
        options.binary_location = chromium_path
        if disable_logging:
            options.add_argument("--disable-logging")
            options.add_experimental_option(
                "excludeSwitches", ["enable-logging"])
        if disable_save_passwords:
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            }
            options.add_experimental_option("prefs", prefs)
        if incognito:
            options.add_argument("--incognito")
        if start_maximize:
            options.add_argument("--start-maximized")
        if start_fullscreen:
            options.add_argument("--start-fullscreen")
        if window_size:
            options.add_argument("--window-size=" +
                                 window_size["x"] + "," + window_size["y"])
        if window_position:
            options.add_argument(
                "--window-position=" + window_position["x"] + "," + window_position["y"]
            )
        if configForDocker:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-dev-shm-usage")
        if disable_translate:
            options.add_argument("--disable-features=Translate")
        if headless and not configForDocker:
            options.add_argument("--headless")
        service = ChromiumService(
            chromedriver_path, service_args=[
                "--verbose", "--log-path=" + self.log_path]
        )
        browser_name = "goog"
        vendor_prefix = "goog"
        self.driver = ChromiumDriver(
            browser_name=browser_name,
            vendor_prefix=vendor_prefix,
            options=options,
            service=service
        )
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.normal_wait_scs = normal_wait_scs
        self.wait = WebDriverWait(self.driver, normal_wait_scs)
        self.shortWait = WebDriverWait(self.driver, short_wait_scs)
        self.longWait = WebDriverWait(self.driver, long_wait_scs)
        self.browser_windows = browser_windows
        self.windows_list = {}
        self.__registryNewWindow()
        for i in range(len(browser_windows) - 1):
            self.__openNewWindow()
        self.switchToWindow()

    def __openNewWindow(self) -> None:
        self.driver.execute_script("window.open();")
        self.__registryNewWindow()

    def __registryNewWindow(self) -> None:
        index = len(self.driver.window_handles) - 1
        new_window = {
            self.browser_windows(index).name: self.driver.window_handles[index]
        }
        self.windows_list.update(new_window)

    def __disableTransitions(self) -> None:
        """Desactiva las transiciones. Muy útil para antes de abrir pestañas con animaciones, etc..."""
        disable_transitions_script = """
        let css = ` * {
            -o-transition-property: none !important;
            -moz-transition-property: none !important;
            -ms-transition-property: none !important;
            -webkit-transition-property: none !important;
            transition-property: none !important;
            -o-transform: none !important;
            -moz-transform: none !important;
            -ms-transform: none !important;
            -webkit-transform: none !important;
            transform: none !important;
            -webkit-animation: none !important;
            -moz-animation: none !important;
            -o-animation: none !important;
            -ms-animation: none !important;
            animation: none !important;
        }`;
        head = document.head || document.getElementsByTagName('head')[0];
        style = document.createElement('style');
        style.type = 'text/css';
        head.appendChild(style);
        if (style.styleSheet){
        // This is required for IE8 and below.
            style.styleSheet.cssText = css;
        } else {
            style.appendChild(document.createTextNode(css));
        }
        """
        self.executeScript([], disable_transitions_script)

    def __clearLog(self) -> None:
        """Vacía el log del navegador"""
        open(self.log_path, "w").close()

    def __readLogNetworkEntries(self) -> list[dict]:
        """Lee el log del navegador y retorna una lista con las entradas.\n
        Devuelve una lista con diccionarios ``{ "documentURL": str, "requestId": str }``
        """
        matches = []
        with open(self.log_path, "r") as log_file:
            log = log_file.read()
        # https://regex101.com/r/C8PSqd/1
        patron = r"Network\.requestWillBeSent\s\(\w*=\w*\)\s\w*\s({.*?})\n\[\d*\.\d*\]\[DEBUG\]"
        matches = re.findall(patron, log, re.DOTALL)
        dicts = [json.loads(m) for m in matches]
        dicts = [{"documentURL": d["request"]["url"],
                  "requestId": d["requestId"]} for d in dicts]
        return dicts

    def getRequestResponseOf(self, url: str) -> dict:
        """Retorna un diccionario con el cuerpo de la ``última`` respuesta de la petición a ``url``\n
        o un diccionario vacío si no se encuentra la petición.\n
            ``{ "base64Encoded" : str , "body" : str }`` or ``{}``
        """
        self.waitForPageLoad()
        network = self.__readLogNetworkEntries()
        network.reverse()
        for request in network:
            if url in request["documentURL"]:
                return self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request["requestId"]})
        return {}

    def getAllRequestedURLS(self) -> list[dict]:
        network = self.__readLogNetworkEntries()
        return [request["documentURL"] for request in network]

    def goTo(self, url, disable_transitions=False) -> None:
        self.driver.get(url)
        if self.disable_transitions or disable_transitions:
            self.__disableTransitions()

    def getCurrentURL(self) -> str:
        return self.driver.current_url

    def sleep(self, seconds: float) -> None:
        sleep(seconds)

    def findElement(self, element: Locator, wait="normal") -> WebElement:
        if wait == "short":
            return self.shortWait.until(EC.presence_of_element_located(element))
        else:
            return self.wait.until(EC.presence_of_element_located(element))

    def findElements(self, elements: Locator, wait="normal") -> list[WebElement]:
        if wait == "short":
            return self.shortWait.until(
                EC.presence_of_all_elements_located(elements)
            )
        else:
            return self.wait.until(EC.presence_of_all_elements_located(elements))

    def hiddeElement(self, element: Locator) -> None:
        elem = self.findElement(element)
        self.executeScript([elem], 'args[0].style.display = "none";')

    def click(self, element: Locator | WebElement, wait="normal", maybe=False) -> None:
        def func():
            if wait in "long":
                self.longWait.until(EC.element_to_be_clickable(element)).click()
            elif maybe:
                self.shortWait.until(EC.element_to_be_clickable(element)).click()
            else:
                self.wait.until(EC.element_to_be_clickable(element)).click()
        if not maybe:
            return func()
        try:
            func()
        except:
            return

    def switchToFrame(self, frame: Locator = (By.XPATH, "/html")) -> None:
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(frame))
        """ self.driver.switch_to.frame(wait.until(EC.presence_of_element_located(frame))) """

    def waitForNewWindow(self) -> None:
        oldWindows = self.driver.window_handles
        self.wait.until(EC.new_window_is_opened(oldWindows))

    def waitForNumberWindows(self, number) -> None:
        self.wait.until(EC.number_of_windows_to_be(number))

    def getCurrentWindow(self) -> str:
        current_window_id = self.driver.current_window_handle
        for key, id in self.windows_list.items():
            if id == current_window_id:
                for page in self.browser_windows:
                    if page.name == key:
                        return page

    def switchToWindow(self, window=None) -> None:
        if window == None:
            w = self.browser_windows(0)
        else:
            w = window
        if (not window) or (self.getCurrentWindow() != window):
            self.driver.switch_to.window(self.windows_list[w.name])

    def clearCurrentWindow(self) -> None:
        self.driver.get("about:blank")

    def waitForPageLoad(self) -> None:
        """Espera a que la pagina termine de cargar"""
        loaded = False
        start_time = time.time()
        while not loaded and time.time() - start_time < self.normal_wait_scs:
            loaded = self.executeScript([], """return document.readyState === "complete";""")
            self.sleep(1)

    def close(self) -> None:
        self.driver.quit()
        if self.OS == "linux":
            KillAllChromiumProcessOnLinux()
        else:
            KillAllChromiumProcessOnWindows()
        self.__clearLog()

    def fullScreenshot(self, imageName) -> None:
        """ScreenShot a la pantalla y lo guarda en ``self.screenshots_path + "/" + imageName + ".png"``"""
        self.findElement((By.TAG_NAME, "body")).screenshot(
            self.screenshots_path + "/" + imageName + ".png"
        )

    def elementScreenshot(self, element: Locator, imageName) -> None:
        """ScreenShot a un elemento y lo guarda en ``self.screenshots_path + "/" + imageName + ".png"``"""
        self.findElement(element).screenshot(
            self.screenshots_path + "/" + imageName + ".png"
        )

    def executeScript(self, args=[], script="") -> any:
        """Ejecuta un script de javascript y retorna el resultado. \n
        Para acceder a los argumentos dentro del script \n
        utilizar la constante "args". \n
        Ejemplo:
        ```js
            console.log(args[0]); // Imprime el primer argumento
        ```
        """
        scriptSetup = "const args = arguments[0];\n"
        return self.driver.execute_script(scriptSetup + script, args)

    def scrollIntoView(self, element: WebElement) -> None:
        """Hace scroll hasta que el elemento sea visible"""
        self.executeScript(
            [element],
            'args[0].scrollIntoView({ behavior: "instant", block: "center",  inline: "center" });',
        )

    def scrollToBottom(self) -> None:
        """Hace scroll hasta el final de la pagina"""
        self.executeScript(
            [], "window.scrollTo(0, document.body.scrollHeight);")

    def scrollToTop(self) -> None:
        """Hace scroll hasta el principio de la pagina"""
        self.executeScript([], "window.scrollTo(0, 0);")

    def handleCaptcha(self, captcha_iframe_xPath: str) -> None:
        def solveCaptcha():
            # Comprobamos si es de 3x3 o 4x4
            tiles_list = self.findElements((By.CLASS_NAME, "rc-imageselect-tile"))
            if len(tiles_list) == 16:
                matrix_size = 4
                x_offset = 113
                y_offset = 103
            else:
                matrix_size = 3
                x_offset = 136
                y_offset = 134
            Log("Tamaño de captcha : ", matrix_size, " x ", matrix_size)
            self.fullScreenshot("robot_image")
            # Recortamos la imagen
            img = Image.open(self.screenshots_path + "/robot_image.png")
            draw = ImageDraw.Draw(img)
            count = 1
            for row in range(matrix_size):
                for col in range(matrix_size):
                    position = (4 + ((col) * x_offset), 127 + (row * y_offset))
                    text = "(" + str(count) + ")"
                    bbox = draw.textbbox(position, text)
                    draw.rectangle(bbox, fill="black")
                    draw.text(position, text, fill="red")
                    count += 1
            img.save(self.screenshots_path +
                     "/robot_image_text.png", format="png")
            Log("Por favor, resuelve el captcha y pulsa enter")
            Log("imagen => <API URL>/image/robot_image_text")
            Log("Formato: numeros separados por puntos o comas ")
            blocks_to_click: list[int] = []
            while True:
                try:
                    str_input = Input()
                    if str_input == "":
                        continue
                    str_input = str_input.replace(" ", "").strip()
                    str_input = str_input.replace(",,", ",")
                    str_input = str_input.replace(".", ",")
                    str_input = str_input.split(",")
                    max = 1
                    min = 1
                    for number in str_input:
                        if int(number) > max:
                            max = int(number)
                        if int(number) < min:
                            min = int(number)
                        if int(number) not in blocks_to_click:
                            blocks_to_click.append(int(number))
                    if (max <= count - 1) and (min >= 1):
                        break
                    else:
                        raise Exception("Números fuera de rango")
                except Exception:
                    Log("Por favor, escribe un numero entre 1 y ", count - 1)
                    str_input = None
            Log("Clickando en los cuadrados: ", blocks_to_click)
            for index in blocks_to_click:
                tiles_list[index - 1].click()
                self.sleep(0.5)
            self.click((By.XPATH, '//*[@id="recaptcha-verify-button"]'))
            Log("Comprobando...")
            self.sleep(6)
            try:
                tiles_list = self.findElements((By.CLASS_NAME, "rc-imageselect-tile"), wait="short")
                if (not tiles_list) or (len(tiles_list) == 0):
                    raise Exception("Captcha resulto")
            except Exception:
                Log("Captcha resuelto  ✔️")
                return
            Log("Captcha no resuelto aún, intentando de nuevo")
            solveCaptcha()
            return
        self.switchToFrame((By.XPATH, captcha_iframe_xPath))
        solveCaptcha()
        self.switchToFrame()

    def markElement(self, element: Locator | WebElement, width=4, color="red") -> None:
        """Marca un elemento con un borde de color rojo"""
        if not isinstance(element, WebElement):
            element = self.findElement(element)
        self.executeScript(
            [element],
            'args[0].style.border = "' +
            str(width) + "px solid " + color + '";',
        )

    def addCss(self, css: str) -> None:
        """Añade css a la pagina"""
        script = """
        const css = `""" + css + """`;
        const head = document.head || document.getElementsByTagName('head')[0];
        const style = document.createElement('style');
        style.type = 'text/css';
        if (style.styleSheet){
        // This is required for IE8 and below.
            style.styleSheet.cssText = css;
        } else {
            style.appendChild(document.createTextNode(css));
        }
        head.appendChild(style);
        """
        self.executeScript([], script)

    class FromContainer():
        def __init__(self, container: Locator | WebElement):
            self.b = Browser()
            if isinstance(container, WebElement):
                self.container: WebElement = container
            else:
                self.container: WebElement = self.b.findElement(container)

        def clickBetterMatch(
            self,
            target_buttons: Locator,
            target_text: str,
            format_button_text=None,
        ) -> bool:
            """
            Busca un botón con el texto mas similar a ``text`` en los ``target_buttons`` y hace click. \n
            Retorna true si lo encuentra, false si no.
            """
            self.b.markElement(self.container)
            target_buttons = self.container.find_elements(
                target_buttons[0], target_buttons[1]
            )
            if format_button_text:
                target_buttons_text = list(
                    map(lambda x: format_button_text(x.text), target_buttons)
                )
            else:
                target_buttons_text = list(
                    map(lambda x: x.text, target_buttons))
            better_matches = difflib.get_close_matches(
                target_text, target_buttons_text, n=1, cutoff=0.6
            )
            if not better_matches:
                return False
            match = better_matches[0]
            match_index = target_buttons_text.index(match)
            self.b.scrollIntoView(target_buttons[match_index])
            self.b.click(target_buttons[match_index])
            return True

        def clickBetterMatchFromCollapsedList(
            self,
            collapsed_buttons: Locator,
            target_buttons: Locator,
            target_text: str,
        ) -> bool:
            """
            Busca un botón con el texto mas similar a ``text`` dentro de la lista de pestañas/dropdowns (``tabs``) y lo clicka.\n
            Retorna true si lo encuentra, false si no.
            """
            self.b.markElement(self.container)
            collapsed_list = self.container.find_elements(
                collapsed_buttons[0], collapsed_buttons[1])
            for c in collapsed_list:
                self.b.scrollIntoView(c)
                self.b.click(c)
            target_buttons_list = self.container.find_elements(
                target_buttons[0], target_buttons[1]
            )
            target_buttons_text = list(
                map(lambda b: b.text, target_buttons_list))
            better_matches = difflib.get_close_matches(
                target_text,
                target_buttons_text,
                n=1,
                cutoff=0.5
            )
            if not better_matches:
                return False
            match_index = target_buttons_text.index(better_matches[0])
            target_button = target_buttons_list[match_index]
            self.b.scrollIntoView(target_button)
            self.b.click(target_button)
            return True

        def mapListOfElements(self, elements: Locator, func) -> list:
            """
            Aplica una función a cada elemento de la lista y retorna una lista con los resultados. \n
            """
            self.b.markElement(self.container)
            elements = self.container.find_elements(
                elements[0], elements[1])
            return list(map(func, elements))

        def findElementWithText(self, elements: Locator, target_text) -> WebElement | None:
            """
            Busca un elemento dentro de un contenedor que contenga el texto ``text``. \n\n
            ``if target_text in element.text :``\n
            Si no lo encuentra retorna None. \n
            """
            elements = self.container.find_elements(
                elements[0], elements[1])
            for element in elements:
                if target_text in element.text:
                    return element
            return None
