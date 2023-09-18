# -*- coding: utf-8 -*-
import os
import os.path

import requests
from fundrive.download.core import Downloader
from fundrive.download.work import WorkerFactory, Worker
from tqdm import tqdm


class SpiltDownloader(Downloader):
    def __init__(self, blocks_num=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocks_num = blocks_num or self.filesize // (100 * 1024 * 1024)
        # self.blocks_num = max(self.blocks_num, 2)
        if not self.check_available():
            print(f"{self.filename} this url not support range requests,set blocks_num=1.")
            self.blocks_num = 1

    def download(self, worker_num=5, capacity=100, prefix="", overwrite=False, *args, **kwargs):
        if not overwrite and os.path.exists(self.filepath) and self.filesize == os.path.getsize(self.filepath):
            return False

        prefix = f"{prefix}--" if prefix is not None and len(prefix) > 0 else ""
        size = self.filesize // self.blocks_num
        splits = [i for i in range(0, self.filesize, size)]
        if self.blocks_num == 1:
            splits = [0, self.filesize]
        splits[-1] = self.filesize

        cache_dir = f"{self.filepath}.cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        success_files = []
        pbar = tqdm(
            total=self.filesize,
            ncols=120,
            desc=f"{prefix}{os.path.basename(self.filepath)}",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )

        def update_pbar(total, curser, current):
            pbar.update(current)
            pbar.refresh()

        with WorkerFactory(worker_num=worker_num, capacity=capacity, timeout=1) as pool:
            for index in range(1, len(splits)):
                tmp_file = f"{cache_dir}/split-{str(index).zfill(5)}.tmp"

                def finish_callback(worker: Worker, *args, **kwargs):
                    dst = f"{worker.filepath}.success"
                    os.rename(worker.filepath, dst)
                    success_files.append(dst)

                start = splits[index - 1]
                end = splits[index]

                pool.submit(
                    Worker(
                        url=self.url,
                        range_start=start,
                        range_end=end,
                        filepath=tmp_file,
                        update_callback=update_pbar,
                        finish_callback=finish_callback,
                    )
                )

        assert len(success_files) == self.blocks_num
        with open(self.filepath, "wb") as fw:
            for file in success_files:
                with open(file, "rb") as fr:
                    fw.write(fr.read())
                os.remove(file)
            os.removedirs(cache_dir)

    def check_available(self) -> bool:
        header = {"Range": f"bytes=0-100"}
        with requests.get(self.url, stream=True, headers=header) as req:
            return req.status_code == 206


def download(url, filepath, overwrite=False, worker_num=5, capacity=100, prefix=""):
    SpiltDownloader(url=url, filepath=filepath, overwrite=overwrite).download(
        worker_num=worker_num, capacity=capacity, prefix=prefix
    )
