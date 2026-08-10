"""Jerarquia de titulos y accordion accesible en los tres formularios.

Hace tres cosas:

1. HTML — cada cabecera de seccion pasa de <div onclick> a
   <h3 class="section-head"><button aria-expanded aria-controls>. Eso le da a
   las secciones un encabezado real (hoy son <span>, invisibles para un lector
   de pantalla) y las vuelve operables con teclado (hoy no lo son).
2. CSS — escala tipografica con saltos perceptibles, usando los pesos Spectral
   600 que las paginas ya descargan pero nunca pintan.
3. JS  — toggleSection resuelve el cuerpo por aria-controls y mantiene
   aria-expanded en sincronia con el estado visual.

Uso:  python scripts/mejorar_titulos.py [--check]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FORMULARIOS = ("mono", "bp", "iigg")

# ---------------------------------------------------------------- HTML

CABECERA = re.compile(
    r'( *)<div class="section-head" onclick="toggleSection\(this, event\)">\n'
    r'(.*?)\n'
    r' *</div>\n'
    r'( *)<div class="section-body([^"]*)"',
    re.S,
)


def transformar_cabeceras(texto: str, slug: str) -> tuple[str, int]:
    contador = [0]

    def reemplazo(m: re.Match) -> str:
        sangria, interior, sangria_body, clases_body = (
            m.group(1), m.group(2), m.group(3), m.group(4)
        )
        contador[0] += 1
        ident = f"sec-{slug}-{contador[0]}"
        abierta = "hidden" not in clases_body

        # el interior se indenta un nivel mas: ahora vive dentro del <button>
        interior = "\n".join("  " + l if l.strip() else l
                             for l in interior.split("\n"))

        return (
            f'{sangria}<h3 class="section-head">\n'
            f'{sangria}  <button type="button" aria-expanded="{str(abierta).lower()}" '
            f'aria-controls="{ident}" onclick="toggleSection(this, event)">\n'
            f'{interior}\n'
            f'{sangria}  </button>\n'
            f'{sangria}</h3>\n'
            f'{sangria_body}<div id="{ident}" class="section-body{clases_body}"'
        )

    return CABECERA.sub(reemplazo, texto), contador[0]


# ---------------------------------------------------------------- CSS

CSS_VIEJO = (
    "  .section-head { padding: 1rem 1.5rem; display: flex; align-items: center; "
    "gap: .75rem; cursor: pointer; user-select: none; transition: background .15s; }\n"
    "  .section-head:hover { background: var(--card-hover); }"
)
CSS_NUEVO = """  .section-head { margin: 0; font-size: inherit; font-weight: inherit; }
  .section-head button {
    width: 100%;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: .75rem;
    cursor: pointer;
    user-select: none;
    transition: background .15s;
    background: transparent;
    border: none;
    font-family: inherit;
    color: inherit;
    text-align: left;
  }
  .section-head button:hover { background: var(--card-hover); }
  .section-head button:focus-visible { outline: 2px solid var(--accent-text); outline-offset: -2px; }"""

# Escala: saltos de 28% y 18% en lugar del 4-5% actual, y peso 600 (ya cargado).
TIPOGRAFIA: list[tuple[str, str]] = [
    # titulo del formulario — el mas grande del cuerpo
    ('.intro-box h2 { font-family: var(--serif); font-size: 1.3rem; font-weight: 400;',
     '.intro-box h2 { font-family: var(--serif); font-size: 1.6rem; font-weight: 600;'),
    # titulo de seccion
    ('.section-title { font-family: var(--serif); font-size: 1.1rem; font-weight: 400;',
     '.section-title { font-family: var(--serif); font-size: 1.25rem; font-weight: 600;'),
    ('.section-letter { font-family: var(--serif); font-size: 1rem; font-weight: 500;',
     '.section-letter { font-family: var(--serif); font-size: 1.25rem; font-weight: 600;'),
    # marca en el header
    ('.header-text h1 { font-family: var(--serif); font-size: 1.35rem; font-weight: 400;',
     '.header-text h1 { font-family: var(--serif); font-size: 1.35rem; font-weight: 600;'),
    # sub-bloques (solo bp/iigg)
    ('.sub-section-title { font-family: var(--serif); font-size: .95rem; color: var(--text); font-weight: 400; }',
     '.sub-section-title { font-family: var(--serif); font-size: 1.0625rem; color: var(--text); font-weight: 600; }'),
    # "Conformidad" — hermano de las secciones, mismo tratamiento
    ('.firma-box h3 { font-family: var(--serif); font-size: 1.05rem; font-weight: 400;',
     '.firma-box h3 { font-family: var(--serif); font-size: 1.25rem; font-weight: 600;'),
    # el padding responsive se muda al boton
    ('    .section-head { padding: .85rem 1rem; }',
     '    .section-head button { padding: .85rem 1rem; }'),
]

# mono/ nunca tuvo regla para su <h3>Conformidad</h3>: sale con el default del
# navegador (sans, bold). Se inserta junto a las demas reglas de firma.
REGLA_H3_MONO = (
    "  .firma-box { background: var(--card);",
    '  .firma-box h3 { font-family: var(--serif); font-size: 1.25rem; font-weight: 600; '
    'color: var(--text); margin-bottom: .75rem; }\n  .firma-box { background: var(--card);',
)

# ---------------------------------------------------------------- JS

# mono/ y bp+iigg/ escriben la misma logica de dos formas distintas.
JS_VIEJO_VARIANTES = [
    """function toggleSection(head, event) {
  event.stopPropagation();
  const body = head.nextElementSibling;
  const toggle = head.querySelector('.section-toggle');
  body.classList.toggle('hidden');
  toggle.classList.toggle('open');
}""",
    """function toggleSection(head, event) {
  event.stopPropagation();
  const body = head.nextElementSibling;
  const toggle = head.querySelector('.section-toggle');
  if (body.classList.contains('hidden')) {
    body.classList.remove('hidden');
    toggle.classList.add('open');
  } else {
    body.classList.add('hidden');
    toggle.classList.remove('open');
  }
}""",
]

JS_NUEVO = """function toggleSection(btn, event) {
  event.stopPropagation();
  // el cuerpo se resuelve por aria-controls: el boton ya no es hermano del body
  const body = document.getElementById(btn.getAttribute('aria-controls'));
  const toggle = btn.querySelector('.section-toggle');
  const abierta = body.classList.toggle('hidden') === false;
  toggle.classList.toggle('open', abierta);
  btn.setAttribute('aria-expanded', String(abierta));
}"""


def migrar(texto: str, slug: str) -> tuple[str, list[str]]:
    avisos: list[str] = []

    texto, n = transformar_cabeceras(texto, slug)
    if n == 0:
        avisos.append("NO se transformo ninguna cabecera")
    else:
        avisos.append(f"ok: {n} cabeceras -> <h3><button>")

    if CSS_VIEJO in texto:
        texto = texto.replace(CSS_VIEJO, CSS_NUEVO, 1)
    else:
        avisos.append("NO se encontro el CSS de .section-head")

    for variante in JS_VIEJO_VARIANTES:
        if variante in texto:
            texto = texto.replace(variante, JS_NUEVO, 1)
            break
    else:
        avisos.append("NO se encontro toggleSection")

    for viejo, nuevo in TIPOGRAFIA:
        if viejo in texto:
            texto = texto.replace(viejo, nuevo)

    # regla faltante del h3 de mono
    if ".firma-box h3" not in texto:
        if REGLA_H3_MONO[0] in texto:
            texto = texto.replace(*REGLA_H3_MONO, 1)
            avisos.append("ok: se agrego la regla .firma-box h3 que faltaba")
        else:
            avisos.append("NO se pudo insertar la regla .firma-box h3")

    return texto, avisos


def main() -> int:
    check = "--check" in sys.argv
    fallos = 0

    for nombre in FORMULARIOS:
        ruta = REPO / nombre / "index.html"
        migrado, avisos = migrar(ruta.read_text(encoding="utf-8"), nombre)

        print(f"=== {nombre}/index.html")
        for a in avisos:
            print(f"    {a}")
            if a.startswith("NO"):
                fallos += 1
        if check:
            print("    (--check: no se escribio nada)")
        else:
            ruta.write_text(migrado, encoding="utf-8")
            print("    escrito")
        print()

    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
