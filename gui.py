import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import Carretera_A as ca

DATA_FILE = 'data.json'

# Cargar / guardar

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # datos por defecto
    conexiones = {
        'Jiloyork': {'CDMX': 125, 'QRO': 513},
        'CDMX': {'Jiloyork': 125, 'QRO': 423},
        'QRO': {'CDMX': 423, 'MTY': 603},
        'MTY': {'QRO': 603}
    }
    coord = {
        'Jiloyork': (19.952408902750292, -99.53304570197712),
        'CDMX': (19.432684900517486, -99.13333701698),
        'QRO': (20.587956563302367, -100.38793290667115),
        'MTY': (25.66616067388393, -100.32880810205152)
    }
    return {'conexiones': conexiones, 'coord': coord}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Front Carreteras')
        self.geometry('720x420')
        raw = load_data()
        # json convierte tuplas en listas, asegurarse
        self.conexiones = raw.get('conexiones', {})
        self.coord = {k: tuple(v) for k, v in raw.get('coord', {}).items()}
        self.create_widgets()
        self.refresh_places()

    def create_widgets(self):
        # Lista de lugares
        frame_left = ttk.Frame(self)
        frame_left.pack(side='left', fill='y', padx=8, pady=8)

        ttk.Label(frame_left, text='Lugares').pack()
        self.places_list = tk.Listbox(frame_left, height=20, width=30)
        self.places_list.pack()

        # Form para nuevo lugar
        frame_right = ttk.Frame(self)
        frame_right.pack(side='left', fill='both', expand=True, padx=8, pady=8)

        ttk.Label(frame_right, text='Agregar lugar').grid(column=0, row=0, sticky='w')
        ttk.Label(frame_right, text='Nombre:').grid(column=0, row=1, sticky='e')
        self.entry_name = ttk.Entry(frame_right)
        self.entry_name.grid(column=1, row=1, sticky='w')

        ttk.Label(frame_right, text='Latitud:').grid(column=0, row=2, sticky='e')
        self.entry_lat = ttk.Entry(frame_right)
        self.entry_lat.grid(column=1, row=2, sticky='w')

        ttk.Label(frame_right, text='Longitud:').grid(column=0, row=3, sticky='e')
        self.entry_lon = ttk.Entry(frame_right)
        self.entry_lon.grid(column=1, row=3, sticky='w')

        ttk.Button(frame_right, text='Agregar lugar', command=self.on_add_place).grid(column=1, row=4, sticky='w')

        # Agregar arista
        ttk.Separator(frame_right).grid(column=0, row=5, columnspan=3, sticky='ew', pady=8)
        ttk.Label(frame_right, text='Agregar conexión (arista)').grid(column=0, row=6, sticky='w')
        ttk.Label(frame_right, text='Desde:').grid(column=0, row=7, sticky='e')
        self.combo_from = ttk.Combobox(frame_right, values=[], state='readonly')
        self.combo_from.grid(column=1, row=7, sticky='w')
        ttk.Label(frame_right, text='Hasta:').grid(column=0, row=8, sticky='e')
        self.combo_to = ttk.Combobox(frame_right, values=[], state='readonly')
        self.combo_to.grid(column=1, row=8, sticky='w')
        ttk.Label(frame_right, text='Costo (km):').grid(column=0, row=9, sticky='e')
        self.entry_cost = ttk.Entry(frame_right)
        self.entry_cost.grid(column=1, row=9, sticky='w')
        ttk.Button(frame_right, text='Agregar conexión', command=self.on_add_edge).grid(column=1, row=10, sticky='w')

        ttk.Separator(frame_right).grid(column=0, row=11, columnspan=3, sticky='ew', pady=8)
        # Búsqueda
        ttk.Label(frame_right, text='Buscar ruta').grid(column=0, row=12, sticky='w')
        ttk.Label(frame_right, text='Inicio:').grid(column=0, row=13, sticky='e')
        self.combo_start = ttk.Combobox(frame_right, values=[], state='readonly')
        self.combo_start.grid(column=1, row=13, sticky='w')
        ttk.Label(frame_right, text='Objetivo:').grid(column=0, row=14, sticky='e')
        self.combo_goal = ttk.Combobox(frame_right, values=[], state='readonly')
        self.combo_goal.grid(column=1, row=14, sticky='w')
        ttk.Button(frame_right, text='Calcular ruta', command=self.on_compute).grid(column=1, row=15, sticky='w')

        # Resultado
        self.result_text = tk.Text(frame_right, height=6, width=60)
        self.result_text.grid(column=0, row=16, columnspan=3, pady=8)

        # Guardar
        ttk.Button(frame_right, text='Guardar datos', command=self.on_save).grid(column=0, row=17, sticky='w')

    def refresh_places(self):
        self.places_list.delete(0, tk.END)
        names = sorted(self.conexiones.keys())
        for n in names:
            latlon = self.coord.get(n)
            if latlon:
                display = f"{n} — {latlon[0]:.6f}, {latlon[1]:.6f}"
            else:
                display = n
            self.places_list.insert(tk.END, display)
        # actualizar combos
        vals = names
        for c in (self.combo_from, self.combo_to, self.combo_start, self.combo_goal):
            c['values'] = vals
            if vals:
                c.current(0)

    def on_add_place(self):
        name = self.entry_name.get().strip()
        lat = self.entry_lat.get().strip()
        lon = self.entry_lon.get().strip()
        if not name or not lat or not lon:
            messagebox.showwarning('Faltan datos', 'Rellena nombre, latitud y longitud')
            return
        try:
            latf = float(lat)
            lonf = float(lon)
        except ValueError:
            messagebox.showerror('Error', 'Latitud y longitud deben ser números')
            return
        # agregar
        self.coord[name] = (latf, lonf)
        if name not in self.conexiones:
            self.conexiones[name] = {}
        self.refresh_places()
        messagebox.showinfo('Agregado', f'Lugar "{name}" agregado')

    def on_add_edge(self):
        frm = self.combo_from.get()
        to = self.combo_to.get()
        cost = self.entry_cost.get().strip()
        if not frm or not to or not cost:
            messagebox.showwarning('Faltan datos', 'Selecciona origen, destino y costo')
            return
        try:
            costf = float(cost)
        except ValueError:
            messagebox.showerror('Error', 'Costo debe ser numérico')
            return
        if frm not in self.conexiones:
            self.conexiones[frm] = {}
        self.conexiones[frm][to] = costf
        messagebox.showinfo('Conexión', f'Conexión {frm} -> {to} agregada ({costf})')

    def on_compute(self):
        start = self.combo_start.get()
        goal = self.combo_goal.get()
        if not start or not goal:
            messagebox.showwarning('Faltan datos', 'Selecciona inicio y objetivo')
            return
        ruta, costo = ca.a_star(self.conexiones, self.coord, start, goal)
        self.result_text.delete('1.0', tk.END)
        if ruta is None:
            self.result_text.insert(tk.END, 'No se encontró ruta\n')
        else:
            self.result_text.insert(tk.END, f'Ruta: {ruta}\nCosto: {costo:.2f}\n')

    def on_save(self):
        data = {'conexiones': self.conexiones, 'coord': self.coord}
        # convertir tuplas a listas para json
        data['coord'] = {k: list(v) for k, v in data['coord'].items()}
        save_data(data)
        messagebox.showinfo('Guardado', 'Datos guardados en data.json')


if __name__ == '__main__':
    app = App()
    app.mainloop()
