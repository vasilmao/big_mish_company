#coding:utf-8
import pygame
import requests
import sys
import os


def form_map(response):
    # Формируем карту.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    return map_file


def form_request(**kwargs):
    # Формируем запрос.
    x = 'http://static-maps.yandex.ru/1.x/'
    if kwargs:
        x += '?'
        for i in kwargs.keys():
            x += i + "=" + str(kwargs[i])
            x += '&'
        x = x[:-1:]
    return x


def move_map_left(ll, spnx, spny):
    # Изменяем параметр ll.
    new_ll = '{},{}'.format(float(ll.split(',')[0]) - spnx, float(ll.split(',')[1]))
    return form_request(ll=new_ll, l="map", spn='{},{}'.format(spnx, spny)), new_ll


def move_map_right(ll, spnx, spny):
    new_ll = '{},{}'.format(float(ll.split(',')[0]) + spnx, float(ll.split(',')[1]))
    return form_request(ll=new_ll, l="map", spn='{},{}'.format(spnx, spny)), new_ll


def move_map_up(ll, spnx, spny):
    new_ll = '{},{}'.format(float(ll.split(',')[0]), float(ll.split(',')[1]) + spny)
    return form_request(ll=new_ll, l="map", spn='{},{}'.format(spnx, spny)), new_ll


def move_map_down(ll, spnx, spny):
    new_ll = '{},{}'.format(float(ll.split(',')[0]), float(ll.split(',')[1]) - spny)
    return form_request(ll=new_ll, l="map", spn='{},{}'.format(spnx, spny)), new_ll


def map_change_size(delta, ll, spnx, spny):
    # Изменяем параметр spn.
    if spnx * delta >= 0.001 and spny * delta >= 0.001:
        spnx *= delta
        spny *= delta
        new_spn = (round(spnx, 3), round(spny, 3))
    else:
        new_spn = (spnx, spny)
    # Возвращаем запрос карты с измененным spn.
    return form_request(ll=ll, l="map", spn='{},{}'.format(new_spn[0], new_spn[1])), new_spn


def show_map(ll=None, spn=(0.02, 0.02), map_type='map', add_params=None):
    # Формируем начальный запрос.
    if ll:
        map_request = form_request(ll=ll, spn='{},{}'.format(spn[0], spn[1]), l=map_type)
    else:
        map_request = form_request(l=map_type)

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Инициализируем pygame.
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    map_file = form_map(response)
    screen.blit(pygame.image.load(map_file), (0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    # новый запрос и переопределенный spn
                    new_req, spn = map_change_size(0.5, ll, spn[0], spn[1])
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

                if event.key == pygame.K_PAGEDOWN:
                    new_req, spn = map_change_size(2, ll, spn[0], spn[1])
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

                if event.key == pygame.K_LEFT:
                    new_req, ll = move_map_left(ll, spn[0], spn[1])
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

                if event.key == pygame.K_RIGHT:
                    new_req, ll = move_map_right(ll, spn[0], spn[1])
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

                if event.key == pygame.K_UP:
                    new_req, ll = move_map_up(ll, spn[0], spn[1])
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

                if event.key == pygame.K_DOWN:
                    new_req, ll = move_map_down(ll, spn[0], spn[1])
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)
