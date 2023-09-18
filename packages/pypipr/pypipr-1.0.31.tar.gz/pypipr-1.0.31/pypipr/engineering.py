"""
Modul untuk analisa perhitungan 
"""


from .ifunctions import *
from .lib import *

""" format variabel: __[function]__[var_name]__ """
# batchmaker()
__batchmaker__regex_pattern__ = r"{(?:[^a-zA-Z0-9{}]+)?([a-zA-Z]|\d+)[^a-zA-Z0-9{}]+([a-zA-Z]|\d+)(?:[^a-zA-Z0-9{}]+(\d+))?(?:[^a-zA-Z0-9{}]+)?}"
__batchmaker__regex_compile__ = re.compile(__batchmaker__regex_pattern__)


def batchmaker(pattern: str):
    """
    Alat Bantu untuk membuat teks yang berulang.
    Gunakan `{[start][separator][finish]([separator][step])}`.
    ```
    [start] dan [finish]    -> bisa berupa huruf maupun angka
    ([separator][step])     -> bersifat optional
    [separator]             -> selain huruf dan angka
    [step]                  -> berupa angka positif
    ```

    ```python
    s = "Urutan {1/6/3} dan {10:9} dan {j k} dan {Z - A - 15} saja."
    print(batchmaker(s))
    print(list(batchmaker(s)))
    ```
    """
    s = __batchmaker__regex_compile__.search(pattern)
    if s is None:
        yield pattern
        return

    find = s.group()
    start, finish, step = s.groups()

    for i in irange(start, finish, step):
        r = pattern.replace(find, i, 1)
        yield from batchmaker(r)


def calculate(teks):
    """
    Mengembalikan hasil dari perhitungan teks menggunakan modul pint.
    Mendukung perhitungan matematika dasar dengan satuan.

    Return value:
    - Berupa class Quantity dari modul pint

    Format:
    - f"{result:~P}"            -> pretty
    - f"{result:~H}"            -> html
    - result.to_base_units()    -> SI
    - result.to_compact()       -> human readable

    ```python
    fx = "3 meter * 10 cm * 3 km"
    res = calculate(fx)
    print(res)
    print(res.to_base_units())
    print(res.to_compact())
    print(f"{res:~P}")
    print(f"{res:~H}")
    ```
    """
    return PintUregQuantity(teks)


def batch_calculate(pattern):
    """
    Analisa perhitungan massal.
    Bisa digunakan untuk mencari alternatif terendah/tertinggi/dsb.


    ```python
    iprint(batch_calculate("{1 10} m ** {1 3}"))
    ```
    """
    patterns = batchmaker(pattern)

    c = None
    for i in patterns:
        try:
            c = calculate(i)
        except Exception:
            c = None
        yield (i, c)


if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
