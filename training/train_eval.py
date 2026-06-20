#!/usr/bin/env python3
import argparse
import json
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from imutils import paths
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.layers import Conv2D, Dense, Flatten, Input, MaxPooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from tensorflow.keras.utils import to_categorical


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train and evaluate the face mask CNN from the paper repository."
    )
    parser.add_argument(
        "--dataset",
        default="dataset",
        help="Path to dataset directory with with_mask/ and without_mask/ subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        default="runs/default",
        help="Directory for trained model, plots, and evaluation outputs.",
    )
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=32, help="Training batch size.")
    parser.add_argument("--learning-rate", type=float, default=5e-4, help="Adam learning rate.")
    parser.add_argument("--seed", type=int, default=10, help="Random seed.")
    parser.add_argument(
        "--image-size", type=int, default=96, help="Square input image size used by the paper."
    )
    return parser.parse_args()


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def load_dataset(dataset_dir: Path, image_size: int):
    image_paths = sorted(list(paths.list_images(str(dataset_dir))))
    if not image_paths:
        raise FileNotFoundError(f"No images found under {dataset_dir}")

    data = []
    labels = []

    for image_path in image_paths:
        label = Path(image_path).parent.name
        image = load_img(image_path, target_size=(image_size, image_size))
        image = img_to_array(image)
        image = preprocess_input(image)
        data.append(image)
        labels.append(label)

    data = np.array(data, dtype="float32")
    labels = np.array(labels)

    lb = LabelBinarizer()
    labels = lb.fit_transform(labels)
    labels = to_categorical(labels)
    return data, labels, lb


def build_model(input_shape):
    inputs = Input(shape=input_shape)
    x = Conv2D(16, (3, 3), activation="relu", padding="same")(inputs)
    x = MaxPooling2D((2, 2), padding="same")(x)
    x = Conv2D(32, (3, 3), activation="relu", padding="same")(x)
    x = MaxPooling2D((2, 2), padding="same")(x)
    x = Conv2D(64, (3, 3), activation="relu", padding="same")(x)
    x = MaxPooling2D((2, 2), padding="same")(x)
    x = Conv2D(128, (3, 3), activation="relu", padding="same")(x)
    x = MaxPooling2D((2, 2), padding="same")(x)
    x = Conv2D(256, (3, 3), activation="relu", padding="same")(x)
    x = MaxPooling2D((2, 2), padding="same")(x)
    x = Flatten()(x)
    x = Dense(1024)(x)
    x = Dense(64)(x)
    outputs = Dense(2, activation="softmax")(x)
    return Model(inputs=inputs, outputs=outputs)


def make_augmenter():
    return ImageDataGenerator(
        rotation_range=20,
        zoom_range=0.15,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        horizontal_flip=True,
        fill_mode="nearest",
    )


def save_training_plots(history, output_dir: Path):
    history_dict = history.history
    epochs = range(1, len(history_dict["loss"]) + 1)

    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history_dict["loss"], label="train_loss")
    plt.plot(epochs, history_dict["val_loss"], label="val_loss")
    plt.title("Training and Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "loss_curve.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history_dict["accuracy"], label="train_accuracy")
    plt.plot(epochs, history_dict["val_accuracy"], label="val_accuracy")
    plt.title("Training and Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "accuracy_curve.png", dpi=160)
    plt.close()


def main():
    args = parse_args()
    set_seed(args.seed)

    dataset_dir = Path(args.dataset).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    data, labels, lb = load_dataset(dataset_dir, args.image_size)
    train_x, test_x, train_y, test_y = train_test_split(
        data,
        labels,
        test_size=0.20,
        random_state=args.seed,
        stratify=labels,
    )

    augmenter = make_augmenter()
    model = build_model((args.image_size, args.image_size, 3))
    optimizer = tf.keras.optimizers.legacy.Adam(
        learning_rate=args.learning_rate, decay=args.learning_rate / args.epochs
    )
    model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=["accuracy"])

    history = model.fit(
        augmenter.flow(train_x, train_y, batch_size=args.batch_size),
        steps_per_epoch=max(1, len(train_x) // args.batch_size),
        validation_data=(test_x, test_y),
        validation_steps=max(1, len(test_x) // args.batch_size),
        epochs=args.epochs,
        verbose=1,
    )

    predictions = model.predict(test_x, batch_size=args.batch_size, verbose=0)
    predicted_idx = np.argmax(predictions, axis=1)
    true_idx = np.argmax(test_y, axis=1)

    report = classification_report(true_idx, predicted_idx, target_names=lb.classes_, output_dict=True)
    report_text = classification_report(true_idx, predicted_idx, target_names=lb.classes_)
    matrix = confusion_matrix(true_idx, predicted_idx)

    model.save(output_dir / "face_mask_model.h5")
    with (output_dir / "classification_report.txt").open("w", encoding="utf-8") as fh:
        fh.write(report_text)
    with (output_dir / "classification_report.json").open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    with (output_dir / "confusion_matrix.json").open("w", encoding="utf-8") as fh:
        json.dump(matrix.tolist(), fh, indent=2)
    with (output_dir / "label_map.json").open("w", encoding="utf-8") as fh:
        json.dump(lb.classes_.tolist(), fh, indent=2)
    with (output_dir / "history.json").open("w", encoding="utf-8") as fh:
        json.dump(history.history, fh, indent=2)

    save_training_plots(history, output_dir)

    summary = {
        "dataset_dir": str(dataset_dir),
        "num_images": int(len(data)),
        "train_samples": int(len(train_x)),
        "test_samples": int(len(test_x)),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "seed": args.seed,
        "final_train_accuracy": float(history.history["accuracy"][-1]),
        "final_val_accuracy": float(history.history["val_accuracy"][-1]),
        "test_accuracy": float(report["accuracy"]),
    }
    with (output_dir / "run_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(json.dumps(summary, indent=2))
    print()
    print(report_text)


if __name__ == "__main__":
    main()
