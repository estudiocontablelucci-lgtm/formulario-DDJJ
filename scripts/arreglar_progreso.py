"""Hace que la barra de progreso cuente solo los campos que el cliente tiene que
completar, y que las cajas de texto ocupen el ancho de su tarjeta.

EL PROBLEMA. Las cuatro barras contaban todos los campos del HTML, incluidos los
de bloques que estaban ocultos porque no aplicaban. Medido antes de este script:

    mono   18 de 40 campos ocultos  -> techo real  55%
    bp     94 de 104               -> techo real  10%
    iigg   (mismo mecanismo que bp)
    sas    ~20 de ~70              -> techo real  70%   (ya arreglado)

Es decir: un cliente que completaba TODO el formulario veia la barra a la mitad o
menos, y nunca llegaba a 100. Ademas arrancaban por encima de cero, porque la
fecha de firma se autocompleta sola y contaba como campo ya resuelto.

EL ARREGLO. Un helper `campoCuentaParaProgreso()` que descarta:
  - campos dentro de un bloque de reveal cerrado, en los DOS mecanismos que
    conviven en el repo: `.conditional` sin `.visible` (mono, sas) y
    `.reveal-slot` con display:none (bp, iigg);
  - campos marcados `data-autocompletado` (la fecha de firma, la nacionalidad
    precargada de sas).
Lo excluido sale del numerador Y del denominador: si sale de uno solo, el 100%
se vuelve inalcanzable, que es justo el bug que se esta arreglando.

Las tres implementaciones de actualizarProgreso() son distintas entre si (mono y
sas iteran querySelectorAll; bp e iigg iteran form.elements), asi que cada una se
parchea por su propio ancla.

TAMBIEN. Quita `max-width: 62ch` de las cajas con fondo y borde (.nota, .aviso,
.intro-box p, .firma-box p). Esa medida es correcta para un parrafo suelto, pero
dentro de una caja que esta al lado de inputs que llegan al borde, el corte no se
lee como linea corta: se lee como layout roto. `.field .hint` la conserva, que es
texto suelto y ahi si ayuda.

    python scripts/arreglar_progreso.py --check    # que cambiaria, sin escribir
    python scripts/arreglar_progreso.py
"""
import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FORMS = ['mono', 'bp', 'iigg', 'sas']

HELPER = '''/* Solo cuentan para el progreso los campos que el cliente tiene que completar.
   Quedan afuera los de un bloque de reveal cerrado —conviven dos mecanismos en
   el repo: .conditional sin .visible, y .reveal-slot con display:none— y los que
   el formulario resuelve solo (data-autocompletado). Lo excluido sale del
   numerador y del denominador: si saliera de uno solo, el 100% no se alcanza. */
function campoCuentaParaProgreso(el) {
  if (el.dataset && el.dataset.autocompletado !== undefined) return false;
  var cond = el.closest('.conditional');
  if (cond && !cond.classList.contains('visible')) return false;
  var slot = el.closest('.reveal-slot');
  while (slot) {
    if (slot.style.display === 'none') return false;
    slot = slot.parentElement ? slot.parentElement.closest('.reveal-slot') : null;
  }
  return true;
}

'''

# (ancla, reemplazo) por formulario. Cada actualizarProgreso es distinta.
PARCHES = {
    'mono': [
        ("  form.querySelectorAll('input[type=radio]').forEach(r => { radios[r.name] = radios[r.name] || r.checked; });",
         "  form.querySelectorAll('input[type=radio]').forEach(r => {\n"
         "    if (!campoCuentaParaProgreso(r)) return;\n"
         "    radios[r.name] = radios[r.name] || r.checked;\n"
         "  });"),
        ("  inputs.forEach(i => { total++; if (i.value.trim()) filled++; });",
         "  inputs.forEach(i => {\n"
         "    if (!campoCuentaParaProgreso(i)) return;\n"
         "    total++; if (i.value.trim()) filled++;\n"
         "  });"),
    ],
    'bp': [
        ("    if (!el.name || seen.has(el.name)) continue;",
         "    if (!el.name || seen.has(el.name)) continue;\n"
         "    if (!campoCuentaParaProgreso(el)) continue;"),
    ],
}
PARCHES['iigg'] = PARCHES['bp']
PARCHES['sas'] = []  # ya parcheado a mano

# Cajas con fondo/borde: el 62ch se saca. .field .hint no esta en la lista.
SELECTORES_CAJA = ['.nota', '.aviso', '.intro-box p', '.firma-box p']


def quitar_62ch(html, selector):
    """Saca max-width: 62ch del bloque de un selector, sin tocar los demas."""
    patron = re.compile(
        r'(' + re.escape(selector) + r'\s*\{[^}]*?)\s*max-width:\s*62ch;([^}]*\})', re.S)
    nuevo, n = patron.subn(r'\1\2', html)
    return nuevo, n


def procesar(form, check):
    ruta = REPO / form / 'index.html'
    html = original = ruta.read_text(encoding='utf-8')
    cambios = []

    # 1. helper (una sola vez)
    if 'function campoCuentaParaProgreso' not in html:
        ancla = 'function actualizarProgreso()'
        if html.count(ancla) != 1:
            sys.exit(f'{form}: esperaba 1 "{ancla}", hay {html.count(ancla)}')
        html = html.replace(ancla, HELPER + ancla, 1)
        cambios.append('helper campoCuentaParaProgreso')

    # 2. usarlo en actualizarProgreso
    for viejo, nuevo in PARCHES[form]:
        if nuevo.strip() in html:
            continue
        if html.count(viejo) != 1:
            sys.exit(f'{form}: el ancla del progreso aparece {html.count(viejo)} veces, esperaba 1')
        html = html.replace(viejo, nuevo, 1)
        cambios.append('conteo de progreso')

    # 3. la fecha de firma se autocompleta: no es un campo a completar
    m = re.search(r'<input[^>]*id="firmaFecha"[^>]*>', html)
    if m and 'data-autocompletado' not in m.group(0):
        html = html.replace(m.group(0), m.group(0).replace('<input', '<input data-autocompletado', 1), 1)
        cambios.append('firma_fecha marcada')

    # 4. 62ch fuera de las cajas
    for sel in SELECTORES_CAJA:
        html, n = quitar_62ch(html, sel)
        if n:
            cambios.append(f'62ch fuera de {sel}')

    if not cambios:
        print(f'  {form}: sin cambios (ya estaba)')
        return False

    print(f'  {form}: {", ".join(cambios)}')
    if not check:
        ruta.write_text(html, encoding='utf-8')
    return html != original


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='no escribe, solo informa')
    args = ap.parse_args()

    print('--check (nada se escribe)\n' if args.check else 'aplicando\n')
    tocados = sum(procesar(f, args.check) for f in FORMS)
    print(f'\n{tocados} formulario(s) {"a modificar" if args.check else "modificados"}')


if __name__ == '__main__':
    main()
