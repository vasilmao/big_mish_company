#coding:utf-8
import pygame
import requests
import sys
import os


def form_map(response):
    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    return map_file


def form_request(**kwargs):
    x = 'http://static-maps.yandex.ru/1.x/'
    if kwargs:
        x += '?'
        for i in kwargs.keys():
            x += i + "=" + str(kwargs[i])
            x += '&'
        x = x[:-1:]
    print(x)
    return x


def map_bigger(map_request, delta, sizex, sizey, ll, type, z):
    if 0 <= z + delta <= 17:
        z += delta
    return form_request(ll=ll, l=type, size=str(sizex)+','+str(sizey), z=z), z


def show_map(ll=None, z=17, sizex=600, sizey=450, map_type='map', add_params=None):
    z = 1
    if ll:
        map_request = "http://static-maps.yandex.ru/1.x/?ll={0}&z={1}&size={2},{3}&l={4}".format(ll, z, sizex, sizey, map_type)
        print(map_request)
    else:
        map_request = "http://static-maps.yandex.ru/1.x/?l={map_type}".format(**locals())

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    map_file = form_map(response)
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Рисуем картинку, загружаемую из только что созданного файла.
    # Переключаем экран и ждем закрытия окна.
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
                new_req, z = map_bigger(map_request, 1, sizex, sizey, ll, map_type, z)
                response = requests.get(new_req)
                map_file = form_map(response)
                screen.blit(pygame.image.load(map_file), (0, 0))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
                new_req, z = map_bigger(map_request, -1, sizex, sizey, ll, map_type, z)
                response = requests.get(new_req)
                map_file = form_map(response)
                screen.blit(pygame.image.load(map_file), (0, 0))
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)
