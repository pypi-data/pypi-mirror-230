import os.path
import unittest

from random import Random
from kevo.common import FencePointers
from tempfile import TemporaryFile


class TestFencePointers(unittest.TestCase):
    tmpfile = 'tmpfile'

    def tearDown(self):
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)

    def test_ser_der(self):
        rng = Random(1)

        fp1 = FencePointers()

        for i in range(1_000):
            randbytes = rng.randbytes(rng.randint(0, 100))
            randint = rng.randint(0, 10_000_000_000)
            fp1.add(randbytes, randint)

        with open(self.tmpfile, 'wb') as f:
            fp1.to_file_as_blob(f, 2)

        fp2 = FencePointers()
        with open(self.tmpfile, 'rb') as f:
            fp2.from_file_descriptor(f, 2)

        self.assertEqual(fp1.pointers, fp2.pointers)


if __name__ == "__main__":
    unittest.main()
