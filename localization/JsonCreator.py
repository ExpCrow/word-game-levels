import openpyxl
import json
import os

# XLSX dosyan
xlsx_file = r'Localization.xlsx'

# Manifest dosyası
manifest_file = 'manifest.json'

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

# JSON dosyalarını kaydet
for folder, entries in data_per_language.items():
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "ui_texts.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=2)

# Manifesti yükle veya oluştur
if os.path.exists(manifest_file):
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
else:
    manifest = {"languages": []}

# Her dil için manifesti güncelle
for folder in languages.keys():
    # Daha önce manifestte var mı kontrol et
    existing = next((item for item in manifest["languages"] if item["code"] == folder), None)
    if existing:
        existing["version"] += 1
    else:
        existing = {
            "code": folder,
            "name": folder.capitalize(),
            "version": 1,
            "json_url": f"{base_url}/{folder}/ui_texts.json",
            "flag_url": f"{base_url}/{folder}/flag.png"
        }
        manifest["languages"].append(existing)

# Manifesti kaydet
with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Tüm JSON dosyaları oluşturuldu ve manifest güncellendi!")
