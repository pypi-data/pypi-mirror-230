import os
from os.path import join as fjoin


def find_src_root(rpath, checks):
    if checks is None or not isinstance(checks, list) or len(checks) == 0:
        return None

    import os
    from os.path import join as fjoin

    _r = rpath if rpath is not None else os.getcwd()
    _r = os.path.abspath(_r)
    spt = _r.split(os.sep)

    def is_root(parr):
        if len(parr) > 0:
            _rpath = os.path.sep.join(parr)
            for check in checks:
                if not os.path.exists(fjoin(_rpath,check)):
                    return False

        return True

    while not is_root(spt):
        spt.pop()
    ret = os.path.sep.join(spt) if len(spt) > 0 else None
    return ret
