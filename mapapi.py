#coding:utf-8
import pygame
import os
from classes import Map
from classes import GUI
from classes import TextBox
from classes import Button
from geocoder import *


def search(text, cur_map):
    lat, lon = get_coordinates(text)
    if lat is None or lon is None:
        print('Не нашлось')
        return
    lat, lon = round(lat, 3), round(lon, 3)
    cur_map.go_to_coords(lat, lon, True)


def show_map(ll=None, spnx=0.02, spny=0.02, map_type='map', add_params=[]):
    cur_map = Map(map_file='map.png', ll=ll, map_type=map_type, spnx=spnx, spny=spny, add_params=add_params)
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
    gui = GUI()
    search_box = TextBox((0, 0, 350, 30))
    gui.add_element(search_box)
    search_button = Button((350, 0, 100, 30), 'искать')
    map_button = Button((450, 0, 50, 30), 'map')
    sat_button = Button((500, 0, 50, 30), 'sat')
    skl_button = Button((550, 0, 50, 30), 'skl')
    gui.add_element(map_button)
    gui.add_element(sat_button)
    gui.add_element(skl_button)
    gui.add_element(search_button)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    cur_map.map_change_size(2)
                elif event.key == pygame.K_PAGEDOWN:
                    cur_map.map_change_size(0.5)
                elif event.key == pygame.K_RIGHT:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(cur_map.spnx * 3, 0)
                elif event.key == pygame.K_LEFT:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(-cur_map.spnx * 3, 0)
                elif event.key == pygame.K_DOWN:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(0, -cur_map.spny)
                elif event.key == pygame.K_UP:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(0, cur_map.spny)
                else:
                    search_box.get_event(event)
            else:
                gui.get_event(event)
                if search_button.pressed:
                    search(search_box.text, cur_map)
                screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

        if map_button.pressed and cur_map.l != "map":
            cur_map.change_map_type("map")
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
        if sat_button.pressed and cur_map.l != "sat":
            cur_map.change_map_type("sat")
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
        if skl_button.pressed and cur_map.l != "sat,skl":
            cur_map.change_map_type("sat,skl")
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

        gui.update()
        gui.render(screen)
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(cur_map.map_file)
