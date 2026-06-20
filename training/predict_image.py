#!/usr/bin/env python3
import argparse
from pathlib import Path

import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array


def parse_args():
    parser = argparse.ArgumentParser(description="Run mask detection on a single image.")
    parser.add_argument("--image", required=True, help="Path to input image.")
    parser.add_argument("--model", required=True, help="Path to trained .h5 model.")
    parser.add_argument(
        "--prototxt",
        default="deploy.prototxt.txt",
        help="Path to face detector prototxt.",
    )
    parser.add_argument(
        "--weights",
        default="res10_300x300_ssd_iter_140000.caffemodel",
        help="Path to face detector weights.",
    )
    parser.add_argument(
        "--output",
        default="prediction_output.jpg",
        help="Path to save annotated prediction image.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.3,
        help="Minimum face detection confidence.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    model = load_model(args.model)
    net = cv2.dnn.readNet(args.weights, args.prototxt)
    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {args.image}")

    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    detected = 0
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < args.confidence:
            continue

        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (start_x, start_y, end_x, end_y) = box.astype("int")
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(w - 1, end_x)
        end_y = min(h - 1, end_y)

        face = image[start_y:end_y, start_x:end_x]
        if face.size == 0:
            continue

        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(face, (96, 96))
        face = img_to_array(face)
        face = preprocess_input(face)
        face = np.expand_dims(face, axis=0)

        without_mask, mask = model.predict(face, verbose=0)[0]
        label = "Mask" if mask > without_mask else "No Mask"
        color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
        score = max(mask, without_mask) * 100
        text = f"{label}: {score:.2f}%"

        cv2.putText(image, text, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        cv2.rectangle(image, (start_x, start_y), (end_x, end_y), color, 2)
        detected += 1

    output_path = Path(args.output).resolve()
    cv2.imwrite(str(output_path), image)
    print(f"Saved annotated image to {output_path}")
    print(f"Faces processed: {detected}")


if __name__ == "__main__":
    main()
