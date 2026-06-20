# Reproduction Notes

Paper: "A real time face mask detection system using convolutional neural network"

## Paper settings extracted from the PDF

- Dataset: 4000 images
- Classes: `with_mask` and `without_mask`
- Input size: `96x96`
- Split: `80:20`
- Augmentation: rotation, zoom, width/height shift, shear, horizontal/vertical flip
- Model: 5 `Conv2D` + 5 `MaxPooling2D` + `Flatten` + `Dense(1024)` + `Dense(64)` + `Dense(2, softmax)`
- Optimizer: `Adam`
- Learning rate: `0.0005`
- Epochs: `100`
- Batch size: `32`
- Loss: `binary_crossentropy`

## Local environment used here

- Python: `3.11` in `.venv`
- TensorFlow: `2.15.1`

## Commands

Activate environment:

```bash
cd /home/nashiru/comvis/Facemask_Detection
. .venv/bin/activate
```

Or use the wrapper that already injects the required runtime libraries:

```bash
cd /home/nashiru/comvis/Facemask_Detection
./run_with_env.sh --version
```

Train and evaluate:

```bash
./run_with_env.sh train_eval.py --dataset dataset --output-dir runs/paper_repro --epochs 100 --batch-size 32 --learning-rate 0.0005 --seed 10
```

Run prediction on one image:

```bash
./run_with_env.sh predict_image.py --image demo-images/group2.png --model runs/paper_repro/face_mask_model.h5 --output runs/paper_repro/group2_pred.jpg
```

## Files produced by training

- `face_mask_model.h5`
- `classification_report.txt`
- `classification_report.json`
- `confusion_matrix.json`
- `history.json`
- `run_summary.json`
- `accuracy_curve.png`
- `loss_curve.png`

## Suggested report structure

1. Short summary of the paper and objective.
2. Hardware/software used on your laptop.
3. Dataset and preprocessing actually used in your run.
4. Model architecture and hyperparameters.
5. Experimental results from `run_summary.json` and `classification_report.txt`.
6. Comparison with the paper's reported accuracy.
7. Discussion of why your results differ from the paper.
