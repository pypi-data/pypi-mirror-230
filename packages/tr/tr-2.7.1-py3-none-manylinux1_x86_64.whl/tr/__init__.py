# coding: utf-8
import ctypes
import numpy as np
from pathlib import Path
import platform
try: from . import conlib
except: import conlib

_dll_map = {"Linux":"libtr.so", "Windows": "libtr.dll", "Darwin": None}
_libc = ctypes.cdll.LoadLibrary(str(Path(__file__).parent.joinpath(_dll_map.get(platform.system())).resolve()))
assert _libc is not None

SHAPE_T = ctypes.c_int*8
class CTENSOR(ctypes.Structure):
    _fields_ = [
        ("buffer", ctypes.c_void_p),
        ("shape", SHAPE_T),
        ("ndim", ctypes.c_int),
        ("kind", ctypes.c_int),
        ("itemsize", ctypes.c_int),
        ("alloc", ctypes.c_int),
    ]

_libc.ctensor_free.argtypes = (
    ctypes.POINTER(CTENSOR),
)

_libc.crnn_init.argtypes = (
    ctypes.POINTER(ctypes.c_char),
)
_libc.crnn_init.restype = ctypes.c_void_p

_libc.crnn_release.argtypes = (
    ctypes.c_void_p,
)
_libc.crnn_release.restype = ctypes.c_int

_libc.crnn_run.argtypes = (
    ctypes.c_void_p,
    ctypes.POINTER(CTENSOR),
    ctypes.POINTER(CTENSOR),

)
_libc.crnn_run.restype = ctypes.c_int

def ndarray2ctensor(*args):
    t = (CTENSOR*len(args))()
    for i, arr in enumerate(args):
        assert arr.flags['C_CONTIGUOUS']
        t[i].buffer = ctypes.cast(np.ctypeslib.as_ctypes(arr), ctypes.c_void_p)
        t[i].kind = int(ord(arr.dtype.kind))
        t[i].itemsize = int(arr.dtype.itemsize)
        t[i].alloc = 0
        t[i].ndim = arr.ndim
        t[i].shape = SHAPE_T(*arr.shape)  
    return t

def str2ctensor(s):
    t = (CTENSOR*1)()
    i = 0
    s = s.encode()
    t[i].buffer = ctypes.cast(ctypes.create_string_buffer(s), ctypes.c_void_p) 
    t[i].kind = int(ord('u'))
    t[i].itemsize = 1
    t[i].alloc = 0
    t[i].ndim = 1
    t[i].shape = SHAPE_T(len(s)+1)
    return t  

def ctensor2ndarray(t, deepcopy=False):
    if t.ndim <= 0: return None
    if t.kind == ord('u') and t.itemsize == 1:
        buffer = ctypes.cast(t.buffer, ctypes.POINTER(ctypes.c_uint8))
    elif t.kind == ord('i') and t.itemsize == 4:
        buffer = ctypes.cast(t.buffer, ctypes.POINTER(ctypes.c_int32))
    elif t.kind == ord('i') and t.itemsize == 8:
        buffer = ctypes.cast(t.buffer, ctypes.POINTER(ctypes.c_int64))
    elif t.kind == ord('f') and t.itemsize == 4:
        buffer = ctypes.cast(t.buffer, ctypes.POINTER(ctypes.c_float))
    else:
        print(chr(t.kind), t.itemsize, t.kind == ord('i') and t.itemsize == 4)
        raise NotImplementedError(f"{chr(t.kind)} {t.itemsize} {t.kind == ord('i') and t.itemsize == 4}")
    shape = []
    for _ in range(t.ndim):
        shape.append(t.shape[_])
    arr = np.ctypeslib.as_array(buffer, shape=shape)    
    if deepcopy: return arr.copy()
    return arr


class CRNN(object):
    def __init__(self, **kwargs) -> None:
        
        cfg = dict(
            model_path=kwargs.get("model_path", str(Path(__file__).parent.joinpath("crnn.bin"))),
        )

        self._model = _libc.crnn_init(conlib.dumps(cfg).encode("utf-8"))   
        self.char_table = Path(kwargs.get("char_table", Path(__file__).parent.joinpath("char_table.txt"))).read_text(encoding='utf-8')
        
    def __del__(self):
        _libc.crnn_release(self._model)

    def run(self, img):
        if isinstance(img, (str, Path)): pt = str2ctensor(str(img))
        elif isinstance(img, np.ndarray): pt = ndarray2ctensor(img)
        else: raise NotImplementedError()

        _outputs = (CTENSOR * 2)()

        _libc.crnn_run(self._model, pt, _outputs)
        outputs = []
        for _ in range(2):
            outputs.append(ctensor2ndarray(_outputs[_], deepcopy=False))

        chars = []
        scores = []
        numbers = []
        pre_idx = None
        for i in range(outputs[0].shape[1]):
            val = float(outputs[0][0][i])
            idx = round(outputs[1][0][i])
            if idx <= 0: 
                pre_idx = idx
                continue

            if idx != pre_idx:
                chars.append(self.char_table[idx-1])
                scores.append(val)
                numbers.append(1)
                pre_idx = idx
            else:
                scores[-1] += val
                numbers[-1] += 1

        for i in range(len(scores)):
            scores[i] /= numbers[i]

        _libc.ctensor_free(_outputs[0])
        _libc.ctensor_free(_outputs[1])

        return chars, scores


if __name__ == "__main__":  
    pass