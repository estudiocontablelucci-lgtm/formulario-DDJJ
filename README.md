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

## Los HTML se editan acá

Este repo es el único lugar donde viven los formularios, y el único con git. Las
specs de diseño, los prompts y los workflows de n8n están en
`Ecosistema/formularios-dev/`.

Hasta ago 2026 cada HTML tenía una copia en `formularios-dev` y el flujo era
"editar allá → copiar acá". No había build de por medio: eran dos copias del mismo
archivo, y la copia pisaba el destino, así que una tanda de trabajo hecha
directamente acá quedó a un `cp` de desaparecer. Se eliminó la duplicación.

Ver `CLAUDE.md` para el design system, los patrones de UI y las reglas de contraste.

**El repo es público**: nada de claves, workflows de n8n ni datos de clientes.

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
