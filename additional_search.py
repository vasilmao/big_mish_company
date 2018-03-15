# coding:utf-8

from geocoder import *
from mapapi import show_map


def main():
    toponym_to_find = "Саратов, Большая Горная, 1"
    # Показываем карту с фиксированным масштабом.
    lat, lon = get_coordinates(toponym_to_find)
    ll = "{0},{1}".format(lat, lon)
    show_map(ll=ll, map_type="map", add_params=["pt={},pm2dgm".format(ll)])
