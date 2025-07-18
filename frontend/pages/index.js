import { useEffect, useState } from 'react';

export default function Home() {
  const [aep, setAep] = useState([]);
  const [eze, setEze] = useState([]);

  useEffect(() => {
    fetch('/data/vuelos-aep.json')
      .then(res => res.json())
      .then(setAep);
    fetch('/data/vuelos-eze.json')
      .then(res => res.json())
      .then(setEze);
  }, []);

  const renderVuelos = (vuelos) => (
    vuelos.map(v => (
      <div key={`${v.origen}-${v.numero_vuelo}`} style={{border:'1px solid #ddd', padding: '1rem', margin: '0.5rem'}}>
        <h4>{v.hora_salida} - {v.aerolinea} ({v.numero_vuelo})</h4>
        <p>Origen: {v.origen} | Estado: {v.estado}</p>
        <small>🕓 Hora estimada de arribo a Corrientes: {v.hora_estimacion_arribo}</small>
      </div>
    ))
  );

  return (
    <main style={{padding:'2rem', fontFamily:'sans-serif'}}>
      <h1>Vuelos AEP → CNQ</h1>
      {renderVuelos(aep)}
      <h1>Vuelos EZE → CNQ</h1>
      {renderVuelos(eze)}
    </main>
  );
}
