import logging
import os
import shutil
import subprocess
import json
import time

from functools import reduce
from pathlib import Path
from typing import NamedTuple, Optional, List

from biliup.common.tools import NamedLock
from biliup.config import config

logger = logging.getLogger('biliup')


class UploadBase:
    class FileInfo(NamedTuple):
        video: str
        danmaku: Optional[str]

    def __init__(self, principal, data, persistence_path=None, postprocessor=None):
        self.principal = principal
        self.persistence_path = persistence_path
        self.data: dict = data
        self.post_processor = postprocessor

    @staticmethod
    def file_list(index) -> List[FileInfo]:
        from biliup.handler import event_manager
        media_extensions = ['.mp4', '.flv', '.3gp', '.webm', '.mkv', '.ts']

        # 获取文件列表
        file_list = []
        for file_name in os.listdir('.'):
            if index in file_name and os.path.isfile(file_name):
                file_list.append(file_name)
        if len(file_list) == 0:
            return []
        file_list = sorted(file_list, key=lambda x: os.path.getctime(x))

        # 正在上传的文件列表
        upload_filename: list = event_manager.context['upload_filename']

        results = []
        for index, file in enumerate(file_list):
            old_name = file
            if file.endswith('.part'):
                file_list[index] = os.path.splitext(file)[0]
                file = os.path.splitext(file)[0]

            name, ext = os.path.splitext(file)
            # 过滤正在上传的
            if name in upload_filename:
                continue
            # 过滤不是视频的
            if ext not in media_extensions:
                continue

            if old_name != file:
                logger.info(f'{old_name} 已更名为 {file}')
                shutil.move(old_name, file)

            file_size = os.path.getsize(file) / 1024 / 1024
            threshold = config.get('filtering_threshold', 0)
            if file_size <= threshold:
                logger.info(f'过滤删除 - {file}')
                UploadBase.remove_file(file)
                continue

            video = file
            danmaku = None
            if f'{name}.xml' in file_list:
                danmaku = f'{name}.xml'

            result = UploadBase.FileInfo(video=video, danmaku=danmaku)
            results.append(result)

        # 过滤弹幕
        for file in file_list:
            name, ext = os.path.splitext(file)
            # 过滤正在上传的
            if name in upload_filename:
                continue
            if ext == '.xml':
                have_video = False
                for result in results:
                    if result.danmaku == file:
                        have_video = True
                        break
                if not have_video:
                    logger.info(f'无视频，过滤删除 - {file}')
                    UploadBase.remove_file(file)
        return results

    @staticmethod
    def remove_filelist(file_list: List[FileInfo]):
        for f in file_list:
            UploadBase.remove_file(f.video)
            if f.danmaku is not None:
                UploadBase.remove_file(f.danmaku)

    @staticmethod
    def remove_file(file: str):
        try:
            os.remove(file)
            logger.info(f'删除 - {file}')
        except:
            logger.warning(f'删除失败 - {file}')

    def upload(self, file_list: List[FileInfo]) -> List[FileInfo]:
        raise NotImplementedError()

    def start(self):
        from biliup.handler import event_manager
        # 保证一个name同时只有一个上传线程扫描文件列表
        lock = NamedLock(f'upload_file_list_{self.principal}')
        upload_filename_list = []
        try:
            lock.acquire()
            file_list = UploadBase.file_list(self.principal)
            if len(file_list) > 0:
                # 下载后处理 上传前处理
                downloaded_processor = config['streamers'].get(self.principal, {}).get('downloaded_processor')
                if downloaded_processor:
                    from biliup.handler import processor
                    default_date = time.localtime()
                    processor(downloaded_processor, json.dumps({
                        "name": self.principal,
                        "url": self.data.get('url'),
                        "room_title": self.data.get('title', self.principal),
                        "start_time": int(time.mktime(self.data.get('date', default_date))),
                        "end_time": int(time.mktime(self.data.get('end_time', default_date))),
                        "file_list": [file.video for file in file_list]
                    }, ensure_ascii=False))
                    # 后处理完成后重新扫描文件列表
                    file_list = UploadBase.file_list(self.principal)

                if len(file_list) > 0:
                    logger.info('准备上传' + self.data["format_title"])
                    upload_filename_list = [os.path.splitext(file.video)[0] for file in file_list]
                    with NamedLock('upload_filename'):
                        event_manager.context['upload_filename'].extend(upload_filename_list)
                    lock.release()
                    needed2process = self.upload(file_list)
                    if needed2process:
                        self.postprocessor(needed2process)
        finally:
            with NamedLock('upload_filename'):
                event_manager.context['upload_filename'] = list(
                    set(event_manager.context['upload_filename']) - set(upload_filename_list))
            if lock.locked():
                lock.release()

    def postprocessor(self, data: List[FileInfo]):
        # data = file_list
        if self.post_processor is None:
            # 删除封面
            if self.data.get('live_cover_path') is not None:
                UploadBase.remove_file(self.data['live_cover_path'])
            return self.remove_filelist(data)

        file_list = []
        for i in data:
            file_list.append(i.video)
            if i.danmaku is not None:
                file_list.append(i.danmaku)

        for post_processor in self.post_processor:
            if post_processor == 'rm':
                # 删除封面
                if self.data.get('live_cover_path') is not None:
                    UploadBase.remove_file(self.data['live_cover_path'])
                self.remove_filelist(data)
                continue
            if post_processor.get('mv'):
                for file in file_list:
                    path = Path(file)
                    dest = Path(post_processor['mv'])
                    if not dest.is_dir():
                        dest.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(path, dest / path.name)
                    except Exception as e:
                        logger.exception(e)
                        continue
                    logger.info(f"move to {(dest / path.name).absolute()}")
            if post_processor.get('run'):
                try:
                    process_output = subprocess.check_output(
                        post_processor['run'], shell=True,
                        input=reduce(lambda x, y: x + str(Path(y).absolute()) + '\n', file_list, ''),
                        stderr=subprocess.STDOUT, text=True)
                    logger.info(process_output.rstrip())
                except subprocess.CalledProcessError as e:
                    logger.exception(e.output)
                    continue
