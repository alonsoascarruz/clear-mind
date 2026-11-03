// Menú común. Para agregar una página nueva, añade una línea a PAGINAS.
const PAGINAS = [
  { nombre: 'Pendientes', ruta: '/' },
  { nombre: 'Mochila Trabajo', ruta: '/mochila' },
  { nombre: 'Morral', ruta: '/morral' },
  { nombre: 'Hábitos', ruta: '/habitos' }
];

(function () {
  const estilo = document.createElement('style');
  estilo.textContent = `
    html { padding-top: 52px; }
    body { min-height: calc(100vh - 52px) !important; }
    .menu-barra {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100; height: 52px;
      display: flex; align-items: stretch; gap: 4px; padding: 0 16px;
      background: #1B2A55; font-family: "Segoe UI", system-ui, sans-serif;
      overflow-x: auto; white-space: nowrap;
    }
    .menu-barra a {
      display: flex; align-items: center; padding: 0 14px;
      color: #B8C4E3; text-decoration: none; font-size: 15px; font-weight: 600;
      border-bottom: 3px solid transparent;
    }
    .menu-barra a:hover { color: #fff; }
    .menu-barra a[aria-current="page"] { color: #fff; border-bottom-color: #8FB1FF; }
    .menu-barra a:focus-visible { outline: 3px solid #8FB1FF; outline-offset: -3px; }
    @media print {
      .menu-barra { display: none; }
      html { padding-top: 0; }
      body { min-height: 0 !important; }
    }
  `;
  document.head.append(estilo);

  const nav = document.createElement('nav');
  nav.className = 'menu-barra';
  nav.setAttribute('aria-label', 'Menú principal');

  const actual = location.pathname.replace(/\/+$/, '') || '/';
  for (const p of PAGINAS) {
    const a = document.createElement('a');
    a.href = p.ruta;
    a.textContent = p.nombre;
    if (p.ruta === actual) a.setAttribute('aria-current', 'page');
    nav.append(a);
  }
  document.body.prepend(nav);
})();
