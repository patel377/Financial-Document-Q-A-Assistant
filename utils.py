# utils.py
import tempfile
import os

def save_uploaded_file(uploaded_file):
    tmpdir = tempfile.gettempdir()
    path = os.path.join(tmpdir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def readable_file_size(size, decimal_places=2):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024.0 or unit == 'TB':
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024.0
