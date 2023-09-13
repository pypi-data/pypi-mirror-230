import os
import re

import requests
from tqdm import tqdm

sess = requests.Session()


def verify_password(pwd: str, share_key: str):
    global sess

    r = sess.get(f"https://cloud.tsinghua.edu.cn/d/{share_key}/")
    pattern = '<input type="hidden" name="csrfmiddlewaretoken" value="(.*)">'
    csrfmiddlewaretoken = re.findall(pattern, r.text)
    if not csrfmiddlewaretoken:
        return

    # Verify password
    csrfmiddlewaretoken = csrfmiddlewaretoken[0]
    print("PASSWORD", pwd)
    r = sess.post(
        f"https://cloud.tsinghua.edu.cn/d/{share_key}/",
        data={"csrfmiddlewaretoken": csrfmiddlewaretoken, "token": share_key, "password": pwd},
        headers={"Referer": f"https://cloud.tsinghua.edu.cn/d/{share_key}/"},
    )
    # print(r.text)
    if "Please enter a correct password" in r.text:
        raise ValueError("Couldn't download files, please check your password.")
    elif "Please enter the password" in r.text:
        raise ValueError("This share link needs password.")


def dfs_search_files(share_key: str, path="/"):
    global sess
    filelist = []
    r = sess.get(f"https://cloud.tsinghua.edu.cn/api/v2.1/share-links/{share_key}/dirents/?path={path}")
    objects = r.json()["dirent_list"]
    for obj in objects:
        if obj["is_dir"]:
            filelist += dfs_search_files(share_key, obj["folder_path"])
        else:
            filelist.append(obj)
    return filelist


def download_single_file(url: str, fname: str, overwrite=False):
    global sess
    resp = sess.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))

    if os.path.exists(fname) and not overwrite and os.path.getsize(fname) == total:
        return
    with open(fname, "wb") as file, tqdm(
        total=total,
        ncols=120,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def download(share_key, save="./tmp/tsinghua", path="/", overwrite=False, *args, **kwargs):
    print("Searching for files to be downloaded...")
    filelist = sorted(dfs_search_files(share_key, path=path), key=lambda x: x["file_path"])
    print("Found {} files in the share link.".format(len(filelist)))
    print("Last Modified Time".ljust(25), " ", "File Size".rjust(10), " ", "File Path")
    print("-" * 100)
    for file in filelist:
        print(file["last_modified"], " ", str(file["size"]).rjust(10), " ", file["file_path"])
    print("-" * 100)

    for i, file in enumerate(filelist):
        file_url = "https://cloud.tsinghua.edu.cn/d/{}/files/?p={}&dl=1".format(share_key, file["file_path"])
        save_path = os.path.join(save, file["file_path"][1:])
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        print("[{}/{}] Downloading File: {}".format(i + 1, len(filelist), save_path))
        try:
            download_single_file(file_url, save_path, overwrite=overwrite)
        except Exception as e:
            print("Error happened when downloading file: {}".format(save_path))
            print(e)

    print("Download finished.")
