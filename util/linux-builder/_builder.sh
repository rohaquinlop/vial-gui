#!/bin/bash

set -e

cd /vial-gui
uv sync --no-dev
uv run fbs freeze
uv run fbs installer
/pkg2appimage-*/pkg2appimage misc/Vial.yml
mv out/Vial-*.AppImage /output/Vial-x86_64.AppImage
