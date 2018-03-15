#coding:utf-8
import pygame
import requests
import sys
import os

class Map:
    def __init__(self, map_file, x, y, sizex, sizey, map_type, z, add_params):
        self.map_file, self.x, self.y, self.sizex, self.sizey, self.l, self.z, self.params = map_file, x, y, sizex, sizey, map_type, z, add_params
        self.request = self.form_request(self.params, ll=str(x)+','+str(y), size=str(sizex) + ',' + str(sizey), l=map_type, z=z)
        self.map_file = self.form_map(requests.get(self.request))

    def form_request(self, args, **kwargs):
        x = 'http://static-maps.yandex.ru/1.x/'
        if kwargs or args:
            x += '?'
            for i in kwargs.keys():
                x += i + "=" + str(kwargs[i])
                x += '&'
            x = x[:-1:]
            if args:
                if kwargs:
                    x += '&'
                for i in args:
                    x += i
                    x += '&'
            if x[-1] == '&':
                x = x[:-1:]
        print(x)
        return x

    def form_map(self, response):
        # Запишем полученное изображение в файл.
        try:
            with open(self.map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

        return self.map_file

    def change_size(self, d=0):
        if 0<= self.z + d <= 17:
            self.z += d
        self.request = self.form_request(self.params, ll=str(self.x)+','+str(self.y), size=str(self.sizex) + ',' + str(self.sizey), l=self.l, z=self.z)
        self.map_file = self.form_map(requests.get(self.request))

def show_map(ll=None, z=17, sizex=600, sizey=450, map_type='map', add_params=None):
    ll_h = list(map(float, ll.split(',')))
    x = ll_h[0]
    y = ll_h[1]
    cur_map = Map('map.png', x, y, sizex, sizey, map_type, 17, [])
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((sizex, sizey))
    screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
    # Рисуем картинку, загружаемую из только что созданного файла.
    # Переключаем экран и ждем закрытия окна.
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    cur_map.change_size(1)
                    screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
                if event.key == pygame.K_PAGEDOWN:
                    cur_map.change_size(-1)
                    screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(cur_map.map_file)
