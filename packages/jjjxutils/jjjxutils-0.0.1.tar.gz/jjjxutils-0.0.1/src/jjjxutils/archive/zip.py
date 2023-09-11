import zipfile
import io
import os


def extract_ignoring_folders(zip_data):
    files = []
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        for filename in z.namelist():
            if os.path.exists(filename.split("/")[-1]):
                os.remove(filename.split("/")[-1])
            z.extract(filename)
            os.rename(filename, filename.split("/")[-1])
            os.removedirs("/".join(filename.split("/")[:-1]))
            files.append(filename.split("/")[-1])
    return files
