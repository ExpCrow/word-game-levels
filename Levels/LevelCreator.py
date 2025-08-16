import os
import pandas as pd
import json
import math

PACKAGE_FILE = "Package.json"  # Python kodunun bulunduğu konumdaki Package.json

def parse_excel_to_levels(excel_path):
    df = pd.read_excel(excel_path)
    grouped = df.groupby("id")
    levels = []

    for level_id, group in grouped:
        letters = group.iloc[0]["letters"].split(',')
        answers = []
        extra = []

        for _, row in group.iterrows():
            entry = {"word": row["word"], "meaning": row["meaning"]}
            if row["type"] == "answer":
                answers.append(entry)
            elif row["type"] == "extra":
                extra.append(entry)

        levels.append({
            "id": int(level_id),
            "letters": [l.strip() for l in letters],
            "answers": answers,
            "extra": extra
        })

    return levels

def save_levels_in_parts(levels, lang_code, output_dir, part_size=10):
    total_parts = math.ceil(len(levels) / part_size)
    for i in range(total_parts):
        part_levels = levels[i * part_size : (i + 1) * part_size]
        filename = f"{lang_code}_part{i+1}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"levels": part_levels}, f, ensure_ascii=False, indent=2)
        print(f"✅ Kaydedildi: {filename}")

def update_package_version(lang_code):
    """Package.json dosyasını okuyup ilgili dilin versiyonunu 1 artırır."""
    if not os.path.exists(PACKAGE_FILE):
        print(f"⚠️ {PACKAGE_FILE} bulunamadı, oluşturuluyor...")
        package_data = {}
    else:
        with open(PACKAGE_FILE, "r", encoding="utf-8") as f:
            package_data = json.load(f)

    if lang_code not in package_data:
        package_data[lang_code] = {"version": 0}

    package_data[lang_code]["version"] += 1

    with open(PACKAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(package_data, f, ensure_ascii=False, indent=4)

    print(f"📦 Package.json güncellendi: {lang_code} → v{package_data[lang_code]['version']}")

def process_all_languages(base_dir):
    for lang_folder in os.listdir(base_dir):
        lang_path = os.path.join(base_dir, lang_folder)
        excel_path = os.path.join(lang_path, "Wordlist.xlsx")

        if os.path.isdir(lang_path) and os.path.exists(excel_path):
            print(f"🔍 İşleniyor: {lang_folder}")
            levels = parse_excel_to_levels(excel_path)
            save_levels_in_parts(levels, lang_folder, lang_path)
            update_package_version(lang_folder)  # ✅ Versiyon artırma
        else:
            print(f"⚠️ Atlandı: {lang_folder} (Wordlist.xlsx bulunamadı)")

# Kullanım
process_all_languages(".")  # Mevcut klasördeki alt klasörleri tarar
