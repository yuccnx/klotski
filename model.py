#-*- coding: UTF-8 -*-

WIDTH = 4
HEIGH = 5

class Board:
    '''
    cards: dir{role:card}
    blanks:set((x,y))
    '''
    def __init__(self, cards, blanks):
        self.cards = {card.role:card for card in cards}
        self.blanks = blanks

    def isBlanks(self, x, y):
        return (x, y) in self.blanks

    def isAllBlanks(self, points):
        for (x,y) in points:
            if not self.isBlanks(x,y):
                return False

        return True

    def clone(self):
        cards = [card for role, card in self.cards.items()]
        blanks = {blank for blank in self.blanks}

        return Board(cards, blanks)

    def updateCard(self, card):
        self.cards[card.role] = card

    def updateBlanks(self, enter_points, leave_points):
        for point in enter_points:
            if point in self.blanks:
                self.blanks.remove(point)

        for point in leave_points:
            self.blanks.add(point)

    def __str__(self):
        ans = ''
        state = [['0' for i in range(WIDTH)] for j in range(HEIGH)]

        for role, card in self.cards.items():
            x, y, width, height = card.x, card.y, card.width, card.height
            for offset_x in range(width):
                for offset_y in range(height):
                    state[y + offset_y][x + offset_x] = role

        for row in state:
            ans += ''.join(row)

        return ans


    def hash(self):
        # 等效值分类
        categories = {
            "0":"0", # 空
            "a":"1", # 卒1
            "b":"1", # 卒2
            "c":"1", # 卒3
            "d":"1", # 卒4
            "M":"2", # 马超
            "H":"2", # 黄忠
            "Z":"2", # 张飞
            "Y":"2", # 赵云
            "G":"3", # 关羽
            "C":"4", # 曹操
        }

        return ''.join([categories[c] for c in str(self)])

class Card:
    def __init__(self, role, x, y, width, height):
        self.role = role

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def clone(self):
        return Card(self.role, self.x, self.y, self.width, self.height)

    def move(self, offset_x, offset_y):
        self.x = self.x + offset_x
        self.y = self.y + offset_y

    def isLeftMost(self):
        return self.x == 0

    def isRightMost(self):
        return self.x + self.width == WIDTH

    def isTopMost(self):
        return self.y == 0

    def isBottomMost(self):
        return self.y + self.height == HEIGH

    def getTopLines(self):
        return [(self.x + i, self.y) for i in range(self.width)]

    def getBottomLines(self):
        return [(self.x + i, self.y + self.height - 1) for i in range(self.width)]

    def getLeftLines(self):
        return [(self.x, self.y + i) for i in range(self.height)]

    def getRightLines(self):
        return [(self.x + self.width - 1, self.y + i) for i in range(self.height)]

class Game:
    def __init__(self):
        self.state_count = 0

    def createBoard(self, state):
        # 空白位置
        blanks = set((x, y) for x in range(WIDTH) for y in range(HEIGH) if state[y][x] == '0')

        # 收集盘面存在的角色
        card_roles = set(state[y][x] for x in range(WIDTH) for y in range(HEIGH) if state[y][x] != '0')

        # 创建角色卡片
        cards = [self.cardFromState(state, role) for role in card_roles]

        return Board(cards, blanks)

    def cardFromState(self, state, role):
        min_x, min_y = WIDTH - 1, HEIGH - 1
        max_x, max_y = 0, 0

        for x in range(WIDTH):
            for y in range(HEIGH):
                if state[y][x] != role:
                    continue

                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

        return Card(role, min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def play(self, state):
        board = self.createBoard(state)

        traversed = set()

        if self.isAnswer(board):
            return [str(board)]

        forest = [Tree(None, board)]

        return self.dfs(forest, traversed, 1)

    def dfs(self, forest, traversed, level):
        next_forest = []

        for tree in forest:
            child_boards = self.nextBoards(tree.board)
            for child_board in child_boards:
                key = child_board.hash()
                if key in traversed:
                    continue

                child_tree = Tree(tree, child_board)

                if self.isAnswer(child_board):
                    return child_tree.sourceBoard()

                traversed.add(key)
                next_forest.append(child_tree)
                self.state_count = self.state_count + 1

        print(" 正在计算，搜索深度:%d, 当前局面数:%d, 总局面数:%d" %  (level, len(next_forest), self.state_count))
        if len(next_forest) == 0:
            return []

        return self.dfs(next_forest, traversed, level + 1)

    def moveUp(self, card, board):
        if card.isTopMost():
            return None

        # 进入区域为顶边偏移-1，离开区域为底边，偏移值得 为(0,-1)
        above_tops = [(x, y - 1) for (x, y) in card.getTopLines()]
        return self.move(card, board, above_tops, card.getBottomLines(), 0, -1)

    def moveDown(self, card, board):
        if card.isBottomMost():
            return None

        # 进入区域为低边偏移+1，离开区域为顶边边，偏移值得 为(0,+1)
        below_bottoms = [(x, y + 1) for (x, y) in card.getBottomLines()]
        return self.move(card, board, below_bottoms, card.getTopLines(), 0, 1)

    def moveLeft(self, card, board):
        if card.isLeftMost():
            return None

        # 进入区域为做边偏移-1，离开区域为右边边，偏移值得 为(-1,0)
        left_of_left = [(x - 1, y) for (x, y) in card.getLeftLines()]
        return self.move(card, board, left_of_left, card.getRightLines(), -1, 0)

    def moveRight(self, card, board):
        if card.isRightMost():
            return None

        # 进入区域为右边偏移+1，离开区域为左边，偏移值得 为(1,0)
        right_of_right = [(x + 1, y) for (x, y) in card.getRightLines()]

        return self.move(card, board, right_of_right, card.getLeftLines(), 1, 0)

    def move(self, card, board, enter_points, leave_points, offset_x, offset_y):
        # 进入的空间要求为空白
        if not board.isAllBlanks(enter_points):
            return None

        new_card = card.clone()
        new_card.move(offset_x, offset_y)

        new_board = board.clone()
        new_board.updateCard(new_card)
        new_board.updateBlanks(enter_points, leave_points)

        return new_board

    def nextBoards(self, board):
        boards = []

        def storageWithCheck(boards, board):
            if board != None:
                boards.append(board)

        for role, card in board.cards.items():
            card = board.cards[role]

            storageWithCheck(boards, self.moveUp(card, board))
            storageWithCheck(boards, self.moveDown(card, board))
            storageWithCheck(boards, self.moveLeft(card, board))
            storageWithCheck(boards, self.moveRight(card, board))

        return boards

    def isAnswer(self, board):
        caocao = board.cards['C']
        return (caocao.x, caocao.y)  == (1,3)

class Tree:
    def __init__(self, parent, board):
        self.parent = parent
        self.board = board

    def sourceBoard(self):
        if self.parent == None:
            return [self.board]

        sources = self.parent.sourceBoard()
        sources.append(self.board)

        return sources
