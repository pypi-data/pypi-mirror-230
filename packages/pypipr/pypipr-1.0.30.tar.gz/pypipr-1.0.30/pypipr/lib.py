'''
Modul ini digunakan untuk menambahkan modul berdasarkan kondisi tertentu
yang akan berbeda-beda antara environment
'''


from .libstd import *
from .libvendor import *


if WINDOWS:
    import msvcrt as getch

if LINUX:
    import getch as getch



if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
