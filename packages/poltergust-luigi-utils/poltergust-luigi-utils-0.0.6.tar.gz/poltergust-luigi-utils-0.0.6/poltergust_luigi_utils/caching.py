import os.path
import contextlib
import luigi.contrib.opener
import shutil

cachedir = os.path.expanduser(os.environ.get("POLTERGUST_CACHE", "~/.cache/poltergust-luigi-utils"))

def local_cache_path_from_url(url):
    return os.path.join(cachedir, url.replace("://", "/")).replace("//", "/")

class CachingOpenerTarget():
    def __init__(self, url, **kw):
        self.target = luigi.contrib.opener.OpenerTarget(url, **kw)
        cachekw = {}
        if "format" in kw:
            cachekw["format"] = kw["format"]
        self.cachetarget = luigi.contrib.opener.OpenerTarget(local_cache_path_from_url(url), **cachekw)

    def ensure(self):
        if not self.cachetarget.exists():
            with self.target.open() as fr:
                with self.cachetarget.open("w") as fw:
                    shutil.copyfileobj(fr, fw)
                    
    @contextlib.contextmanager
    def open(self, mode="r"):
        if mode == "r":
            self.ensure()
            with self.cachetarget.open("r") as f:
                yield f
        elif mode == "w":
            with self.cachetarget.open("w") as f:
                yield f
            with self.cachetarget.open("r") as fr:
                with self.target.open("w") as fw:
                    shutil.copyfileobj(fr, fw)

    def exists(self):
        if self.cachetarget.exists(): return True
        if self.target.exists(): return True
        return False
    
    def __getattr__(self, name):
        return getattr(self.target, name)

    def __enter__(self):
        self.ensure()
        if hasattr(self.cachetarget, "url"):
            return self.cachetarget.url
        return self.cachetarget.path
        
    def __exit__(self):
        pass
        # For now, we don't bother deleting, this is a NOP with a
        # future possibility of cleanup :)
