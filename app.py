from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import json
import Carretera_A as ca

DATA_FILE = 'data.json'

app = Flask(__name__, static_folder='static', template_folder='templates')


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # coord stored as lists -> convert to tuples
            data['coord'] = {k: tuple(v) for k, v in data.get('coord', {}).items()}
            return data
    # valores por defecto coherentes con el ejemplo completo de `Carretera_A`
    conexiones = {
        'Jiloyork': {'CDMX': 125, 'QRO': 513},
        'MORELOS': {'QRO': 524},
        'CDMX': {'Jiloyork': 125, 'QRO': 423, 'HGO': 491},
        'HGO': {'CDMX': 491, 'QRO': 356, 'MEXICALI': 309, 'MTY': 346},
        'QRO': {'SLP': 203, 'MORELOS': 514, 'Jiloyork': 513, 'CDMX': 423, 'MTY': 603,
                'SONORA': 437, 'HGO': 356, 'MEXICALI': 313, 'AGS': 599},
        'SLP': {'AGS': 390, 'QRO': 203},
        'AGS': {'SLP': 390, 'QRO': 599},
        'SONORA': {'QRO': 437, 'MEXICALI': 394},
        'MEXICALI': {'MTY': 296, 'HGO': 309, 'QRO': 313},
        'MTY': {'MEXICALI': 296, 'QRO': 603, 'HGO': 346}
    }
    coord = {
        'Jiloyork': (19.952408902750292, -99.53304570197712),
        'CDMX': (19.432684900517486, -99.13333701698),
        'QRO': (20.587956563302367, -100.38793290667115),
        'MORELOS': (18.930555912984644, -99.22237799899486),
        'HGO': (20.127000042049925, -98.73156416258126),
        'AGS': (21.856150731885958, -102.28915655184271),
        'SLP': (22.151749211629454, -100.97643458591887),
        'SONORA': (29.07865856228773, -110.94760761628041),
        'MEXICALI': (32.6245, -115.4526),
        'MTY': (25.66616067388393, -100.32880810205152)
    }
    return {'conexiones': conexiones, 'coord': coord}


def save_data(data):
    # convertir tuplas a listas para JSON
    out = {
        'conexiones': data['conexiones'],
        'coord': {k: list(v) for k, v in data['coord'].items()}
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


# Cargar en memoria
state = load_data()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data', methods=['GET'])
def api_data():
    return jsonify(state)


@app.route('/api/place', methods=['POST'])
def api_place():
    payload = request.get_json() or {}
    name = payload.get('name')
    lat = payload.get('lat')
    lon = payload.get('lon')
    if not name or lat is None or lon is None:
        return jsonify({'error': 'faltan campos'}), 400
    try:
        latf = float(lat)
        lonf = float(lon)
    except ValueError:
        return jsonify({'error': 'lat/lon invalidos'}), 400
    ca.add_place(state['coord'], state['conexiones'], name, latf, lonf)
    save_data(state)
    return jsonify({'ok': True, 'place': name})


@app.route('/api/edge', methods=['POST'])
def api_edge():
    payload = request.get_json() or {}
    frm = payload.get('from')
    to = payload.get('to')
    cost = payload.get('cost')
    if not frm or not to or cost is None:
        return jsonify({'error': 'faltan campos'}), 400
    try:
        costf = float(cost)
    except ValueError:
        return jsonify({'error': 'costo invalido'}), 400
    if frm not in state['conexiones']:
        state['conexiones'][frm] = {}
    state['conexiones'][frm][to] = costf
    save_data(state)
    return jsonify({'ok': True})


@app.route('/api/route', methods=['POST'])
def api_route():
    payload = request.get_json() or {}
    start = payload.get('start')
    goal = payload.get('goal')
    if not start or not goal:
        return jsonify({'error': 'faltan campos'}), 400
    ruta, costo = ca.a_star(state['conexiones'], state['coord'], start, goal)
    if ruta is None:
        return jsonify({'route': None, 'cost': None})
    return jsonify({'route': ruta, 'cost': costo})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    #https://gps1.onrender.com
