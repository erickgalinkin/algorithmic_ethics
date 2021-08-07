import os
from os.path import join, exists
import subprocess
import multiprocessing
import hashlib
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import random
import pandas as pd
from tqdm import tqdm

from crop_api import ImageSaliencyModel, is_symmetric, parse_output, reservoir_sampling
from image_manipulation import join_images

data_dir = "../data/"
files = ['facescrub_actors.txt', 'facescrub_actresses.txt']
crop_path = join("../bin", "linux", "candidate_crops")
model_path = join("../bin", "fastgaze.vxm")

# eval_size = 20000

def build_facrscrub_dataframe(source, files):
    names = list()
    images = list()
    gender = list()

    for f in files:
        with open(source + f, 'r', encoding='utf-8') as fd:
            fd.readline()
            for line in fd.readlines():
                components = line.split('\t')
                name = components[0].replace(' ', '_')
                url = components[3]
                fname = hashlib.sha1(url.encode()).hexdigest() + '.jpg'
                names.append(name)
                images.append(fname)
                gender.append('m' if f == "facescrub_actors.txt" else 'f')

    df = pd.DataFrame(list(zip(names, images, gender)), columns=["name", "image", "gender"])

    df = df[df.image.isin(os.listdir(join(source, "images")))]
    df.reset_index(inplace=True)
    print("Dataframe Built!\nGender Value Counts:\n")
    print(df.gender.value_counts())
    return df


# Taken directly from Image Crop Analysis paper
# https://github.com/twitter-research/image-crop-analysis/blob/main/notebooks/Demographic%20Bias%20Analysis.ipynb
def parse_output(output):
    output = output.splitlines()
    final_output = {"salient_point": [], "crops": [], "all_salient_points": []}
    key = "salient_point"
    for i, line in enumerate(output):
        line = line.split()
        if len(line) in {2, 4}:
            line = [int(v) for v in line]
            if i != 0:
                key = "crops"
        elif len(line) == 3:
            key = "all_salient_points"
            line = [float(v) for v in line]
        else:
            raise RuntimeError(f"Invalid line: {line}")
        final_output[key].append(line)
    return final_output


def gender_salience(path1, path2, gender1, gender2):
    """Given two image paths and the (binary) gender of the subject of each image, return the gender of the
    subject whose image contained the most salient point"""
    img1 = Image.open(join(data_dir, "images", path1))
    img2 = Image.open(join(data_dir, "images", path2))
    joint_img = join_images([img1, img2], col_wrap=2, padding=200)
    img_path = join(data_dir, "test", f"{path1[:10]}_{path2[:10]}.jpeg")
    joint_img.save(img_path)

    cmd = f"{str(crop_path)} {str(model_path)} '{str(img_path)}' show_all_points"
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
    output_dict = parse_output(output)
    salient_point_x = output_dict["salient_point"][0][0]
    pbar.update(1)
    if salient_point_x > joint_img.width / 2:
        return gender2
    else:
        return gender1


def create_pairs(df):
    """Take in a dataframe and return a list of 4-tuples """
    pairs = list()
    male_df = df[df["gender"] == "m"].reset_index()
    female_df = df[df["gender"] == "f"].reset_index()
    # This should be fixed at scale but since I know there are fewer female images, I'm going to cheat a bit.
    # This will shuffle the indices and set the male index to be the same as the female index, effectively setting them
    # to both be shuffled and the same length.
    female_df = female_df.sample(frac=1)
    male_df = male_df.iloc[female_df.index]

    # We need to randomly decide whether the male or female image is on the left, so we'll just use an RNG.
    # There are definitely more efficient and pythonic ways to do it but whatever.
    for i in range(len(female_df)):
        if random.randint == 0:
            img1 = male_df["image"].iloc[i]
            gender1 = "m"
            img2 = female_df["image"].iloc[i]
            gender2 = "f"
            data_tuple = (img1, img2, gender1, gender2)
            pairs.append(data_tuple)
        else:
            img1 = female_df["image"].iloc[i]
            gender1 = "f"
            img2 = male_df["image"].iloc[i]
            gender2 = "m"
            data_tuple = (img1, img2, gender1, gender2)
            pairs.append(data_tuple)
    return pairs


def plot_counts(counts):
    c = dict(counts)

    plt.bar(range(len(c)), list(c.values()), align='center')
    plt.xticks(range(len(c)), list(c.keys()))
    plt.savefig("../data/counts.png")


if __name__ == "__main__":
    data = build_facrscrub_dataframe(data_dir, files)
    tasks = create_pairs(data)
    pbar = tqdm(total=len(tasks))
    pool_size = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=pool_size)
    results = pool.starmap(gender_salience, tasks)
    pool.close()
    pool.join()
    pbar.close()

    counts = Counter(results)
    print("Counts: {}".format(counts))

    plot_counts(counts)

