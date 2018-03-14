#coding:utf-8
import pygame
import requests
import sys
import os


def map_bigger(map_request, delta, spnx, spny):
    if spnx + delta > 0 and spny + delta > 0:
        new_spn = str(spnx+delta) + ',' + str(spny+delta)
        map_request.replace("spn={},{}".format(spnx, spny), "spn="+new_spn)
    return map_request

def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = "http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}".format(**locals())
        spn = ll_spn[0]
        spnx, spny = map(float, spn.split(','))
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

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Инициализируем pygame
    pygame.init() 
    screen = pygame.display.set_mode((600,450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.K_PAGEUP:



    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)
