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


def map_change_size(delta, ll, z):
    # Изменяем масштаб карты.
    if 0 <= z + delta <= 17:
        z += delta
    # Возвращаем запрос карты с измененным масштабом.
    return form_request(ll=ll, l="map", z=z), z


def show_map(ll=None, z=14, map_type='map', add_params=None):
    # Формируем начальный запрос.
    if ll:
        map_request = form_request(ll=ll, z=z, l=map_type)
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
                    new_req, z = map_change_size(-1, ll, z)  # новый запрос и переопределенный масштаб
                    response = requests.get(new_req)

                    if not response:
                        print("Ошибка выполнения запроса:")
                        print(map_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                        sys.exit(1)

                    map_file = form_map(response)
                    screen.blit(pygame.image.load(map_file), (0, 0))

                if event.key == pygame.K_PAGEDOWN:
                    new_req, z = map_change_size(1, ll, z)
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
