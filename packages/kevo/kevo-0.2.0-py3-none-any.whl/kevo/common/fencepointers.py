from sys import getsizeof
import struct

from sortedcontainers import SortedDict


class FencePointers:
    def __init__(self, density_factor=20, from_str: str | None = None):
        self.pointers = SortedDict()

        self.density_factor = density_factor
        self.counter = 0
        self.incr = 0

    def add(self, key: bytes, offset: int):
        if self.incr % self.density_factor == 0:
            self.pointers[key] = offset
            self.counter += 1

        self.incr += 1

    def bisect(self, key: bytes):
        return self.pointers.bisect(key)
    
    def peekitem(self, idx):
        return self.pointers.peekitem(idx)

    def to_file_as_blob(self, fd, enc_len):
        fd.write(struct.pack('<QQ', self.density_factor, self.counter))
        for k, v in self.pointers.items():
            fd.write(len(k).to_bytes(enc_len, byteorder='little'))
            fd.write(k)
            fd.write(v.to_bytes(8, byteorder='little'))

    def _read_kv_pair(self, fd, enc_len):
        key_len = int.from_bytes(fd.read(enc_len), byteorder='little')
        key = fd.read(key_len)
        value = int.from_bytes(fd.read(8), byteorder='little')
        self.pointers[key] = value

    def from_file_descriptor(self, fd, enc_len):
        metadata = fd.read(16)
        self.density_factor, self.counter = struct.unpack('<QQ', metadata)
        cnt = self.counter
        while cnt > 0:
            self._read_kv_pair(fd, enc_len)
            cnt -= 1

    def __len__(self):
        return self.incr

    def __sizeof__(self):
        return sum((getsizeof(k) + getsizeof(v) for k, v in self.pointers.items()))
