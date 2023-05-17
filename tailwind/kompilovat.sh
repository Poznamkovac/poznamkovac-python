#!/bin/bash
cd "$(dirname "$0")"

npx tailwindcss -i ../poznamkovac/sablony/static/_tailwind.css -o ../poznamkovac/sablony/static/compiled.css
npx cleancss ../poznamkovac/sablony/static/compiled.css -o ../poznamkovac/sablony/static/compiled.min.css
