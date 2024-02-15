from flask import Flask, render_template, request, redirect, url_for
import requests
import urllib

app = Flask(__name__)

api_url = "https://www.mapquestapi.com/directions/v2/route?"
api_url_mapa = "https://www.mapquestapi.com/staticmap/v5/map?"
key = "MAlXFY1w42ermH0kPQ3BeoMeNWk6SzDu"

# Diccionario global para mantener los detalles del viaje
detalles_viaje = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    nombre = request.form['nombre']
    detalles_viaje['nombre'] = nombre
    return redirect(url_for('pagina_viaje', nombre=nombre))

@app.route('/viaje/<nombre>')
def pagina_viaje(nombre):
    return render_template('viaje.html', nombre=nombre)

def obtener_datos_ruta(origen, destino):
    parametros = {
        "key": key,
        "from": origen,
        "to": destino,
        "outFormat": "json",
        "routeType": "fastest",
        "traffic": "true"  # Habilitar el tráfico en tiempo real
    }
    url = api_url + urllib.parse.urlencode(parametros)
    response = requests.get(url)
    json_data = response.json()
    return json_data

@app.route('/procesar_viaje', methods=['POST'])
def procesar_viaje():
    origen = request.form['origen']
    destino = request.form['destino']
    detalles_viaje['origen'] = origen.capitalize()
    detalles_viaje['destino'] = destino.capitalize()

    json_data = obtener_datos_ruta(origen, destino)

    return redirect(url_for('pagina_ruta', origen=origen, destino=destino, json_data=json_data))

@app.route('/ruta/<origen>/<destino>')
def pagina_ruta(origen, destino):
    json_data = obtener_datos_ruta(origen, destino)
    status_code = json_data["info"]["statuscode"]
    if status_code == 0:
        distancia = json_data['route']['distance'] * 1.61
        duracion_viaje = json_data["route"]["formattedTime"]

    precio = int(distancia * 2200)
    zoom = obtener_nivel_zoom(distancia)
    url_mapa = obtener_mapa_ruta(origen, destino, zoom)
    detalles_viaje['distancia'] = str("{:.2f}".format(distancia))
    detalles_viaje['duracion_viaje'] = duracion_viaje
    detalles_viaje['precio'] = precio
    detalles_viaje['url_mapa'] = url_mapa
    mensaje = request.args.get('mensaje')
    return render_template('ruta.html', origen=origen.capitalize(), destino=destino.capitalize(), duracion_viaje=duracion_viaje, 
                           distancia=str("{:.2f}".format(distancia) + " Km"), precio=precio, url_mapa=url_mapa, mensaje=mensaje)

def obtener_mapa_ruta(origen, destino, zoom):
    parametros = {
        "key": key,
        "start": origen,
        "end": destino,
        "size": "600,400",
        "zoom": zoom
    }
    url = api_url_mapa + urllib.parse.urlencode(parametros)
    return url

def obtener_nivel_zoom(distancia):
    if distancia < 12:
        return 12
    elif distancia < 28:
        return 11
    elif distancia < 45:
        return 10
    elif distancia < 90:
        return 9
    else:
        return 8

@app.route('/proceso_conductor', methods=['POST'])
def proceso_conductor():
    return redirect(url_for('pagina_conductor'))

@app.route('/conductor')
def pagina_conductor():
    return render_template('conductor.html', nombre=detalles_viaje.get('nombre'), origen=detalles_viaje.get('origen'), 
                           destino=detalles_viaje.get('destino'), distancia=detalles_viaje.get('distancia'), 
                           duracion_viaje=detalles_viaje.get('duracion_viaje'), precio=detalles_viaje.get('precio'),
                           url_mapa=detalles_viaje.get('url_mapa'))

@app.route('/aceptar_conductor', methods=['GET','POST'])
def aceptar_conductor():
    return redirect(url_for('viaje_aceptado'))

@app.route('/rechazo_conductor', methods=['POST'])
def rechazo_conductor():
    if 'rechazar' in request.form:
        return redirect(url_for('pagina_conductor'))
    
@app.route('/viaje_aceptado', methods=['GET','POST'])
def viaje_aceptado():
    return render_template('viaje_aceptado.html', nombre=detalles_viaje.get('nombre'), origen=detalles_viaje.get('origen'), 
                           destino=detalles_viaje.get('destino'), distancia=detalles_viaje.get('distancia'), 
                           duracion_viaje=detalles_viaje.get('duracion_viaje'), precio=detalles_viaje.get('precio'),
                           url_mapa=detalles_viaje.get('url_mapa'), mensaje='¡EL VIAJE HA SIDO ACEPTADO, Y PRONTO LLEGARÁ TÚ SERVICIO!')

if __name__ == '__main__':
    app.run(debug=True)