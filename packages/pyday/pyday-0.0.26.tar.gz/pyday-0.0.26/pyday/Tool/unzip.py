# 解壓 壓縮文件
import os
import zipfile
import tarfile
import rarfile

# 解壓縮
def unzip(filepath, savepath):
    if filepath.endswith(".zip"):
        f = zipfile.ZipFile(filepath, "r")
        for file in f.namelist():
            f.extract(file, savepath)
        f.close()
    elif filepath.endswith(".tar.gz") or filepath.endswith(".tgz"):
        f = tarfile.open(filepath)
        for file in f.getnames():
            f.extract(file, savepath)
        f.close()
    elif filepath.endswith(".rar"):
        f = rarfile.RarFile(filepath)
        for file in f.namelist():
            f.extract(file, savepath)
        f.close()
    else:
        print("not support")
