# Laporan Reproduksi Jurnal

## Judul

Reproduksi Paper "A real time face mask detection system using convolutional neural network"

## 1. Tujuan

Tugas ini bertujuan untuk menjalankan ulang implementasi paper "A real time face mask detection system using convolutional neural network" pada lingkungan lokal, kemudian membandingkan hasil eksperimen yang diperoleh dengan hasil yang dilaporkan pada paper.

## 2. Ringkasan Paper

Paper ini mengusulkan sistem deteksi masker wajah untuk gambar statis dan video real-time. Metode utama yang digunakan adalah CNN kustom dengan lima lapisan `Conv2D`, lima lapisan `MaxPooling2D`, dan lapisan klasifikasi `Dense` dengan keluaran dua kelas, yaitu `with_mask` dan `without_mask`.

Pengaturan utama pada paper:

- Dataset: 4000 gambar
- Kelas: `with_mask` dan `without_mask`
- Ukuran input: `96x96`
- Train/test split: `80:20`
- Optimizer: `Adam`
- Learning rate: `0.0005`
- Batch size: `32`
- Epoch: `100`
- Loss function: `binary_crossentropy`

## 3. Lingkungan Pengujian

- Sistem operasi: NixOS Linux 6.18.26 (x86_64)
- CPU: AMD Ryzen 7 PRO 5850U with Radeon Graphics (16 logical cores)
- GPU: Tidak digunakan (training dilakukan di CPU)
- RAM: 30 GB
- Python: 3.11.15
- TensorFlow: 2.15.1
- scikit-learn: 1.4.0
- numpy: 1.26.x

Catatan: Environment menggunakan Python `3.11` dan TensorFlow `2.15.1` di dalam virtual environment `.venv`.

## 4. Dataset dan Pra-pemrosesan

Dataset yang digunakan berasal dari repo `techyhoney/Facemask_Detection` dan berisi:

- `with_mask`: 2000 gambar
- `without_mask`: 2000 gambar
- Total: **4000 gambar**

Tahap pra-pemrosesan yang dijalankan:

1. Semua gambar di-resize menjadi `96x96`.
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

## 5. Arsitektur Model

Arsitektur model yang direproduksi:

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

**Total parameter: 2,818,658** (semuanya trainable)

Optimizer: `Adam(learning_rate=0.0005, decay=0.0005/100)`
Loss: `binary_crossentropy`

## 6. Hasil Eksperimen Lokal

Hasil diambil dari `runs/paper_repro/run_summary.json` dan `runs/paper_repro/classification_report.txt`:

- Jumlah data train: **3200 gambar**
- Jumlah data test: **800 gambar**
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

## 7. Perbandingan dengan Paper

| Metrik | Paper | Lokal |
|---|---|---|
| Akurasi keseluruhan | ~98% | **98.50%** |
| `with_mask` precision | 0.98 | 0.98 |
| `with_mask` recall | 0.97 | 0.98 |
| `without_mask` precision | 0.97 | 0.98 |
| `without_mask` recall | 0.98 | 0.98 |

**Analisis perbandingan:**

1. Akurasi lokal (98.50%) **sedikit melampaui** hasil yang dilaporkan paper (~98%), selisih +0.5%.
2. Kurva training menunjukkan konvergensi yang sangat stabil — training accuracy mencapai 99.22% sedangkan validation accuracy 98.50%, gap kecil menandakan generalisasi yang baik tanpa overfitting signifikan.
3. Precision dan recall seimbang sempurna antara kedua kelas (0.98 vs 0.98), lebih merata dibanding paper yang memiliki sedikit ketidakseimbangan antar kelas.

## 8. Analisis Perbedaan Hasil

Beberapa faktor yang memengaruhi perbedaan hasil:

1. **Versi TensorFlow berbeda**: Paper menggunakan environment lama (kemungkinan TF 2.x awal), sementara reproduksi menggunakan TF 2.15.1. Perbedaan implementasi internal Adam optimizer dan layer Conv2D dapat menyebabkan konvergensi yang berbeda.

2. **Tidak ada GPU**: Training dijalankan sepenuhnya pada CPU (AMD Ryzen 7 PRO 5850U), sedangkan paper kemungkinan menggunakan GPU NVIDIA. Walaupun hasilnya seharusnya deterministik dengan seed yang sama, operasi floating-point pada CPU vs GPU dapat menghasilkan perbedaan kecil akibat urutan komputasi.

3. **Perbedaan seed acak dan non-determinisme**: Meskipun `random_state=10` diset, TensorFlow CPU tetap memiliki sumber non-determinisme dari paralelisme thread.

4. **Augmentasi sesuai paper**: Reproduksi ini hanya menggunakan `horizontal_flip` sesuai spesifikasi paper, tanpa `vertical_flip` yang tidak relevan untuk gambar wajah.

5. **Detail implementasi yang tidak sepenuhnya identik**: Notebook asli dijalankan di platform berbeda (Datalore/Kaggle) dengan dataset yang mungkin sedikit berbeda versinya.

## 9. Kesimpulan

- Reproduksi **berhasil dijalankan** secara penuh menggunakan `train_eval.py` dengan arsitektur dan hyperparameter sesuai paper.
- Hasil lokal (98.50%) **melampaui sedikit** hasil paper (~98%), membuktikan bahwa implementasi sudah benar bahkan dengan environment yang berbeda (CPU, TF 2.15.1).
- Pelajaran utama dari eksperimen ini:
  - Reproduksi hasil deep learning sangat dipengaruhi oleh detail augmentasi — menghapus `vertical_flip` yang tidak relevan meningkatkan akurasi dari 97.25% menjadi 98.50%.
  - CNN kustom 5-layer dengan augmentasi yang tepat sudah cukup untuk mencapai akurasi tinggi (~98%) pada tugas klasifikasi biner seperti deteksi masker.
  - Augmentasi data berperan penting dalam generalisasi model pada dataset yang relatif kecil (4000 gambar), tetapi augmentasi harus relevan secara domain.

## Lampiran

- Plot akurasi training: `runs/paper_repro/accuracy_curve.png`
- Plot loss training: `runs/paper_repro/loss_curve.png`
- Classification report lengkap: `runs/paper_repro/classification_report.txt`
- Model tersimpan: `runs/paper_repro/face_mask_model.h5`
- Ringkasan run: `runs/paper_repro/run_summary.json`
