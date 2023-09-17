import struct


class BASICTokenSet(object):
    def __init__(self, tokens, codes):
        self.token_to_string = {t: s for s, t in tokens}
        self.string_to_token = {s: t for s, t in tokens}
        self.code_to_string = {c: s for s, c in codes}
        self.string_to_code = {s: c for s, c in codes}

    def expand(self, tokens):
        ret = ''
        in_str = False

        for b in tokens:
            if b == ord('"'):
                # invert quote flag
                in_str = not in_str
                ret += chr(b)
            else:
                if in_str:
                    if b in self.code_to_string:
                        ret += self.code_to_string[b]
                    else:
                        ret += chr(b)
                elif b in self.token_to_string:
                    # expand token to string
                    ret += self.token_to_string[b]
                else:
                    ret += chr(b)

        return ret


_bASICv2Tokens = (
    ("END", 0x80),
    ("FOR", 0x81),
    ("NEXT", 0x82),
    ("DATA", 0x83),
    ("INPUT#", 0x84),
    ("INPUT", 0x85),
    ("DIM", 0x86),
    ("READ", 0x87),
    ("LET", 0x88),
    ("GOTO", 0x89),
    ("RUN", 0x8A),
    ("IF", 0x8B),
    ("RESTORE", 0x8C),
    ("GOSUB", 0x8D),
    ("RETURN", 0x8E),
    ("REM", 0x8F),
    ("STOP", 0x90),
    ("ON", 0x91),
    ("WAIT", 0x92),
    ("LOAD", 0x93),
    ("SAVE", 0x94),
    ("VERIFY", 0x95),
    ("DEF", 0x96),
    ("POKE", 0x97),
    ("PRINT#", 0x98),
    ("PRINT", 0x99),
    ("CONT", 0x9A),
    ("LIST", 0x9B),
    ("CLR", 0x9C),
    ("CMD", 0x9D),
    ("SYS", 0x9E),
    ("OPEN", 0x9F),
    ("CLOSE", 0xA0),
    ("GET", 0xA1),
    ("NEW", 0xA2),
    ("TAB(", 0xA3),
    ("TO", 0xA4),
    ("FN", 0xA5),
    ("SPC(", 0xA6),
    ("THEN", 0xA7),
    ("NOT", 0xA8),
    ("STEP", 0xA9),
    ("+", 0xAA),
    ("-", 0xAB),
    ("*", 0xAC),
    ("/", 0xAD),
    ("^", 0xAE),
    ("AND", 0xAF),
    ("OR", 0xB0),
    (">", 0xB1),
    ("=", 0xB2),
    ("<", 0xB3),
    ("SGN", 0xB4),
    ("INT", 0xB5),
    ("ABS", 0xB6),
    ("USR", 0xB7),
    ("FRE", 0xB8),
    ("POS", 0xB9),
    ("SQR", 0xBA),
    ("RND", 0xBB),
    ("LOG", 0xBC),
    ("EXP", 0xBD),
    ("COS", 0xBE),
    ("SIN", 0xBF),
    ("TAN", 0xC0),
    ("ATN", 0xC1),
    ("PEEK", 0xC2),
    ("LEN", 0xC3),
    ("STR$", 0xC4),
    ("VAL", 0xC5),
    ("ASC", 0xC6),
    ("CHRS", 0xC7),
    ("LEFT$", 0xC8),
    ("RIGHT$", 0xC9),
    ("MID$", 0xCA),
    ("GO", 0xCB),
    ("~", 0xFF)  # PI
    )

_bASICv2ScreenCodes = (
    ("{stop}", 0x03),
    ("{wht}", 0x05),
    ("{dish}", 0x08),
    ("{ensh}", 0x09),
    ("{lcas}", 0x0E),
    ("{down}", 0x11),
    ("{rvon}", 0x12),
    ("{home}", 0x13),
    ("{del}", 0x14),
    ("{red}", 0x1C),
    ("{rght}", 0x1D),
    ("{grn}", 0x1E),
    ("{blu}", 0x1F),
    ("{orng}", 0x81),
    ("{f1}", 0x85),
    ("{f3}", 0x86),
    ("{f5}", 0x87),
    ("{f7}", 0x88),
    ("{f2}", 0x89),
    ("{f4}", 0x8A),
    ("{f6}", 0x8B),
    ("{f8}", 0x8C),
    ("{sret}", 0x8D),
    ("{ucas}", 0x8E),
    ("{blk}", 0x90),
    ("{up}", 0x91),
    ("{rvof}", 0x92),
    ("{clr}", 0x93),
    ("{ins}", 0x94),
    ("{brn}", 0x95),
    ("{lred}", 0x96),
    ("{gry1}", 0x97),
    ("{gry2}", 0x98),
    ("{lgrn}", 0x99),
    ("{lblu}", 0x9A),
    ("{gry3}", 0x9B),
    ("{pur}", 0x9C),
    ("{left}", 0x9D),
    ("{yel}", 0x9E),
    ("{cyn}", 0x9F),
)

bASICv2TokenSet = BASICTokenSet(_bASICv2Tokens, _bASICv2ScreenCodes)


class BASICFile(object):
    def __init__(self, fileh, start_addr):
        self.start_addr = start_addr
        self.lines = {}
        self.length = 0

        while True:
            link, = struct.unpack('<H', fileh.read(2))
            self.length += 2

            if link == 0:
                # NUL follows
                self.length += 1
                break

            line_no, = struct.unpack('<H', fileh.read(2))
            self.length += 2

            tokens = b''
            while True:
                b = fileh.read(1)
                self.length += 1
                if b == b'\x00':
                    break
                else:
                    tokens += b

            self.lines[line_no] = tokens

    def dump(self):
        for line_no in sorted(self.lines.keys()):
            yield (line_no, self.lines[line_no])

    def list(self, start=None, end=None):
        for line_no in sorted(self.lines.keys()):
            if end is not None and line_no > end:
                break
            if start is None or line_no >= start:
                line = "{} {}".format(line_no, bASICv2TokenSet.expand(self.lines[line_no]))
                yield line
