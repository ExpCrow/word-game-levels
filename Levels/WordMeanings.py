import os
import pandas as pd
from openai import OpenAI

# OpenAI client
client = OpenAI(api_key="API_KEY")

# Tarama yapılacak ana klasör
root_dir = "."

# Wordlist.xlsx dosyalarını bul
wordlist_files = []
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith("Wordlist.xlsx"):
            wordlist_files.append(os.path.join(root, file))

print(f"{len(wordlist_files)} dosya bulundu!")

for filepath in wordlist_files:
    print(f"İşleniyor: {filepath}")

    # Dosya adından dil kodunu çıkar (ör: en_Wordlist.xlsx → en)
    filename = os.path.basename(filepath)
    lang_code = filename.split("_")[0]

    # Excel'i oku (formatı korumak için openpyxl)
    df = pd.read_excel(filepath, engine="openpyxl")

    # Eğer 'meaning' sütunu yoksa ekle
    if "meaning" not in df.columns:
        df["meaning"] = ""

    meanings = []

    for word in df["word"]:
        if pd.isna(word):
            meanings.append("")
            continue

        # Prompt dil koduna göre ayarlanıyor
        prompt = f"Lütfen '{word}' kelimesinin {lang_code} dilinde anlamını yaz."
        
        try:
            response = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "Sen bir sözlük asistanısın."},
                    {"role": "user", "content": prompt}
                ]
            )
            meaning = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Hata: {e}")
            meaning = ""

        meanings.append(meaning)

    # Meaning sütununu güncelle
    df["meaning"] = meanings

    # Üzerine yaz (formatı koruyarak)
    df.to_excel(filepath, index=False, engine="openpyxl")

print("✅ Tüm dosyalar işlendi!")
