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
    return x


def map_bigger(map_request, delta, spnx, spny, ll):
    if spnx + delta > 0.005 and spny + delta > 0.005:
        #print(map_request)
        newx = round(spnx+delta, 5)
        newy = round(spny+delta, 5)
        spnx = newx
        spny = newy
        spn=str(newx) + ',' + str(newy)
        #print(map_request)
    return form_request(ll=ll, spn=spn), spnx, spny


def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = "http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}".format(**locals())
        spn = ll_spn.split('&')[1][4:]
        spnx, spny = map(float, spn.split(','))
    else:
        map_request = "http://static-maps.yandex.ru/1.x/?l={map_type}".format(**locals())
        spnx, spny = 0.005, 0.005

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Инициализируем pygame
    ll = ll_spn.split('&')[0][3::]
    pygame.init()
    screen = pygame.display.set_mode((600,450))
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
                new_req, spnx, spny = map_bigger(map_request, 0.01, spnx, spny, ll)
                print(new_req, spnx, spny)
                response = requests.get(new_req)
                map_file = form_map(response)
                screen.blit(pygame.image.load(map_file), (0, 0))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
                new_req, spnx, spny = map_bigger(map_request, -0.01, spnx, spny)
                response = requests.get(new_req)
                map_file = form_map(response)
                screen.blit(pygame.image.load(map_file), (0, 0))
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)
