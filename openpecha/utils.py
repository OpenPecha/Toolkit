'''Utilities functions
'''
import gzip
import io
import shutil

from openpecha.github_utils import create_release


def gzip_str(string_):
    # taken from https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode='w') as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


def ocr_result_input(path):
    return path


def create_release_with_assets(path):
    asset_paths = []
    for asset_path in (path/'releases').iterdir():
        shutil.make_archive(asset_path, 'zip', asset_path)
        asset_paths.append(f'{str(asset_path)}.zip')

    create_release(path.name, asset_paths=asset_paths)