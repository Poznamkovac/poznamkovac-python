#!/bin/bash
cd "$(dirname "$0")"

npx tailwindcss -i ../poznamkovac/sablony/staticke/_tailwind.css -o ../site/staticke/styly.css
npx cleancss ../site/staticke/styly.css -o ../site/staticke/styly.min.css
