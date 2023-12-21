# -*- coding: utf-8 -*-

import io
import random
import zipfile

import requests
import yaml


class NovelaiImageGenerator:
    def __init__(self, cfg: dict):

        self.api = cfg["api"]
        self.headers = {
            "Authorization": f"Bearer {cfg['token']}"
        }
        self.headers.update(cfg["request_headers"])
        self.negative_prompt = ",".join(cfg["negative_prompts"])

        self.proxy = cfg["proxy"]

        self.body = {
            "input": "",
            "model": "nai-diffusion-3",
            "action": "generate",
            "parameters": {},
        }

        self.body["parameters"].update(cfg["request_body_parameters"])
        self.body["parameters"]["negative_prompt"] = ",".join(
            cfg["negative_prompts"])

        self.prompt_prefix = ",".join(cfg["prompt_prefix"])

        self.prompts = []
        self.load_prompts(cfg["prompt_file"])

    def load_prompts(self, fn: str):
        with open(fn, "r", encoding="utf-8") as f:
            for item in yaml.load(f, yaml.Loader):
                if len(item.get("prompt", "")) == 0:
                    continue
                self.prompts.append(item)
        print("loaded {} prompts".format(len(self.prompts)))

    def generate_image(self) -> bytes:
        seed = random.randint(0, 9999999999)
        self.body["parameters"]["seed"] = seed

        prompt = random.choice(self.prompts)
        prompt["images_num"] -= 1
        if prompt["images_num"] <= 0:
            self.prompts.remove(prompt)

        # Inherit or ignore global prompt
        if prompt.get("inherit_global_prompt", True):
            self.body["input"] = self.prompt_prefix + "," + prompt["prompt"]
        else:
            self.body["input"] = prompt["prompt"]

        # Inherit or ignore global prompt
        if prompt.get("inherit_global_negative_prompt", True):
            self.body["parameters"]["negative_prompt"] = self.negative_prompt
            if len(prompt.get("negative_prompt", "")) > 0:
                self.body["parameters"]["negative_prompt"] += "," + \
                    prompt["negative_prompt"]
        else:
            self.body["parameters"]["negative_prompt"] = prompt["negative_prompt"]

        r = requests.post(
            self.api, json=self.body, headers=self.headers, proxies=self.proxy)
        try:
            assert r.status_code == 200
            with zipfile.ZipFile(
                io.BytesIO(r.content), mode="r"
            ) as zip:
                with zip.open("image_0.png") as image:
                    return image.read()
        except AssertionError:
            print(r.status_code)
            print(r.text)
            raise
