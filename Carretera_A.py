"""
Módulo de rutas por carretera con búsqueda A*/UCS.

Provee funciones reutilizables:
- `geodist(lat1, lon1, lat2, lon2)` : distancia aproximada entre coordenadas (km)
- `a_star(conexiones, coord, inicio, objetivo)` : devuelve (ruta, costo) usando A*
- `add_place(coord, conexiones, nombre, lat, lon)` : agrega un lugar al grafo

El script también incluye un ejemplo cuando se ejecuta directamente.
"""
from math import radians, sin, cos, asin, sqrt
import heapq


def geodist(lat1, lon1, lat2, lon2):
    """Calcula distancia aproximada (km) entre dos coordenadas usando la fórmula haversine."""
    # convertir a radianes
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    R = 6371.0  # radio de la Tierra en km
    return R * c


def a_star(conexiones, coord, inicio, objetivo):
    """Busca la mejor ruta desde `inicio` hasta `objetivo`.

    conexiones: dict(nombre -> dict(vecino -> costo))
    coord: dict(nombre -> (lat, lon))
    Devuelve (ruta_lista, costo_total) o (None, None) si no hay ruta.
    """
    if inicio not in conexiones:
        return None, None
    # función heurística: distancia geográfica
    def h(n):
        if n in coord and objetivo in coord:
            return geodist(coord[n][0], coord[n][1], coord[objetivo][0], coord[objetivo][1])
        return 0

    open_heap = []  # elementos: (f_score, contador, nodo)
    counter = 0
    g_score = {inicio: 0}
    f_score = {inicio: h(inicio)}
    heapq.heappush(open_heap, (f_score[inicio], counter, inicio))
    came_from = {}

    closed = set()
    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current == objetivo:
            # reconstruir ruta
            path = []
            n = current
            while n in came_from:
                path.append(n)
                n = came_from[n]
            path.append(inicio)
            path.reverse()
            return path, g_score[current]

        closed.add(current)
        for neighbor, cost in conexiones.get(current, {}).items():
            tentative_g = g_score.get(current, float('inf')) + float(cost)
            if neighbor in closed and tentative_g >= g_score.get(neighbor, float('inf')):
                continue
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + h(neighbor)
                counter += 1
                heapq.heappush(open_heap, (f, counter, neighbor))

    return None, None


def add_place(coord, conexiones, nombre, lat, lon):
    """Agrega un nuevo lugar al diccionario de coordenadas y crea un nodo en conexiones."""
    coord[nombre] = (float(lat), float(lon))
    if nombre not in conexiones:
        conexiones[nombre] = {}


if __name__ == "__main__":
    # ejemplo de grafo corregido
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

    inicio = 'Jiloyork'
    objetivo = 'MTY'
    ruta, costo = a_star(conexiones, coord, inicio, objetivo)
    print('Ruta:', ruta)
    print('Costo:', costo)