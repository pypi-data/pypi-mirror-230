# -*- coding: utf-8 -*-
import os
import os.path

from fundrive.download.core import Downloader
from fundrive.download.work import WorkerFactory, Worker


class SpiltDownloader(Downloader):
    def __init__(self, blocks_num=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocks_num = blocks_num or self.filesize // (100 * 1024 * 1024)

    def download(self, worker_num=5, capacity=100, *args, **kwargs):
        size = self.filesize // self.blocks_num
        splits = [i for i in range(0, self.filesize, size)]
        splits[-1] = self.filesize

        cache_dir = f"{self.filepath}.cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        success_files = []
        with WorkerFactory(worker_num=worker_num, capacity=capacity, timeout=2) as pool:
            for index in range(1, len(splits)):
                tmp_file = f"{cache_dir}/split-{str(index).zfill(5)}.tmp"

                def callback(worker: Worker, *args, **kwargs):
                    dst = f"{worker.filepath}.success"
                    os.rename(worker.filepath, dst)
                    success_files.append(dst)

                start = splits[index - 1]
                end = splits[index]
                pool.submit(
                    Worker(url=self.url, range_start=start, range_end=end, filepath=tmp_file, callback=callback)
                )

        assert len(success_files) == self.blocks_num
        with open(self.filepath, "wb") as fw:
            for file in success_files:
                with open(file, "rb") as fr:
                    fw.write(fr.read())
                os.remove(file)
            os.removedirs(cache_dir)
