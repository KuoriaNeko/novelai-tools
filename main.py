# -*- coding: utf-8 -*-

import json
import os
import random
import time
import zipfile
from datetime import datetime

import requests
import yaml
from requests.exceptions import RequestException, SSLError

from image_generator import NovelaiImageGenerator


def main():
    with open("config.yml", "r", encoding="utf-8") as f:
        cfg = yaml.load(f, yaml.Loader)

    random_delay_min = cfg["generator"]["random_delay"]["min"]
    random_delay_max = cfg["generator"]["random_delay"]["max"]
    max_retries = cfg["generator"]["retries"]
    retry_delay = cfg["generator"]["retry_delay"]
    output_dir = cfg["generator"]["output"]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    novelai_cfg = cfg["novelai_api"]
    novelai_cfg.update(cfg["prompt"])
    novelai_cfg["proxy"] = cfg["proxy"]
    generator = NovelaiImageGenerator(novelai_cfg)

    total_images = 0
    for prompt in generator.prompts:
        total_images += prompt["images_num"]

    retry_count = 0
    for i in range(total_images):
        try:
            print("[{}/{}] generating image".format(i+1, total_images))

            image_data = generator.generate_image()
            filename = "{:.0f}.png".format(datetime.now().timestamp())
            file_path = os.path.join(output_dir, filename)
            try:
                with open(file_path, "wb") as file:
                    file.write(image_data)
                print("Image saved as: ", file_path)
            except IOError as e:
                print("an error ocurred while saving image, ", e)

            if i+1 < total_images:
                retry_count = 0
                delay_s = random.randint(random_delay_min, random_delay_max)
                print("delay {}s".format(delay_s))
                time.sleep(delay_s)
        except (SSLError, RequestException, zipfile.BadZipFile) as e:
            print(e)
            retry_count += 1

            if retry_count > max_retries:
                print("maximum retries exceeded, exiting")
                return

            print("[{}/{}] retry in {}s".format(retry_count,
                  max_retries, retry_delay))

            try:
                time.sleep(retry_delay)
            except KeyboardInterrupt:
                return
        except KeyboardInterrupt:
            return

    print("done")

if __name__ == "__main__":
    main()
