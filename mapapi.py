#coding:utf-8
import pygame
import requests
import sys
import os

class Map:
    def __init__(self, map_file, ll, map_type, spnx, spny, add_params):
        self.map_file = map_file
        self.ll = ll
        self.spnx = spnx
        self.spny = spny
        self.l = map_type
        self.params = add_params
        self.request = self.form_request(self.params, ll=ll, spn=str(spnx) + ',' + str(spny), l=map_type)
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

    def request_map(self, request):
        response = requests.get(request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(self.request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        return response

    def form_map(self, response):
        # Запишем полученное изображение в файл.
        try:
            with open(self.map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

        return self.map_file

    def map_change_size(self, delta):
        # Изменяем параметр spn.
        self.spnx = round(self.spnx * delta, 3)
        self.spnx = min(2, max(0.002, self.spnx))
        self.spny = round(self.spny * delta, 3)
        self.spny = min(2, max(0.002, self.spny))
        self.request = self.form_request(self.params, ll=self.ll, l=self.l, spn=str(self.spnx) + ',' + str(self.spny))
        response = self.request_map(self.request)
        self.map_file = self.form_map(response)

    def move_map(self, move_x, move_y):
        # Изменяем параметр ll.
        new_ll = '{},{}'.format(float(self.ll.split(',')[0]) + move_x, float(self.ll.split(',')[1]) + move_y)
        self.ll = new_ll
        self.request = self.form_request(self.params, ll=self.ll, l=self.l, spn=str(self.spnx) + ',' + str(self.spny))
        response = self.request_map(self.request)
        self.map_file = self.form_map(response)
        # Возвращаем запрос карты с измененным ll.

def show_map(ll=None, z=17, spnx=0.02, spny=0.02, map_type='map', add_params=[]):
    cur_map = Map(map_file='map.png', ll=ll, map_type=map_type, spnx=spnx, spny=spny, add_params=add_params)
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
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
                    cur_map.map_change_size(2)
                if event.key == pygame.K_PAGEDOWN:
                    cur_map.map_change_size(0.5)
                if event.key == pygame.K_RIGHT:
                    cur_map.move_map(cur_map.spnx * 4, 0)
                if event.key == pygame.K_LEFT:
                    cur_map.move_map(-cur_map.spnx * 4, 0)
                if event.key == pygame.K_DOWN:
                    cur_map.move_map(0, -cur_map.spny * 2)
                if event.key == pygame.K_UP:
                    cur_map.move_map(0, cur_map.spny * 2)
                screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(cur_map.map_file)
