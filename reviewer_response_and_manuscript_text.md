# Draft Jawaban Reviewer dan Teks Revisi Manuscript

## 1. Representativeness of 750 Manually Annotated Images

### 1. Komentar Reviewer

The severity ground truth is computed only from 750 manually annotated images, a relatively small subset compared to the full dataset (11,053 images). The representativeness of this sample is not statistically justified.

### 2. Tindakan yang Diambil untuk Menjawab Komentar Reviewer

Kami menambahkan analisis statistik untuk menjelaskan representativeness dari 750 gambar beranotasi manual. Analisis dilakukan dengan:

- Membandingkan distribusi kelas pada full filtered dataset dan subset anotasi.
- Menghitung coverage subset anotasi terhadap jumlah data penuh pada setiap kelas.
- Menghitung conservative finite-population margin of error.
- Membandingkan karakteristik metadata gambar, yaitu width, height, aspect ratio, dan file size, antara full dataset dan subset anotasi menggunakan Kolmogorov-Smirnov test.

### 3. Apa Hasilnya

Subset anotasi terdiri dari 250 gambar per kelas, sehingga desainnya adalah balanced stratified sample, bukan prevalence-proportional sample. Coverage subset anotasi adalah:

- Healthy: 250 dari 4,624 gambar, atau 5.41%.
- Frog-eye leaf spot: 250 dari 4,352 gambar, atau 5.74%.
- Rust: 250 dari 2,077 gambar, atau 12.04%.

Conservative finite-population 95% margin of error berada pada kisaran sekitar 5.81-6.03 percentage points untuk tiap kelas.

Hasil Kolmogorov-Smirnov test per kelas menunjukkan bahwa tidak terdapat perbedaan signifikan pada width, height, dan aspect ratio antara subset anotasi dan full filtered dataset. Ini mendukung bahwa subset anotasi masih representatif dari sisi karakteristik akuisisi gambar. Namun, distribusi kelas memang berbeda secara signifikan dari full dataset karena subset sengaja dibuat seimbang, bukan mengikuti prevalensi kelas asli.

### 4. Teks yang Dapat Dimasukkan ke Dalam Jurnal

The 750 manually annotated images were selected using a balanced stratified design, with 250 images from each retained class. This design was used to provide equal annotation support across healthy, rust, and frog-eye leaf spot classes, rather than to preserve the natural class prevalence of the full filtered dataset. The subset represented 5.41% of healthy images, 5.74% of frog-eye leaf spot images, and 12.04% of rust images. Using a conservative finite-population calculation, the 95% margin of error was approximately 5.81-6.03 percentage points across classes. In addition, per-class Kolmogorov-Smirnov tests indicated no significant differences in image width, height, or aspect ratio between the annotated subset and the full filtered dataset, suggesting that the annotated subset preserved the main image-acquisition characteristics of the source data.

### 5. Apakah Perlu Menambah Data?

Tidak wajib menambah data untuk menjawab reviewer ini, karena masalah utamanya adalah tidak adanya justifikasi statistik, bukan reviewer secara eksplisit meminta anotasi tambahan. Data 750 dapat dipertahankan jika manuscript menjelaskan bahwa subset tersebut adalah balanced stratified sample, bukan sampel acak yang mengikuti prevalensi kelas asli.

Namun, jika ingin memperkuat manuscript lebih jauh, tambahan data anotasi bisa diprioritaskan pada kelas healthy dan frog-eye leaf spot karena coverage keduanya lebih kecil daripada rust. Tambahan ini bersifat optional, bukan syarat minimal untuk menjawab komentar reviewer.

## 2. Largest-Leaf ROI Assumption

### 1. Komentar Reviewer

The two-stage pipeline selects only the largest detected leaf as the ROI, which the authors acknowledge may not correspond to the most diseased leaf. However, no quantitative analysis of how often this assumption holds in the test set is provided, leaving an important gap.

### 2. Tindakan yang Diambil untuk Menjawab Komentar Reviewer

Kami menambahkan analisis kuantitatif pada test set menggunakan ground-truth segmentation labels. Untuk setiap gambar, dihitung:

- Daun dengan area terbesar.
- Daun dengan lesion area terbesar.
- Daun dengan severity tertinggi.
- Selisih severity jika yang dipilih adalah daun terbesar, bukan daun paling parah.

Selain itu, dilakukan audit tambahan menggunakan model deteksi untuk melihat apakah largest detected bounding box sesuai dengan ground-truth largest leaf dan most severe leaf.

### 3. Apa Hasilnya

Pada test set:

- Largest annotated leaf adalah most severe leaf pada 97.3% dari seluruh test images.
- Largest annotated leaf adalah leaf dengan lesion area terbesar pada 98.0% dari seluruh test images.
- Pada multi-leaf test images saja, largest leaf adalah most severe leaf pada 91.1% kasus.
- Pada multi-leaf test images saja, largest leaf adalah leaf dengan lesion area terbesar pada 93.3% kasus.
- Mean severity gap karena memilih largest leaf adalah 0.052 percentage points untuk seluruh test images.
- Mean severity gap pada multi-leaf images adalah 0.172 percentage points.

Audit berbasis model deteksi menunjukkan:

- Detection success rate: 100%.
- Largest detected box cocok dengan ground-truth largest leaf pada IoU > 0.5 di 98.0% test images.
- Largest detected box cocok dengan ground-truth most severe leaf pada IoU > 0.5 di 95.3% test images.

### 4. Teks yang Dapat Dimasukkan ke Dalam Jurnal

To quantify the largest-leaf ROI assumption, an additional audit was performed on the test set using ground-truth segmentation annotations. The largest annotated leaf corresponded to the most severe leaf in 97.3% of all test images and to the leaf with the largest lesion area in 98.0% of all test images. When only multi-leaf images were considered, the largest leaf remained the most severe leaf in 91.1% of cases and had the largest lesion area in 93.3% of cases. The mean severity gap introduced by selecting the largest leaf was 0.052 percentage points across all test images and 0.172 percentage points among multi-leaf images. A model-based audit showed that the largest detected ROI matched the ground-truth largest leaf at IoU > 0.5 in 98.0% of test images and matched the most severe leaf in 95.3% of test images. These results support the largest-leaf strategy as a practical approximation, although failure cases remain and motivate future multi-leaf or symptom-aware ROI selection.

### 5. Apakah Perlu Menambah Data?

Tidak perlu menambah data untuk menjawab komentar ini. Reviewer meminta quantitative analysis, dan analisis tersebut sudah dapat dilakukan dari label ground truth yang ada.

Yang perlu ditambahkan adalah tabel atau paragraf hasil audit di manuscript. Jika ruang jurnal terbatas, cukup masukkan ringkasan angka utama pada bagian Results and Discussion atau Limitations.

## 3. Fig. 18 and Fig. 19 Labeling Inconsistency

### 1. Komentar Reviewer

Fig. 18 and Fig. 19 are described as showing performance on the "training set," which appears to be a labeling inconsistency since model selection should be based on validation or test performance. This should be clarified.

### 2. Tindakan yang Diambil untuk Menjawab Komentar Reviewer

Kami melakukan audit terhadap sumber CSV yang digunakan untuk grafik YOLOv12 size comparison. Hasil audit menunjukkan bahwa terdapat dua jenis informasi:

- Training CSV berisi training dynamics.
- Validation/test CSV berisi class metrics yang dipakai untuk membandingkan performa final model.

Caption dan narasi perlu diperjelas agar model selection didasarkan pada validation/test performance, sedangkan training curve hanya digunakan untuk menjelaskan convergence behavior.

### 3. Apa Hasilnya

Pada validation/test metrics YOLOv12 size comparison:

- Nano memperoleh mAP50 tertinggi, yaitu 0.972.
- Small memperoleh mAP50-95 tertinggi, yaitu 0.943.
- Medium memperoleh mAP50 0.953 dan mAP50-95 0.918.
- Large memperoleh mAP50 0.932 dan mAP50-95 0.899.

Karena mAP50-95 lebih penting untuk kualitas lokalisasi pada berbagai IoU threshold, YOLOv12-small tetap dapat dipertahankan sebagai pilihan model deteksi.

### 4. Teks yang Dapat Dimasukkan ke Dalam Jurnal

Model-size selection was based on held-out test-set performance, not on training-set performance. In the YOLOv12 size comparison, the nano model achieved the highest mAP50 of 0.972, whereas the small model achieved the highest mAP50-95 of 0.943. Because mAP50-95 better reflects localization quality across stricter IoU thresholds, YOLOv12-small was selected for subsequent detection-guided severity estimation. Training curves are reported only to describe convergence behavior and were not used as the sole basis for model selection.

Suggested revised captions:

- Fig. 18. Performance comparison of different YOLOv12 model sizes on the held-out test set.
- Fig. 19. Training dynamics of different YOLOv12 model sizes during model development.

### 5. Apakah Perlu Menambah Data?

Tidak perlu menambah data. Ini adalah masalah labeling dan wording, bukan kekurangan eksperimen. Yang perlu dilakukan adalah memperbaiki caption Fig. 18 dan Fig. 19, serta memastikan teks pembahasan tidak menyatakan bahwa model dipilih berdasarkan training set.

## 4. YOLO26 Mention in Conclusion

### 1. Komentar Reviewer

The paper references "YOLO26" in the conclusion as a future direction, but this is mentioned without any citation or explanation, which may confuse readers at the time of publication.

### 2. Tindakan yang Diambil untuk Menjawab Komentar Reviewer

Kami mengaudit artifact YOLO26 di repository. Memang terdapat file eksperimen lokal seperti `yolo26n.pt`, `yolo26s.pt`, dan `yolo26m.pt`, tetapi manuscript tidak memberikan citation atau penjelasan resmi mengenai YOLO26. Oleh karena itu, rujukan spesifik ke YOLO26 sebaiknya dihapus dari conclusion.

### 3. Apa Hasilnya

Kesimpulan menjadi lebih aman dan tidak membingungkan pembaca. Future work tetap dapat menyebutkan evaluasi arsitektur object detection terbaru, tetapi tanpa menyebut nama rilis yang belum dijelaskan atau belum memiliki citation yang kuat.

### 4. Teks yang Dapat Dimasukkan ke Dalam Jurnal

Future work should evaluate newer well-documented object detection architectures as they become available, as well as transformer-based detectors such as DETR variants, to examine potential gains in localization robustness and generalization under complex orchard backgrounds.

### 5. Apakah Perlu Menambah Data?

Tidak perlu menambah data. Ini murni revisi teks. Saran paling aman adalah menghapus penyebutan YOLO26 kecuali Anda memiliki citation resmi dan penjelasan singkat yang valid. Jika tidak, gunakan frasa umum seperti "newer well-documented object detection architectures".

## 5. Statistical Significance of MAE Improvement

### 1. Komentar Reviewer

Statistical significance of the MAE improvement (1.49% vs 0.66%) is not assessed. A simple significance test or confidence interval would strengthen the claim.

### 2. Tindakan yang Diambil untuk Menjawab Komentar Reviewer

Kami menambahkan paired statistical analysis pada 149 test images yang memiliki hasil prediksi dari single-stage dan two-stage pipeline. Analisis dilakukan dengan:

- Menghitung absolute error per gambar untuk masing-masing pipeline.
- Menghitung paired MAE reduction.
- Menggunakan one-sided paired t-test untuk menguji apakah error single-stage lebih tinggi daripada two-stage.
- Menghitung 95% confidence interval berbasis paired t-test untuk mean MAE reduction.
- Menggunakan bootstrap 95% confidence interval.
- Menggunakan one-sided Wilcoxon signed-rank test.
- Menggunakan sign test sebagai uji non-parametrik tambahan.

### 3. Apa Hasilnya

Hasil analisis menunjukkan:

- Single-stage MAE: 1.488%.
- Two-stage MAE: 0.660%.
- Mean paired MAE reduction: 0.828 percentage points.
- Paired t-test: t(148) = 5.189, one-sided p = 3.42 x 10^-7.
- Paired t-test 95% confidence interval untuk mean reduction: 0.513 sampai 1.143 percentage points.
- Cohen's dz paired effect size: 0.425.
- Bootstrap 95% confidence interval: 0.549 sampai 1.157 percentage points.
- One-sided Wilcoxon signed-rank test: p = 1.23 x 10^-12.
- Dari 149 paired test images, 80 gambar membaik, 18 memburuk, dan 51 sama.
- One-sided sign test: p = 8.30 x 10^-11.

Dengan demikian, peningkatan two-stage pipeline signifikan secara statistik berdasarkan paired t-test, dan kesimpulan tersebut konsisten dengan uji non-parametrik pendukung.

### 4. Teks yang Dapat Dimasukkan ke Dalam Jurnal

A paired t-test was conducted on the per-image absolute severity errors to assess whether the MAE reduction from the single-stage to the two-stage pipeline was significant. Using 149 paired test images, the single-stage pipeline produced an MAE of 1.488%, whereas the two-stage pipeline reduced the MAE to 0.660%. The mean paired reduction was 0.828 percentage points, with a paired t-test 95% confidence interval of 0.513-1.143 percentage points. The improvement was statistically significant in a one-sided paired t-test (t(148) = 5.189, p = 3.42 x 10^-7), supporting the conclusion that detection-guided cropping significantly reduced severity estimation error. This conclusion was also consistent with the non-parametric Wilcoxon signed-rank test (p = 1.23 x 10^-12) and the bootstrap 95% confidence interval of 0.549-1.157 percentage points.

### 5. Apakah Perlu Menambah Data?

Tidak perlu menambah data. Reviewer meminta significance test atau confidence interval, dan ini sudah dapat dijawab menggunakan paired test images yang tersedia.

Yang perlu ditambahkan adalah satu paragraf pada bagian Results and Discussion, atau satu kalimat tambahan setelah pelaporan MAE. Jika jurnal mengizinkan, tambahkan juga confidence interval agar klaim improvement lebih kuat.
