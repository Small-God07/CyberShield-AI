"""Script autonome pour générer et visualiser le dataset d'entraînement."""
import sys
import os

# Allow running from the data/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from model import CyberShieldModel


def main():
    m = CyberShieldModel()
    X, y = m.generer_dataset()

    print(f"Dataset généré : {X.shape[0]} échantillons, {X.shape[1]} features")
    print()

    # Distribution par classe
    unique, counts = np.unique(y, return_counts=True)
    print("Distribution des classes :")
    for cls, cnt in zip(unique, counts):
        bar = "█" * (cnt // 25)
        print(f"  {cls:<15} {cnt:>4}  {bar}")

    print()
    # Feature statistics per class
    print("Statistiques par feature (moyenne) :")
    header = f"{'Feature':<28}" + "".join(f"{c:>15}" for c in unique)
    print(header)
    print("-" * len(header))
    for i, feat in enumerate(m.FEATURES):
        row = f"{feat:<28}"
        for cls in unique:
            mask = y == cls
            row += f"{X[mask, i].mean():>15.2f}"
        print(row)

    # Save to CSV
    out_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    import csv
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(m.FEATURES + ["label"])
        for row, label in zip(X, y):
            writer.writerow(list(row) + [label])
    print(f"\nDataset sauvegardé dans : {out_path}")


if __name__ == "__main__":
    main()
