# Laporan Perbandingan Model

## Perbandingan CNN Paper vs MobileNetV2 (Transfer Learning)

## 1. Latar Belakang

Paper "A real time face mask detection system using convolutional neural network" (Goyal et al., 2022) tidak hanya mengusulkan satu model, tetapi juga membandingkan beberapa metode untuk menemukan arsitektur terbaik. Untuk melengkapi reproduksi ini, kami menambahkan **satu model pembanding**, yaitu **MobileNetV2 dengan pendekatan transfer learning**, lalu membandingkannya dengan CNN kustom yang diusulkan paper.

MobileNetV2 dipilih karena:

1. Merupakan arsitektur ringan yang umum digunakan untuk deteksi masker secara real-time.
2. Fungsi pra-pemrosesan yang dipakai pada reproduksi ini memang berasal dari MobileNetV2 (`preprocess_input`), sehingga perbandingannya konsisten.
3. Mewakili pendekatan **transfer learning** (memakai bobot pretrained) sebagai lawan dari pendekatan **training from scratch** (CNN paper).

## 2. Kondisi Eksperimen yang Disamakan

Agar perbandingan adil, semua faktor di luar arsitektur model **dibuat identik**:

| Faktor | Nilai (sama untuk kedua model) |
|---|---|
| Dataset | 4000 gambar (2000 `with_mask`, 2000 `without_mask`) |
| Train/test split | 80:20 stratified, `random_state=10` |
| Ukuran input | 96×96 |
| Pra-pemrosesan | `preprocess_input` MobileNetV2 (rentang [-1, 1]) |
| Augmentasi | rotation 20, zoom 0.15, shift 0.2, shear 0.15, horizontal_flip |
| Optimizer | Adam |
| Loss | binary_crossentropy |
| Batch size | 32 |
| Seed | 10 |

## 3. Perbedaan Arsitektur (Inti Perbandingan)

| Aspek | CNN Paper (from scratch) | MobileNetV2 (transfer learning) |
|---|---|---|
| Pendekatan | Dilatih dari nol | Backbone pretrained ImageNet (frozen) + head baru |
| Backbone | 5× Conv2D (16→256) | MobileNetV2 (bobot ImageNet, dibekukan) |
| Head klasifikasi | Flatten → Dense(1024) → Dense(64) → Dense(2) | GlobalAveragePooling2D → Dense(128) → Dropout(0.5) → Dense(2) |
| Total parameter | ± 2,818,658 (semua dilatih) | ± 2,422,210 total, hanya head (± 164,226) yang dilatih |
| Learning rate | 0.0005 | 0.0001 |
| Epoch | 100 | 20 |

Catatan: MobileNetV2 hanya butuh **20 epoch** karena backbone-nya sudah "pintar" mengenali fitur visual dari ImageNet, sehingga konvergensi jauh lebih cepat dibanding CNN yang harus belajar dari nol selama 100 epoch.

## 4. Hasil Eksperimen

### 4.1 CNN Paper (from scratch)

- Epoch: 100
- Akurasi training akhir: 99.22%
- Akurasi test: **98.50%**

| Kelas | Precision | Recall | F1-Score |
|---|---|---|---|
| `with_mask` | 0.98 | 0.98 | 0.98 |
| `without_mask` | 0.98 | 0.98 | 0.98 |

**Confusion Matrix:**

|  | Pred: with_mask | Pred: without_mask |
|---|---|---|
| **True: with_mask** | 394 | 6 |
| **True: without_mask** | 6 | 394 |

### 4.2 MobileNetV2 (transfer learning)

- Epoch: 20
- Akurasi training akhir: 95.81%
- Akurasi test: **98.00%**

| Kelas | Precision | Recall | F1-Score |
|---|---|---|---|
| `with_mask` | 0.99 | 0.97 | 0.98 |
| `without_mask` | 0.97 | 0.99 | 0.98 |

**Confusion Matrix:**

|  | Pred: with_mask | Pred: without_mask |
|---|---|---|
| **True: with_mask** | 388 | 12 |
| **True: without_mask** | 4 | 396 |

## 5. Perbandingan Langsung

| Metrik | CNN Paper | MobileNetV2 |
|---|---|---|
| Akurasi test | **98.50%** | 98.00% |
| Epoch dibutuhkan | 100 | **20** |
| Parameter dilatih | ± 2.8 juta | **± 164 ribu** |
| Pendekatan | From scratch | Transfer learning |
| F1 rata-rata | 0.98 | 0.98 |
| Kesalahan total | 12 (6+6) | 16 (12+4) |

## 6. Analisis

1. **Akurasi hampir setara.** CNN paper sedikit lebih unggul (98.50% vs 98.00%), selisih hanya 0.5%. Keduanya sama-sama mencapai F1-score 0.98, menandakan kedua pendekatan sama-sama valid untuk tugas ini.

2. **Efisiensi pelatihan jauh berbeda.** MobileNetV2 mencapai akurasi setara hanya dalam **20 epoch** dan hanya melatih **± 164 ribu parameter** (head saja), sedangkan CNN paper butuh **100 epoch** melatih **2.8 juta parameter**. Artinya transfer learning jauh lebih hemat waktu dan komputasi.

3. **Karakter kesalahan berbeda.** CNN paper menghasilkan kesalahan seimbang (6 dan 6). MobileNetV2 cenderung salah mengklasifikasikan `with_mask` menjadi `without_mask` (12 kasus) tetapi sangat jarang sebaliknya (4 kasus) — recall `with_mask`-nya sedikit lebih rendah (0.97).

4. **Kesimpulan praktis.** Untuk dataset relatif kecil seperti ini, CNN kustom dari paper sudah cukup baik. Namun jika tujuannya adalah pelatihan cepat atau dataset terbatas, MobileNetV2 (transfer learning) memberikan hasil setara dengan biaya komputasi jauh lebih kecil.

## 7. Kesimpulan

Reproduksi ini berhasil membandingkan dua pendekatan: CNN from scratch (model paper) dan MobileNetV2 transfer learning. Keduanya mencapai akurasi tinggi (98.50% vs 98.00%) dengan F1-score sama (0.98). Perbedaan utama bukan pada akurasi akhir, melainkan pada **efisiensi**: MobileNetV2 mencapai hasil setara dengan 5× lebih sedikit epoch dan ± 17× lebih sedikit parameter yang dilatih. Hal ini sesuai dengan motivasi paper dalam membandingkan beberapa metode untuk menemukan trade-off terbaik antara akurasi dan efisiensi.

## Lampiran

### CNN Paper
- Plot akurasi: `runs/paper_repro/accuracy_curve.png`
- Plot loss: `runs/paper_repro/loss_curve.png`
- Classification report: `runs/paper_repro/classification_report.txt`
- Model: `runs/paper_repro/face_mask_model.h5`

### MobileNetV2
- Plot akurasi: `runs/mobilenetv2/accuracy_curve.png`
- Plot loss: `runs/mobilenetv2/loss_curve.png`
- Classification report: `runs/mobilenetv2/classification_report.txt`
- Model: `runs/mobilenetv2/face_mask_model.h5`
- Script training: `train_eval_mobilenetv2.py`
