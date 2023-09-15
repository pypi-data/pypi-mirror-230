"""Math from Nums"""
from .Number4 import (Num, 
                      ComplexNum, 
                      RealNum, ImagNum, 
                      RationalNum, 
                      IntegralNum, Digit, Sign,
                      NaturalNum, CountIndex,
                      num, built)
from typing import Iterable, Callable, Tuple, Mapping
import math
import cmath


__all__ = ["e", "pi", "tau", "inf", "infj", "nan", "nanj", 
           "acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh", 
           "cos",  "cosh",  "sin",  "sinh",  "tan",           "tanh", 
           "ceil", "floor", "comb", "copysign", 
           "degrees", "radians", 
           "dist", 
           "erf", "erfc", 
           "exp", "exp2", "expm1", 
           "factorial", "frexp", 
           "gamma", "lgamma", 
           "gcd", "hypot", 
           "isclose", "isinf", "isfinite", "isnan", 
           "isqrt", "sqrt", 
           "lcm", "ldexp", 
           "log", "log1p", "log2", "log10", 
           "modf", "nextafter", "perm", "prod", 
           "remainder", "trunc", "ulp", 
           "abs", "bin", "chr", "hex", "oct", "ord", "pow", 
           "isprime", "factors", "factorization"]


e: RealNum = RealNum(math.e)
pi: RealNum = RealNum(math.pi)
tau: RealNum = pi*2 # type: ignore
inf: RealNum = RealNum(math.inf)
infj: ImagNum = ImagNum(cmath.infj.imag)
nan: RealNum = RealNum(math.nan)
nanj: ImagNum = ImagNum(cmath.nanj.imag)

_babs = abs
_bpow = pow
_bbin = bin
_bhex = hex
_boct = oct
_bord = ord
_bchr = chr


def _doc(f: Callable) -> Callable:
    n: str = f.__name__
    d: str = getattr(math, n).__doc__
    f.__doc__ = d
    return f


@_doc
def acos(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.acos(_b)
    else:
        res = math.acos(_b)
    return num(res)

@_doc
def acosh(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.acosh(_b)
    else:
        res = math.acosh(_b)
    return num(res)

@_doc
def asin(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.asin(_b)
    else:
        res = math.asin(_b)
    return num(res)
  
@_doc
def asinh(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.asinh(_b)
    else:
        res = math.asinh(_b)
    return num(res)

@_doc  
def atan(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.atan(_b)
    else:
        res = math.atan(_b)
    return num(res)
    
@_doc
def atan2(__y: Num, __x: Num) -> Num:
    _bx = built(__x)
    _by = built(__y)
    if isinstance(_bx, complex) or isinstance(_by, complex):
        raise TypeError(f"Type Not Allow: ({__y}, {__x})")
    else:
        res = math.atan2(_by, _bx)
    return num(res)

@_doc
def atanh(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.atanh(_b)
    else:
        res = math.atanh(_b)
    return num(res)

@_doc
def sin(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.sin(_b)
    else:
        res = math.sin(_b)
    return num(res)

@_doc
def sinh(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.atanh(_b)
    else:
        res = math.atanh(_b)
    return num(res)

@_doc
def cos(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.cos(_b)
    else:
        res = math.cos(_b)
    return num(res)

@_doc
def cosh(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.cosh(_b)
    else:
        res = math.cosh(_b)
    return num(res)

@_doc
def tan(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.tan(_b)
    else:
        res = math.tan(_b)
    return num(res)

@_doc
def tanh(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.tanh(_b)
    else:
        res = math.tanh(_b)
    return num(res)


@_doc
def ceil(_n: RealNum) -> IntegralNum:
    return IntegralNum(_n.__ceil__())

@_doc
def floor(_n: RealNum) -> IntegralNum:
    return IntegralNum(_n.__floor__())


@_doc
def comb(_n: IntegralNum, _k: IntegralNum) -> IntegralNum:
    _bn = int(_n)
    _bk = int(_k)
    res = math.comb(_bn, _bk) # type: ignore
    return IntegralNum(res)


@_doc
def copysign(__x: RealNum, __y: RealNum) -> RealNum:
    _bx = built(__x)
    _by = built(__y)
    res = math.copysign(_bx, _by) # type: ignore
    return num(res) # type: ignore


@_doc
def degrees(_n: RealNum) -> RealNum:
    _b = built(_n)
    res = math.degrees(_b) # type: ignore
    return num(res) # type: ignore

@_doc
def radians(_n: RealNum) -> RealNum: 
    _b = built(_n)
    res = math.radians(_b) # type: ignore
    return num(res) # type: ignore


@_doc
def dist(__p: Iterable[RealNum], __q: Iterable[RealNum]) -> RealNum:
    _bp = [built(n) for n in __p]
    _bq = [built(n) for n in __q]
    res = math.dist(_bp, _bq) # type: ignore
    return num(res) # type: ignore


@_doc
def erf(_n: RealNum) -> RealNum:
    _b = built(_n)
    res = math.erf(_b) # type: ignore
    return res # type: ignore

@_doc
def erfc(_n: RealNum) -> RealNum:
    _b = built(_n)
    res = math.erfc(_b) # type: ignore
    return res # type: ignore


@_doc
def exp(_n: Num) -> Num:
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.exp(_b)
    else:
        res = math.exp(_b)
    return num(res)

@_doc
def exp2(_n: RealNum) -> RealNum:
    _b = built(_n)
    res = math.exp(_b) # type: ignore
    return num(res) # type: ignore

@_doc
def expm1(_n: RealNum) -> RealNum:
    _b = built(_n)
    res = math.expm1(_b) # type: ignore
    return num(res) # type: ignore


@_doc
def factorial(_n: IntegralNum) -> IntegralNum:
    _b = built(_n)
    res = math.factorial(_b) # type: ignore
    return num(res) # type: ignore


@_doc
def frexp(_n: RealNum) -> Tuple[RealNum, IntegralNum]:
    _b = built(_n)
    res = math.frexp(_b) # type: ignore
    return num(res) # type: ignore


@_doc
def gamma(_n: RealNum) -> RealNum:
    _b = built(_n)
    res = math.gamma(_b) # type: ignore
    return num(res) # type: ignore

@_doc
def lgamma(_n: RealNum) -> RealNum: 
    _b = built(_n)
    res = math.lgamma(_b) # type: ignore
    return num(res) # type: ignore


@_doc
def gcd(*integers: IntegralNum) -> IntegralNum:
    _b = [built(x) for x in integers]
    res = math.gcd(*_b) # type: ignore
    return num(res) # type: ignore


@_doc
def hypot(*coordinates: RealNum) -> RealNum:
    _b = [built(x) for x in coordinates]
    res = math.gcd(*_b) # type: ignore
    return num(res) # type: ignore


@_doc
def isclose(a: Num, b: Num, *, rel_tol: RealNum = RationalNum(1, 10**9), abs_tol: RealNum = RationalNum(0)) -> bool:
    ba = built(a)
    bb = built(b)
    brel_tol = built(rel_tol)
    babs_tol = built(abs_tol)
    if isinstance(ba, complex) or isinstance(bb, complex):
        res = cmath.isclose(ba, bb, rel_tol=brel_tol, abs_tol=babs_tol) # type: ignore
    else:
        res = math.isclose(ba, bb, rel_tol=brel_tol, abs_tol=babs_tol) # type: ignore
    return res

@_doc
def isinf(_n: Num) -> bool: 
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.isinf(_b)
    else:
        res = math.isinf(_b)
    return res

@_doc
def isfinite(_n: Num) -> bool: 
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.isfinite(_b)
    else:
        res = math.isfinite(_b)
    return res

@_doc
def isnan(_n: Num) -> bool: 
    _b = built(_n)
    if isinstance(_b, complex):
        res = cmath.isnan(_b)
    else:
        res = math.isnan(_b)
    return res


@_doc
def isqrt(_n: IntegralNum) -> IntegralNum: 
    _b = int(_n)
    res = math.isqrt(_b)
    return IntegralNum(res)

@_doc
def sqrt(_n: RealNum) -> RealNum: 
    _b = built(_n)
    res = math.sqrt(_b) # type: ignore
    return num(res) # type: ignore


@_doc
def lcm(*integers: IntegralNum) -> IntegralNum: 
    _b = [int(x) for x in integers]
    res = math.lcm(*_b)
    return IntegralNum(res)


@_doc
def ldexp(__x: RealNum, __i: IntegralNum) -> RealNum: 
    _bx = built(__x)
    _bi = int(__i)
    res = math.ldexp(_bx, _bi) # type: ignore
    return num(res) # type: ignore


@_doc
def log(x: Num, base: Num = e) -> Num:
    _bx = built(x)
    _bb = built(base)
    if isinstance(_bx, complex) or isinstance(_bb, complex):
        res = cmath.log(_bx, _bb)
    else:
        res = math.log(_bx, _bb) # type: ignore
    return num(res) # type: ignore

@_doc
def log10(_n: Num) -> Num: 
    return log(_n, IntegralNum(10))

@_doc
def log1p(_n: RealNum) -> RealNum: 
    return log(_n+1, e) # type: ignore

@_doc
def log2(_n: RealNum) -> RealNum: 
    return log(_n, IntegralNum(2)) # type: ignore


@_doc
def modf(_n: RealNum) -> tuple[RealNum, IntegralNum]: 
    _b = built(_n)
    res = math.modf(_b) # type: ignore
    return num(res[0]), IntegralNum(res[1]) # type: ignore


@_doc
def nextafter(__x: RealNum, __y: RealNum) -> RealNum: 
    _bx = built(__x)
    _by = built(__y)
    res = math.nextafter(_bx, _by) # type: ignore
    return num(res) # type: ignore


@_doc
def perm(_n: IntegralNum, _k: IntegralNum | None = None) -> IntegralNum: 
    _bn = int(_n)
    if _k is not None:
        _bk = int(_k)
    else:
        _bk = _k
    res = math.comb(_bn, _bk) # type: ignore
    return IntegralNum(res)


@_doc
def prod(__iterable: Iterable[RealNum], *, start: RealNum = IntegralNum(1)) -> RealNum:
    _b = [built(x) for x in __iterable]
    _s = built(start)
    res = math.prod(*_b, start=_s) # type: ignore
    return num(res) # type: ignore


@_doc
def remainder(__x: RealNum, __y: RealNum) -> RealNum: 
    _bx = built(__x)
    _by = built(__y)
    res = math.remainder(_bx, _by) # type: ignore
    return num(res) # type: ignore


@_doc
def trunc(_n: RealNum) -> IntegralNum: 
    _b = built(_n)
    res = math.trunc(_b) # type: ignore
    return IntegralNum(res)


@_doc
def ulp(_n: RealNum) -> RealNum: 
    _b = built(_n)
    res = math.ulp(_b) # type: ignore
    return num(res) # type: ignore


def abs(_n: Num) -> RealNum:
    _b = built(_n)
    res = _babs(_b)
    return num(res) # type: ignore
abs.__doc__ = _babs.__doc__


def pow(__x: RealNum, __y: RealNum, __m: RealNum | None = None) -> RealNum: 
    _bx = built(__x)
    _by = built(__y)
    if __m is not None:
        _bm = built(__m)
    else:
        _bm = __m
    res = _bpow(_bx, _by, _bm) # type: ignore
    return num(res) # type: ignore
pow.__doc__ = _bpow.__doc__


def bin(_n: IntegralNum) -> str:
    _b = int(_n)
    res = _bbin(_b)
    return res
bin.__doc__ = _bbin.__doc__

def oct(_n: IntegralNum) -> str:
    _b = int(_n)
    res = _boct(_b)
    return res
oct.__doc__ = _boct.__doc__

def hex(_n: IntegralNum) -> str:
    _b = int(_n)
    res = _bhex(_b)
    return res
hex.__doc__ = _bhex.__doc__


def ord(_n: str) -> IntegralNum:
    res = _bord(_n)
    return IntegralNum(res)
ord.__doc__ = _bord.__doc__

def chr(_n: IntegralNum) -> str:
    _b = int(_n)
    res = _bchr(_b)
    return res
chr.__doc__ = _bchr.__doc__


def isprime(_n: IntegralNum) -> bool:
    """
    Test a integer is a prime
    """
    if not isinstance(_n, IntegralNum):
        raise TypeError("Factors only consider positive integers.")
    if _n[0] is not Sign.positive:
        raise TypeError("Factors only consider positive integers.")
    if _n < 2:
        return False
    if _n == 2 or _n == 5:
        return True
    if _n[1] not in (Digit(1), Digit(3), Digit(7), Digit(9)):
        return False
    for i in range(2, floor(sqrt(_n))+1):
        if _n % i == 0:
            return False
    return True


def factors(_n: IntegralNum) -> Iterable[IntegralNum]:
    """
    Generator a integer its factors
    """
    if _n == 1:
        return [IntegralNum(1)]
    if isprime(_n):
        return [IntegralNum(1), IntegralNum(int(_n))]
    factors = [IntegralNum(1)]
    for i in range(2, floor(sqrt(_n))+1):
        if _n % i == 0:
            factors.append(IntegralNum(i))
    factors.append(IntegralNum(int(_n)))
    return factors


def factorization(_n: IntegralNum) -> Mapping[IntegralNum, CountIndex]:
    if _n == 1:
        return {IntegralNum(1): CountIndex(1)}
    if isprime(_n):
        return {_n: CountIndex(1)}
    _f = factors(_n)
    _z = []
    _m = _n
    for n in _f:
        if isprime(n):
            _z.append(n)
            _m /= n
    _d = dict(zip(_z, [CountIndex(1)]*len(_z)))
    for k in _d.keys():
        if _m % k == 0:
            _m /= k
            _d[k] += 1 # type: ignore
        if _m == 1:
            break
    return _d


del _doc
