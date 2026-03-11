import os
import re

files_to_update = [
    "index.html",
    "tiempo_hoy.html",
    "tiempo_aeropuertos.html",
    "panel_tecnico.html",
    "panel_alerta.html",
    "templates/tiempo_hoy_template.html",
    "templates/tiempo_hoy_ciudades_template.html",
    "templates/tiempo_aeropuertos_template.html",
    "templates/panel_tecnico_template.html",
    "templates/panel_alerta_template.html"
]

base_dir = r"d:\CELSO HOJAS DE RUTA\METEREOLOGIA"

for file_rel_path in files_to_update:
    full_path = os.path.join(base_dir, file_rel_path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        continue
    
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # regex to find <nav> block and remove <svg> tags inside it
    # We look for <nav ...> ... </nav>
    nav_match = re.search(r'(<nav class="flex flex-wrap gap-2">)(.*?)(</nav>)', content, re.DOTALL)
    if nav_match:
        nav_start = nav_match.group(1)
        nav_content = nav_match.group(2)
        nav_end = nav_match.group(3)
        
        # Remove <svg ...> ... </svg> blocks
        cleaned_nav_content = re.sub(r'<svg.*?>.*?</svg>', '', nav_content, flags=re.DOTALL)
        
        new_content = content[:nav_match.start()] + nav_start + cleaned_nav_content + nav_end + content[nav_match.end():]
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {file_rel_path}")
    else:
        print(f"Nav block not found in: {file_rel_path}")
