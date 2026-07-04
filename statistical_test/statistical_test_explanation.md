# Step-by-Step Statistical Test Explanation

Dokumen ini menjelaskan cara perhitungan statistik yang digunakan untuk membandingkan pipeline Single-Stage dan Two-Stage pada estimasi disease severity. Penjelasan ini disusun untuk bahan presentasi.

## 1. Data yang Dibandingkan

Karena Single-Stage dan Two-Stage diuji pada gambar test yang sama, maka datanya bersifat paired.

Untuk setiap gambar ke-i, tersedia:

```text
Ground truth severity      = S_i
Prediksi Single-Stage      = P_single,i
Prediksi Two-Stage         = P_two,i
```

Absolute error dihitung sebagai:

```text
E_single,i = |S_i - P_single,i|
E_two,i    = |S_i - P_two,i|
```

Contoh:

| Image | GT Severity | Single Pred | Two-Stage Pred | Single Error | Two Error | Reduction |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 2.00 | 3.20 | 2.40 | 1.20 | 0.40 | 0.80 |
| 2 | 1.00 | 2.50 | 1.30 | 1.50 | 0.30 | 1.20 |
| 3 | 0.50 | 0.20 | 0.60 | 0.30 | 0.10 | 0.20 |
| 4 | 3.00 | 2.20 | 2.60 | 0.80 | 0.40 | 0.40 |
| 5 | 1.50 | 1.80 | 2.10 | 0.30 | 0.60 | -0.30 |

Reduction dihitung sebagai:

```text
Delta_i = E_single,i - E_two,i
```

Interpretasinya:

```text
Delta_i > 0  berarti Two-Stage lebih baik
Delta_i < 0  berarti Two-Stage lebih buruk
Delta_i = 0  berarti keduanya sama
```

## 2. Menghitung MAE

Mean Absolute Error atau MAE adalah rata-rata absolute error:

```text
MAE = (1 / N) * sum(|S_i - P_i|)
```

Pada hasil thesis:

```text
N = 149 paired test images

Single-Stage MAE = 1.488%
Two-Stage MAE    = 0.660%
```

Penurunan rata-rata MAE:

```text
Mean reduction = 1.488 - 0.660
               = 0.828 percentage points
```

Artinya secara deskriptif, Two-Stage menurunkan error severity sekitar 0.828 percentage points. Namun, angka ini belum cukup untuk menyimpulkan bahwa improvement signifikan. Karena itu dilakukan uji statistik.

## 3. Mengecek Normalitas dengan Shapiro-Wilk

Sebelum memilih uji statistik utama, distribusi paired reduction `Delta_i` dicek dengan Shapiro-Wilk normality test.

Hipotesis Shapiro-Wilk:

```text
H0: Delta_i berdistribusi normal
H1: Delta_i tidak berdistribusi normal
```

Aturan keputusan:

```text
Jika p >= 0.05:
    distribusi dianggap cukup normal
    gunakan paired t-test sebagai uji utama

Jika p < 0.05:
    distribusi tidak normal
    gunakan Wilcoxon signed-rank test sebagai uji utama
```

Hasil thesis:

```text
Shapiro-Wilk statistic = 0.523
p-value = 5.077 x 10^-20
```

Karena:

```text
5.077 x 10^-20 < 0.05
```

maka H0 ditolak. Artinya distribusi reduction tidak normal. Oleh karena itu, uji utama yang digunakan adalah Wilcoxon signed-rank test.

## 4. Wilcoxon Signed-Rank Test

Wilcoxon digunakan karena data bersifat paired tetapi distribusi reduction tidak normal.

Hipotesis Wilcoxon:

```text
H0: Two-Stage tidak menurunkan error dibanding Single-Stage
H1: Two-Stage menurunkan error dibanding Single-Stage
```

Karena tujuan penelitian adalah membuktikan Two-Stage lebih baik, maka digunakan one-sided test.

Langkah Wilcoxon:

1. Hitung `Delta_i = E_single,i - E_two,i`.
2. Buang data dengan `Delta_i = 0`.
3. Ambil nilai absolut `|Delta_i|`.
4. Ranking nilai absolut dari kecil ke besar.
5. Kembalikan tanda positif atau negatif dari `Delta_i`.
6. Jumlahkan rank bertanda.
7. Hitung p-value.

Contoh kecil:

| Image | Delta | Absolute Delta | Rank | Sign |
|---|---:|---:|---:|---|
| 1 | 0.80 | 0.80 | 4 | + |
| 2 | 1.20 | 1.20 | 5 | + |
| 3 | 0.20 | 0.20 | 1 | + |
| 4 | 0.40 | 0.40 | 3 | + |
| 5 | -0.30 | 0.30 | 2 | - |

Positive rank sum:

```text
W+ = 1 + 3 + 4 + 5
   = 13
```

Negative rank sum:

```text
W- = 2
```

Karena positive rank jauh lebih besar, hasil contoh ini menunjukkan arah improvement lebih dominan ke Two-Stage.

Hasil thesis:

```text
Wilcoxon statistic = 4402.5
p-value one-sided = 1.23 x 10^-12
```

Karena:

```text
1.23 x 10^-12 < 0.05
```

maka hasilnya signifikan. Kesimpulannya:

```text
Two-Stage secara statistik signifikan menurunkan MAE dibanding Single-Stage.
```

## 5. Cara Menghitung P-Value

P-value adalah probabilitas mendapatkan hasil setidaknya se-ekstrem hasil observasi, dengan asumsi H0 benar.

Dalam konteks penelitian ini:

```text
H0: Two-Stage tidak lebih baik dari Single-Stage
```

Maka p-value menjawab pertanyaan:

```text
Jika sebenarnya Two-Stage tidak lebih baik,
seberapa mungkin kita tetap melihat improvement sebesar ini atau lebih ekstrem?
```

Jika p-value sangat kecil, artinya hasil improvement yang diamati sangat tidak mungkin terjadi hanya karena kebetulan. Karena itu H0 ditolak.

### 5.1 Contoh P-Value pada Sign Test

Sign test adalah cara paling mudah untuk memahami p-value.

Dari hasil thesis:

```text
Improved images = 80
Worse images    = 18
Equal images    = 51
```

Untuk sign test, gambar yang equal diabaikan. Jadi:

```text
Non-zero images = 80 + 18
                = 98
```

Di bawah H0, peluang satu gambar membaik sama dengan peluang memburuk:

```text
P(improved) = 0.5
P(worse)    = 0.5
```

Kita mengamati 80 improvement dari 98 kasus non-zero. P-value one-sided adalah probabilitas mendapatkan 80 atau lebih improvement jika peluang improvement sebenarnya hanya 0.5.

Secara matematis:

```text
p-value = P(X >= 80), X ~ Binomial(n = 98, p = 0.5)
```

Rumusnya:

```text
p-value = sum from k=80 to 98 of C(98, k) * (0.5)^k * (0.5)^(98-k)
```

Karena `(0.5)^k * (0.5)^(98-k) = (0.5)^98`, maka:

```text
p-value = sum from k=80 to 98 of C(98, k) * (0.5)^98
```

Contoh satu komponen untuk k = 80:

```text
P(X = 80) = C(98, 80) * (0.5)^98
```

Nilai kombinasi:

```text
C(98, 80) = 98! / (80! * 18!)
```

Lalu dijumlahkan sampai k = 98:

```text
P(X >= 80) = P(X=80) + P(X=81) + ... + P(X=98)
```

Hasil dari notebook:

```text
p-value = 8.303 x 10^-11
```

Interpretasi:

```text
Jika Two-Stage sebenarnya tidak lebih baik,
peluang mendapatkan 80 atau lebih improvement dari 98 kasus
hanya sekitar 0.00000000008303.
```

Karena sangat kecil dan lebih kecil dari 0.05, maka hasilnya signifikan.

### 5.2 Contoh P-Value pada Paired T-Test

Paired t-test menghitung statistik:

```text
t = mean reduction / standard error
```

Dari hasil thesis:

```text
Mean reduction = 0.8279
SD reduction   = 1.9475
N              = 149
```

Standard error:

```text
SE = SD / sqrt(N)
   = 1.9475 / sqrt(149)
   = 1.9475 / 12.206
   = 0.1595
```

T-statistic:

```text
t = 0.8279 / 0.1595
  = 5.189
```

Degree of freedom:

```text
df = N - 1
   = 149 - 1
   = 148
```

P-value one-sided dihitung dari distribusi t:

```text
p-value = P(T >= 5.189), T ~ t(df = 148)
```

Artinya p-value adalah luas area di ekor kanan distribusi t mulai dari 5.189 sampai tak hingga.

Hasil dari notebook:

```text
p-value = 3.423 x 10^-7
```

Interpretasi:

```text
Jika rata-rata reduction sebenarnya <= 0,
peluang mendapatkan t-statistic sebesar 5.189 atau lebih ekstrem
hanya sekitar 0.0000003423.
```

Karena lebih kecil dari 0.05, paired t-test juga mendukung bahwa Two-Stage memberikan improvement signifikan.

### 5.3 Contoh P-Value pada Wilcoxon Signed-Rank Test

Pada Wilcoxon, p-value dihitung dari distribusi statistik rank di bawah H0.

Di bawah H0:

```text
Tanda positif dan negatif dari setiap paired difference dianggap acak.
```

Artinya, jika tidak ada efek nyata, rank besar dan kecil seharusnya tersebar relatif seimbang antara tanda positif dan negatif.

Contoh kecil dengan 5 non-zero pairs:

```text
Rank = 1, 2, 3, 4, 5
```

Total rank:

```text
1 + 2 + 3 + 4 + 5 = 15
```

Misalkan hasil observasi:

```text
W+ = 13
W- = 2
```

Untuk menghitung p-value one-sided, kita hitung probabilitas mendapatkan `W+ >= 13` jika tanda positif/negatif sebenarnya acak.

Karena ada 5 rank, setiap rank bisa positif atau negatif. Jumlah kemungkinan tanda:

```text
2^5 = 32 kemungkinan
```

Kombinasi yang menghasilkan `W+ >= 13`:

```text
W+ = 13: rank positif {1,3,4,5}
W+ = 14: rank positif {2,3,4,5}
W+ = 15: rank positif {1,2,3,4,5}
```

Ada 3 kombinasi dari 32.

Maka contoh p-value:

```text
p-value = 3 / 32
        = 0.09375
```

Pada contoh kecil ini belum signifikan karena:

```text
0.09375 > 0.05
```

Namun pada thesis jumlah data jauh lebih besar, yaitu 149 paired images. Setelah zero differences dikelola dengan metode Wilcoxon, hasilnya:

```text
Wilcoxon statistic = 4402.5
p-value = 1.23 x 10^-12
```

Interpretasinya:

```text
Jika sebenarnya Two-Stage tidak lebih baik,
peluang mendapatkan dominasi signed-rank sekuat hasil observasi
hanya sekitar 0.00000000000123.
```

Karena jauh lebih kecil dari 0.05, maka improvement Two-Stage signifikan.

## 6. Bootstrap Confidence Interval

Bootstrap digunakan sebagai additional robustness test. Tujuannya adalah melihat rentang estimasi penurunan MAE tanpa terlalu bergantung pada asumsi distribusi normal.

Langkah bootstrap:

1. Ambil data `Delta_i` sebanyak 149.
2. Sampling ulang dengan replacement.
3. Hitung rata-rata reduction dari sampel bootstrap.
4. Ulangi ribuan kali.
5. Ambil percentile 2.5% dan 97.5% sebagai confidence interval 95%.

Hasil thesis:

```text
Bootstrap 95% CI = [0.549, 1.157]
```

Artinya, dengan pendekatan bootstrap, penurunan MAE rata-rata diperkirakan berada antara:

```text
0.549 sampai 1.157 percentage points
```

Karena seluruh interval berada di atas nol, maka hasil ini mendukung bahwa improvement Two-Stage memang positif.

## 7. Sign Test

Sign test mengecek jumlah gambar yang membaik vs memburuk, tanpa memperhatikan besar kecilnya improvement.

Hasil thesis:

```text
Improved images = 80
Worse images    = 18
Equal images    = 51
```

Untuk sign test, yang dihitung adalah non-zero differences:

```text
80 improved + 18 worse = 98 images
```

Hipotesisnya:

```text
H0: peluang improved = peluang worse = 0.5
H1: peluang improved > peluang worse
```

Hasil:

```text
p-value = 8.303 x 10^-11
```

Karena:

```text
8.303 x 10^-11 < 0.05
```

maka jumlah image yang membaik secara statistik jauh lebih banyak daripada yang memburuk. Ini memperkuat hasil Wilcoxon.

## 8. Paired T-Test sebagai Sensitivity Check

Walaupun Shapiro-Wilk menunjukkan data tidak normal, paired t-test tetap dihitung sebagai pembanding tambahan atau sensitivity check.

Formula paired t-test:

```text
t = mean reduction / standard error
```

Dengan angka thesis:

```text
Mean reduction = 0.8279
SD reduction   = 1.9475
N              = 149
```

Standard error:

```text
SE = SD / sqrt(N)
   = 1.9475 / sqrt(149)
   = 1.9475 / 12.206
   = 0.1595
```

Maka:

```text
t = 0.8279 / 0.1595
  = 5.189
```

Degree of freedom:

```text
df = N - 1
   = 149 - 1
   = 148
```

Hasil:

```text
t(148) = 5.189
p-value one-sided = 3.423 x 10^-7
```

Karena:

```text
3.423 x 10^-7 < 0.05
```

paired t-test juga menunjukkan improvement signifikan.

Confidence interval 95%:

```text
[0.513, 1.143]
```

Karena interval tidak melewati nol, hasilnya konsisten dengan Wilcoxon dan bootstrap.

## 9. Cohen's dz untuk Effect Size

Signifikan secara statistik belum tentu besar secara praktis. Karena itu dihitung effect size.

Cohen's dz:

```text
d_z = mean reduction / SD reduction
```

Dengan angka thesis:

```text
d_z = 0.8279 / 1.9475
    = 0.425
```

Interpretasi umum:

```text
0.2 = small effect
0.5 = medium effect
0.8 = large effect
```

Maka:

```text
d_z = 0.425
```

berarti efeknya berada di antara small dan medium, atau dapat disebut small-to-moderate practical effect.
