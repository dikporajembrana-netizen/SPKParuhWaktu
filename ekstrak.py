import json
import fitz  # PyMuPDF

pdf_path = "dokumen.pdf"  # Ganti sesuai nama file PDF kamu jika berbeda
print("Membuka file PDF...")
doc = fitz.open(pdf_path)
total_pages = len(doc)
print(f"Total halaman terdeteksi: {total_pages} halaman.")

extracted_data = []

print("Memulai ekstraksi teks...")
for page_num in range(total_pages):
    page = doc[page_num]
    text = page.get_text()

    # Bersihkan spasi kosong berlebih agar ukuran file JSON lebih hemat
    clean_text = " ".join(text.split())

    if clean_text:
        extracted_data.append({
            "id": page_num + 1,
            "page": page_num + 1,
            "text": clean_text
        })

    # Tampilkan progress setiap 200 halaman
    if (page_num + 1) % 200 == 0 or (page_num + 1) == total_pages:
        percent = ((page_num + 1) / total_pages) * 100
        print(f"Proses: {page_num + 1}/{total_pages} halaman ({percent:.1f}%)")

print("Menyimpan ke data.json...")
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(extracted_data, f, ensure_ascii=False)

print(" Selesai! File data.json berhasil dibuat di folder yang sama.")