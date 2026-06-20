# Laporan Reproduksi Jurnal

## Judul

Reproduksi Paper "A real time face mask detection system using convolutional neural network"

---

## 1. Tujuan

Tugas ini bertujuan untuk menjalankan ulang implementasi paper "A real time face mask detection system using convolutional neural network" pada lingkungan lokal, kemudian membandingkan hasil eksperimen yang diperoleh dengan hasil yang dilaporkan pada paper. Selain itu, sebagai pembanding, kami juga melatih model **MobileNetV2 dengan pendekatan transfer learning** menggunakan kondisi eksperimen yang identik, untuk melihat perbedaan antara pendekatan from-scratch (CNN paper) dan transfer learning.

---

## 2. Ringkasan Paper

Paper ini mengusulkan sistem deteksi masker wajah untuk gambar statis dan video real-time. Metode utama yang digunakan adalah CNN kustom dengan lima lapisan `Conv2D`, lima lapisan `MaxPooling2D`, dan lapisan klasifikasi `Dense` dengan keluaran dua kelas, yaitu `with_mask` dan `without_mask`.

Pengaturan utama pada paper:

- Dataset: 4000 gambar
- Kelas: `with_mask` dan `without_mask`
- Ukuran input: `96×96`
- Train/test split: `80:20`
- Optimizer: `Adam`
- Learning rate: `0.0005`
- Batch size: `32`
- Epoch: `100`
- Loss function: `binary_crossentropy`

---

## 3. Lingkungan Pengujian

- Sistem operasi: NixOS Linux 6.18.26 (x86_64)
- CPU: AMD Ryzen 7 PRO 5850U with Radeon Graphics (16 logical cores)
- GPU: Tidak digunakan (training dilakukan di CPU)
- RAM: 30 GB
- Python: 3.11.15
- TensorFlow: 2.15.1
- scikit-learn: 1.4.0
- numpy: 1.26.x

---

## 4. Dataset dan Pra-pemrosesan

Dataset yang digunakan berasal dari repo `techyhoney/Facemask_Detection` dan berisi:

- `with_mask`: 2000 gambar
- `without_mask`: 2000 gambar
- Total: **4000 gambar**

Tahap pra-pemrosesan yang dijalankan:

1. Semua gambar di-resize menjadi `96×96`.
2. Nilai piksel dinormalisasi ke rentang `[-1, 1]` menggunakan `preprocess_input` dari `MobileNetV2` (fungsi yang sama digunakan oleh paper asli).
3. Label kelas diubah ke format one-hot categorical.
4. Dataset dibagi dengan rasio `80:20` (stratified) menggunakan `random_state=10`.
5. Augmentasi data diterapkan pada data training menggunakan:
   - `rotation_range=20`
   - `zoom_range=0.15`
   - `width_shift_range=0.2`, `height_shift_range=0.2`
   - `shear_range=0.15`
   - `horizontal_flip=True`
   - `fill_mode='nearest'`

---

## 5. Arsitektur Model

### 5.1 CNN Kustom (Model Paper — From Scratch)

| Layer | Output Shape | Parameter |
|---|---|---|
| Input | (96, 96, 3) | 0 |
| Conv2D(16, 3×3, relu, same) + MaxPooling2D | (48, 48, 16) | 448 |
| Conv2D(32, 3×3, relu, same) + MaxPooling2D | (24, 24, 32) | 4,640 |
| Conv2D(64, 3×3, relu, same) + MaxPooling2D | (12, 12, 64) | 18,496 |
| Conv2D(128, 3×3, relu, same) + MaxPooling2D | (6, 6, 128) | 73,856 |
| Conv2D(256, 3×3, relu, same) + MaxPooling2D | (3, 3, 256) | 295,168 |
| Flatten | (2304,) | 0 |
| Dense(1024) | (1024,) | 2,360,320 |
| Dense(64) | (64,) | 65,600 |
| Dense(2, softmax) | (2,) | 130 |

**Total parameter: 2,818,658** (semua trainable)

- Optimizer: `Adam(learning_rate=0.0005, decay=0.0005/100)`
- Loss: `binary_crossentropy`
- Epochs: 100

### 5.2 MobileNetV2 (Model Pembanding — Transfer Learning)

| Komponen | Detail |
|---|---|
| Backbone | MobileNetV2 pretrained ImageNet (semua layer dibekukan) |
| Head klasifikasi | GlobalAveragePooling2D → Dense(128, relu) → Dropout(0.5) → Dense(2, softmax) |
| Total parameter | 2,422,210 |
| Parameter dilatih | 164,226 (head saja) |
| Parameter dibekukan | 2,257,984 (backbone) |

- Optimizer: `Adam(learning_rate=0.0001, decay=0.0001/20)`
- Loss: `binary_crossentropy`
- Epochs: 20

MobileNetV2 dipilih sebagai pembanding karena merupakan arsitektur ringan yang umum digunakan untuk deteksi masker secara real-time, dan mewakili pendekatan transfer learning sebagai lawan dari pendekatan from-scratch CNN paper.

---

## 6. Hasil Eksperimen

### 6.1 CNN Kustom (Model Paper)

- Jumlah data train: 3200 gambar
- Jumlah data test: 800 gambar
- Akurasi training akhir (epoch 100): **99.22%**
- Akurasi validasi akhir (epoch 100): **98.50%**
- Akurasi test: **98.50%**

| Kelas | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| `with_mask` | 0.98 | 0.98 | 0.98 | 400 |
| `without_mask` | 0.98 | 0.98 | 0.98 | 400 |
| **Rata-rata (macro)** | **0.98** | **0.98** | **0.98** | **800** |

**Confusion Matrix:**

|  | Pred: with_mask | Pred: without_mask |
|---|---|---|
| **True: with_mask** | 394 (TP) | 6 (FN) |
| **True: without_mask** | 6 (FP) | 394 (TN) |

### 6.2 MobileNetV2 (Model Pembanding)

- Jumlah data train: 3200 gambar
- Jumlah data test: 800 gambar
- Akurasi training akhir (epoch 20): **95.81%**
- Akurasi validasi akhir (epoch 20): **98.00%**
- Akurasi test: **98.00%**

| Kelas | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| `with_mask` | 0.99 | 0.97 | 0.98 | 400 |
| `without_mask` | 0.97 | 0.99 | 0.98 | 400 |
| **Rata-rata (macro)** | **0.98** | **0.98** | **0.98** | **800** |

**Confusion Matrix:**

|  | Pred: with_mask | Pred: without_mask |
|---|---|---|
| **True: with_mask** | 388 (TP) | 12 (FN) |
| **True: without_mask** | 4 (FP) | 396 (TN) |

---

## 7. Perbandingan Antar Model dan dengan Paper

### 7.1 Perbandingan dengan Paper Asli (CNN Paper)

| Metrik | Paper | Lokal (CNN Paper) |
|---|---|---|
| Akurasi keseluruhan | ~98% | **98.50%** |
| `with_mask` precision | 0.98 | 0.98 |
| `with_mask` recall | 0.97 | 0.98 |
| `without_mask` precision | 0.97 | 0.98 |
| `without_mask` recall | 0.98 | 0.98 |

### 7.2 Perbandingan CNN Paper vs MobileNetV2

| Metrik | CNN Paper (from scratch) | MobileNetV2 (transfer learning) |
|---|---|---|
| Akurasi test | **98.50%** | 98.00% |
| Epoch dibutuhkan | 100 | **20** |
| Parameter dilatih | 2,818,658 | **164,226** |
| F1 rata-rata | 0.98 | 0.98 |
| Kesalahan total | 12 (6+6) | 16 (12+4) |
| Waktu training (CPU) | ~600 detik | **~140 detik** |

---

## 8. Analisis

### 8.1 Perbandingan CNN Paper dengan Paper Asli

1. Akurasi lokal (98.50%) **sedikit melampaui** hasil yang dilaporkan paper (~98%), selisih +0.5%.
2. Kurva training menunjukkan konvergensi yang sangat stabil — training accuracy mencapai 99.22% sedangkan validation accuracy 98.50%, gap kecil menandakan generalisasi yang baik tanpa overfitting signifikan.
3. Precision dan recall seimbang sempurna antara kedua kelas (0.98 vs 0.98), lebih merata dibanding paper yang memiliki sedikit ketidakseimbangan antar kelas.

### 8.2 Perbandingan CNN Paper vs MobileNetV2

1. **Akurasi hampir setara.** CNN paper sedikit lebih unggul (98.50% vs 98.00%), selisih hanya 0.5%. Keduanya mencapai F1-score 0.98.

2. **Efisiensi pelatihan jauh berbeda.** MobileNetV2 mencapai akurasi setara hanya dalam **20 epoch** dengan hanya melatih **164 ribu parameter** (head saja), sedangkan CNN paper butuh **100 epoch** melatih **2.8 juta parameter** penuh. Transfer learning jauh lebih hemat komputasi.

3. **Karakter kesalahan berbeda.** CNN paper menghasilkan kesalahan seimbang (6+6). MobileNetV2 lebih sering salah mengklasifikasikan `with_mask` sebagai `without_mask` (12 kasus) tapi sangat jarang sebaliknya (4 kasus).

---

## 9. Faktor Perbedaan Hasil dengan Paper

1. **Versi TensorFlow berbeda**: Paper menggunakan environment lama (kemungkinan TF 2.x awal), sementara reproduksi menggunakan TF 2.15.1.

2. **Tidak ada GPU**: Training dijalankan sepenuhnya pada CPU, sedangkan paper kemungkinan menggunakan GPU. Walaupun hasilnya seharusnya deterministik dengan seed yang sama, operasi floating-point pada CPU vs GPU dapat menghasilkan perbedaan kecil.

3. **Perbaikan augmentasi**: Notebook asli menggunakan `vertical_flip=True`, yang tidak sesuai paper dan tidak relevan untuk gambar wajah. Reproduksi ini menghapus parameter tersebut sesuai spesifikasi paper, menghasilkan akurasi yang lebih tinggi.

---

## 10. Kesimpulan

1. Reproduksi **berhasil dijalankan** secara penuh dengan arsitektur dan hyperparameter sesuai paper. Hasil lokal (98.50%) **melampaui sedikit** hasil paper (~98%).

2. Model pembanding **MobileNetV2 transfer learning** mencapai akurasi 98.00% — hampir setara CNN paper — namun dengan efisiensi yang jauh lebih tinggi: 5× lebih sedikit epoch dan 17× lebih sedikit parameter yang dilatih.

3. Pelajaran utama dari eksperimen ini:
   - Transfer learning (MobileNetV2) sangat efisien untuk dataset kecil: konvergen cepat, parameter sedikit, akurasi tetap tinggi.
   - CNN from-scratch paper sedikit lebih akurat (98.50% vs 98.00%) dengan augmentasi yang tepat.
   - Augmentasi yang relevan secara domain sangat penting — menghapus `vertical_flip` yang tidak relevan meningkatkan akurasi CNN paper dari 97.25% menjadi 98.50%.

---

## Lampiran

### CNN Paper (Model Utama)
- Plot akurasi training: `runs/paper_repro/accuracy_curve.png`
- Plot loss training: `runs/paper_repro/loss_curve.png`
- Classification report: `runs/paper_repro/classification_report.txt`
- Confusion matrix: `runs/paper_repro/confusion_matrix.json`
- Model tersimpan: `runs/paper_repro/face_mask_model.h5`
- Ringkasan run: `runs/paper_repro/run_summary.json`
- History 100 epoch: `runs/paper_repro/history.json`

### MobileNetV2 (Model Pembanding)
- Plot akurasi training: `runs/mobilenetv2/accuracy_curve.png`
- Plot loss training: `runs/mobilenetv2/loss_curve.png`
- Classification report: `runs/mobilenetv2/classification_report.txt`
- Confusion matrix: `runs/mobilenetv2/confusion_matrix.json`
- Model tersimpan: `runs/mobilenetv2/face_mask_model.h5`
- Ringkasan run: `runs/mobilenetv2/run_summary.json`
- Script training: `train_eval_mobilenetv2.py`
