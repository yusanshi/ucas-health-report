import argparse
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--first', type=str, required=True)
parser.add_argument('--second', type=str, required=True)
parser.add_argument('--threshold', type=float, default=0.9)
args = parser.parse_args()


def get_image_similiarity(first_image_path, second_image_path):
    """Input two images and calculate similarity of them
    """
    first_image = Image.open(first_image_path)
    second_image = Image.open(second_image_path)
    first_image = np.array(first_image).flatten()
    second_image = np.array(second_image).flatten()
    assert first_image.shape == second_image.shape
    return (first_image == second_image).sum() / len(first_image)


similiarity = get_image_similiarity(args.first, args.second)
print(f'Similiarity: {similiarity}')
assert similiarity >= args.threshold
