let map = null;
let markers = [];
let routeLayer = null;
let lastData = null;

async function fetchData(){
  // allow opening the HTML file locally: if protocol is file:, use localhost server
  const base = (location.protocol === 'file:') ? 'http://127.0.0.1:5000' : '';
  const url = base + '/api/data';
  const res = await fetch(url);
  if(!res.ok){
    const txt = await res.text().catch(()=>'<no body>');
    throw new Error('HTTP '+res.status+' from '+url+' - '+txt);
  }
  const text = await res.text();
  try{
    return JSON.parse(text);
  }catch(e){
    throw new Error('Invalid JSON from '+url+': '+text.slice(0,300));
  }
}

function initMap(){
  if(map) return;
  map = L.map('map', {zoomControl:false}).setView([20, 0], 2);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);
  L.control.zoom({position:'topright'}).addTo(map);
}

function clearMapLayers(){
  markers.forEach(marker => map.removeLayer(marker));
  markers = [];
  if(routeLayer){
    map.removeLayer(routeLayer);
    routeLayer = null;
  }
}

function updateMap(data){
  if(!map) initMap();
  clearMapLayers();

  const names = Object.keys(data.conexiones).sort();
  const bounds = L.latLngBounds([]);

  for(const n of names){
    const coord = data.coord[n];
    if(!coord) continue;
    const lat = Number(coord[0]);
    const lon = Number(coord[1]);
    if(!Number.isFinite(lat) || !Number.isFinite(lon)) continue;
    const marker = L.circleMarker([lat, lon], {
      radius: 8,
      color: '#d3b2ff',
      fillColor: '#9f73ff',
      fillOpacity: 0.96,
      weight: 2
    });
    marker.bindPopup(`<strong>${n}</strong><br>${lat.toFixed(4)}, ${lon.toFixed(4)}`);
    marker.addTo(map);
    markers.push(marker);
    bounds.extend([lat, lon]);
  }

  if(bounds.isValid()){
    map.fitBounds(bounds.pad(0.35));
  } else {
    map.setView([20, 0], 2);
  }
}

async function render(){
  let data = null;
  try{
    data = await fetchData();
  }catch(e){
    console.error('Error fetching /api/data', e);
    alert('Error cargando datos: '+e.message);
    return;
  }
  lastData = data;
  const places = document.getElementById('places');
  const connections = document.getElementById('connections');
  places.innerHTML = '';
  connections.innerHTML = '';
  const names = Object.keys(data.conexiones).sort();
  for(const n of names){
    const li = document.createElement('li');
    li.className = 'list-group-item';
    const coord = data.coord[n];
    li.textContent = coord ? `${n} — ${Number(coord[0]).toFixed(6)}, ${Number(coord[1]).toFixed(6)}` : n;
    places.appendChild(li);

    const neighbors = data.conexiones[n] || {};
    const neighborList = Object.entries(neighbors)
      .map(([target, cost]) => `${target} (${Number(cost).toFixed(1)} km)`)
      .join(', ');
    const connLi = document.createElement('li');
    connLi.className = 'list-group-item';
    connLi.textContent = neighborList ? `${n}: ${neighborList}` : `${n}: sin conexiones`;
    connections.appendChild(connLi);
  }

  const labels = {from: 'Desde', to: 'Hasta', start: 'Inicio', goal: 'Destino'};
  for(const id of ['from','to','start','goal']){
    const sel = document.getElementById(id);
    sel.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = labels[id];
    placeholder.disabled = false;
    placeholder.selected = true;
    placeholder.hidden = false;
    placeholder.style.color = '#666';
    sel.appendChild(placeholder);
    for(const n of names){
      const opt = document.createElement('option');
      opt.value = n;
      opt.textContent = n;
      sel.appendChild(opt);
    }
    sel.selectedIndex = 0;
  }

  // make route-point items clickable (populates hidden inputs too)
  // populate selects (from, to, start, goal)
  for(const id of ['from','to','start','goal']){
    const sel = document.getElementById(id);
    if(!sel) continue;
    sel.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = (id==='from' || id==='start') ? '---' : (id==='to' || id==='goal') ? '---' : '';
    placeholder.disabled = true;
    placeholder.selected = true;
    sel.appendChild(placeholder);
    for(const n of names){
      const opt = document.createElement('option');
      opt.value = n;
      opt.textContent = n;
      sel.appendChild(opt);
    }
    sel.selectedIndex = 0;
  }

  updateMap(data);
}

async function addPlace(){
  const name = document.getElementById('name').value.trim();
  const lat = document.getElementById('lat').value.trim();
  const lon = document.getElementById('lon').value.trim();
  if(!name || !lat || !lon){
    alert('Rellena todos los campos');
    return;
  }
  const res = await fetch('/api/place', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name, lat, lon})
  });
  if(!res.ok){
    const e = await res.json();
    alert(e.error || 'Error al guardar lugar');
    return;
  }
  document.getElementById('name').value = '';
  document.getElementById('lat').value = '';
  document.getElementById('lon').value = '';
  await render();
}

async function addEdge(){
  const from = document.getElementById('from').value;
  const to = document.getElementById('to').value;
  const cost = document.getElementById('cost').value.trim();
  if(!from || !to || !cost){
    alert('Rellena todos los campos');
    return;
  }
  const res = await fetch('/api/edge', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({from, to, cost})
  });
  if(!res.ok){
    const e = await res.json();
    alert(e.error || 'Error al guardar conexión');
    return;
  }
  document.getElementById('cost').value = '';
  await render();
}

function drawRoute(route){
  if(!lastData) return;
  const latlngs = route.map(name => {
    const coord = lastData.coord[name];
    if(!coord) return null;
    return [Number(coord[0]), Number(coord[1])];
  }).filter(Boolean);

  if(routeLayer){
    map.removeLayer(routeLayer);
    routeLayer = null;
  }

  if(latlngs.length === 1){
    const [lat, lon] = latlngs[0];
    routeLayer = L.circle([lat, lon], {
      radius: 45000,
      color: '#c48dff',
      fillColor: '#c48dff',
      fillOpacity: 0.35
    }).addTo(map);
    map.setView([lat, lon], 8);
    return;
  }

  if(latlngs.length > 1){
    routeLayer = L.polyline(latlngs, {
      color: '#c48dff',
      weight: 5,
      opacity: 0.9,
      dashArray: '8 6'
    }).addTo(map);
    map.fitBounds(routeLayer.getBounds().pad(0.3));
  }
}

async function calcRoute(){
  const start = document.getElementById('start') ? document.getElementById('start').value : '';
  const goal = document.getElementById('goal') ? document.getElementById('goal').value : '';
  if(!start || !goal){
    alert('Selecciona inicio y objetivo');
    return;
  }
  const res = await fetch('/api/route', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({start, goal})
  });
  const j = await res.json();
  const out = document.getElementById('result');
  if(!j.route){
    out.textContent = 'No se encontró ruta';
    if(routeLayer){
      map.removeLayer(routeLayer);
      routeLayer = null;
    }
    return;
  }
  out.innerHTML = `<strong>Ruta:</strong> ${j.route.join(' → ')}<br><strong>Costo:</strong> ${Number(j.cost).toFixed(2)} km`;
  drawRoute(j.route);
}

window.addEventListener('load', async () => {
  initMap();
  await render();
  document.getElementById('addPlace').addEventListener('click', addPlace);
  document.getElementById('addEdge').addEventListener('click', addEdge);
  document.getElementById('routeBtn').addEventListener('click', calcRoute);
  document.getElementById('refresh').addEventListener('click', render);
});