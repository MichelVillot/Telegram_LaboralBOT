#Importamos las librerias necesarias

#Librerias para extraccion de datos
from bs4 import BeautifulSoup as soup
import requests

#Librerias para manipulacion de datos.
import pandas as pd
import numpy as np

#Libreria para acortar URL
import pyshorteners
#Libreria de tiempo
from datetime import datetime, timedelta
import time

#Librerias para visualizaciones
import seaborn as sns
import matplotlib.pyplot as plt

#Display 6 registros
pd.options.display.min_rows = 6


def ws_getonboard(palabra_clave):
    palabra_clave = palabra_clave

    #url de Getonboard
    url = f"https://www.getonbrd.com/empleos-{palabra_clave}"


    #headers para que no detecten el web scraping
    headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

    #Instanciamos la libreria requests en una variable y adicional hacemos la consulta.
    response = requests.get(url, headers=headers)

    #Hacemos un condicional donde indica que si el estatus es = 200 entonces utilice bs4 para extraer el text en formato "html.parser"
    if response.status_code == 200:
        pageSoup = soup(response.text, "html.parser")

    #buscamos todos los enlaces
    enlaces = pageSoup.find_all("a", href=True)

    #creamos una lista
    lista_links_raw = []

    #recorremos los enlaces para extraer uno por uno y asi agregarlo a la lista de los links:
    for enlace in enlaces:
        lista_links_raw.append(enlace["href"])


    #Depuramos la lista de los links: En getonboard a partir del "link" 21 es que inician los verdaderos links para ingresar a las ofertas laborales.
    lista_links_raw = lista_links_raw[20:]
    lista_links_depurada = []



    #Recorremos la lista de los links para remover la informacion que no usaremos.
    for indice, elemento in enumerate(lista_links_raw):
        if "getonbrd" in lista_links_raw[indice]:
            lista_links_depurada.append(elemento)
        else:
            break

    # Creamos el Dataframe para poder ingestar la informacion que necesitamos de una vez ya que extraer senority y contrato directamente en la oferta se complica.
    df = pd.DataFrame(data = "-", index=range(len(lista_links_depurada)), columns=["cargo", "empresa", "rango_salario", "postulaciones", "ubicacion","lugar_empleo", "remoto_pre_hibrid", "senority", "tipo_contrato", "link"])

    for indice, elemento in enumerate(lista_links_depurada):
        #Extraemos el senority
        senority = pageSoup.find_all("span", class_="opacity-half")
        senority = str(senority[indice])
        inicio = senority.find(">")+1
        final = senority.find("dot")-14
        senority = senority[inicio:final]
        df.loc[indice, "senority"] = senority

        #Extraemos si es tiempo completo.
        tipo_contrato = pageSoup.find_all("span", class_="opacity-half")
        tipo_contrato = str(tipo_contrato[indice])
        inicio = tipo_contrato.find("</span")+8
        final = len(tipo_contrato)-7
        tipo_contrato = tipo_contrato[inicio:final]
        df.loc[indice, "tipo_contrato"] = tipo_contrato
    
    #iteramos sobre los primeros 20 elementos de la lista
    for indice, elemento in enumerate(lista_links_depurada[:20]):
        #
        url = lista_links_depurada[indice]

        #headers para que no detecten el web scraping
        headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                }

        #Instanciamos la libreria requests en una variable y adicional hacemos la consulta.
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pageSoup = soup(response.text, "html.parser")
            
        #Ingesta del link
        type_tiny = pyshorteners.Shortener()
        url = type_tiny.tinyurl.short(elemento)
        df.loc[indice, "link"] = url

        #Extraccion del Cargo RAW
        cargos = pageSoup.find("h1", class_="gb-landing-cover__title mb1")
        cargo = list(cargos)[1].string

        #Extraccion del cargo Depurado
        cargo = cargo.replace("\n", "")
        df.loc[indice, "cargo"] = cargo



        # #Extraccion del nombre de la empresa RAW
        empresas = pageSoup.find("h1", class_="gb-landing-cover__title mb1")
        empresa = list(empresas)[3].string

        # #Extraccion del nombre de la empresa Depurado
        empresa = empresa.replace("\n", "")
        empresa = empresa[2:]
        df.loc[indice, "empresa"] = empresa



        #Extraccion del rango salarial RAW
        salarios = pageSoup.find("span", class_="tooltipster-basic")

        #Extraccion del rango salarial Depurado
        if salarios == None:
            df.loc[indice, "rango_salario"] = "Sin informacion de Salario"
        else:
            salario = list(salarios)[3].string.strip()
            df.loc[indice, "rango_salario"] = salario
            

        #Extraccion de cantidad de postulaciones RAW
        postulaciones = pageSoup.find("div", class_="size0 mt1")
        postulacion = list(postulaciones)[2].string

        # #Extraccion de cantidad de postulaciones Depurado
        postulacion = postulacion.replace("\n", " ").strip()
        postulacion = postulacion.replace("applications", "postulaciones").replace("application", "postulacion")
        df.loc[indice, "postulaciones"] = postulacion
            
        #Depuramos las ubicaciones
        ubicaciones = pageSoup.find("span", class_="tooltipster")
        ubicacion = pageSoup.find("span", class_="js-locations-tooltip")
        if ubicaciones == None and "cities" not in str(ubicacion):
            ubicacion = ubicacion.find("a").text.strip()
            df.loc[indice, "ubicacion"] = ubicacion
        elif ubicaciones == None and "cities" in str(ubicacion):
            ubicacion = "Varias ubicaciones"
            df.loc[indice, "ubicacion"] = ubicacion
        else:
            ubicacion = ubicaciones.text.strip()
            ubicacion = ubicacion.replace("\n", " ")
            df.loc[indice, "ubicacion"] = ubicacion
            
        #Cambiamos los index donde esta "remote" ya que es remote mundial.    
        df.loc[df[df["ubicacion"] == "Remote"].index, "ubicacion"] = "Remote (Mundial)"

        #Los 10 primeros cargos

        cargo_1, postulaciones_1, salario_1, lugar_1, skills_1, empresa_1, link_1 = df.loc[0, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_2, postulaciones_2, salario_2, lugar_2, skills_2, empresa_2, link_2 = df.loc[1, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_3, postulaciones_3, salario_3, lugar_3, skills_3, empresa_3, link_3 = df.loc[2, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_4, postulaciones_4, salario_4, lugar_4, skills_4, empresa_4, link_4 = df.loc[3, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_5, postulaciones_5, salario_5, lugar_5, skills_5, empresa_5, link_5 = df.loc[4, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_6, postulaciones_6, salario_6, lugar_6, skills_6, empresa_6, link_6 = df.loc[5, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_7, postulaciones_7, salario_7, lugar_7, skills_7, empresa_7, link_7 = df.loc[6, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_8, postulaciones_8, salario_8, lugar_8, skills_8, empresa_8, link_8 = df.loc[7, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_9, postulaciones_9, salario_9, lugar_9, skills_9, empresa_9, link_9 = df.loc[8, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]
        cargo_10, postulaciones_10, salario_10, lugar_10, skills_10, empresa_10, link_10 = df.loc[9, ["cargo", "postulaciones", "rango_salario", "ubicacion", "senority", "empresa", "link"]]

            #retornamos los 10 primeros cargos.
return f"ANUNCIO 1: \nCargo: {cargo_1} \nPostulaciones: {postulaciones_1} \nSalario: {salario_1} \nLugar de Trabajo: {lugar_1} \nSenority: {skills_1} \nEmpresa: {empresa_1} \nLink {link_1}\n\n\
                ANUNCIO 2: \nCargo: {cargo_2} \nPostulaciones: {postulaciones_2}  \nSalario: {salario_2} \nLugar de Trabajo: {lugar_2} \nSenority: {skills_2}  \nEmpresa: {empresa_2} \nLink: {link_2}\n\n\
                ANUNCIO 3: \nCargo: {cargo_3} \nPostulaciones: {postulaciones_3}  \nSalario: {salario_3} \nLugar de Trabajo: {lugar_3} \nSenority: {skills_3}  \nEmpresa: {empresa_3} \nLink: {link_3}\n\n\
                ANUNCIO 4: \nCargo: {cargo_4} \nPostulaciones: {postulaciones_4}  \nSalario: {salario_4} \nLugar de Trabajo: {lugar_4} \nSenority: {skills_4}  \nEmpresa: {empresa_4} \nLink: {link_4}\n\n\
                ANUNCIO 5: \nCargo: {cargo_5} \nPostulaciones: {postulaciones_5}  \nSalario: {salario_5} \nLugar de Trabajo: {lugar_5} \nSenority: {skills_5}  \nEmpresa: {empresa_5} \nLink: {link_5}\n\n\
                ANUNCIO 6: \nCargo: {cargo_6} \nPostulaciones: {postulaciones_6}  \nSalario: {salario_6} \nLugar de Trabajo: {lugar_6} \nSenority: {skills_6}  \nEmpresa: {empresa_6} \nLink: {link_6}\n\n\
                ANUNCIO 7: \nCargo: {cargo_7} \nPostulaciones: {postulaciones_7}  \nSalario: {salario_7} \nLugar de Trabajo: {lugar_7} \nSenority: {skills_7}  \nEmpresa: {empresa_7} \nLink: {link_7}\n\n\
                ANUNCIO 8: \nCargo: {cargo_8} \nPostulaciones: {postulaciones_8}  \nSalario: {salario_8} \nLugar de Trabajo: {lugar_8} \nSenority: {skills_8}  \nEmpresa: {empresa_8} \nLink: {link_8}\n\n\
                ANUNCIO 9: \nCargo: {cargo_9} \nPostulaciones: {postulaciones_9}  \nSalario: {salario_9} \nLugar de Trabajo: {lugar_9} \nSenority: {skills_9}  \nEmpresa: {empresa_9} \nLink: {link_9}\n\n\
                ANUNCIO 10: \nCargo: {cargo_10} \nPostulaciones: {postulaciones_10}  \nSalario: {salario_10} \nLugar de Trabajo: {lugar_10} \nHabilidades: {skills_10}  \nEmpresa: {empresa_10} \nLink: {link_10}\
                \n\
                \n\
                Si deseas hacer una nueva busqueda da click sobre: /start \
                \n\
                Si deseas calificar el bot da click sobre: /calificar"

