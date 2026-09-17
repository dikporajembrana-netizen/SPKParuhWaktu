import os
import re
import json
import pandas as pd
import fitz  # PyMuPDF

EXCEL_PATH = "daftar_nama.xlsx"  # Nama file Excel kamu
KOLOM_NAMA = "Nama"              # Nama header kolom di Excel
PDF_PATH = "dokumen.pdf"         # File PDF 3.206 halaman
OUTPUT_DIR = "hasil_split"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Baca daftar nama dari Excel
print("Membaca file Excel...")
df = pd.read_excel(EXCEL_PATH)

if KOLOM_NAMA not in df.columns:
    raise ValueError(f"Kolom '{KOLOM_NAMA}' tidak ditemukan di file Excel. Kolom yang ada: {list(df.columns)}")

# Ambil nama unik, buang nilai kosong (NaN)
daftar_nama = df[KOLOM_NAMA].dropna().astype(str).str.strip().unique().tolist()
print(f"Total nama yang ditemukan di Excel: {len(daftar_nama)} nama.")

# 2. Buka PDF & baca seluruh teks sekali jalan ke memori
print("Membaca seluruh isi teks PDF...")
doc = fitz.open(PDF_PATH)
total_pages = len(doc)

pages_text = []
for page_num in range(total_pages):
    page = doc[page_num]
    # Normalisasi spasi dan huruf kecil agar pencocokan nama akurat
    clean_text = " ".join(page.get_text().split()).lower()
    pages_text.append(clean_text)

# 3. Proses pencocokan rentang halaman dan potong PDF
print("\nMemulai proses pemotongan PDF...")
hasil_metadata = []
gagal_ditemukan = []

for idx, nama in enumerate(daftar_nama, 1):
    clean_target = nama.lower()
    halaman_cocok = []

    # Cari di halaman mana saja nama tersebut muncul
    for page_idx, text in enumerate(pages_text):
        if clean_target in text:
            halaman_cocok.append(page_idx + 1)

    if not halaman_cocok:
        print(f"[{idx}/{len(daftar_nama)}] Lewati: '{nama}' tidak ada di PDF.")
        gagal_ditemukan.append(nama)
        continue

    # Tentukan rentang halaman
    start_page = min(halaman_cocok)
    end_page = max(halaman_cocok)

    # Potong PDF menggunakan PyMuPDF
    sub_doc = fitz.open()
    # insert_pdf menggunakan zero-based index: from_page s/d to_page
    sub_doc.insert_pdf(doc, from_page=start_page - 1, to_page=end_page - 1)

    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', nama)
    file_name = f"{safe_name}_Hal_{start_page}-{end_page}.pdf"
    file_path = os.path.join(OUTPUT_DIR, file_name)

    # Simpan file PDF potongan
    sub_doc.save(file_path, garbage=3, deflate=True)
    sub_doc.close()

    print(f"[{idx}/{len(daftar_nama)}] Berhasil: {nama} -> Hal {start_page} s/d {end_page}")

    hasil_metadata.append({
        "nama": nama,
        "start_page": start_page,
        "end_page": end_page,
        "total_halaman": (end_page - start_page) + 1,
        "file_name": file_name,
        "drive_url": ""  # Siap diisi link Google Drive jika nanti diunggah
    })

doc.close()

# 4. Simpan hasil pemetaan ke JSON
with open("data_drive.json", "w", encoding="utf-8") as f:
    json.dump(hasil_metadata, f, ensure_ascii=False, indent=2)

print("\n=== RINGKASAN PROSES ===")
print(f"Total nama diproses : {len(daftar_nama)}")
print(f"Berhasil dipotong   : {len(hasil_metadata)} file PDF")
print(f"Tidak ditemukan     : {len(gagal_ditemukan)} nama")
print(f"Folder hasil        : {OUTPUT_DIR}/")
print(f"Metadata JSON       : data_drive.json")