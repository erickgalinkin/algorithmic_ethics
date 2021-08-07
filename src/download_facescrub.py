import os
from os.path import join, exists
import multiprocessing
import hashlib
import cv2
from tqdm import tqdm

data_dir = "../data/"
files = ['facescrub_actors.txt', 'facescrub_actresses.txt']

# Locate and pull FaceScrub data
# Download function adopted from Faceteam
# https://github.com/faceteam/facescrub/blob/master/download.py

def download(data):
    """
        download from urls into folder names using wget
    """
    names = data[0]
    urls = data[1]

    assert(len(names) == len(urls))

    # download using external wget
    CMD = 'wget -c -t 1 -T 3 "%s" -O "%s"'
    for i in tqdm(range(len(names))):
        directory = join(data_dir, "images")
        fname = hashlib.sha1(urls[i].encode()).hexdigest() + '.jpg'
        dst = join(directory, fname)
        if exists(dst):
#             print("already downloaded, skipping...")
            continue
        else:
            res = os.system(CMD % (urls[i], dst))
        img = cv2.imread(dst)
        if img is None:
            # no image data
            os.remove(dst)
            
if __name__ == "__main__":
    for f in files:
        with open(data_dir + f, 'r', encoding='utf-8') as fd:
            fd.readline()
            names = list()
            urls = list()
            for line in fd.readlines():
                components = line.split('\t')
                name = components[0].replace(' ', '_')
                url = components[3]
                names.append(name)
                urls.append(url)
            last_name = names[0]
            task_names = list()
            task_urls = list()
            tasks = list()
            for i in range(len(names)):
                if names[i] == last_name:
                    task_names.append(names[i])
                    task_urls.append(urls[i])
                else:
                    tasks.append((task_names, task_urls))
                    task_names = [names[i]]
                    task_urls = [urls[i]]
                    last_name = names[i]
            tasks.append((task_names, task_urls))

            pool_size = multiprocessing.cpu_count()
            pool = multiprocessing.Pool(processes=pool_size, maxtasksperchild=2)
            pool.map(download, tasks)
            pool.close()
            pool.join()