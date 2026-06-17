const WHATSAPP_NUMBER = '84981778670';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

const allProducts = window.SOLA_PRODUCTS || [];

const wa = (text = 'Hello SOLA Medical Supply, I would like to request a wholesale quotation.') =>
  `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;

$('.menu')?.addEventListener('click', () => $('.links')?.classList.toggle('open'));

$$('[data-wa]').forEach(a => {
  a.href = wa(a.dataset.wa || undefined);
});

function productCard(p) {
  return `
    <article class="product" data-name="${p.name.toLowerCase()}" data-cat="${p.category}" data-brand="${p.brand}">
      <figure>
        <img src="${p.image}" alt="${p.name}">
      </figure>
      <div class="product-body">
        <h3>${p.name}</h3>
        <div class="meta">
          <span class="badge">${p.category}</span>
          <span class="badge">${p.brand}</span>
        </div>
        <p>${p.origin || 'International'} supply • ${p.tag || 'Available on request'}</p>
        <a class="request" href="${wa('Hello SOLA Medical Supply, please quote: ' + p.name)}" target="_blank">
          Request quotation →
        </a>
      </div>
    </article>
  `;
}

function getProductsByMode(grid) {
  const mode = grid.dataset.mode || 'all';

  if (mode === 'featured') {
    return allProducts.filter(p => p.featured === true);
  }

  return allProducts;
}

function renderGrid(grid, list) {
  grid.innerHTML = list.map(productCard).join('') || '<p>No products found.</p>';
}

function renderTable(list) {
  const table = $('[data-products-table]');
  if (!table) return;

  table.innerHTML = list.map(p => `
    <tr>
      <td>${p.name}</td>
      <td>${p.category}</td>
      <td>${p.brand}</td>
      <td>${p.origin || ''}</td>
      <td>
        <a class="request" href="${wa('Hello SOLA Medical Supply, please quote: ' + p.name)}" target="_blank">
          Quote
        </a>
      </td>
    </tr>
  `).join('');
}

function setupProductSections() {
  $$('[data-products-grid]').forEach(grid => {
    const list = getProductsByMode(grid);
    renderGrid(grid, list);
  });
}

function categories(list = allProducts) {
  return ['All', ...new Set(list.map(p => p.category))];
}

function brands(list = allProducts) {
  return ['All', ...new Set(list.map(p => p.brand))].sort();
}

function setupFilters() {
  const cat = $('[data-category-filter]');
  const brand = $('[data-brand-filter]');
  const search = $('[data-search]');
  const grid = $('[data-products-grid][data-mode="all"]') || $('[data-products-grid]');

  if (!cat && !brand && !search) return;

  if (cat) cat.innerHTML = categories(allProducts).map(c => `<option>${c}</option>`).join('');
  if (brand) {
    brand.innerHTML = brands().map(b =>
        `<option value="${b}">${b}</option>`
    ).join('');

    brand.value = 'All';
}

  function apply() {
    const q = (search?.value || '').toLowerCase().trim();
    const c = cat?.value || 'All';
    const b = brand?.value || 'All';

    const list = allProducts.filter(p =>
      (c === 'All' || p.category === c) &&
      (b === 'All' || p.brand === b) &&
      (!q || `${p.name} ${p.category} ${p.brand} ${p.tag || ''}`.toLowerCase().includes(q))
    );

    if (grid) renderGrid(grid, list);
    renderTable(list);
  }

  [cat, brand, search].forEach(el => el?.addEventListener('input', apply));
  apply();
}

function renderBrands() {
  const el = $('[data-brands-grid]');
  if (!el) return;

  const bs = [...new Set(allProducts.map(p => p.brand))].sort();

  el.innerHTML = bs.map(b => `
    <div class="brand-card">
      ${b}<br>
      <small>${allProducts.filter(p => p.brand === b).length} items</small>
    </div>
  `).join('');
}

function setupForm() {
  const f = $('[data-quote-form]');
  if (!f) return;

  f.addEventListener('submit', e => {
    e.preventDefault();

    const data = new FormData(f);

    const msg =
      `Hello SOLA Medical Supply,\n` +
      `Name: ${data.get('name') || ''}\n` +
      `Country: ${data.get('country') || ''}\n` +
      `Products: ${data.get('products') || ''}\n` +
      `Quantity: ${data.get('quantity') || ''}\n` +
      `Message: ${data.get('message') || ''}`;

    window.open(wa(msg), '_blank');
  });
}

setupProductSections();
setupFilters();
renderBrands();
setupForm();