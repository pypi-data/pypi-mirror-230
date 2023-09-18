import colorama
import lxml
import lxml.html
import lxml.etree
import requests
import yaml
import pint


""" colorama """
colorama.init()


""" pint """
"""
Class Pint Unit Registry dasar untuk membuat Pint Object
Setiap instance Unit Registry hanya bisa dilakukan operasi perhitungan
dengan instance Unit Registry itu sendiri
"""
PintUreg = pint.UnitRegistry()
""" Class untuk membuat Object Pint Quantity """
PintUregQuantity = PintUreg.Quantity


if __name__ == "__main__":
    print_colorize("Anda menjalankan module pypipr", color=colorama.Fore.RED)
