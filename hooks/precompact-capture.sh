#!/usr/bin/env bash
# Hook PreCompact: frena la compactacion y le pide a Claude que capture el
# conocimiento de la conversacion ANTES de que el resumen lo degrade.
#
# Por que el hook no extrae nada el mismo: un hook es un comando de shell, no
# puede razonar sobre la conversacion. Lo que si puede es elegir el momento y
# devolverle el control a Claude, que todavia tiene el contexto completo. Con
# exit code 2, Claude Code frena la compactacion y le muestra este mensaje a
# Claude; recien despues de que el skill corra, la compactacion sigue.
#
# Recibe por stdin un JSON con session_id, transcript_path, cwd, trigger
# ("auto" o "manual"), entre otros.
#
# Instalacion: ver README.md del plugin (bloque `hooks` en settings.json).

set -uo pipefail

INPUT="$(cat)"

# Sin jq disponible en todas las maquinas, se extrae con sed. El session_id es
# lo unico que hace falta: sin el, la captura no sabe a que conversacion
# pertenece el fragmento.
SESSION_ID="$(printf '%s' "${INPUT}" | sed -nE 's/.*"session_id"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p')"
TRIGGER="$(printf '%s' "${INPUT}" | sed -nE 's/.*"trigger"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p')"

if [[ -z "${SESSION_ID}" ]]; then
  # Sin session_id no se puede archivar el fragmento. Se deja compactar en vez
  # de bloquear la conversacion: perder una captura es molesto, dejar la sesion
  # trabada es peor.
  echo "intelica-arca: no se pudo leer el session_id del hook; se omite la captura." >&2
  exit 0
fi

# Marca de una captura por compactacion. Si el skill ya corrio para esta
# compactacion, no se vuelve a frenar -- si no, el hook y el skill se
# bloquearian mutuamente en loop.
STAGING_ROOT="${INTELICA_ARCA_STAGING:-${HOME}/.intelica-arca/sessions}"
GUARD="${STAGING_ROOT}/$(printf '%s' "${SESSION_ID}" | tr -c 'A-Za-z0-9._-' '_')/.capturing"

if [[ -f "${GUARD}" ]]; then
  rm -f "${GUARD}"
  exit 0
fi

mkdir -p "$(dirname "${GUARD}")"
touch "${GUARD}"

cat >&2 <<EOF
Antes de compactar: invoca el skill intelica-arca-capture para guardar el
conocimiento de esta conversacion en el staging local, con
session_id = ${SESSION_ID} (compactacion ${TRIGGER:-auto}).

La compactacion va a resumir la conversacion para poder seguir trabajando, y
en el proceso pierde los identificadores exactos y el detalle de las
decisiones -- justo lo que vale documentar. Capturalo ahora, mientras todavia
esta en contexto.

Cuando termines, reintenta la compactacion.
EOF

exit 2
