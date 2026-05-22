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
  const names = Object.keys(data.conexiones).sort();
  
  const tbody = document.getElementById('placesBody');
  tbody.innerHTML = '';
  for(const n of names){
    const tr = document.createElement('tr');
    const coord = data.coord[n];
    const lat = coord ? Number(coord[0]).toFixed(4) : 'N/A';
    const lon = coord ? Number(coord[1]).toFixed(4) : 'N/A';
    const neighbors = data.conexiones[n] || {};
    const connectionCount = Object.keys(neighbors).length;
    tr.innerHTML = '<td><strong>' + n + '</strong></td><td>' + lat + ', ' + lon + '</td><td><span class="badge">' + connectionCount + ' conexiones</span></td>';
    tbody.appendChild(tr);
  }
  
  for(const id of ['from','to','start','goal']){
    const sel = document.getElementById(id);
    if(!sel) continue;
    sel.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = '-- Selecciona --';
    placeholder.disabled = true;
    placeholder.selected = true;
    sel.appendChild(placeholder);
    for(const n of names){
      const opt = document.createElement('option');
      opt.value = n;
      opt.textContent = n;
      sel.appendChild(opt);
    }
  }
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



async function calcRoute(){
  const start = document.getElementById('start').value;
  const goal = document.getElementById('goal').value;
  if(!start || !goal){
    alert('Selecciona inicio y destino');
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
    out.textContent = 'No se encontro ruta entre los puntos seleccionados';
    out.className = 'result-box error';
    return;
  }
  
  out.innerHTML = '<strong>Ruta encontrada:</strong> ' + j.route.join(' → ') + '<br><strong>Distancia:</strong> ' + Number(j.cost).toFixed(2) + ' km';
  out.className = 'result-box success';
}

window.addEventListener('load', async () => {
  await render();
  document.getElementById('addPlace').addEventListener('click', addPlace);
  document.getElementById('addEdge').addEventListener('click', addEdge);
  document.getElementById('routeBtn').addEventListener('click', calcRoute);
  document.getElementById('refresh').addEventListener('click', render);
});