# coding:utf-8

from geocoder import *
from mapapi import show_map


def main():
    toponym_to_find = "Саратов, Большая Горная, 1"
    # Показываем карту с фиксированным масштабом.
    lat, lon = get_coordinates(toponym_to_find)
    ll_spn = "ll={0},{1}&spn=0.005,0.005".format(lat, lon)
    show_map(ll_spn, "map")
