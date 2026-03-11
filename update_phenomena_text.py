import re
import os

file_path = r"d:\CELSO HOJAS DE RUTA\METEREOLOGIA\index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern for the compact structure we just created
pattern = r"""<div
\s+class="fenomeno-card p-2 bg-slate-50 dark:bg-slate-800 rounded-sm shadow-none flex items-center justify-between gap-2">
\s+<div class="flex items-center gap-2 min-w-0 flex-grow">
\s+<span class="font-bold text-red-700 dark:text-red-400 uppercase text-\[11px\] leading-none shrink-0 font-technical">(.*?)</span>
\s+<span class="text-\[11px\] text-slate-600 dark:text-slate-400 italic truncate">(.*?)</span>
\s+</div>
\s+<span class="fen-weather-icon text-lg flex-shrink-0 opacity-80" data-fen="(.*?)"></span>
\s+</div>"""

def replacement(match):
    city = match.group(1).strip()
    phenomenon = match.group(2).strip()
    data_fen = match.group(3).strip()
    return f"""<div
                            class="fenomeno-card p-2 bg-slate-50 dark:bg-slate-800 rounded-sm shadow-none flex items-center justify-between gap-2">
                            <div class="flex items-center gap-2 min-w-0 flex-grow">
                                <span class="font-bold text-red-700 dark:text-red-400 uppercase text-[11px] leading-none shrink-0 font-technical">{city}</span>
                                <span class="text-xs text-slate-900 dark:text-slate-100 font-bold truncate">{phenomenon}</span>
                            </div>
                            <span class="fen-weather-icon text-lg flex-shrink-0 opacity-80" data-fen="{data_fen}"></span>
                        </div>"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Updated index.html: Increased font size, bold, no italics, removed border.")
