"""
Network-File-System
===================

A python-library to make moves, copys and writes safer on remote drives.
Writing a file is not atomic. In the worst case the process writing your file
dies while the file is not complete. To at least spot such incomplete files,
all writing-operations (write, move, copy, ...) will be followed by an
atomic move.
"""
from .version import __version__
import uuid
import os
import shutil
import errno
import tempfile
import builtins


def copy(src, dst):
    """
    Tries to copy `src` to `dst`. First `src` is copied to `dst.tmp` and then
    renmaed atomically to `dst`.

    Parameters
    ----------
    src : str
        Path to source.
    dst : str
        Path to destination.
    """
    copy_id = uuid.uuid4().__str__()
    tmp_dst = "{:s}.{:s}.tmp".format(dst, copy_id)
    try:
        shutil.copytree(src, tmp_dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy2(src, tmp_dst)
        else:
            raise
    os.rename(tmp_dst, dst)


def move(src, dst):
    """
    Tries to move `src` to `dst`. In case the move goes across devices,
    `src` is copied first to `dst.tmp` and then renmaed atomically to `dst`.

    Parameters
    ----------
    src : str
        Path to source.
    dst : str
        Path to destination.
    """
    try:
        os.rename(src, dst)
    except OSError as err:
        if err.errno == errno.EXDEV:
            copy(src, dst)
            os.unlink(src)
        else:
            raise


def write(content, path, mode="wt"):
    """
    Writes content to `path.tmp` and attempt an atomic move to `path`.

    Parameters
    ----------
    content : bytes / str
        Payload to be written.
    path : str
        Path to destination.
    mode : str (`wt`)
        Mode of writing.
    """
    copy_id = uuid.uuid4().__str__()
    tmp_path = "{:s}.{:s}.tmp".format(path, copy_id)
    with open(tmp_path, mode) as f:
        f.write(content)
    move(src=tmp_path, dst=path)


def read(path, mode="rt"):
    """
    I think reading an entire file is rather safe across the nfs.
    But in case I am wrong, here is the wrapper.

    Parameters
    ----------
    path : str
        Path to source.
    mode : str (`rt`)
        Mode of reading.
    """
    with open(path, mode) as f:
        content = f.read()
    return content


def open(file, mode, tmp_dir=None):
    if "r" in str.lower(mode):
        return builtins.open(file=file, mode=mode)
    elif "w" in str.lower(mode):
        return NfsFileWriter(file=file, mode=mode, tmp_dir=tmp_dir)
    else:
        AttributeError("'mode' must either be 'r' or 'w'.")


class NfsFileWriter:
    """
    Write to tmp-dir first and move to final destination after closeing.
    This guarantees that when the output 'file' exists, the file is also
    complete.
    """

    def __init__(self, file, mode, tmp_dir=None):
        """
        tmp_dir : str (default: None)
            Path to the temporary-directory where the file is initially written
            to. Make sure this is a fast drive.
        """
        self.file = file
        self.mode = mode
        self.tmp_dir = tmp_dir
        self.ready = False
        self.closed = False

    def close(self):
        self.rc = self.f.close()
        move(src=self.tmp_file, dst=self.file)
        self.tmp.cleanup()
        self.closed = True
        return self.rc

    def write(self, payload):
        if not self.ready:
            self.__enter__()
        return self.f.write(payload)

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory(dir=self.tmp_dir)
        self.tmp_file = os.path.join(
            self.tmp.name, os.path.basename(self.file)
        )
        self.f = builtins.open(file=self.tmp_file, mode=self.mode)
        self.ready = True
        return self.f

    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.close()
