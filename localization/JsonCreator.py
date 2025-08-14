import openpyxl
import json
import os

# XLSX dosyan
xlsx_file = r'Localization.xlsx'

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

print("Tüm JSON dosyaları oluşturuldu!")
