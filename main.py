#Importamos la libreria telegram para hacer el envio de las ofertas.
import telebot
from telebot import types
from computrabajo_anuncios_chile import ws_computrabajo_chile
from getonboard_anuncios_chile import ws_getonboard

#Tiempo
import time
import datetime as dt
#Librerias para extraccion de datos
from bs4 import BeautifulSoup as soup
import requests
from threading import Thread

#Libreria para llevar el registro:
import logging
#Libreria para conexion con MySQl e ingesta de calificaciones
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


#Token para nuestro BOT
TOKEN = "Tu_token"


#INSTANCIAMOS el bot
bot = telebot.TeleBot(TOKEN)

#emojis - Banderas
emoji_bandera_argentina = "\U0001F1E6\U0001F1F7"
emoji_bandera_chile = "\U0001F1E8\U0001F1F1"
emoji_bandera_colombia = "\U0001F1E8\U0001F1F4"
emoji_bandera_peru = "\U0001F1F5\U0001F1EA"

#Emojis
emoji_estrella_bright = "\U0001F31F"

#Variable para llevar un registro del estado actual
estado = None
dia = ""

# Configura el registro (logging)
logging.basicConfig(filename='bot.log', level=logging.INFO)

# Creamos la conexión a la base de datos MySQL
mysql_engine = create_engine("La_Informacion_de_tu_DB")

#Instanciamos declarative_base()
Base = declarative_base()


class Calificacion(Base):
    __tablename__ = 'calificaciones'
    
    idcalificaciones = Column(Integer, primary_key=True)
    fecha = Column(String(45))
    nombre = Column(String(45))
    apellido = Column(String(45))
    calificacion = Column(Integer)
    comentario = Column(String(500))
    

# Crea la tabla si no existe
Base.metadata.create_all(mysql_engine)

# Función para manejar el comando /calificar
@bot.message_handler(commands=["calificar"])
def calificar(message):
    bot.send_message(message.chat.id, "Por favor califica el BOT en General:")
    bot.send_message(message.chat.id, "1 > Muy malo\n2 > Malo\n3 > Normal\n4 > Bueno\n5 > Muy bueno")

# Función para manejar las respuestas de calificación
@bot.message_handler(func=lambda message: message.text in ("1", "2", "3", "4", "5"))
def comentario(message):
    try:
        puntuacion = int(message.text)
        
        #Solicita un comentario al usuario
        bot.send_message(message.chat.id, "Por favor, ingresa un comentario en base a lo que te parecio el BOT")
        bot.register_next_step_handler(message, guardar_calificacion, puntuacion)

    except ValueError:
        bot.send_message(message.chat.id, "Por favor, ingresa un número del 1 al 5.")


def guardar_calificacion(message, puntuacion):
    try:
        
        # Guarda la puntuación en la base de datos
        comentario = message.text
        nombre = message.from_user.first_name
        apellido = message.from_user.last_name
        session = sessionmaker(bind=mysql_engine)()
        nueva_calificacion = Calificacion(fecha=dt.datetime.now(), nombre=nombre, apellido=apellido, calificacion=puntuacion, comentario=comentario)
        session.add(nueva_calificacion)
        session.commit()
        session.close()
        bot.send_message(message.chat.id, f"Muchas gracias {nombre}, tu puntuacion y comentario nos ayuda a mejorar la informacion e interfaz del BOT")
    except Exception as e:
        bot.send_message(message.chat.id, "Hubo un error al guardar tu calificación y comentario. Por favor, inténtalo de nuevo.")


@bot.message_handler(commands=["start"])
def cmd_inicio(message):
    global dia
    #Da la bienvenida al usuario
    bot.reply_to(message, f"Hola! Me llamo Katherine {emoji_estrella_bright}.\nFui creada por Michel Villot para ayudarte en tu busqueda de ofertas laborales.")

    #Creamos el markup
    markup = types.InlineKeyboardMarkup(row_width=1)
    #Opciones
    # argentina = types.InlineKeyboardButton(f"Argentina {emoji_bandera_argentina} ", callback_data="argentina")
    chile = types.InlineKeyboardButton(f"Chile {emoji_bandera_chile}", callback_data="chile")
    # colombia = types.InlineKeyboardButton(f"Colombia {emoji_bandera_colombia}", callback_data="colombia")
    # peru = types.InlineKeyboardButton(f"Peru {emoji_bandera_peru}", callback_data="peru")
    
    #Agregamos las opciones al Menu
    markup.add(chile)

    #Elegimos el pais
    bot.send_chat_action(message.chat.id, "typing", timeout=60)
    bot.send_message(message.chat.id, "Por favor selecciona un portal de empleos", reply_markup=markup)
    # bot.send_message(messag111e.chat.id, f"Has seleccionado el país: {message.text}")
    print(f"Nombre y Apellido: {message.from_user.first_name} {message.from_user.last_name}")
    dia = dt.datetime.now()
    print(f"Hora de Conexion: {dia.time().strftime('%H:%M')}")



@bot.callback_query_handler(func=lambda call:True)
def pais(call):
    global estado
    if call.data == "chile":
        estado = "chile"
        print(f"Pais Seleccionado: {call.data}")
        bot.send_message(call.message.chat.id, f"Seleccionaste: {call.data.upper()}")
        
        markup = types.InlineKeyboardMarkup(row_width=1)

        #chiletrabajos = types.InlineKeyboardButton(f"Chile Trabajos", callback_data="chiletrabajos")      
        computrabajo = types.InlineKeyboardButton(f"CompuTrabajo", callback_data="computrabajo")
        getonboard = types.InlineKeyboardButton(f"GetonBoard", callback_data="getonboard")
        #indeed = types.InlineKeyboardButton(f"Indeed", callback_data="indeed")
        #linkedin = types.InlineKeyboardButton(f"LinkedIn", callback_data="linkedin")

        #Agregamos las opciones al Menu
        markup.add(computrabajo, getonboard)
        bot.send_message(call.message.chat.id, "Por favor selecciona el portal que deseas consultar", reply_markup=markup)

    if call.data == "computrabajo":
        #Generamos 
        estado = "computrabajo"
        print(f"Portal Seleccionado: {call.data}")
        bot.send_message(call.message.chat.id, "VALIDACION")
        bot.send_message(call.message.chat.id, "Escribe la palabra computrabajo").text.lower()   

        

    if call.data == "getonboard":
        estado = "getonboard"
        print(f"Portal Seleccionado: {call.data}")
        bot.send_message(call.message.chat.id, "VALIDACION")
        bot.send_message(call.message.chat.id, "Escribe la palabra getonboard").text.lower()
        @bot.message_handler(func=lambda message: message.text.lower() == "getonboard")
        def bot_mensaje_cargo_getonboard_1(message):
            bot.send_chat_action(message.chat.id, "typing")
            bot.send_message(message.chat.id, "Por favor ingresa el cargo a buscar en GetonBoard")
            print(f"Cargo: {message.text}")
            


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global estado
    if (estado == "computrabajo") and (message.text == "computrabajo" or message.text == "Computrabajo"):
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "Por favor ingresa el cargo a buscar en Computrabajo")
        estado = "computrabajo_cargo"
        


    elif (estado == "getonboard") and (message.text.lower() == "getonboard"):
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "Por favor ingresa el cargo a buscar en GetonBoard")
        estado = "getonboard_cargo"
        
        

    elif estado == "computrabajo_cargo":
        print(f"Cargo: {message.text}")
        bot.send_message(message.chat.id, f"El BOT está extrayendo información en tiempo real, esto podria tardar hasta 1 minuto. \n\n CARGO: {message.text} \n\nEstos son los 10 anuncios más recientes de {message.text} en CompuTrabajo")
        bot.send_message(message.chat.id, ws_computrabajo_chile(message.text), disable_web_page_preview=True)
        # Manejar la búsqueda en CompuTrabajo aquí
        # Cuando termines, regresa el estado a None para permitir otras opciones
        print(f"Web Scraping finalizado para: {message.from_user.first_name} {message.from_user.last_name}")
        estado = None

    elif estado == "getonboard_cargo":
        print(f"Cargo: {message.text}")
        # Manejar la búsqueda en GetonBoard aquí
        bot.send_message(message.chat.id, f"El BOT está extrayendo información en tiempo real, esto podria tardar hasta 1 minuto. \n\n CARGO: {message.text} \n\nEstos son los 10 anuncios más recientes de {message.text} en GetonBoard")
        bot.send_message(message.chat.id, ws_getonboard(message.text), disable_web_page_preview=True)
        print(f"Web Scraping finalizado para: {message.from_user.first_name} {message.from_user.last_name}")
        # Cuando termines, regresa el estado a None para permitir otras opciones
        estado = None




# #MAIN
if __name__ =="__main__":
    print("Iniciando el Bot")
    bot.infinity_polling()
    print("Finalizando el Bot")


