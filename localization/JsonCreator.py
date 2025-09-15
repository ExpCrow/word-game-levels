import openpyxl
import json
import os
from datetime import datetime

# XLSX dosyan
xlsx_file = r'Localization.xlsx'

# Manifest dosyası
manifest_file = 'manifest.json'

# Update log dosyası
log_file = 'update_log.txt'

# Base URL (GitHub raw link)
base_url = "https://raw.githubusercontent.com/ExpCrow/word-game-levels/main/localization"

# XLSX yükle
wb = openpyxl.load_workbook(xlsx_file)
sheet = wb.active

# Header satırını oku (1. satır)
headers = [cell.value for cell in sheet[1]]

# İlk kolon Key, diğerleri diller
languages = {header.lower(): header_index for header_index, header in enumerate(headers) if header_index != 0}

# Her dil için entries listesi oluştur
data_per_language = {lang: [] for lang in languages}

# 2. satırdan itibaren oku
for row in sheet.iter_rows(min_row=2, values_only=True):
    key = row[0]
    for folder, idx in languages.items():
        value = row[idx]
        data_per_language[folder].append({"key": key, "value": value})

# Manifesti yükle veya oluştur
if os.path.exists(manifest_file):
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
else:
    manifest = {"languages": []}

# Değişiklik raporu için listeler
updated_languages = []
unchanged_languages = []
new_languages = []

# Her dil için JSON dosyalarını kaydet ve manifesti güncelle
for folder, entries in data_per_language.items():
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "ui_texts.json")

    new_json = {"entries": entries}
    old_json = None

    # Önceki dosya varsa oku
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                old_json = json.load(f)
            except:
                old_json = None

    # Yeni JSON'u yaz
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_json, f, ensure_ascii=False, indent=2)

    # Manifest güncellemesi
    existing = next((item for item in manifest["languages"] if item["code"] == folder), None)

    if existing:
        if old_json != new_json:
            existing["version"] += 1
            updated_languages.append((folder, existing["version"]))
        else:
            unchanged_languages.append((folder, existing["version"]))
    else:
        existing = {
            "code": folder,
            "name": folder.capitalize(),
            "version": 1,
            "json_url": f"{base_url}/{folder}/ui_texts.json",
            "flag_url": f"{base_url}/{folder}/flag.png"
        }
        manifest["languages"].append(existing)
        new_languages.append((folder, existing["version"]))

# Manifesti kaydet
with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("✅ Tüm JSON dosyaları oluşturuldu ve manifest güncellendi!\n")

# --- LOG YAZDIRMA ---
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_lines = [f"\n[{timestamp}] Güncelleme Raporu"]

if updated_languages:
    line = "🔼 Versiyonu artan diller: " + ", ".join([f"{code} (v{ver})" for code, ver in updated_languages])
    print(line)
    log_lines.append(line)
if unchanged_languages:
    line = "⏸ Değişmeyen diller: " + ", ".join([f"{code} (v{ver})" for code, ver in unchanged_languages])
    print(line)
    log_lines.append(line)
if new_languages:
    line = "🆕 Yeni eklenen diller: " + ", ".join([f"{code} (v{ver})" for code, ver in new_languages])
    print(line)
    log_lines.append(line)

# Log dosyasına ekle
with open(log_file, 'a', encoding='utf-8') as f:
    f.write("\n".join(log_lines) + "\n")

print(f"\n📄 Güncelleme detayları '{log_file}' dosyasına eklendi.")
