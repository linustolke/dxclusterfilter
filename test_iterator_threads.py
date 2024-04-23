import iterator_threads

import itertools
import unittest

class Tests(unittest.TestCase):
    def test_simple(self):
        for x in iterator_threads.chain(range(1)):
            self.assertEqual(0, x)

    def test_simple2(self):
        for x, y in itertools.zip_longest(iterator_threads.chain(range(3)), range(3)):
            self.assertEqual(x, y)

    def test_double(self):
        for x, y in itertools.zip_longest(iterator_threads.chain(range(1), range(1)), [0, 0]):
            self.assertEqual(x, y)

if __name__ == "__main__":
    unittest.main()
