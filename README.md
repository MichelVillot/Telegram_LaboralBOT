# `LaboralBot - Busqueda de empleo en Tiempo Real`

# `Introduccion`

Se lo dificil que es buscar trabajo, pasar de un portal a otro, de una app a otra y que siempre tengas que entrar en cada link para ver que hay dentro de ese anuncio (resultando tanto tedioso como un poco abrumador) como es algo que me sucedia a mi decidi hacer algo y encontre la forma de hacerlo... Y es por ello que llegue a la conclusion de crear un Bot que pudiera activarse y hacer la busqueda por mi. Es aqui donde entra `LaboralBOT`.

# `¿Que es LaboralBot?`
LaboralBot es un Bot creado en telegram para poder realizar una busqueda en tiempo real en los portales mas usados en los siguientes paises: Argentina, Chile, Colombia, Mexico y Peru. 

# `Como funciona`
LaboralBot realiza la busqueda del cargo que el usuario digite, una vez que el usuario digita el cargo el bot se activa y realiza un proceso de web scraping en tiempo real (en el portal que selecciono) dando como resultado una lista con los 10 anuncios mas recientes en el portal para el cargo que fue digitado.

# `Archivos`
Los archivos que se encuentran en este repositorio son los siguientes:
* computrabajo_anuncios_chile.py > El cual contiene la funcion que realiza el web scraping en tiempo real.
* getonboard_anuncios_chile.py > El cual contiene la funcion que realiza el web scraping en tiempo real.
* main.py > El archivo main donde se ejecutan las funciones y el codigo que genera la conversacion entre el usuario y el BOT.

# `Stack y librerias`
Se utiliza Python para realizar la creacion del Bot asi como el proceso de Web Scraping, a su vez se utiliza MySQL para poder guardar la informacion de todos los pasos que realiza el usuario en pro de tener datos para mejorar el BOT.

Librerias:
* `Telebot` > Libreria para crear el BOT de Telegram 
* `Pandas` > Para realizar la manipulacion de los datos, la limpieza de los mismos.
* `Requests` > Para realizar la conexion con la pagina web y asi extraer la informacion en formato HTML
* `BeautifullSoup` > Para realizar web scraping y extraer los tags, class del formato HTML de la pagina web.
* `Time` > Para fecha y hora del proceso.
* `SqlAlchemy` > Para realizar la conexion entre VSCode y MySQL, y asi almacenar toda la informacion del usuario.


# `Video - Tutorial de como usar LaboralBOT`
Link del video: [Video](https://www.youtube.com/watch?v=Trk73cb1E_k)

# `Implementacion del repositorio`
1) En caso que quieras emular este bot debes crear un Bot de Telegram.  [Video Tutorial](https://www.youtube.com/watch?v=wxOeEb2ElSU) Minuto 00:00 al 02:07.
2) Buscar la variable TOKEN al inicio del archivo `main.py` y cambiarlo por el Token que te da el `BotFather`
3) Disfruta el bot.

# `Creacion y uso`
Este bot fue creado por Michel Villot para poder ayudar a los que estan en constante busqueda de empleo, su uso es netamente para poder obtener los anuncios de una manera mas rapida y en una plataforma de mensajeria que es usada mundialmente.

# `Imagenes`:
![Diapositiva1](https://github.com/MichelVillot/Telegram_LaboralBOT/assets/107226318/f13557b9-9a1d-4eae-8f6f-986076fbbd39)
![Diapositiva2](https://github.com/MichelVillot/Telegram_LaboralBOT/assets/107226318/c5cae080-e1ec-4dbe-896a-7526e7788f29)





