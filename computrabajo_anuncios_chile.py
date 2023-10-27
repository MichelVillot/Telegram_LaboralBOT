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


def ws_computrabajo_chile(palabra_clave):
    #Creamos listas nuevas para poder ingresar los links depurados
    links_nuevos = []
    links_existentes = []

    #Iteramos por los links
    for i in range(2):
        url = f"https://cl.computrabajo.com/trabajo-de-{palabra_clave}-en-rmetropolitana?p={i}"

        #Header: Lo utilizamos para establecer que la solicitud viene de un navegador
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                    }

        #Instanciamos la libreria requests en una variable y adicional hacemos la consulta.
        response = requests.get(url, headers=headers)

        #Hacemos un condicional donde indica que si el estatus es = 200 entonces utilice bs4 para extraer el text en formato "html.parser"
        if response.status_code == 200:
            pageSoup = soup(response.text, "html.parser")
            link = pageSoup.find_all("a", class_="js-o-link fc_base")

            #Iteramos para extraer y depurar los links
            for indice, elemento in enumerate(link):
                elemento = str(elemento)
                inicio, final = elemento.find('/'), elemento.find('>')-1
                if elemento[inicio:final] not in links_existentes:
                    links_nuevos.append(elemento[inicio:final])

    #Creamos el Dataframe donde vamos a ingresar la informacion
    df = pd.DataFrame(data = 0, index=range(20), columns=["link","titulo_oferta", "descripcion_cargo", "salario","lugar_trabajo","jornada_laboral", "tipo_contrato",  "nombre_empresa", "keywords", "hora_publicacion"])  

    #Iteramos sobre los primeros 20 links
    for indice, elemento in enumerate(links_nuevos[:20]):
        url_ejemplo = "https://cl.computrabajo.com"+links_nuevos[indice]
        response = requests.get(url_ejemplo, headers=headers)

        if response.status_code == 200:
            pageSoup = soup(response.text, "html.parser")


            #Titulo
            titulo_oferta = pageSoup.find("h1", class_="fwB fs24 mb5 box_detail w100_m").string

            #Salario
            salario = pageSoup.find_all("span", class_="tag base mb10")[0].string.title()

            #Contrato
            tipo_contrato = pageSoup.find_all("span", class_="tag base mb10")[1].string.title()
            
            #Jornada
            jornada_semanal = pageSoup.find_all("span", class_="tag base mb10")[2].string.title()

            #Empresa 
            nombre_empresa = str(pageSoup.find("a", class_="dIB fs16 js-o-link"))
            inicio, final = nombre_empresa.find(">"), len(nombre_empresa)
            nombre_empresa = nombre_empresa[inicio+1:final-4]

            #Lugar
            lugar_empleo = pageSoup.find("p", class_="fs16").string.replace(", R.Metropolitana", "")
            inicio, final = lugar_empleo.find("-"), len(lugar_empleo)
            lugar_empleo = lugar_empleo[inicio+2:final]

            #Descripcion
            descripcion_cargo = pageSoup.find("p", class_="mbB")
            descripcion_cargo = str(descripcion_cargo).replace("<br/>", " ").replace('<p class="mbB">', "").replace("</p>", "").replace("\t", "").strip()
        

            #Hacemos una URL acortada
            type_tiny = pyshorteners.Shortener()
            url_ejemplo = type_tiny.tinyurl.short(url_ejemplo)

            # #Ingestamos el df
            df.loc[indice, "link"]= url_ejemplo
            df.loc[indice, "titulo_oferta"] = titulo_oferta
            df.loc[indice,"descripcion_cargo"] = descripcion_cargo
            df.loc[indice,"salario"] = salario
            df.loc[indice, "lugar_trabajo"]= lugar_empleo
            df.loc[indice, "jornada_laboral"]= jornada_semanal
            df.loc[indice, "tipo_contrato" ]= tipo_contrato
            if nombre_empresa == "":
                df.loc[indice, "nombre_empresa"] = "Confidencial"
            else:
                df.loc[indice, "nombre_empresa"] = nombre_empresa



            #Cremoa listas para poder extraer habilidades especificas encontradas en los anuncios.
            keywords = ["excel", "ingles", "python", "sql", "mysql", "erp", "cmr", "big data", "power bi"]
            lista_keywords = [0,0,0,0,0,0,0,0,0]
            
            #Condicional de las habilidades especificas.
            if "power bi" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[8] = "POWER BI"
            else:
                lista_keywords.pop(8)

            if "big data" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[7] = "BIG DATA"
            else:
                lista_keywords.pop(7)

            if "cmr" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[6] = "CMR"
            else:
                lista_keywords.pop(6)

            if "erp" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[5] = "ERP"
            else:
                lista_keywords.pop(5)

            if "mysql" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[4] = "MYSQL"
            else:
                lista_keywords.pop(4)

            if "sql" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[3] = "SQL"
            else:
                lista_keywords.pop(3)

            if "python" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[2] = "PYTHON"
            else:
                lista_keywords.pop(2)

            if "ingles" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[1] = "INGLES"
            else:
                lista_keywords.pop(1)
        
            if "excel" in str(df.loc[indice,"descripcion_cargo"]).lower():
                lista_keywords[0] = "EXCEL"
            else:
                lista_keywords.pop(0)

            if len(lista_keywords) == int(0):
                df.loc[indice, "keywords"] = "Sin Informacion"
            else:
                df.loc[indice, "keywords"] = str(lista_keywords)


    #Creamos los 10 anuncios a mostrar
    cargo_1, hora_1, salario_1, lugar_1, skills_1, empresa_1, link_1 = df.loc[0, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_2, hora_2, salario_2, lugar_2, skills_2, empresa_2, link_2 = df.loc[1, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_3, hora_3, salario_3, lugar_3, skills_3, empresa_3, link_3 = df.loc[2, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_4, hora_4, salario_4, lugar_4, skills_4, empresa_4, link_4 = df.loc[3, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_5, hora_5, salario_5, lugar_5, skills_5, empresa_5, link_5 = df.loc[4, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_6, hora_6, salario_6, lugar_6, skills_6, empresa_6, link_6 = df.loc[5, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_7, hora_7, salario_7, lugar_7, skills_7, empresa_7, link_7 = df.loc[6, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_8, hora_8, salario_8, lugar_8, skills_8, empresa_8, link_8 = df.loc[7, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_9, hora_9, salario_9, lugar_9, skills_9, empresa_9, link_9 = df.loc[8, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]
    cargo_10, hora_10, salario_10, lugar_10, skills_10, empresa_10, link_10 = df.loc[9, ["titulo_oferta", "hora_publicacion", "salario", "lugar_trabajo", "keywords", "nombre_empresa", "link"]]


    #Retornamos los 10 anuncios a mostrar.
    return f"\n\nANUNCIO 1: \nCargo: {cargo_1} \nSalario: {salario_1} \nLugar de Trabajo: {lugar_1} \nHabilidades: {skills_1} \nEmpresa: {empresa_1} \nLink: {link_1}\n\n\
            ANUNCIO 2: \nCargo: {cargo_2} \nSalario: {salario_2} \nLugar de Trabajo: {lugar_2} \nHabilidades: {skills_2}  \nEmpresa: {empresa_2} \nLink: {link_2}\n\n\
            ANUNCIO 3: \nCargo: {cargo_3} \nSalario: {salario_3} \nLugar de Trabajo: {lugar_3} \nHabilidades: {skills_3}  \nEmpresa: {empresa_3} \nLink: {link_3}\n\n\
            ANUNCIO 4: \nCargo: {cargo_4} \nSalario: {salario_4} \nLugar de Trabajo: {lugar_4} \nHabilidades: {skills_4}  \nEmpresa: {empresa_4} \nLink: {link_4}\n\n\
            ANUNCIO 5: \nCargo: {cargo_5} \nSalario: {salario_5} \nLugar de Trabajo: {lugar_5} \nHabilidades: {skills_5}  \nEmpresa: {empresa_5} \nLink: {link_5}\n\n\
            ANUNCIO 6: \nCargo: {cargo_6} \nSalario: {salario_6} \nLugar de Trabajo: {lugar_6} \nHabilidades: {skills_6}  \nEmpresa: {empresa_6} \nLink: {link_6}\n\n\
            ANUNCIO 7: \nCargo: {cargo_7} \nSalario: {salario_7} \nLugar de Trabajo: {lugar_7} \nHabilidades: {skills_7}  \nEmpresa: {empresa_7} \nLink: {link_7}\n\n\
            ANUNCIO 8: \nCargo: {cargo_8} \nSalario: {salario_8} \nLugar de Trabajo: {lugar_8} \nHabilidades: {skills_8}  \nEmpresa: {empresa_8} \nLink: {link_8}\n\n\
            ANUNCIO 9: \nCargo: {cargo_9} \nSalario: {salario_9} \nLugar de Trabajo: {lugar_9} \nHabilidades: {skills_9}  \nEmpresa: {empresa_9} \nLink: {link_9}\n\n\
            ANUNCIO 10: \nCargo: {cargo_10} \nSalario: {salario_10} \nLugar de Trabajo: {lugar_10} \nHabilidades: {skills_10}  \nEmpresa: {empresa_10} \nLink: {link_10}\
            \n\
            \nSi deseas hacer una nueva busqueda da click sobre: /start \
            \nSi deseas calificar el bot da click sobre: /calificar"



