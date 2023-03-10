import hashlib
import os
import time
import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging
import tkinter as tk
import threading
import sys
from threading import Thread
from tkinter.scrolledtext import ScrolledText
from win10toast import ToastNotifier
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import random
from  tkinter import *
import tkinter.filedialog as tkFileDialog




# GLOBALS
configDict = dict()
filesAndHashes = dict()
newFilesAndHashes = dict()
badIntegrity = list()
graphDate = list()
numberOfGoodIntegrity = list()
numberOfBadIntegrity = list()
directorio=str()
cantidadDeArchivos = [0, 1000]
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
interval = 0
running = bool()
window = tk.Tk()
window.geometry("1340x512")
window.resizable(0, 0)
window.title("HIDS G8 PAI 1")
entry = ScrolledText(window, width=80, height=20)
logBox = ScrolledText(window, width=80, height=20)
toaster = ToastNotifier()
salt = random.randint(0,10000)

switch_value = True
currentThemeBG = "#26242f"
currentThemeFont = "white"
lista_hashes = ["sha3_256", "sha3_384", "sha3_512", "sha_256", "sha_512", "shake_128", "shake_256"]
valor_seleccionado = tk.StringVar(window)
valor_seleccionado.set("sha_256")

lista_intervalos = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
intervalo_seleccionado = tk.StringVar(window)
intervalo_seleccionado.set("10")


def folderHash(pathName):       ## esta función te permite seleccionar el tipo de hasheo en función del texto que se le pasa sobre la carpeta especificada
    """ Params: ruta """
    """ Return: devuelve un diccionario formato por la ruta y el hash: key=ruta, value=hash """
    """ Se le pasa una ruta y viaja por todos los archivos y las subrutas de dicha ruta y calcula los hashes
    de cada uno de los archivos encontrados """

    global salt

    fileAndHash = dict()
    for root, dirs, files in os.walk(pathName):
        for file in files:
            with open(os.path.join(root, file), "rb") as fileRaw:
                if(valor_seleccionado.get() == "sha3_256"):  ## a cambiar cuando se haga por una lista con las diferentes opciones
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.sha3_256(
                        fileRaw.read()).hexdigest()
                elif(valor_seleccionado.get() == "sha3_384"):                       ##valor_seleccionado.get()
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.sha3_384(
                        fileRaw.read()).hexdigest()
                elif(valor_seleccionado.get() == "sha3_512"):
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.sha3_512(
                        fileRaw.read()).hexdigest()
                elif(valor_seleccionado.get() == "sha_256"):
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.sha256(
                        fileRaw.read()).hexdigest()
                elif(valor_seleccionado.get() == "sha_512"):
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.sha512(
                        fileRaw.read()).hexdigest()
                elif(valor_seleccionado.get() == "shake_128"):
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.shake_128(
                        fileRaw.read()).hexdigest(salt)
                elif(valor_seleccionado.get() == "shake_256"):
                    fileAndHash[os.path.join(root, file).replace("\\", "/")] = hashlib.shake_256(
                        fileRaw.read()).hexdigest(salt)
    return fileAndHash


def readLogFile():  ## creo que es prescindible, se podría acceder manualmente al log y nos haría algo mas diferente a este proyecto
    text = str()
    if (os.path.exists(os.path.join('c:/top_secret', 'log.log'))):
        with open(os.path.join('c:/top_secret', 'log.log')) as reader:
            text = reader.read()
    else:
        f = open(os.path.join('C:\\top_secret', 'log.log'), "x")
    return text


def logBoxContainer():  ## npi de lo que hace
    logBox.delete("1.0", tk.END)
    text = readLogFile()
    logBox.insert(tk.INSERT, text)
    logBox.insert(tk.END, "")


def importConfig():   ## explicado en el comentario 
    """ Params: NONE """
    """ Return: NONE """
    """ Crea un archivo de configuración si no lo hay con las opciones de la plantilla de 'configs'
    y en caso de que ya exista (que sería siempre menos la primera vez que se ejecute el script)
    carga la configuración de dicho archivo y la importa al diccionario del script llamado 'configDict',
    mediante este diccionario vamos a poder manejar dichas opciones indicadas en el archivo de configuración"""
    path = os.path.abspath('.').split(os.path.sep)[
        0]+os.path.sep+"top_secret\config.config"
    if (os.path.exists(path)):
        try:
            with open(path, "r") as config:
                for line in config:
                    if "#" not in line:
                        confSplitted = line.split("=")
                        configDict[confSplitted[0].strip(
                        )] = confSplitted[1].strip()

                        entry.insert(tk.INSERT, confSplitted[0].strip(
                        ) + "=" + confSplitted[1].strip() + "\n")

                    else:
                        entry.insert(tk.INSERT, line)
                    entry.insert(tk.END, "")
            logging.info("La configuración se ha importado correctamente!")
            # entry.insert(tk.END, " in ScrolledText")
            # print(configDict)
        except:
            logging.error("Error al importar la configuración!")
    else:
        configs = ["\n"]
        try:
            with open(os.path.abspath('.').split(os.path.sep)[0]+os.path.sep+"top_secret\config.config", "w") as file:
                file.write(
                    "# Pasos a seguir para hacer funcionar la aplicación.\n# Elegir un directorio que vigilar con el botón seleccionar directorio\n# Seleccionar del menú desplegable el hash a utilizar\n# Seleccionar el intervalo de tiempo entre examenes en segundos\n# Iniciar el examen lanza el programa con la configuración establecida\n# Para pararlo, finalmente pulsar parar el examen\n# Abrir gráfico histórico muestra los errores de todo el log\n# Abrir último gráfico muestra una representación del último log guardado en el fichero")
                for config in configs:
                    file.write(config)
            logging.info("Archivo de configuración creado satisfactoriamente!")

        except:
            logging.error(
                "Error al crear el archivo de configuración, problema con los permisos?")
        importConfig()


def exportHashedFiles():  ## vale, esta parece ser la función que guarda los hashes
    """ Params: NONE """
    """ Return: NONE """
    """ Comprueba las rutas que hemos indicado en el archivo de configuración y carga todos los archivos de cada una
    de ellas gracias a la función anterior 'folderHash', una vez hecho esto crea un archivo 'hashes.hash' si no lo hay y escribe
    en el todas las rutas junto a su hash, separadas mediante un simbolo '=' """
    # TIME
    begin_time = datetime.datetime.now()
    splittedPathsToHash = configDict["Directories to protect"].split(
        ",")  # para ser mejor, hacer strip con un for para cada elemento por si acaso
    for path in splittedPathsToHash:
        filesAndHashes.update(folderHash(path))
    with open(os.path.abspath('.').split(os.path.sep)[0]+os.path.sep+"top_secret\hashes.hash", "w") as writer:
        for key, value in filesAndHashes.items():
            writer.write(key + "=" + value + "\n")
    end = datetime.datetime.now() - begin_time
    strr = "Hashes exportados correctamente en: " + str(end)
    logging.info(strr)


def importHashedFiles():  ## este es el que coge los hashes y los mete en un diccionario
    """ Params: NONE """
    """ Return: NONE """
    """ Lee el archivo 'C:\top_secret\hashes.hash' y carga cada una de las entradas en el diccionario 'newFilesAndHashes' presente en el script """
    try:
        with open(os.path.abspath('.').split(os.path.sep)[0]+os.path.sep+"top_secret\hashes.hash", "r") as reader:
            line = reader.readline()
            while line:
                splittedLineList = line.split("=")
                newFilesAndHashes[splittedLineList[0].replace(
                    "\n", "")] = splittedLineList[1].replace("\n", "")
                line = reader.readline()
        logging.info("Hashes importados correctamente!")
    except:
        logging.error("Error al importar los hashes!")
        # print(newFilesAndHashes)


def calculateHashedFiles():  ## esta es la segunda vuelta de cálculos de hashees
    """ Params: NONE """
    """ Return: NONE """
    """ Calcula los hashes de los archivos nuevamente, y reutilizamos el diccionario creado al principio 'filesAndHashes' esto servirá
    para comparar los items de este diccionario con los del 'newFilesAndHashes'. """

    logging.info("Calculando los hashes de los archivos...")
    splittedPathsToHash = configDict["Directories to protect"].split(
        ",")  # para ser mejor, hacer strip con un for para cada elemento por si acaso
    for path in splittedPathsToHash:
        filesAndHashes.update(folderHash(path))
    strr = "Hashes calculados satisfactoriamente!"


def compareHashes():  ## comparador de hashes para comprobar que los archivos no se hayan modificado
    """ Params: NONE """
    """ Return: NONE """
    """ Compara los dos diccionarios, uno contiene los hashes cargados del archivo hashes.hash y el otro contiene los hashes recien calculados,
    tras dicha comparación los resultados saldran por consola """
    numberOfFilesOK = int()
    numberOfFilesNoOk = int()
    listOfNoMatches = list()
    for key, value in filesAndHashes.items():
        if newFilesAndHashes[key] == value:
            numberOfFilesOK += 1
        else:
            numberOfFilesNoOk += 1
            cadena = "DIR: " + str(key) + " ¡Los hashes no coinciden!"
            listOfNoMatches.append(cadena)
    badIntegrity.append(numberOfFilesNoOk)
    numberOfGoodIntegrity.append(numberOfFilesOK)
    numberOfBadIntegrity.append(numberOfFilesNoOk)
    graphDate.append(datetime.datetime.now().strftime("%M"))
    str1 = "Número de archivos OK: " + str(numberOfFilesOK)
    str2 = "Número de archivos MODIFICADOS: " + str(numberOfFilesNoOk)
    logging.info(str1)
    logging.info(str2)
    if(listOfNoMatches):
        str3 = "Archivos con integridad comprometida: "
        noMatchesToPrint = list()
        for entry in listOfNoMatches:
            noMatchesToPrint.append("           "+entry)
        logging.warning(str3 + "\n" + '\n'.join(noMatchesToPrint))
        toaster.show_toast(
            "HIDS", "Hay un problema integridad. Revisar LOG.", duration=interval, threaded=True)
    else:
        toaster.show_toast(
            "HIDS", "Examen finalizado. Se mantiene la integridad.", duration=interval, threaded=True)


def graph():  ## creo que no es intrinsecamente necesaria para el programa
    """ Params: NONE """
    """ Return: NONE """
    """ Muestra una gráfica en el navegador en base a los datos de las dos listas 'badIntegrity' y 'graphDate' """
    layout_title = "Evolución de la integridad de los archivos fecha:  " + \
        str(datetime.datetime.now().strftime("%d-%m-%Y"))
    df = pd.DataFrame(dict(
        x=graphDate,
        y=badIntegrity
    ))
    fig = px.bar(df,
                 x='x', y='y',
                 color_discrete_sequence=[
                     'red']*3,
                 title=layout_title,
                 labels={'x': 'Hora', 'y': 'Numero de fallos de integridad'})
    fig.show()

def graph2():  ## muestra grafico con forma de queso de los archivos
    
    labels = 'Archivos Ok','Archivos modificados'
    sizes = [numberOfGoodIntegrity[-1],numberOfBadIntegrity[-1]]
    fig, ax = plt.subplots()
    def func(pct, allvals):
        absolute = int(np.round(pct/100.*np.sum(allvals)))
        return f"{pct:.1f}%\n({absolute:d})"
    ax.pie(sizes, labels=labels,autopct=lambda pct: func(pct, sizes))
    ax.set_title("Grafico de la integridad de los archivos\n"+"Numero Total de archivos:"+str(numberOfGoodIntegrity[-1]+numberOfBadIntegrity[-1])+"\nNúmero de archivos OK:"+str(numberOfGoodIntegrity[-1])
          +"\nNúmero de archivos modificados:"+str(numberOfBadIntegrity[-1]))
    
    plt.show()


def run():  ## empieza a llamar a las funciones en serie en el momento en que se invoca
    """ Params: NONE """
    """ Return: NONE """
    """  """
    if running == True:
        begin_time = datetime.datetime.now()
        calculateHashedFiles()
        compareHashes()
        logBox.config(state=tk.NORMAL)
        logBoxContainer()  # AQUI EL LOG BOX
        logBox.config(state=tk.DISABLED)
        # graph()
        threading.Timer(float(interval), run).start()
        end = datetime.datetime.now() - begin_time
        strr = "Comprobación realizada con éxito en: " + str(end)
        logging.info(strr)


def runHandle():  ## npi, creo que es importante, creo que es lo que decide el número de hilos del procesador a usar
    t = Thread(target=run)
    global running
    running = True
    t.start()


def initExam():  ## parece una prueba de los logs y tal
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(100)
    root_logger = logging.getLogger("")
    root_logger.addHandler(console)
    global interval
    interval = int(intervalo_seleccionado.get())
    # supuestamente el admin nos pasa a nosotros el hasheado de todos los archivos -> Si no, ejecutar exportHashedFiles()
    exportHashedFiles()
    importHashedFiles()
    runHandle()

def theme_swap():
    global switch_value
    global currentThemeBG
    global currentThemeFont
    
    if switch_value == True:
        currentThemeBG = "white"
        currentThemeFont = "black"
        switch_value = False
    else:
        currentThemeBG = "#26242f"
        currentThemeFont = "white"
        switch_value = True

    gui() ##si no se vuelve a llamar a GUI por algún motivo no refresca el cambio de tema

def openDirectory():
    directorio = tkFileDialog.askdirectory()
    norm_path = os.path.normpath(directorio)
    configDict["Directories to protect"]=norm_path

def gui():
    global switch_value
    global currentThemeBG
    global currentThemeFont

    btnTheme = tk.Button(window, bg=currentThemeBG, text="cambiar tema", fg=currentThemeFont, command=theme_swap)
    btnTheme.pack(pady=15, padx=15)
    btnTheme.place(x=1230, y=435)

    question_menu = tk.OptionMenu(window,valor_seleccionado,*lista_hashes)
    question_menu.pack(pady=15, padx=15)
    question_menu.place(x=570, y=330)
    question_menu.config(bg=currentThemeBG, fg=currentThemeFont)

    btnDirectory = tk.Button(window, bg=currentThemeBG, text="Seleccionar directorio", fg=currentThemeFont, command=openDirectory)
    btnDirectory.pack(pady=15, padx=15)
    btnDirectory.place(x=600, y=380)

    interval_menu = tk.OptionMenu(window,intervalo_seleccionado,*lista_intervalos)
    interval_menu.pack(pady=15, padx=15)
    interval_menu.place(x=670, y=330)
    interval_menu.config(bg=currentThemeBG, fg=currentThemeFont)

    labelConf = tk.Label(window, bg=currentThemeBG, text="Información", fg=currentThemeFont, font=("Arial", 14))
    labelLog = tk.Label(window, bg=currentThemeBG, text="Fichero de log en tiempo real", fg=currentThemeFont, font=("Arial", 14))
    labelConf.pack()
    labelConf.place(x=230, y=333)
    labelLog.pack()
    labelLog.place(x=870, y=333)
    entry.pack()
    entry.config(bg=currentThemeBG, fg=currentThemeFont)
    entry.place(x=5, y=0)
    window.config(bg=currentThemeBG)
    btnGraphLatest = tk.Button(window, bg=currentThemeBG, text="Abrir último gráfico", fg=currentThemeFont, command=graph2)
    btnGraphLatest.pack(pady=15, padx=15)
    btnGraphLatest.place(x=670, y=455)
    btnGraphHistoric = tk.Button(window, bg=currentThemeBG, text="Abrir grafico histórico", fg=currentThemeFont, command=graph)
    btnGraphHistoric.pack(pady=15, padx=15)
    btnGraphHistoric.place(x=530, y=455)
    btnIniciar = tk.Button(window, bg=currentThemeBG, text="Iniciar el examen", fg=currentThemeFont, command=initExam)
    btnIniciar.pack(pady=15, padx=15)
    btnIniciar.place(x=420, y=455)
    btnDetener = tk.Button(window, bg=currentThemeBG, text="Parar el examen", fg=currentThemeFont, command=stop)
    btnDetener.pack(pady=15, padx=15)
    btnDetener.place(x=795, y=455)
    logBox.pack()
    logBox.config(bg=currentThemeBG, fg=currentThemeFont)
    logBox.place(x=670, y=0)
    window.protocol("WM_DELETE_WINDOW", stopAndClose)

    window.mainloop()

def stop():  ## entiendo que esto es por si peta
    toaster.show_toast(
        "HIDS", "Servicio interrumpido. El sistema NO está examinando los directorios.", threaded=True)
    global running
    running = False
    logging.critical("EXAMEN INTERRUMPIDO")


def stopAndClose():  ## entiendo que esto es por si lo quieres cerrar mid process
    global running
    running = False
    logging.critical("HIDS CERRADO")
    os._exit(1)


def iniciar():  ## no entiendo que hace exactamente, parece que coge el path absoluto y lo mete en el log?
    try:
        Path("C:\\top_secret").mkdir(parents=True)
    except:
        pass
    readLogFile()
    filename = os.path.abspath('.').split(os.path.sep)[
        0]+os.path.sep+"top_secret\log.log"
    logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', filename=filename, level=logging.INFO)
    importConfig()
    gui()

if __name__ == "__main__":
    iniciar()