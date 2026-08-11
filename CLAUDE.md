# Formularios DDJJ — Lucci & Asociados

Cuestionarios HTML autocontenidos que los clientes completan para que el estudio
liquide impuestos en ARCA. **Relevan datos, no liquidan.**

**Se trabaja acá.** Este repo tiene los HTML, git y el historial. Las specs, los
prompts de diseño y los workflows de n8n viven en `Ecosistema/formularios-dev/`.

| Ruta | Formulario |
|---|---|
| `/` | Landing |
| `/mono/` | Inscripción Monotributo |
| `/bp/` | Bienes Personales (Ley 23.966) |
| `/iigg/` | Ganancias Personas Humanas (Ley 20.628) |

Deploy: GitHub Pages desde `main` → **formularios.estudiolucci.com.ar**.
Push a `main` publica; el build tarda ~50s. **El repo es público: nada de claves,
workflows de n8n ni datos de clientes acá.**

```bash
python -m http.server 8123     # probar en local
gh api repos/estudiocontablelucci-lgtm/formularios-DDJJ/pages/builds/latest --jq .status
```

---

## Design system

Tema claro desde ago 2026, con los tokens de `Pagina web/pagina-web/app/globals.css`
(`.theme-light`) — los mismos del Dashboard Macro. No es estético: el cliente entra
desde estudiolucci.com.ar y antes la tinta cambiaba de temperatura al cruzar el
link. **Si cambia la paleta de la web, cambiar acá también.**

```
/* Banda superior (header + progress) — oscura, como el nav de la web */
--navy: #162032   --navy-text: #EEEEE8   --navy-muted: #b4b4ac
--navy-border: rgba(255,255,255,0.07)

/* Cuerpo claro */
--bg: #F4F2EC        --card: #FBFAF6      --card-hover: #EFEBE3
--surface: #EFECE4   /* inputs */         --text: #16202F
--muted: #5A6472     --border: rgba(22,32,47,0.10)
--border2: rgba(22,32,47,0.16)
--accent: #00C896       /* SOLO fills sobre navy: la barra de progreso */
--accent-text: #007A5E  /* texto, iconos, bordes y foco sobre claro */

/* Propios del formulario: la web no tiene campos y no los define */
--border-input: #7a7e84   --placeholder: #5A6472   --mid: #7a7e84
--danger: #c0392b         --success: #007A5E
--accent-veil: rgba(0,122,94,.07)
```

### Reglas de color que no son negociables

Los tokens propios existen porque copiar la paleta de la web al pie de la letra
rompe los formularios. Ratios calculados, no elegidos a ojo:

- **Foco y teal de texto usan `--accent-text`, nunca `--accent`.** El #00C896
  sobre un input claro da **1.83:1**: el anillo de foco desaparece.
- **El placeholder no usa el `--muted-2` de la web** (#9BA1AC → **2.20:1**).
- **El borde de input va gris sólido.** Ningún alpha de tinta llega a 3:1 sobre
  cream, ni `rgba(22,32,47,0.45)`.
- **Peso mínimo 400.** El 300 se ve lavado en claro y emborronado en oscuro.
- **Nada de texto por debajo de 12px**, menos aún en mayúsculas.

Al tocar colores, verificar con un cálculo de contraste — no a ojo. Mínimos: 4.5:1
texto, 3:1 bordes y anillos de foco.

### Tipografía

| Rol | Tamaño | Peso |
|---|---|---|
| Título del formulario | 1.6rem | Spectral 600 |
| Título de sección | 1.25rem | Spectral 600 |
| Sub-sección / Conformidad | 1.0625rem | Spectral 600 |
| Marca (header) | 1.35rem | Spectral 600 |
| Labels | 15px | Outfit 400 |
| Hints y notas | 14px | Outfit 400 |

Logo: JPEG base64 embebido, compartido entre los cuatro archivos.

---

## Patrones

- **Secciones colapsables**: `<h3 class="section-head"><button aria-expanded aria-controls>`
  — patrón ARIA de disclosure. **No volver a `<div onclick>`**: antes eran `<span>`
  dentro de un div, así que las secciones no existían como encabezados para un
  lector de pantalla y el acordeón no se abría sin mouse. `toggleSection` resuelve
  el cuerpo por `aria-controls` y sincroniza `aria-expanded` con la clase `hidden`.
- **Progressive reveal** (`toggleReveal`/`REVEAL_MAP`): campos hijos visibles sólo
  si la pregunta gatillo lo habilita. Soporta cascada.
- **Slot cards** para bienes repetibles, con textarea de overflow al final.
- **Autoguardado** en localStorage por formulario; `syncAllReveals()` al restaurar.
- **Export XLSX** con estilos vía xlsx-js-style (CDN).
- **Conformidad legal**: checkbox obligatorio (Art. 11 Ley 11.683) + nombre + fecha.
- **Envío**: `fetch()` POST al webhook n8n. Hash SHA-256 del payload; la IP la
  captura n8n desde headers de Cloudflare.

## scripts/

Transforman los tres formularios a la vez. Todos aceptan `--check` para correr en
seco. Trabajan por selector, no con reemplazos globales: `iigg` tiene un bloque
`.alerta-mono` propio que un search & replace ciego pisaría.

| Script | Qué hace |
|---|---|
| `migrar_tema_claro.py` | Migra la paleta al tema claro |
| `mejorar_titulos.py` | Escala tipográfica y acordeón accesible |

---

## Zonas protegidas

- **Los formularios no calculan impuestos.** Sólo relevan datos.
- **Valores normativos** (escalas Art. 94, deducciones Art. 30, topes Art. 85) no
  van acá: van en las planillas de liquidación del estudio.
- **Sin notas técnicas para el cliente**: criterios de valuación y artículos de
  ley los maneja el estudio.
- Si se agregan o quitan campos, hay que actualizar `n8n/headers-*.tsv` en
  `formularios-dev` y regenerar la Ficha de la Sheet, o el envío se desalinea.
