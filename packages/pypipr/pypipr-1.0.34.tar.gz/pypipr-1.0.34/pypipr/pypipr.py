'''
Modul utama pypipr yang berisi semua yg ada dalam pypipr.

Urutan dari import modul menandakan bahwa modul hanya diperbolehkan
mengimport modul yang berada diatasnya. Karena apabila mengimport 
modul yang ada dibawahnya maka akan terjadi circular import. 

lib - uncategorize - ifunctions - console - engineering - django
'''


from .lib import *
from .uncategorize import *
from .ifunctions import *
from .console import *
from .engineering import *
from .flow import *
from .idjango import *


if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
