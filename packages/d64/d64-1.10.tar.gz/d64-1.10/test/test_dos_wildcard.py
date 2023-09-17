import unittest

from d64 import DOSPath


class TestWildcards(unittest.TestCase):

    def test_wildcards_plain(self):
        self.assertTrue(DOSPath.wildcard_match(b'EXACT', 'PRG', b'EXACT'))
        self.assertFalse(DOSPath.wildcard_match(b'EXYCT', 'PRG', b'EXACT'))
        self.assertFalse(DOSPath.wildcard_match(b'EXACTLY', 'PRG', b'EXACT'))
        self.assertFalse(DOSPath.wildcard_match(b'EXA', 'PRG', b'EXACT'))

    def test_wildcards_single(self):
        self.assertTrue(DOSPath.wildcard_match(b'SINGLE', 'PRG', b'SINGL?'))
        self.assertTrue(DOSPath.wildcard_match(b'SINGLE', 'PRG', b'?INGLE'))
        self.assertFalse(DOSPath.wildcard_match(b'SINGLE', 'PRG', b'SINGLE?'))

    def test_wildcards_multi(self):
        self.assertTrue(DOSPath.wildcard_match(b'MULTIPLE', 'PRG', b'MULTIPLE*'))
        self.assertTrue(DOSPath.wildcard_match(b'MULTIPLE', 'PRG', b'MULTIPL*'))
        self.assertTrue(DOSPath.wildcard_match(b'MULTIPLE', 'PRG', b'MULTIP*'))
        self.assertTrue(DOSPath.wildcard_match(b'MULTIPLE', 'PRG', b'*'))

    def test_wildcards_type(self):
        self.assertTrue(DOSPath.wildcard_match(b'TYPE', 'PRG', b'*=PRG'))
        self.assertTrue(DOSPath.wildcard_match(b'TYPE', 'PRG', b'*=P'))
        self.assertFalse(DOSPath.wildcard_match(b'TYPE', 'PRG', b'*=S'))

    def test_wildcards_mixed(self):
        self.assertTrue(DOSPath.wildcard_match(b'TYPE', 'PRG', b'TYPE=PRG'))
        self.assertFalse(DOSPath.wildcard_match(b'TYPER', 'PRG', b'TYPE=PRG'))
        self.assertFalse(DOSPath.wildcard_match(b'TYPE', 'PRG', b'TYPE=SEQ'))
        self.assertTrue(DOSPath.wildcard_match(b'TYPE', 'PRG', b'TYPE*=PRG'))
        self.assertFalse(DOSPath.wildcard_match(b'TYPE', 'PRG', b'TYPE*=SEQ'))

    def test_wildcards_bad(self):
        with self.assertRaises(ValueError):
            DOSPath.wildcard_match(b'EXACT', 'PRG', b'EXACT=')


if __name__ == '__main__':
    unittest.main()
