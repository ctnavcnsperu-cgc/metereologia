import re
import os

file_path = r"d:\CELSO HOJAS DE RUTA\METEREOLOGIA\index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern for the structure we just created in the previous step
pattern = r"""<div
\s+class="fenomeno-card p-2 bg-slate-50 dark:bg-slate-800 rounded-sm shadow-none flex items-center justify-between gap-2">
\s+<div class="flex items-center gap-2 min-w-0 flex-grow">
\s+<span class="font-bold text-red-700 dark:text-red-400 uppercase text-sm leading-none shrink-0 font-technical">(.*?)</span>
\s+<span class="text-sm text-slate-900 dark:text-slate-100 font-bold truncate">(.*?)</span>
\s+</div>
\s+<span class="fen-weather-icon text-lg flex-shrink-0 opacity-80" data-fen="(.*?)"></span>
\s+</div>"""

def replacement(match):
    city = match.group(1).strip()
    phenomenon = match.group(2).strip()
    data_fen = match.group(3).strip()
    return f"""<div
                            class="fenomeno-card p-2.5 bg-white dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-700/50 flex items-center gap-3 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 transition-all duration-200">
                            <span class="fen-weather-icon text-xl flex-shrink-0 opacity-90 shadow-sm" data-fen="{data_fen}"></span>
                            <div class="flex items-center gap-3 min-w-0 flex-grow">
                                <span class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 font-bold px-2 py-1 rounded-md text-[10px] uppercase tracking-wider min-w-[100px] text-center border border-red-100/50 dark:border-red-800/30 font-technical shrink-0">
                                    {city}
                                </span>
                                <span class="text-[13px] text-slate-700 dark:text-slate-300 font-semibold truncate leading-none">
                                    {phenomenon}
                                </span>
                            </div>
                        </div>"""

# Apply replacement for cards
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Update the container and remove p-3 from index.html (match the template change)
new_content = new_content.replace(
    '<div class="p-3 overflow-y-auto flex-grow custom-scrollbar">',
    '<div class="p-0 overflow-y-auto flex-grow custom-scrollbar">'
)
new_content = new_content.replace(
    '<div class="space-y-2">',
    '<div class="divide-y divide-slate-100 dark:divide-slate-800">'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Applied premium design to index.html")
