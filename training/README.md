### Training

The model side of the project. It reproduces the custom CNN from Goyal et al. (2022) trained from scratch, and adds a MobileNetV2 transfer learning model as a comparison.

#### Dataset

4000 images, 2000 `with_mask` and 2000 `without_mask`, 80/20 stratified split. `dataset_sample/` has a few of each so you can see the format. The full set comes from the original repo (see credits).

#### Models

- **Custom CNN** (the paper's, from scratch): 5 Conv2D blocks (16 to 256) then Dense(1024), Dense(64), Dense(2). 100 epochs, Adam at lr 0.0005.
- **MobileNetV2** (transfer learning): frozen ImageNet backbone plus a small head (global average pooling, Dense(128), dropout, Dense(2)). Only the head trains, 20 epochs, lr 0.0001. Converges way faster since the backbone already knows visual features.

Same dataset, split, input size (96x96), preprocessing and augmentation for both, so the comparison is fair.

#### Results

| Model | Approach | Epochs | Test accuracy |
|-------|----------|--------|---------------|
| Custom CNN | from scratch | 100 | 98.50% |
| MobileNetV2 | transfer learning | 20 | 98.00% |

Both land around 0.98 precision and recall on both classes, close to the paper's ~98%. Full breakdown is in `COMPARISON_REPORT.md`.

#### Run

```bash
pip install -r requirements.txt

# notebook
#   open Model_Training.ipynb
# or the script versions
python train_eval.py                 # custom CNN
python train_eval_mobilenetv2.py     # MobileNetV2
```

#### What's here

- `Model_Training.ipynb`, `Model_Image_Testing.ipynb`, `Model_Video_Testing.ipynb`: the notebooks
- `train_eval.py`, `train_eval_mobilenetv2.py`, `predict_image.py`: script versions
- `COMPARISON_REPORT.md`, `LAPORAN_LENGKAP.md`, `REPRO_NOTES.md`: the writeups and reproduction notes
- `dataset_sample/`: a few sample images

#### Credits

Adapted from [techyhoney/Facemask_Detection](https://github.com/techyhoney/Facemask_Detection) (MIT), modified so it trains end to end and extended with the MobileNetV2 comparison. Based on Goyal et al., "A real time face mask detection system using convolutional neural network" (2022).
