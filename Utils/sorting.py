import os
import cv2
import re
import numpy as np

# Path ke folder gambar
folder_path = "comparison_output/test/"  # Ganti path kamu

# Resolusi layar target (Full HD)
MAX_WIDTH = 1920
MAX_HEIGHT = 1080

# Regex nama file
pattern = re.compile(r"(scab_test_(\d+))_jpg\.rf\..*\.jpg")

# Ambil dan filter file
files_with_numbers = []
for filename in os.listdir(folder_path):
    match = pattern.match(filename)
    if match:
        full_tag = match.group(1)  # e.g. "healthy_test_142"
        num = int(match.group(2))
        if num >= 0:
            files_with_numbers.append((filename, num, full_tag))

# Urutkan secara leksikografis berdasarkan filename
files_with_numbers.sort(key=lambda x: x[0])

print(f"Menampilkan {len(files_with_numbers)} gambar... (Tekan [Delete] untuk keluar)")

for filename, _, display_name in files_with_numbers:
    img_path = os.path.join(folder_path, filename)
    img = cv2.imread(img_path)

    if img is None:
        print(f"Gagal membuka: {filename}")
        continue

    # Resize proporsional
    h, w = img.shape[:2]
    scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Buat canvas hitam
    canvas = np.zeros((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8)

    # Hitung posisi tengah
    start_y = (MAX_HEIGHT - new_h) // 2
    start_x = (MAX_WIDTH - new_w) // 2

    # Tempel gambar
    canvas[start_y:start_y + new_h, start_x:start_x + new_w] = img_resized

    # Tambahkan nama file (tanpa .rf...) di kiri atas
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = display_name
    font_scale = 2
    thickness = 3
    text_color = (255, 255, 255)
    bg_color = (0, 0, 0)

    # Hitung ukuran teks
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x, text_y = 50, 80

    # Gambar background kotak hitam (biar teks jelas)
    cv2.rectangle(canvas,
                  (text_x - 10, text_y - text_height - 10),
                  (text_x + text_width + 10, text_y + 10),
                  bg_color, -1)

    # Gambar teks
    cv2.putText(canvas, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

    # Tampilkan full screen
    window_name = "Gambar"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, canvas)
    cv2.moveWindow(window_name, 1920, 0)  # Pindahkan ke monitor ke-2 (kanan)


    print(f"Menampilkan: {filename} — tekan tombol untuk lanjut, [Delete] untuk keluar.")
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Tombol Delete
    if key == 8:
        print("Dihentikan oleh pengguna (tombol Delete).")
        break
