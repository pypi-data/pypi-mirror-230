import io
import os
import tarfile

from tqdm import tqdm


class ProgressFileIO(io.FileIO):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        res = tqdm(
            total=os.path.getsize(path),
            desc=f"解压: {os.path.basename(path)}",
            ncols=120,
            ascii=True,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )
        self._progress_callback = res

    def read(self, size=None) -> bytes:
        self._progress_callback.update(self.tell() - self._progress_callback.n)
        return io.FileIO.read(self, size)


class ProgressExFileObject(tarfile.ExFileObject):
    def __init__(self, tarfile: tarfile.TarFile, tarinfo):
        super().__init__(tarfile, tarinfo)
        res = tqdm(
            total=tarfile.name,
            desc=f"{tarfile.name}",
            ncols=120,
            ascii=True,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )
        self._progress_callback = res

    def read(self, size=None):
        self._progress_callback.update(size)
        return super().read(size)


class FileWrapper(object):
    def __init__(self, fileobj, size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fileobj = fileobj
        self._progress = tqdm(
            total=size,
            ncols=120,
            desc=f"压缩: {os.path.basename(fileobj.name)}",
            ascii=True,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )

    def _update(self, length):
        if self._progress is not None:
            if self._progress.n + length > self._progress.total:
                self._progress.total = self._progress.n + length
            self._progress.update(length)

    def read(self, size=-1):
        data = self._fileobj.read(size)
        self._update(len(data))
        return data

    def readline(self, size=-1):
        data = self._fileobj.readline(size)
        self._update(len(data))
        return data

    def __getattr__(self, name):
        return getattr(self._fileobj, name)

    def __del__(self):
        self._update(0)


class TarFile(tarfile.TarFile):
    fileobject = ProgressExFileObject

    def __init__(
        self,
        name=None,
        mode="r",
        fileobj=None,
        format=None,
        tarinfo=None,
        dereference=None,
        ignore_zeros=None,
        encoding=None,
        errors="surrogateescape",
        pax_headers=None,
        debug=None,
        errorlevel=None,
        copybufsize=None,
    ):
        if "r" in mode:
            fileobj = ProgressFileIO(name)
        super(TarFile, self).__init__(
            name=name,
            mode=mode,
            fileobj=fileobj,
            format=format,
            tarinfo=tarinfo,
            dereference=dereference,
            ignore_zeros=ignore_zeros,
            encoding=encoding,
            errors=errors,
            pax_headers=pax_headers,
            debug=debug,
            errorlevel=errorlevel,
            copybufsize=copybufsize,
        )

    def addfile(self, tarinfo, fileobj=None):
        if fileobj is not None:
            fileobj = FileWrapper(fileobj, tarinfo.size)
        result = super(TarFile, self).addfile(tarinfo, fileobj)
        return result


open = TarFile.open
