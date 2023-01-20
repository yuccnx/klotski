#-*- coding: UTF-8 -*-

# 依赖库
# pip install pygame

# 环境
# mac - python3.10

import os
import time
import sys
import pygame

def NewViewer(conf):
    return TextModelViewer(conf) if conf['text_model'] else ImageModelViewer(conf)


class TextModelViewer:
    def __init__(self, conf):
        self.fps = conf['fps']

    def displays(self, boards):
        for board in boards:
            os.system('clear')
            print("\n\n答案演示：\n")
            self._display(board)
            time.sleep(1 / self.fps)

    def _display(self, board):
        name_map = {
            "0":"  ", # 空
            "a":"\033[38m卒\033[0m", # 卒1
            "b":"\033[38m卒\033[0m", # 卒2
            "c":"\033[38m卒\033[0m", # 卒3
            "d":"\033[38m卒\033[0m", # 卒4
            "M":"\033[36m超\033[0m", # 马超
            "H":"\033[33m忠\033[0m", # 黄忠
            "Z":"\033[38m飞\033[0m", # 张飞
            "Y":"\033[34m云\033[0m", # 赵云
            "G":"\033[31m羽\033[0m", # 关羽
            "C":"\033[32m操\033[0m", # 曹操
        }

        key = str(board)
        ans = '  '
        for i in range(len(key)):
            ans = ans + name_map[key[i]]
            if (i+1) % 4 == 0:
                ans = ans + '\n  '

        print(ans)


class ImageModelViewer:
    def __init__(self, conf):
        view = conf['view']
        self.board_width = view['width']
        self.board_height = view['height']

        self.cell_start_x = view['cell_start_x'] # 格子开始未知
        self.cell_start_y = view['cell_start_y'] # 格子开始未知
        self.cell = view['cell'] # 格子的大小
        self.fps = conf['fps']   # 每秒帧数

        pygame.init()

        screen = pygame.display.set_mode((self.board_width, self.board_height))
        pygame.display.set_caption("华容道-云中买马制作")

        self.screen = screen

        images = conf['images']
        self.board_image = pygame.image.load(images['board'])

        self.role_images = {}

        for role, image in images['roles'].items():
            self.role_images[role] = pygame.image.load(image)

    def displays(self, boards):
        time_start = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("exit~")
                    sys.exit()

            index = int((time.time() - time_start) * self.fps - 2) # -2 是想延后2s 开始播放
            index = max(0, index)
            index = min(index, len(boards) - 1)

            board = boards[index]
            self._display(board)

    def _display(self, board):
        self.screen.blit(self.board_image, (0, 0))


        for role, card in board.cards.items():
            self.screen.blit(self.role_images[role], (self.cell_start_x +  card.x * self.cell, self.cell_start_y +  card.y * self.cell))

        pygame.display.update()

