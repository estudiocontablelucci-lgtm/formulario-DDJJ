# Formularios DDJJ — Lucci & Asociados

Cuestionarios HTML autocontenidos que los clientes del estudio completan para que
el equipo liquide impuestos en ARCA. Los formularios **relevan datos, no liquidan**.

Publicado con GitHub Pages desde `main` en **formularios.estudiolucci.com.ar**
(CNAME en Cloudflare → `estudiocontablelucci-lgtm.github.io`).

| Ruta | Formulario |
|---|---|
| `/` | Landing con los tres accesos |
| `/mono/` | Inscripción Monotributo |
| `/bp/` | Bienes Personales (Ley 23.966) |
| `/iigg/` | Ganancias Personas Humanas (Ley 20.628) |

## Este repo es un artefacto de deploy

Las fuentes de los tres formularios viven en `Ecosistema/formularios-dev/`, junto
con las specs, los workflows de n8n y el `CLAUDE.md` que documenta el design
system. El flujo normal es: editar allá → copiar acá → push a `main`.

**Esa copia pisa el destino.** Si se edita un formulario directamente en este
repo, hay que copiarlo de vuelta a `formularios-dev` o el próximo deploy lo borra.
Antes de tocar algo, verificar que coincidan:

```bash
# desde Ecosistema/
diff "formularios-dev/Monotributo/Formulario - Monotributo.html" mono/index.html
diff "formularios-dev/bienes-personales/cuestionario-bp.html"    bp/index.html
diff "formularios-dev/ganancias-ph/cuestionario-iigg.html"       iigg/index.html
```

Dos cosas existen **sólo acá** y no tienen contraparte en las fuentes: la landing
(`index.html`) y los scripts de mantenimiento (`scripts/`).

## scripts/

Transformaciones sobre los tres formularios a la vez. Cada uno acepta `--check`
para correr en seco y reportar sin escribir nada.

| Script | Qué hace |
|---|---|
| `migrar_tema_claro.py` | Migra la paleta al tema claro de la web |
| `mejorar_titulos.py` | Escala tipográfica y acordeón accesible (`<h3><button aria-expanded>`) |

Los dos transforman cada línea según el selector al que pertenece, en vez de hacer
reemplazos globales: `iigg` tiene un bloque `.alerta-mono` propio que un search &
replace ciego pisaría.

## Probar en local

```bash
python -m http.server 8123     # http://localhost:8123/
```

## Accesibilidad

La paleta y la jerarquía están calculadas, no elegidas a ojo. Todo el texto pasa
WCAG AA y la mayoría AAA; los indicadores no textuales (bordes de input, anillo de
foco) pasan el mínimo de 3:1. Las reglas que sostienen eso están en el
`CLAUDE.md` de `formularios-dev`, sección "Reglas de color que no son negociables".
