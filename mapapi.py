#coding:utf-8
import os
from math import cos
from classes import *
from geocoder import *


def search(text, cur_map, moving=False):
    # Ищем введенный в строку поиска объект
    lat, lon = get_coordinates(text)
    if lat is None or lon is None:
        print('Не нашлось')
        return
    lat, lon = round(lat, 3), round(lon, 3)
    if moving:
        cur_map.go_to_coords(lat, lon, True)  # перемещаем карту


def show_map(ll=None, zoom='17', size='600,450', map_type='map', add_params=[]):
    # инициализируем карту
    cur_map = Map(map_file='map.png', ll=ll, map_type=map_type, size=size, z=zoom, add_params=add_params)
    # инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
    # объявляем объекты gui
    gui = GUI()
    search_box = TextBox((0, 0, 440, 30))  # строка поиска
    address_box = Label((0, 30, 600, 30), "")  # вывод полного адреса
    postal_code = CheckBox((400, 0, 50, 30), "ZIP code")  # показ почтового индекса
    search_button = Button((440, 0, 80, 30), "искать")  # кнопка поиска
    reset_button = Button((520, 0, 80, 30), "сбросить")
    # кнопки переключения вида карты
    map_button = Button((0, 419, 50, 30), "map")
    sat_button = Button((50, 419, 50, 30), "sat")
    skl_button = Button((100, 419, 50, 30), "skl")
    gui.add_element(search_box)
    gui.add_element(map_button)
    gui.add_element(sat_button)
    gui.add_element(skl_button)
    gui.add_element(search_button)
    gui.add_element(reset_button)
    gui.add_element(postal_code)
    print_org = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    cur_map.map_change_size(-1)  # увеличиваем область показа
                elif event.key == pygame.K_PAGEDOWN:
                    cur_map.map_change_size(1)  # уменьшаем область показа
                elif event.key == pygame.K_RIGHT:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(1, 0)  # перемещаем карту вправо
                elif event.key == pygame.K_LEFT:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(-1, 0)  # перемещаем карту влево
                elif event.key == pygame.K_DOWN:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(0, -1)  # перемещаем карту вниз
                elif event.key == pygame.K_UP:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(0, 1)  # перемещаем карту вверх
                else:
                    search_box.get_event(event)
                screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
            else:
                gui.get_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                        and not pygame.Rect((0, 419, 150, 30)).collidepoint(event.pos):  # не пересекается ли клик с кнопками переключения карты
                    if 30 < event.pos[1]:
                        dx = int(event.pos[0] - 300)
                        dy = int(event.pos[1] - 225)
                        kekx = 360 / (2 ** (int(cur_map.z) + 8))
                        lly = float(cur_map.ll.split(',')[1])
                        lly = lly * 2 * pi / 360
                        keky = abs(cos(lly)) * 180 / (2 ** (int(cur_map.z) + 7))
                        kekx *= dx
                        keky *= dy
                        kekll = cur_map.ll
                        kekll = str(round(float(kekll.split(',')[0]) + kekx, 5)) + ',' + str(round(float(kekll.split(',')[1]) - keky, 5))
                        cur_map.change_pt(kekll)
                        search(kekll, cur_map)
                        formatted_address = get_formatted_address(kekll)  # получаем полный адрес объекта
                        zip_code = get_postal_code(search_box.text)  # получаем почтовый индекс
                        print_org = False
                        if postal_code.pressed:  # если был нажат переключатель
                            if zip_code:
                                address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, zip_code)
                            else:
                                address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, "Not found")
                        else:
                            address_box.text = "Адрес: {}".format(formatted_address)
                        if address_box not in gui.elements:  # отображаем строку с адресом
                            gui.add_element(address_box)
                        screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if 30 < event.pos[1]:
                        dx = int(event.pos[0] - 300)
                        dy = int(event.pos[1] - 225)
                        kekx = 360 / (2 ** (int(cur_map.z) + 8))
                        lly = float(cur_map.ll.split(',')[1])
                        lly = lly * 2 * pi / 360
                        keky = abs(cos(lly)) * 180 / (2 ** (int(cur_map.z) + 7))
                        kekx *= dx
                        keky *= dy
                        kekll = cur_map.ll
                        kekll = str(round(float(kekll.split(',')[0]) + kekx, 5)) + ',' + str(round(float(kekll.split(',')[1]) - keky, 5))
                        try:
                            formatted_address, org_name, org_point = get_nearest_organization(get_formatted_address(kekll), kekll)
                            cur_map.change_pt(org_point)
                            search(formatted_address, cur_map)
                            zip_code = get_postal_code(search_box.text)
                            print_org = True
                            if postal_code.pressed:  # если был нажат переключатель
                                if zip_code:
                                    address_box.text = "Ближ. орг-ция: {}, ZIP: {}".format(org_name, zip_code)
                                else:
                                    address_box.text = "Ближ. орг-ция: {}, ZIP: {}".format(org_name, "Not found")
                            else:
                                address_box.text = "Ближ. орг-ция: {}".format(org_name)
                            if address_box not in gui.elements:  # отображаем строку с адресом
                                gui.add_element(address_box)
                            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
                        except TypeError:  # если расстояние больше 50 - ничего не делать
                            pass

        if search_button.pressed:  # нажата кнопка поиска
            search(search_box.text, cur_map, True)  # осуществляем поиск
            formatted_address = get_formatted_address(search_box.text)  # получаем полный адрес объекта
            zip_code = get_postal_code(search_box.text)  # получаем почтовый индекс
            print_org = False
            if postal_code.pressed:  # если был нажат переключатель
                if zip_code:
                    address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, zip_code)
                else:
                    address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, "Not found")
            else:
                address_box.text = "Адрес: {}".format(formatted_address)
            if address_box not in gui.elements:  # отображаем строку с адресом
                gui.add_element(address_box)
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

        if reset_button.pressed:  # нажата кнопка сброса
            cur_map.reset_pt()  # сбрасываем метку
            address_box.erase()  # очищаем строку с адресом
            search_box.erase()  # очищаем поисковую строку
            gui.erase(address_box)  # убираем с экрана строку с адресом
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

        if postal_code.pressed and address_box in gui.elements:  # если переключатель был нажат после поиска
            if zip_code:
                if print_org:
                    address_box.text = "Ближ. орг-ция: {}, ZIP: {}".format(org_name, zip_code)
                else:
                    address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, zip_code)
            else:
                if print_org:
                    address_box.text = "Ближ. орг-ция: {}, ZIP: {}".format(org_name, "Not found")
                else:
                    address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, "Not found")
        elif address_box in gui.elements:
            if print_org:
                address_box.text = "Ближ. орг-ция: {}".format(org_name)
            else:
                address_box.text = "Адрес: {}".format(formatted_address)

        # переключение вида карты
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
