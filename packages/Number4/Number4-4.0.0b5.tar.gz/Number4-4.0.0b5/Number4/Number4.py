"""Nums Defined"""
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from collections import UserList
from functools import total_ordering
from numbers import (Number, Complex, Real, Rational, Integral)
from typing import Any, Callable, Iterator, Tuple, TypeAlias
from fractions import Fraction
from enum import Enum
import math
from typing_extensions import SupportsIndex


__all__ = ["Num", 
           "ComplexNum", 
           "RealNum", "ImagNum", 
           "RationalNum", "IntegralNum", "Digit", "Sign",
           "NaturalNum", "CountIndex",
           "num", "built"]


_BN: TypeAlias = int | float | Fraction | complex


@total_ordering
class Num(Number, metaclass=ABCMeta):
    """
    The Base Class For Nums

    An abstract Class, Cannot use __new__ or __init__!
    """
    __slots__ = ()

    @abstractmethod
    def __int__(self):
        raise NotImplementedError

    @abstractmethod
    def __float__(self):
        raise NotImplementedError

    @abstractmethod
    def __complex__(self):
        raise NotImplementedError

    def __index__(self):
        return int(self)

    def __bool__(self):
        return self != 0

    def __pos__(self):
        return deepcopy(self)

    def __neg__(self):
        return 0 - self

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __invert__(self):
        raise NotImplementedError
    
    def __right(method: Callable): # type: ignore
        def wrapper(self, other, *args):
            return method(other, self, *args)
        
        wrapper.__name__ = f"__r{method.__name__[2:-2]}__"
        wrapper.__doc__ = method.__doc__
        return wrapper
    
    def __add__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self + other
        return num(res)
    
    __radd__ = __right(__add__)

    def __sub__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self - other
        return num(res)
    
    __rsub__ = __right(__sub__)

    def __mul__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self * other
        return num(res)
    
    __rmul__ = __right(__mul__)

    def __truediv__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self / other
        print(res)
        return num(res)
    
    __rtruediv__ = __right(__truediv__)

    def __floordiv__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self // other # type: ignore
        return num(res)
    
    __rfloordiv__ = __right(__floordiv__)

    def __divmod__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = divmod(self, other) # type: ignore
        return num(res)
    
    __rdivmod__ = __right(__divmod__)

    def __pow__(self, other, modulo=0):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        if isinstance(modulo, Num):
            modulo = built(modulo)
        res = pow(self, other, modulo) # type: ignore
        return num(res)
    
    __rpow__ = __right(__pow__)

    def __mod__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other)
        res = self % other # type: ignore
        return num(res)
    
    __rmod__ = __right(__mod__)

    def __lshift__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self << other # type: ignore
        return num(res)
    
    __rlshift__ = __right(__lshift__)

    def __rshift__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self >> other # type: ignore
        return num(res)
    
    __rrshift__ = __right(__rshift__)

    def __and__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self & other # type: ignore
        return num(res)

    def __or__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self | other # type: ignore
        return num(res)

    def __xor__(self, other):
        if isinstance(self, Num):
            self = built(self) 
        if isinstance(other, Num):
            other = built(other) 
        res = self ^ other # type: ignore
        return num(res)

    __rand__ = __right(__and__)

    __ror__ = __right(__or__)

    __rxor__ = __right(__xor__)

    def __trunc__(self) -> int:
        return math.trunc(float(self))
    
    def __round__(self, digits=None):
        return round(float(self), digits)
    
    def __ceil__(self) -> int:
        return math.ceil(float(self))
    
    def __floor__(self) -> int:
        return math.floor(float(self))
    
    @property
    def real(self):
        raise NotImplementedError
    
    @property
    def imag(self):
        raise NotImplementedError
    
    def __cmp__(self, other):
        if isinstance(other, Num):
            other = built(other)
        self = built(self)
        if self.real > other.real: # type: ignore
            return 1
        elif self.real == other.real:
            if self.imag > other.imag:
                return 1
            elif self.imag == other.imag:
                return 0
            else:
                return -1
        else:
            return -1
        
    def __hash__(self):
        self = built(self)
        return hash(self)

    __eq__ = lambda self, other: self.__cmp__(other) == 0 # type: ignore

    __lt__ = lambda self, other: self.__cmp__(other) < 0 # type: ignore

    del __right


class ComplexNum(Num, Complex):
    """
    Nums for Complex

    Same than 'complex'
    """

    __slots__ = ("_real", "_imag")

    def __new__(cls, real: float | int | complex | Complex = 0.0, imag: float | int=0.0, /):
        if isinstance(real, Num):
            real = built(real) # type: ignore
        if isinstance(imag, Num):
            imag = built(imag) # type: ignore
        if imag == 0.0:
            imag = real.imag
            real = real.real
        cplx = complex(real, imag)
        self = super().__new__(cls)
        self._real = cplx.real
        self._imag = cplx.imag

        return self

    def __int__(self):
        a = self._real # type: ignore
        if not isinstance(a, int):
            a = int(a) # type: ignore
        return a
    
    def __float__(self):
        a = self._real # type: ignore
        if not isinstance(a, float):
            a = float(a) # type: ignore
        return a
    
    def __complex__(self):
        a = self._real # type: ignore
        if not isinstance(a, complex):
            a = complex(a) # type: ignore
        return a
    
    def __abs__(self):
        return math.sqrt(self._real ** 2
                       + self._imag ** 2) # type: ignore
    
    def __repr__(self):
        return str(built(self))
    
    def __str__(self):
        return self.__repr__()
    
    def __invert__(self):
        return ~built(self) # type: ignore
    
    @property
    def real(self):
        return num(self._real)
    
    @property
    def imag(self):
        return num(self._imag)
    
    def conjugate(self):
        return num(self._real - self._imag*1j)

ComplexNum.register(complex)


class RealNum(ComplexNum, Real):
    """
    Nums for Real

    Same than 'float'
    """

    __slots__ = ()

    def __new__(cls, flo: float, /):
        if isinstance(flo, Num):
            flo = built(flo) # type: ignore
        self = super().__new__(cls, flo)
        return self
    
    @property
    def imag(self):
        return RealNum(0.0)
    
RealNum.register(float)
    

class ImagNum(ComplexNum):
    __slots__ = ()

    def __new__(cls, flo: float, /):
        self = super().__new__(cls, 0.0, flo)
        return self
    
    @property
    def real(self):
        return RealNum(0.0)

ImagNum.register(complex)
    

class RationalNum(RealNum, Rational):
    """
    Nums for Rational

    It has more than 'Fraction's
    propertys: 
    >>> mixed, percentage, thousandth, ten_thousandth
    """

    __slots__ = ("_numerator", "_denominator")

    def __new__(cls, numerator: int | float | Fraction | str, denominator: int | float | Fraction | None = None, /):
        if isinstance(numerator, Num):
            numerator = built(numerator) # type: ignore
        if isinstance(denominator, Num):
            denominator = built(denominator) # type: ignore
        if denominator is None:
            if isinstance(numerator, int):
                fra = Fraction(numerator, 1)
            else:
                fra = Fraction(numerator)
        elif isinstance(numerator, str):
            raise TypeError(f"Not allow: RationalNum(str, {type(denominator)})")
        else:
            fra = Fraction(Fraction(numerator), Fraction(denominator))
        self = super().__new__(cls, float(fra))
        self._numerator = fra.numerator
        self._denominator = fra.denominator
        return self
    
    @property
    def numerator(self) -> Num:
        return num(self._numerator)
    
    @property
    def denominator(self) -> Num:
        return num(self._denominator)
    
    @property
    def mixed(self):
        if self._numerator > 0:
            sign = Sign.positive
        elif self._numerator == 0:
            sign = Sign.zero
        else:
            sign = Sign.minus
        n = self._numerator
        d = self._denominator
        if n < 0:
            n = -n
        i = n // d
        n = n % d
        f = RationalNum(-n, d)
        return (sign, IntegralNum(i), f)
    
    @property
    def percentage(self) -> str:
        f = round(float(self), 3)
        f *= 100
        s = f"{f} %"
        return s
    
    @property
    def thousandth(self) -> str:
        f = round(float(self), 3)
        f *= 1000
        s = f"{f} ‰"
        return s
    
    @property
    def ten_thousandth(self) -> str:
        f = round(float(self), 6)
        f *= 10000
        s = f"{f} ‱"
        return s

RationalNum.register(Fraction)
    

class IntegralNum(RationalNum, Integral):
    """
    Nums for Integer

    Enhanced version of int, 
    Allow Digits.
    """

    class Digits(UserList):
        """
        Digit list
        """

        def __init__(self, digit_list = None, sign = None, /):
            if digit_list is None:
                digit_list = [Digit(0)]
            if sign is None:
                sign = Sign.zero
            lst = [sign]
            for d in digit_list:
                lst.append(d)
            super().__init__(lst)
        
        def __getitem__(self, i: SupportsIndex | slice):
            if isinstance(i, slice):
                if ((i.start is not None and i.start < 0)
                        or (i.stop is not None and i.stop < 0)
                        or (i.step is not None and i.step < 0)):
                    raise IndexError(i)
                return list(super().__getitem__(i))
            else:
                if i < 0: # type: ignore
                    raise IndexError(i)
                return super().__getitem__(i)
            
        def __setitem__(self, i: SupportsIndex | slice, digit):
            seted = list(self)
            seted[i] = digit
            if not isinstance(seted[0], Sign):
                raise IndexError(i)
            for d in seted[1:]:
                if not isinstance(d, Digit):
                    raise IndexError(i)
            super().__setitem__(i, digit)
        
        def __delitem__(self, i: SupportsIndex | slice) -> None:
            seted = list(self)
            del seted[i]
            if not isinstance(seted[0], Sign):
                raise IndexError(i)
            for d in seted[1:]:
                if not isinstance(d, Digit):
                    raise IndexError(i)
            super().__delitem__(i)
        
        def __repr__(self) -> str:
            a = list(self)
            b = a[1:]
            b.reverse()
            c = f"<{repr(a[0])}> {repr(list(b))}"
            return f"<Digits: {c}>"
        
        def __int__(self):
            sign = self[0]
            digits = list(self)[1:][::-1]
            i = 0
            for d in digits:
                i *= 10
                i += int(d)
            if sign == Sign.minus:
                i = -i
            return i
        
        def __reversed__(self) -> Iterator:
            raise NotImplementedError
        
        @classmethod
        def from_IntegralNum(cls, inte):
            return inte.digits
        
        def to_IntegralNum(self):
            return IntegralNum(int(self))

    __slots__ = ()

    def __new__(cls, integral: int = 0, /):
        if isinstance(integral, Num):
            integral = built(integral) # type: ignore
        self = super().__new__(cls, Fraction(integral, 1))
        return self
    
    @property
    def digits(self) -> Digits:
        if self > 0:
            sign = Sign.positive
        elif self == 0:
            sign = Sign.zero
        else:
            sign = Sign.minus
        s = str(self)
        l = list(s)
        if l[0] == "-":
            del l[0]
        l.reverse()
        l = self.__class__.Digits([Digit(int(i)) for i in l], sign)
        return l
    
    @property
    def sign(self):
        return self.digits[0]
    
    def __getitem__(self, i):
        return self.digits[i]
    
    def __iter__(self):
        return self.digits

IntegralNum.register(int)


class Digit(IntegralNum):
    """
    Integer 's Digit
    """

    __slots__ = ()

    def __new__(cls, one_int: int = 0, /):
        assert 0 <= one_int < 10
        self = super().__new__(cls, one_int)
        return self
    
    @property
    def digits(self):
        raise NotImplementedError
    
    @property
    def sign(self):
        raise NotImplementedError
    
    def __getitem__(self, key: Any) -> Any:
        raise NotImplementedError
    
    def __iter__(self):
        raise NotImplementedError
    

class Sign(Enum):
    """
    Integer 's Sign
    """

    __slots__ = ()

    positive = 0
    minus = 1
    zero = 2

    def __repr__(self) -> str:
        signlst = ["(+)", "-", " "]
        return signlst[self.value]


class NaturalNum(IntegralNum):
    """
    Nums for Natural
    
    Assert >= 0
    """

    __slots__ = ()

    def __new__(cls, integral: int = 0):
        assert integral >= 0
        self = super().__new__(cls, integral)
        return self


class CountIndex(NaturalNum):
    """
    Index/Count Nums
    
    Has different string
    """

    __slots__ = ("_typed")

    class Typed(Enum):
        Count = 0
        Index = 1

    def __new__(cls, integral: int = 0, typed: Typed = Typed.Count):
        self = super().__new__(cls, integral)
        self._typed = typed # type: ignore
        return self

    def __repr__(self):
        if self._typed == CountIndex.Typed.Count: # type: ignore
            return f"<count: {super().__repr__()}>"
        else:
            return f"<index: {super().__repr__()}>"


def num(b: _BN, /) -> Num:
    """
    Built-in number to Nums number
    """

    if b.imag == 0:
        b = b.real
        if b % 1 == 0: # type: ignore
            return IntegralNum(int(b)) # type: ignore
        elif isinstance(b, Fraction):
            return RationalNum(str(b))
        else:
            if (str(b).index(".") - len(str(b))) < -10:
                return RationalNum(str(b)) # type: ignore
            else:
                return RealNum(b) # type: ignore
    elif b.real == 0:
        return ImagNum(b.imag)
    else:
        return ComplexNum(b.real, b.imag)


def built(n: Num, /) -> _BN:
    """
    Nums number to Built-in number
    """

    if isinstance(n, Digit):
        return int(n)
    elif isinstance(n, IntegralNum):
        return int(n)
    elif isinstance(n, RationalNum):
        return Fraction(n)
    elif isinstance(n, RealNum):
        return float(n)
    elif isinstance(n, ComplexNum):
        return complex(n.real, n.imag)
    elif isinstance(n, Num):
        raise TypeError("'Num' class is a abstract class, not numbers.")
    else:
        raise TypeError("Assert use 'Num' class 's subclass!")
