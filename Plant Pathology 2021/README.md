# Petunjuk Singkat 🪴

Panduan singkat untuk menyiapkan dataset lokal dan menjalankan skrip pada repo ini setelah Anda clone/pull dari GitHub.

## Ringkasan singkat ✅
- Repo ini tidak menyertakan file dataset besar. Setelah clone, Anda perlu meletakkan folder dataset yang berisi `original_dataset` di lokasi yang sama dengan repo.
- Setelah dataset tersedia, jalankan dua skrip di folder `utils/`:
  1. `split_by_class.py` — memisahkan gambar berdasarkan class ke `dataset/original_dataset_split_by_class/{class}`
  2. `rename_split_images.py` — (opsional) merename file agar mudah di-import ke Roboflow dan membuat `mapping.csv`.

## Langkah-langkah (Urut) 🧭

1) Clone repo dari GitHub

```bash
git clone <repo-url>
cd <repo-folder>
```

2) Siapkan dataset secara manual 🔽

- Pastikan Anda menempatkan dataset asli di `dataset/original_dataset/`.
- Struktur minimal yang dibutuhkan:
  - `dataset/original_dataset/train.csv` (header: `image,labels`)
  - `dataset/original_dataset/train_images/` (semua file gambar)

> Catatan: jangan commit folder dataset besar ke Git — gunakan penyimpanan eksternal atau Git LFS jika perlu.

3) (Opsional) Sesuaikan konfigurasi split

- File konfigurasi default: `utils/split_config.json`.
- Jika lokasi dataset Anda berbeda, ubah field `csv`, `images`, atau `out` di file tersebut.

4) Jalankan pemisahan per-class 🗂️

```bash
# dry-run (lihat ringkasan tanpa menyalin jika ingin tes):
python3 utils/split_by_class.py --csv dataset/original_dataset/train.csv --images dataset/original_dataset/train_images --out dataset/original_dataset_split_by_class

# atau cukup (menggunakan utils/split_config.json):
python3 utils/split_by_class.py

# untuk mengeksekusi penyalinan sebenarnya (tidak ada flag khusus; script menyalin langsung)
# script akan membuat folder dataset/original_dataset_split_by_class/{class}
```

5) (Opsional) Ubah nama file agar kompatibel dengan Roboflow 🔁

- Script: `utils/rename_split_images.py`
- Dry-run (lihat perubahan yang diusulkan):

```bash
python3 utils/rename_split_images.py
```

- Terapkan rename dan buat mapping CSV:

```bash
python3 utils/rename_split_images.py --apply
```

- Mapping CSV akan disimpan ke: `dataset/original_dataset/mapping.csv` dengan format:
  `original_image_name,new_name`

6) Verifikasi dan lanjutkan ke pipeline/Roboflow ✅

- Pastikan folder `dataset/original_dataset_split_by_class/{class}` ada dan berisi gambar bernama baru jika Anda menjalankan rename.
- Import ke Roboflow atau proses lain sesuai kebutuhan.

## Tips tambahan 💡
- Jika dataset terlalu besar untuk GitHub, gunakan layanan penyimpanan (Google Drive, AWS S3, dsb.) dan unduh dataset ketika memerlukan.
- Jika Anda perlu menyimpan dataset di repo, pertimbangkan Git LFS dan periksa `.gitattributes`.
- Jika ada masalah path karena spasi, gunakan kutip saat menjalankan perintah shell.

---

Jika mau, saya bisa menambahkan skrip kecil `make_dataset.sh` untuk mengotomasi langkah download (jika Anda punya URL) atau menambahkan opsi `--symlink` pada skrip rename untuk menghemat ruang. Mau saya tambahkan?

## Membuat subset terurut untuk train/valid/test 📦

- Script baru: `utils/split_by_subset.py`
- Konfigurasi default ada di `utils/split_config.json` (field `subset`).
- Script akan mengambil 250 gambar pertama per class (urut), lalu membagi
  secara berurutan ke `train` (70%), `valid` (10%), `test` (20%).
- Hasilnya disimpan di `dataset/original_dataset_split_by_subset/{subset}/{class}` dan
  mapping ditulis ke `dataset/original_dataset/mapping_subset.csv`.

Contoh jalankan (tanpa argumen, config di `utils/split_config.json`):

```bash
python3 utils/split_by_subset.py
```

Jika ingin melakukan dry-run, jalankan script setelah menambahkan log/flag dry-run atau modifikasi file untuk memeriksa sebelum menyalin.
