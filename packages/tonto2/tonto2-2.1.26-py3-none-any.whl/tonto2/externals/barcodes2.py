#!/usr/bin/python3

# barcodes2.py
# ccr . 2023 Jul 30

# ==================================================boilerplate»=====
# Copyright 2006—2023 by Chuck Rhode.
# 
# See LICENSE.txt for your rights.
# =================================================«boilerplate======

"""Generate *.html that renders barcodes in various formats.

Verify or generate check digits.

This module obsoletes an earlier module, bar_code.py, from 2010, which
was not widely used.  This is a refactoring.  It is not backward
compatible.  Calling sequences have changed.  This new module,
barcodes2.py is used in Tonto2.  Scripts that import the older
bar_code, will need to be updated.

This module uses fonts from:

+ Fister, Lasse. "Libre Barcode Project."  30 Jul
  2023. <https://graphicore.github.io/librebarcode/>.

Whereas we used to have to sequence barcodes into alternating glyphs
for even and odd parity, nowadays, the TrueType fonts for the
commercial barcodes UPCA and EAN13 handle this internally.  The font
decides how to render adjoining characters using an OpenType feature
called *calt* (contextual alternatives).  Most modern rendering
engines use this, but, for workarounds in those that don't, see:

+ Fister, Lasse. "EAN13." _Libre Barcode Project_. 30 Jul 2023.
  <https://graphicore.github.io/librebarcode/documentation/ean13.html>.

This has the advantage that the UPCA and EAN13 coded string appears
intact within the markup document and will be found when searched for.

Code39 and Code39X do not require a check digit.  

The check digit for Code128 is calculated by this module, which also
tries to optimize the width of the barcode by shifting to a half-byte
representation of even strings of digits like the old IBM COBOL
COMP-3.

Be aware that the Libre fonts for Code39, Code39X, and Code128 are
weirdly considered symbol fonts.  As such, they are not rendered by
the Mozilla browsers such as Firefox, which insist that symbols be
Unicode encoded in order not to depend on locally installed fonts.
The best that can be done is to use a rendering engine such as Qt,
LibreOffice, or Gimp to show these fonts.  Then extract an image from
a screen shot that can be seen by generic browsers on foreign
machines.  Using PIL or perhaps Imagemagick to gin an image directly
from a barcode font may be worth a try.

Or insert this into your Web page:

<head>
  <link 
    rel="stylesheet"
    href="https://fonts.googleapis.com/css?family=Libre+Barcode+EAN13+Text"
    >
  <link 
    rel="stylesheet" 
    href="https://fonts.googleapis.com/css?family=Libre+Barcode+39+Text"
    >
  <link 
    rel="stylesheet" 
    href="https://fonts.googleapis.com/css?family=Libre+Barcode+39+Extended+Text"
    >
  <link 
    rel="stylesheet" 
    href="https://fonts.googleapis.com/css?family=Libre+Barcode+128+Text"
    >
</head>

"""

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

FONT_PTS = 72

class BarcodeError(Exception):

    """Base class for the errors thrown by this module.

    """
    
    def __init__(self, msg):
        self.msg = msg
        return 

    def __str__(self):
        return self.msg


class BarcodeLengthError(BarcodeError):

    """Text length error.

    """
    
    def __init__(self):
        BarcodeError.__init__(self, msg='Wrong length.')
        return

    
class BarcodeNonNumericError(BarcodeError):

    """Non-numeric text error.

    """
    
    def __init__(self):
        BarcodeError.__init__(self, msg='Non-numeric.')
        return

    
class BarcodeCheckDigitError(BarcodeError):

    """Bad check-digit error

    """
    
    def __init__(self):
        BarcodeError.__init__(self, msg='Bad check digit.')
        return

    
class Barcode39EncodingError(BarcodeError):

    """Invalid code 3 of 9 character.

    """
    
    def __init__(self):
        BarcodeError.__init__(self, msg='Bad Code39 encoding.')
        return

    
class Barcode128EncodingError(BarcodeError):

    """Invalid code 128 character.

    """
    
    def __init__(self):
        BarcodeError.__init__(self, msg='Bad Code128 encoding.')
        return

    
class Barcode():

    """Base class for barcode classes.

    The principal method used in this class and its descendents is
    *set_and_audit*.
    
    >>> str(Barcode().set_txt('085227607423'))
    '085227607423'
    >>> Barcode().set_txt('085227607423').get_markup()
    '<font >085227607423</font>'
    >>> Barcode().set_txt('085227607423').get_markup(size=24)
    '<font size="24">085227607423</font>'

    """

    size = 12
    font_face = None
    font_size = None

    def __init__(self):
        self.txt = None
        return

    def set_txt(self, txt):
        self.txt = txt
        return self

    def get_txt(self):
        return self.txt

    def __str__(self):
        return self.get_txt()

    def set_check_digit(self, check_digit):
        self.txt = self.txt[:-1] + check_digit
        return self

    def get_check_digit(self):
        return self.txt[-1]

    def has_check_digit(self):
        return self.get_check_digit() != '?'

    def calc_check_digit(self):
        return '?'

    def is_correct_check_digit(self):
        return self.get_check_digit() == self.calc_check_digit()

    def get_markup(self, **attrs):
        if self.font_face:
            attrs.setdefault('font-family', f"'{self.font_face}'")
        if self.font_size:
            attrs.setdefault('font-size', f'{self.font_size}pt')
        parms = [f"{key}: {value}" for (key, value) in attrs.items()]
        result = []
        result.append('<span style="')
        result.append('; '.join(parms))
        result.append('">')
        result.append(self.get_txt().replace('<', '&lt;').replace('>', '&gt;'))
        result.append('</span>')
        result = NULL.join(result)
        return result

    def audit(self):
        raise NotImplementedError

    def set_and_audit(self, txt):
        self.set_txt(txt)
        self.audit()
        return self


class BarcodeParity(Barcode):

    """Base class for the UPC and EAN barcode classes.

    >>> str(BarcodeParity().set_int('085227607423'))
    '085227607423'
    >>> str(BarcodeParity().set_int('85227607423'))
    '085227607423'
    >>> str(BarcodeParity().set_int(85227607423))
    '085227607423'

    """

    def set_int(self, x):
        self.txt = f'{int(x):0{self.size}n}'
        return self

    def is_correct_size(self):
        return len(self.txt) == self.size

    def audit(self):
        if self.is_correct_size():
            pass
        else:
            raise BarcodeLengthError
        if self.has_check_digit():
            if self.is_correct_check_digit():
                pass
            else:
                raise BarcodeCheckDigitError
        else:
            self.set_check_digit(self.calc_check_digit())
        return self

    def calc_check_digit(self):
        return '?'


class BarcodeUPCA(BarcodeParity):

    """UPC barcode.

    >>> str(BarcodeUPCA().set_and_audit('085227607423'))
    '085227607423'
    >>> str(BarcodeUPCA().set_and_audit('08522760742?'))
    '085227607423'
    >>> BarcodeUPCA().set_and_audit('08522760742?').get_markup()
    '<font face="Libre Barcode EAN13 Text" size="48pt">085227607423</font>'

    """

    font_face = 'Libre Barcode EAN13 Text'
    font_size = FONT_PTS

    def calc_check_digit(self):
        try:
            collection = [int(c) for c in self.get_txt()[:-1]]
        except ValueError:
            collection = None
        if collection:
            pass
        else:
            raise BarcodeNonNumericError
        odds = []
        evens = []
        if self.size in [13]:
            if collection:
                evens.append(collection.pop(ZERO))
        while True:
            if collection:
                odds.append(collection.pop(ZERO))
            else:
                break
            if collection:
                evens.append(collection.pop(ZERO))
            else:
                break
        result = 10 - ((sum(odds) * 3 + sum(evens)) % 10)
        return str(result)[-1:]


class BarcodeEAN13(BarcodeUPCA):

    """EAN barcode.

    >>> str(BarcodeEAN13().set_and_audit('9780451181688'))
    '9780451181688'
    >>> str(BarcodeEAN13().set_and_audit('978045118168?'))
    '9780451181688'
    >>> BarcodeEAN13().set_and_audit('978045118168?').get_markup()
    '<font face="Libre Barcode EAN13 Text" size="48pt">9780451181688</font>'

    """

    size = 13
    font_face = 'Libre Barcode EAN13 Text'
    font_size = FONT_PTS


class Barcode39(Barcode):

    """Code 3 of 9 barcode.

    >>> Barcode39().set_and_audit('HOW NOW.').get_markup()
    '<font face="Libre Barcode 39 Text" size="24pt">*HOW NOW.*</font>'

    """
    
    font_face = 'Libre Barcode 39 Text'
    font_size = FONT_PTS // 2

    def audit(self):
        for c in self.txt:
            if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.$/+% ':
                pass
            else:
                raise Barcode39EncodingError
        return self

    def calc_check_digit(self):
        raise NotImplementedError
    
    def get_markup(self, **attrs):
        if self.font_face:
            attrs.setdefault('font-family', f"'{self.font_face}'")
        if self.font_size:
            attrs.setdefault('font-size', f'{self.font_size}pt')
        parms = [f"{key}: {value}" for (key, value) in attrs.items()]
        result = []
        result.append('<span style="')
        result.append('; '.join(parms))
        result.append('">')
        result.append('*')
        result.append(self.get_txt().replace('<', '&lt;').replace('>', '&gt;'))
        result.append('*')
        result.append('</span>')
        result = NULL.join(result)
        return result


class Barcode39X(Barcode39):

    """Code 3 of 9 extended barcode.

    >>> Barcode39X().set_and_audit('How now?').get_markup()
    '<font face="Libre Barcode 39 Extended Text" size="24pt">*How now?*</font>'

    """
    
    font_face = 'Libre Barcode 39 Extended Text'
    font_size = 24

    def audit(self):
        if self.txt.isascii():
            pass
        else:
            raise Barcode39EncodingError
        return self


CODE128_SET = {
      0: [SPACE, SPACE, 'Â'],
      1: ['!', '!', '!'],
      2: ['"', '"', '"'],
      3: ['#', '#', '#'],
      4: ['$', '$', '$'],
      5: ['%', '%', '%'],
      6: ['&', '&', '&'],
      7: ["'", "'", "'"],
      8: ['(', '(', '('],
      9: [')', ')', ')'],
     10: ['*', '*', '*'],
     11: ['+', '+', '+'],
     12: [',', ',', ','],
     13: ['-', '-', '-'],
     14: ['.', '.', '.'],
     15: ['/', '/', '/'],
     16: ['0', '0', '0'],
     17: ['1', '1', '1'],
     18: ['2', '2', '2'],
     19: ['3', '3', '3'],
     20: ['4', '4', '4'],
     21: ['5', '5', '5'],
     22: ['6', '6', '6'],
     23: ['7', '7', '7'],
     24: ['8', '8', '8'],
     25: ['9', '9', '9'],
     26: [':', ':', ':'],
     27: [';', ';', ';'],
     28: ['<', '<', '<'],
     29: ['=', '=', '='],
     30: ['>', '>', '>'],
     31: ['?', '?', '?'],
     32: ['@', '@', '@'],
     33: ['A', 'A', 'A'],
     34: ['B', 'B', 'B'],
     35: ['C', 'C', 'C'],
     36: ['D', 'D', 'D'],
     37: ['E', 'E', 'E'],
     38: ['F', 'F', 'F'],
     39: ['G', 'G', 'G'],
     40: ['H', 'H', 'H'],
     41: ['I', 'I', 'I'],
     42: ['J', 'J', 'J'],
     43: ['K', 'K', 'K'],
     44: ['L', 'L', 'L'],
     45: ['M', 'M', 'M'],
     46: ['N', 'N', 'N'],
     47: ['O', 'O', 'O'],
     48: ['P', 'P', 'P'],
     49: ['Q', 'Q', 'Q'],
     50: ['R', 'R', 'R'],
     51: ['S', 'S', 'S'],
     52: ['T', 'T', 'T'],
     53: ['U', 'U', 'U'],
     54: ['V', 'V', 'V'],
     55: ['W', 'W', 'W'],
     56: ['X', 'X', 'X'],
     57: ['Y', 'Y', 'Y'],
     58: ['Z', 'Z', 'Z'],
     59: ['[', '[', '['],
     60: ['\\', '\\', '\\'],
     61: [']', ']', ']'],
     62: ['^', '^', '^'],
     63: ['_', '_', '_'],
     64: ['\x00', '`', '`'],
     65: ['\x01', 'a', 'a'],
     66: ['\x02', 'b', 'b'],
     67: ['\x03', 'c', 'c'], 
     68: ['\x04', 'd', 'd'],
     69: ['\x05', 'e', 'e'],
     70: ['\x06', 'f', 'f'],
     71: ['\x07', 'g', 'g'],
     72: ['\x08', 'h', 'h'],
     73: ['\x09', 'i', 'i'],
     74: ['\x0a', 'j', 'j'],
     75: ['\x0b', 'k', 'k'],
     76: ['\x0c', 'l', 'l'],
     77: ['\x0d', 'm', 'm'],
     78: ['\x0e', 'n', 'n'],
     79: ['\x0f', 'o', 'o'],
     80: ['\x10', 'p', 'p'],
     81: ['\x11', 'q', 'q'],
     82: ['\x12', 'r', 'r'],
     83: ['\x13', 's', 's'],
     84: ['\x14', 't', 't'],
     85: ['\x15', 'u', 'u'],
     86: ['\x16', 'v', 'v'],
     87: ['\x17', 'w', 'w'],
     88: ['\x18', 'x', 'x'],
     89: ['\x19', 'y', 'y'],
     90: ['\x1a', 'z', 'z'],
     91: ['\x1b', '{', '{'],
     92: ['\x1c', '|', '|'],
     93: ['\x1d', '}', '}'],
     94: ['\x1e', '~', '~'],
     95: ['\x1f', '\x7f', 'Ã'],
     96: [NULL, NULL, 'Ä'],
     97: [NULL, NULL, 'Å'],
     98: [NULL, NULL, 'Æ'],
     99: [NULL, NULL, 'Ç'],
    100: [NULL, NULL, 'È'],
    101: [NULL, NULL, 'É'],
    102: [NULL, NULL, 'Ê'],
    103: [NULL, NULL, 'Ë'],
    104: [NULL, NULL, 'Ì'],
    105: [NULL, NULL, 'Í'],
    106: [NULL, NULL, 'Î'],
    }
CODE128_IN_A = {}
CODE128_IN_B = {}
CODE128_OUT = {}
for (code_point, (code_point_a, code_point_b, code_point_font)) in CODE128_SET.items():
    CODE128_IN_A[code_point_a] = code_point
    CODE128_IN_B[code_point_b] = code_point
    CODE128_OUT[code_point] = code_point_font
CODE128_CODE = [101, 100, 99]
CODE128_SHIFT = 98
CODE128_START = [103, 104, 105]
CODE128_STOP = 106


class Barcode128(Barcode):

    """Code 128 barcode.

    >>> Barcode128().set_and_audit('Hello World!').get_markup()
    '<font face="Libre Barcode 128 Text" size="24pt">ÌHelloÂWorld!WÎ</font>'
    >>> Barcode128().set_and_audit('53081-2801').get_markup()
    '<font face="Libre Barcode 128 Text" size="24pt">ÍU(É1-Ç&lt;!eÎ</font>'
    >>> Barcode128().set_and_audit('43.761238 -87.704882').get_markup()
    '<font face="Libre Barcode 128 Text" size="24pt">Ë43.Çl,FÉÂ-87.ÇfPrXÎ</font>'

    """
    
    font_face = 'Libre Barcode 128 Text'
    font_size = FONT_PTS // 2

    def is_code_set(self, txt, code_set):
        for c in txt:
            if c in code_set:
                pass
            else:
                result = False
                break
        else:
            result = True
        return result

    def ini_code_set(self, txt):
        if self.is_code_set(txt[:4], '0123456789') and ((len(txt) == 2) or (len(txt) >=4)):
            result = ('C', CODE128_START[2])
        elif self.is_code_set(txt, CODE128_IN_A):
            result = ('A', CODE128_START[ZERO])
        else:
            result = ('B', CODE128_START[1])
#        print(f'txt:  {txt[:6]}..., result:  {result}')
        return result

    def chg_code_set(self, txt, code_set):

        if code_set == 'A':
            if self.is_code_set(txt, '0123456789') and (len(txt) >= 4) and ((len(txt) % 2) == ZERO):
                result = ('C', CODE128_CODE[2]) 
            elif self.is_code_set(txt[:6], '0123456789'):
                result = ('C', CODE128_CODE[2])
            elif self.is_code_set(txt[:1], CODE128_IN_A):
                result = ('A', None)
            elif self.is_code_set(txt[:2], CODE128_IN_B):
                result = ('B', CODE128_CODE[1])
            elif self.is_code_set(txt[:1], CODE128_IN_B):
                result = ('A', CODE128_SHIFT)
            else:
                raise NotImplementedError
        elif code_set == 'B':
            if self.is_code_set(txt, '0123456789') and (len(txt) >= 4) and ((len(txt) % 2) == ZERO):
                result = ('C', CODE128_CODE[2]) 
            elif self.is_code_set(txt[:6], '0123456789'):
                result = ('C', CODE128_CODE[2])
            elif self.is_code_set(txt[:1], CODE128_IN_B):
                result = ('B', None)
            elif self.is_code_set(txt[:2], CODE128_IN_A):
                result = ('A', CODE128_CODE[1])
            elif self.is_code_set(txt[:1], CODE128_IN_A):
                result = ('B', CODE128_SHIFT)
            else:
                raise NotImplementedError
        elif code_set == 'C':
            if self.is_code_set(txt[:2], '0123456789') and (len(txt) >=2):
                result = ('C', None)
            elif self.is_code_set(txt, CODE128_IN_A):
                result = ('A', CODE128_CODE[ZERO])
            else:
                result = ('B', CODE128_CODE[1])
        else:
            raise NotImplementedError
#        print(f'txt:  {txt[:6]}..., result:  {result}')
        return result
        
    def code_point_c(self, txt):
        result= int(txt.pop(ZERO)) * 10 + int(txt.pop(ZERO))
        return result

    def accumulate(self, code_point):
        code = CODE128_OUT[code_point]
        if self.collection:
            factor = len(self.collection)
        else:
            factor = 1
        self.collection.append(code)
        self.checksum += factor * code_point
        return self

    def set_txt(self, txt):
        txt = list(txt)
        self.collection = []
        self.checksum = ZERO
        (code_set, code_point) = self.ini_code_set(txt)
        self.accumulate(code_point)
        while txt:
            if code_set == 'A':
                code_point = CODE128_IN_A.get(txt.pop(ZERO))
            elif code_set == 'B':
                code_point = CODE128_IN_B.get(txt.pop(ZERO))
            elif code_set == 'C':
                code_point = self.code_point_c(txt)
            else:
                raise NotImplementedError
            if code_point is None:
                raise Barcode128EncodingError
            self.accumulate(code_point)
            if txt:
                (code_set, code_point) = self.chg_code_set(txt, code_set)
                if code_point:
                    self.accumulate(code_point)
        self.txt = NULL.join(self.collection)
        return self

    def calc_check_digit(self):
        remainder = self.checksum % 103
        result = CODE128_OUT[remainder]
        return result

    def audit(self):
        check_digit = self.calc_check_digit()
        self.txt += check_digit + CODE128_OUT[CODE128_STOP]
        return self


if __name__ == "__main__":

    """This code is run when this module is executed, not when it is included.

    Do doc tests.

    """
    
    import doctest
    doctest.testmod()


# Fin
