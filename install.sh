#!/bin/zsh
# Instala Nube Delay en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
set -e
DST="$HOME/Library/Application Support/REAPER/Effects/Nube Delay"
cd "$(dirname "$0")"
mkdir -p "$DST"
ln -sf "$PWD/nube_delay.jsfx" "$DST/nube_delay.jsfx"
echo "Listo: en REAPER busca \"Nube Delay\" en el navegador de FX (JS: Nube Delay)."
