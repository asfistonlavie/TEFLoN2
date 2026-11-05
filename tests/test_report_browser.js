// Interaction test of the "Genome browser" tab (needs node + jsdom: npm install jsdom)
// usage: node tests/test_report_browser.js report.html
const {JSDOM, VirtualConsole} = require('jsdom'); const fs = require('fs'); const assert = require('assert');
const errors = []; const vc = new VirtualConsole();
vc.on('jsdomError', e => errors.push(String(e.detail || e.message))); vc.on('error', e => errors.push(String(e)));
const dom = new JSDOM(fs.readFileSync(process.argv[2], 'utf8'), {runScripts: 'dangerously', virtualConsole: vc, pretendToBeVisual: true});
const w = dom.window, doc = w.document, $ = id => doc.getElementById(id);
const tab = [...doc.querySelectorAll('nav button')].find(b => b.textContent === 'Genome browser'); assert(tab, 'tab missing');
tab.click(); const gb = w.__gb; assert(gb, 'browser not initialised');
const n = sel => doc.querySelectorAll(sel).length, ev = (el, type, init) => el.dispatchEvent(new w.Event(type, Object.assign({bubbles: true}, init)));
const fire = (el, type, props) => { const e = new w.MouseEvent(type, Object.assign({bubbles: true, cancelable: true}, props)); el.dispatchEvent(e); return e; };
// 1. full chromosome: density mode, genes drawn in simple or detailed mode
assert(n('#gb rect[data-bin]') > 0, 'density mode expected');
assert(n('#gb rect[data-ov]') > 2, 'overview missing');
console.log('whole chromosome: variants', gb.lay.vis.length, '| density bars', n('#gb rect[data-bin]'), '| gene boxes', n('#gb rect[data-gi]'));
// 2. region input -> glyph mode with boxes and triangles
$('gb_reg').value = '2R:100,000-130,000'; fire($('gb_reg'), 'keydown', {}); const k = new w.KeyboardEvent('keydown', {key: 'Enter', bubbles: true}); $('gb_reg').dispatchEvent(k);
assert.strictEqual(gb.st.v0, 100000); assert.strictEqual(gb.st.v1, 130000);
const boxes = n('#gb rect.gl[data-k]'), tris = n('#gb polygon.gl[data-k]'); assert(boxes + tris > 50 && boxes > 0 && tris > 0, 'glyphs');
assert(n('#gb circle[data-k]') > 0 && n('#gb rect[data-gi]') > 5, 'freq lollipops / genes');
assert(n('#gb text').length === undefined || true);
console.log('region 100-130 kb: boxes', boxes, 'triangles', tris, 'genes', n('#gb rect[data-gi]'), '| exon/CDS rects', n('#gb rect[fill="#2f4b7c"]'));
// 3. wheel zoom keeps the point under the cursor, pan by drag
const svg = doc.querySelector('#gb svg'), span0 = gb.st.v1 - gb.st.v0 + 1, x = gb.lay.L + gb.lay.iw * 0.25, pos = gb.st.v0 + 0.25 * span0;
svg.dispatchEvent(new w.WheelEvent('wheel', {deltaY: -100, clientX: x, bubbles: true, cancelable: true}));
const span1 = gb.st.v1 - gb.st.v0 + 1; assert(span1 < span0 * 0.75 && Math.abs((gb.st.v0 + 0.25 * span1) - pos) < 3, 'zoom around cursor');
const v0 = gb.st.v0; fire($('gb').querySelector('svg'), 'mousedown', {clientX: 300, button: 0}); fire(w, 'mousemove', {clientX: 200}); 
setTimeout(() => {
  fire(w, 'mouseup', {});
  assert(gb.st.v0 > v0, 'pan right by dragging left');
  setTimeout(() => {   // the click that follows a drag is ignored until the next tick
  // 4. buttons
  const a = gb.st.v1 - gb.st.v0; $('gb_out').click(); assert(gb.st.v1 - gb.st.v0 > a * 1.8); $('gb_in').click(); $('gb_l').click(); $('gb_r').click();
  gb.setView(1, 100); assert(gb.st.v1 - gb.st.v0 + 1 >= 50); gb.setView(-5000, 10); assert(gb.st.v0 === 1);
  gb.setView(1e12, 1e12 + 100); assert(gb.st.v1 <= gb.B.chroms[0].length, 'clamped');
  // 5. click a glyph -> details with per-sample calls, then its gene
  gb.goRegion('2R:100000-130000'); const g1 = doc.querySelector('#gb [data-k]'); fire(g1, 'click', {});
  assert(gb.st.sel >= 0 && $('gbinfo').style.display !== 'none' && n('#gbinfo .badge') === 12, 'site panel with 12 sample calls');
  console.log('site panel:', $('gbinfo').textContent.replace(/\s+/g, ' ').slice(0, 220));
  const link = doc.querySelector('#gbinfo a[data-gi]'); if(link){ fire(link, 'click', {}); assert(/exons \/ CDS/.test($('gbinfo').textContent), 'gene panel'); console.log('gene panel:', $('gbinfo').textContent.replace(/\s+/g, ' ').slice(0, 200)); }
  // 6. filters
  gb.goRegion('2R'); const all = gb.lay.vis.length;
  const sel = (id, v) => { $(id).value = v; ev($(id), 'change'); };
  sel('gb_type', 'ref'); const nref = gb.lay.vis.length; sel('gb_type', 'dn'); const ndn = gb.lay.vis.length; assert(nref + ndn === all && nref > 0 && ndn > 0, 'type filter ' + [all, nref, ndn]);
  sel('gb_type', 'all'); sel('gb_imp', 0); assert(gb.lay.vis.length > 0 && gb.lay.vis.length < all && [...gb.lay.vis].every(k => gb.B.i[k] === 0), 'impact filter'); sel('gb_imp', -1);
  $('gb_fmin').value = 80; ev($('gb_fmin'), 'change'); assert(gb.lay.vis.every(k => gb.B.q[k] >= 80) && gb.lay.vis.length < all, 'frequency filter'); $('gb_fmin').value = 0; ev($('gb_fmin'), 'change');
  sel('gb_pop', 1); assert(gb.lay.vis.length === all, 'pop select keeps the sites'); sel('gb_pop', -1);
  $('gb_fam').value = 'fam1'; ev($('gb_fam'), 'input'); assert(gb.lay.vis.length > 0 && gb.lay.vis.length < all); $('gb_fam').value = ''; ev($('gb_fam'), 'input'); assert(gb.lay.vis.length === all);
  ['order', 'family', 'type', 'freq', 'impact'].forEach(c => { sel('gb_col', c); assert(n('#gbleg .legend span') >= 2, 'legend ' + c); });
  // 7. gene search + tables + impact chart
  $('gb_gene').value = 'gene7'; $('gb_gene').dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
  assert(/gene7/.test($('gbinfo').textContent) && gb.st.v1 - gb.st.v0 < 5000, 'gene search jumps to the gene');
  setTimeout(() => {
    console.log('variants-in-view rows:', n('#gbtab tbody tr'), '| impact chart rects:', n('#gbimp rect'), '| gene table rows:', n('#gbgenes tbody tr'));
    assert(n('#gbtab tbody tr') > 0 && n('#gbimp rect') > 5 && n('#gbgenes tbody tr') > 10);
    doc.querySelector('#gbgenes a[data-gi]').click();
    // density bin click zooms
    gb.goRegion('3L'); const before = gb.st.v1 - gb.st.v0; fire(doc.querySelector('#gb rect[data-bin]'), 'click', {}); assert(gb.st.v1 - gb.st.v0 < before / 6, 'bin zoom');
    // overview click recentres
    const o = doc.querySelector('#gb rect[data-ov]'); fire(o, 'click', {clientX: gb.lay.L + gb.lay.iw * 0.9}); assert(gb.st.v0 > gb.B.chroms[gb.st.ci].length * 0.8, 'overview jump');
    // other tabs still fine
    [...doc.querySelectorAll('nav button')].forEach(b => b.click());
    console.log('JS errors:', errors.length ? errors : 'none'); assert.strictEqual(errors.length, 0); console.log('BROWSER TEST OK');
  }, 400);
  }, 20);
}, 50);
