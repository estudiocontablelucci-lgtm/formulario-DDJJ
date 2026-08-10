"""Migra bp/ e iigg/ al tema claro, igualando lo ya aplicado a mono/.

Trabaja linea por linea sobre el bloque <style>: primero las reglas de la banda
superior (que queda navy), despues el resto del cuerpo. No hace reemplazos
globales a ciegas — cada linea se transforma segun el selector al que pertenece.

Uso:  python scripts/migrar_tema_claro.py [--check]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FORMULARIOS = ("bp", "iigg")

ROOT_NUEVO = """  :root {
    /* Banda superior — queda oscura, igual que el nav de estudiolucci.com.ar */
    --navy:       #162032;
    --navy-text:  #EEEEE8;
    --navy-muted: #b4b4ac;
    --navy-border: rgba(255,255,255,0.07);

    /* Cuerpo claro — tokens de pagina-web/app/globals.css (.theme-light) */
    --bg:         #F4F2EC;
    --card:       #FBFAF6;
    --card-hover: #EFEBE3;
    --surface:    #EFECE4;
    --text:       #16202F;
    --muted:      #5A6472;
    --border:     rgba(22,32,47,0.10);
    --border2:    rgba(22,32,47,0.16);
    --accent:     #00C896;
    --accent-text: #007A5E;

    /* Propios del formulario — la web no tiene campos, estos no existen alla */
    --border-input: #7a7e84;
    --placeholder:  #5A6472;
    --mid:          #7a7e84;
    --danger:       #c0392b;
    --success:      #007A5E;
    --accent-veil:  rgba(0,122,94,.07);

    --radius:  6px;
    --serif:   'Spectral', Georgia, serif;
    --sans:    'Outfit', system-ui, sans-serif;
  }"""

# Reglas de la banda superior: mantienen paleta oscura.
BANDA_NAVY: dict[str, list[tuple[str, str]]] = {
    ".site-header": [("var(--dark2)", "var(--navy)"),
                     ("1px solid var(--border)", "1px solid var(--navy-border)")],
    ".header-text h1": [("var(--white)", "var(--navy-text)")],
    ".header-text p": [("var(--muted)", "var(--navy-muted)"), ("font-size: 12px", "font-size: 13px")],
    ".progress-wrap": [("var(--dark2)", "var(--navy)"), ("var(--border)", "var(--navy-border)")],
    ".progress-track": [("background: var(--border)", "background: rgba(255,255,255,0.12)")],
    ".progress-text": [("var(--muted)", "var(--navy-muted)"), ("font-size: 11px", "font-size: 12px")],
}

# Cuerpo claro: (regex de linea, [(buscar, reemplazar)])
CUERPO: list[tuple[str, list[tuple[str, str]]]] = [
    # bloques multilinea, identificados por su selector abierto
    (r"^body$", [("var(--dark)", "var(--bg)"), ("var(--light)", "var(--text)"),
                 ("font-weight: 300", "font-weight: 400")]),
    (r"^select$", [("var(--dark)", "var(--surface)"), ("var(--light)", "var(--text)"),
                   ("font-weight: 300", "font-weight: 400")]),
    (r"^\.btn$", [("var(--light)", "var(--text)"), ("font-size: 13px", "font-size: 14px"),
                  ("1px solid var(--border2)", "1px solid var(--mid)")]),
    (r"^\.radio-option, \.check-option$", [("font-size: 13px", "font-size: 14px")]),
    (r"^\.nota$", [("font-size: 13px", "font-size: 14px"),
                   ("line-height: 1.65;", "line-height: 1.65; max-width: 62ch;")]),
    (r"^\.alerta-mono$", [("var(--light)", "var(--text)"),
                          ("2px solid var(--accent)", "2px solid var(--accent-text)")]),
    (r"^\.alerta-mono \.btn-continuar$", [("var(--accent)", "var(--accent-text)")]),
    # cards
    (r"\.intro-box \{|\.section \{|\.toast \{|\.firma-box \{",
     [("var(--dark2)", "var(--card)")]),
    (r"\.intro-box h2|\.section-title |\.firma-box h3",
     [("var(--white)", "var(--text)")]),
    (r"\.intro-box p", [("font-size: 13px", "font-size: 14px"),
                        ("line-height: 1.7;", "line-height: 1.7; max-width: 62ch;")]),
    (r"\.section-head:hover|\.radio-option:hover|\.btn:hover",
     [("var(--dark3)", "var(--card-hover)")]),
    (r"\.sub-section-title", [("var(--light)", "var(--text)")]),
    # tipografia de campos
    (r"\.field label", [("font-size: 14px", "font-size: 15px"), ("var(--light)", "var(--text)")]),
    (r"\.field \.hint", [("font-size: 12px", "font-size: 14px"), ("#9e9e96", "var(--muted)"),
                         ("font-weight: 400;", "font-weight: 400; max-width: 62ch;")]),
    (r"\.section-badge", [("font-size: 10px", "font-size: 12px")]),
    (r"\.section-toggle", [("font-size: 12px", "font-size: 14px")]),
    (r"\.sub-title", [("font-size: 10px", "font-size: 12px")]),
    (r"\.jurisdiccion-num", [("font-size: 10px", "font-size: 12px"),
                             ("var(--accent)", "var(--accent-text)")]),
    (r"\.btn-remove \{", [("font-size: 11px", "font-size: 12px"),
                          ("1px solid var(--border)", "1px solid var(--border2)")]),
    (r"\.autosave", [("font-size: 11px", "font-size: 12px")]),
    (r"\.monto-item label", [("font-size: 11px", "font-size: 12px")]),
    # sub-bloques
    (r"\.sub-section \{|\.jurisdiccion-item \{", [("var(--dark)", "var(--bg)")]),
    # nota
    (r"background: rgba\(0,200,150,\.04\);", [("rgba(0,200,150,.04)", "var(--accent-veil)")]),
    (r"border-left: 3px solid var\(--accent\);", [("var(--accent)", "var(--accent-text)")]),
    (r"^\s+color: #9e9e96;$", [("#9e9e96", "var(--muted)")]),
    (r"\.nota strong", [("var(--light)", "var(--text)"), ("font-weight: 400", "font-weight: 500")]),
    (r"\.nota a \{", [("var(--accent)", "var(--accent-text)"),
                      ("text-decoration: none", "text-decoration: underline")]),
    # radios
    (r"\.radio-option:hover", [("var(--mid)", "var(--mid)")]),
    (r"\.radio-option input", [("var(--accent)", "var(--accent-text)")]),
    (r"\.radio-option:has", [("var(--accent)", "var(--accent-text)"),
                             ("rgba(0,200,150,.05)", "var(--accent-veil)")]),
    # botones
    (r"\.btn-primary \{", [("background: var(--accent)", "background: var(--accent-text)"),
                           ("color: var(--dark)", "color: #FBFAF6"),
                           ("border-color: var(--accent)", "border-color: var(--accent-text)")]),
    (r"\.btn-primary:hover", [("#00b087", "#00624B")]),
    (r"\.btn-add \{", [("var(--accent)", "var(--accent-text)"),
                       ("dashed var(--border2)", "dashed var(--mid)"),
                       ("font-size: 12px", "font-size: 14px")]),
    (r"\.btn-add:hover", [("var(--accent)", "var(--accent-text)"),
                          ("rgba(0,200,150,.05)", "var(--accent-veil)")]),
    (r"\.toast \{", [("var(--light)", "var(--text)"), ("font-size: 13px", "font-size: 14px"),
                     ("1px solid var(--border)", "1px solid var(--border2)"),
                     ("pointer-events: none;", "pointer-events: none; "
                      "box-shadow: 0 4px 16px rgba(22,32,47,.14);")]),
    (r"\.toast\.success", [("var(--accent)", "var(--success)")]),
    # alerta-mono (solo iigg)
    (r"background: rgba\(0,200,150,\.06\);", [("rgba(0,200,150,.06)", "var(--accent-veil)")]),
    (r"\.alerta-mono \.btn-continuar:hover", [("rgba(0,200,150,.1)", "var(--accent-veil)")]),
    (r"^\s+border: 2px solid var\(--accent\);$", [("var(--accent)", "var(--accent-text)")]),
    (r"^\s+color: var\(--accent\);$", [("var(--accent)", "var(--accent-text)")]),
    # firma
    (r"\.firma-box p", [("font-size: 13px", "font-size: 14px"),
                        ("line-height: 1.7;", "line-height: 1.7; max-width: 62ch;")]),
    (r"\.firma-campo label", [("font-size: 11px", "font-size: 12px")]),
    (r"\.firma-campo input \{", [("1px solid var(--border)", "1px solid var(--border-input)"),
                                 ("var(--light)", "var(--text)"),
                                 ("font-size: 13px", "font-size: 14px")]),
]

# Bloques que se reemplazan enteros (mas claro que parchear pieza por pieza).
BLOQUES: list[tuple[str, str]] = [
    (
        "  input:focus, textarea:focus, select:focus { border-color: var(--mid); background: #0a1018; }",
        "  input:focus, textarea:focus, select:focus { border-color: var(--accent-text); "
        "box-shadow: 0 0 0 2px rgba(0,122,94,.30); background: #FFFFFF; }",
    ),
    (
        "  input::placeholder, textarea::placeholder { color: #6e7280; font-weight: 400; }",
        "  input::placeholder, textarea::placeholder { color: var(--placeholder); font-weight: 400; }",
    ),
]

# Ancla tras la cual se inserta la regla del select. bp/ e iigg/ nunca tuvieron
# chevron propio (usan la flecha nativa), asi que aca se agrega, no se reemplaza.
ANCLA_SELECT = ("  input::placeholder, textarea::placeholder "
                "{ color: var(--placeholder); font-weight: 400; }")

CHEVRON_NUEVO = (
    "  input[type=date] { color-scheme: light; }\n"
    "  select { appearance: none; -webkit-appearance: none; -moz-appearance: none; cursor: pointer; "
    "background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' "
    "height='14' viewBox='0 0 24 24' fill='none' stroke='%235A6472' stroke-width='2'%3E%3Cpolyline "
    "points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E\"); background-repeat: no-repeat; "
    "background-position: right .85rem center; padding-right: 2.4rem; }\n"
    "  select option { background: var(--card); color: var(--text); }"
)

# El bloque de inputs: --border2 pasa a --border-input y el peso sube.
INPUT_BORDE = ("    border: 1px solid var(--border2);", "    border: 1px solid var(--border-input);")


def migrar(texto: str) -> tuple[str, list[str]]:
    avisos: list[str] = []

    # 1. bloque :root completo
    nuevo, n = re.subn(r"  :root \{.*?\n  \}", ROOT_NUEVO, texto, count=1, flags=re.S)
    if n == 0:
        avisos.append("NO se encontro el bloque :root")
    texto = nuevo

    # 2. bloques literales
    for viejo, reemplazo in BLOQUES:
        if viejo in texto:
            texto = texto.replace(viejo, reemplazo)
        else:
            avisos.append(f"NO se encontro el bloque: {viejo.strip()[:60]}")

    # 3. select con flecha propia + date picker claro (se insertan, no existian)
    if ANCLA_SELECT in texto:
        texto = texto.replace(ANCLA_SELECT, ANCLA_SELECT + "\n" + CHEVRON_NUEVO, 1)
    else:
        avisos.append("NO se encontro el ancla para insertar la regla del select")

    # 4. borde de input (dentro del bloque de campos, antes del media query)
    if INPUT_BORDE[0] in texto:
        texto = texto.replace(*INPUT_BORDE, 1)
    else:
        avisos.append("NO se encontro el borde de input")

    # 5. transformaciones, siguiendo el selector abierto (los bloques son multilinea)
    lineas = texto.splitlines()
    en_style = False
    selector = ""          # selector del bloque abierto, "" si estamos fuera
    for i, linea in enumerate(lineas):
        if "<style>" in linea:
            en_style = True
            continue
        if "</style>" in linea:
            en_style = False
        if not en_style:
            continue

        # Un patron aplica si matchea la linea (reglas de una sola linea) o el
        # selector abierto (bloques multilinea). Probarlos por separado: si se
        # concatenaran, los patrones anclados con ^ dejarian de matchear.
        def aplica(patron: str) -> bool:
            return bool(re.search(patron, linea)
                        or (selector and re.search(patron, selector)))

        for marca, subs in BANDA_NAVY.items():
            if marca in linea or (selector and marca in selector):
                for buscar, reemplazar in subs:
                    linea = linea.replace(buscar, reemplazar)

        for patron, subs in CUERPO:
            if aplica(patron):
                for buscar, reemplazar in subs:
                    linea = linea.replace(buscar, reemplazar)

        lineas[i] = linea

        # actualizar el selector abierto DESPUES de transformar
        despojada = linea.strip()
        if despojada.endswith("{") and not despojada.startswith("@"):
            selector = despojada[:-1].strip()
        elif despojada.startswith("}") or despojada.endswith("}"):
            selector = ""

    texto = "\n".join(lineas) + ("\n" if texto.endswith("\n") else "")

    # 6. estilos inline del HTML (fuera del <style>): solo tokens de texto
    texto = texto.replace('style="color:var(--light);', 'style="color:var(--text);')

    # 7. remanentes de tokens oscuros que ninguna regla cubrio
    for n, linea in enumerate(texto.splitlines(), 1):
        for viejo in ("var(--dark2)", "var(--dark3)", "var(--light)",
                      "var(--white)", "var(--dark)"):
            if viejo in linea:
                avisos.append(f"L{n} remanente {viejo}: {linea.strip()[:90]}")

    return texto, avisos


def main() -> int:
    check = "--check" in sys.argv
    problemas = 0

    for nombre in FORMULARIOS:
        ruta = REPO / nombre / "index.html"
        original = ruta.read_text(encoding="utf-8")
        migrado, avisos = migrar(original)

        print(f"=== {nombre}/index.html")
        for a in avisos:
            print(f"    aviso: {a}")
            problemas += 1
        if not avisos:
            print("    sin avisos")

        if check:
            print("    (--check: no se escribio nada)")
        else:
            ruta.write_text(migrado, encoding="utf-8")
            print(f"    escrito ({len(migrado)} bytes)")
        print()

    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
