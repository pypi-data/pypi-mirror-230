from PIL import Image
from pillow_heif import register_heif_opener, register_avif_opener
import os
from math import ceil
from io import BytesIO
import tempfile
from shutil import copyfile
register_heif_opener()  # 支持 heic、heif
register_avif_opener()  # 支持 avif


class Luban:

    def __init__(self, ignore_by=102400, quality=60):
        """默认<100KB不压缩，压缩品质60"""
        self.ignore_by = ignore_by
        self.quality = quality

    def compress(self, file) -> str:
        """返回压缩后的文件路径"""
        if isinstance(file, (bytes, str)):
            filesize = os.path.getsize(file)
        elif isinstance(file, BytesIO):
            filesize = file.getbuffer().nbytes
        else:
            raise ValueError('unsupported file type')

        image = Image.open(file)

        if image.format == 'GIF':  # 不处理GIF，直接保存
            filename = tempfile.mkstemp(suffix='.gif')[1]
            if isinstance(file, (bytes, str)):
                copyfile(file, filename)
            elif isinstance(file, BytesIO):
                with open(filename, 'wb') as f:
                    f.write(file.getbuffer())
            return filename

        if image.mode == "RGB":
            format_ = "JPEG"
        elif image.mode == "RGBA":
            format_ = "PNG"
        else:  # 其他的图片格式转成JPEG
            image = image.convert("RGB")
            format_ = "JPEG"

        # 临时文件路径
        filename = tempfile.mkstemp(suffix='.' + format_.lower())[1]

        if filesize <= self.ignore_by:
            # 直接保存
            image.save(filename, format_)
        else:
            # 先调整大小，再调整品质
            src_width, src_height = image.size
            scale = self._compute_scale(src_width, src_height)
            image = image.resize((src_width // scale, src_height // scale))
            image.save(filename, format_, quality=self.quality)

        return filename

    @staticmethod
    def thumbnail(original_filename, size: tuple) -> str:
        """基于原文件创建缩略图 返回缩略图路径"""
        image = Image.open(original_filename)
        image = image.copy()
        image.thumbnail(size)
        filename = tempfile.mkstemp(suffix=os.path.splitext(original_filename)[1])[1]
        image.save(filename)
        return filename

    @staticmethod
    def _compute_scale(src_width, src_height):
        """计算缩小的倍数"""

        src_width = src_width + 1 if src_width % 2 == 1 else src_width
        src_height = src_height + 1 if src_height % 2 == 1 else src_height

        long_side = max(src_width, src_height)
        short_side = min(src_width, src_height)

        scale = short_side / long_side
        if 1 >= scale > 0.5625:
            if long_side < 1664:
                return 1
            elif long_side < 4990:
                return 2
            elif 4990 < long_side < 10240:
                return 4
            else:
                return max(1, long_side // 1280)
        elif 0.5625 >= scale > 0.5:
            return max(1, long_side // 1280)
        else:
            return ceil(long_side / (1280.0 / scale))
