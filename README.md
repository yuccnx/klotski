# klotski

## 需求来源

## 初步建模
面板大小为 4 X 5 的数组，角色我们称为卡片。
我们观察角色有：曹操、关羽、张飞、黄忠、马超和4个卒（为了表示方便，四个卒我们认为是四个不同角色）。
用一个二维数组表示游戏状态，我们就需要为每个角色定义一个值。
角色值定义，卒用小写字母表示（谁叫你不是大佬？），大将们用大写字母表示，空白用0 表示，如下：
```python
 # "0"：空
 # "a"：卒1
 # "b"：卒2
 # "c"：卒3
 # "d"：卒4
 # "M"：马超
 # "H"：黄忠
 # "Z"：张飞
 # "Y"：赵云
 # "G"：关羽
 # "C"：曹操
 ```

除了0值，其他相邻的相同值，我们认为是不可分割的一块，根据定义，我们构造其中一个初始化局面如下：
```python
[
  ["H","C","C","Y"],
  ["H","C","C","Y"],
  ["Z","G","G","M"],
  ["Z","b","c","M"],
  ["a","0","0","d"]
]
```

从初始状态开始，遍历每个可以移动的卡片进行下一个状态生成，得到一个状态树。
（图）

最终生成树下如果把“曹操”角色移动到（1，3）、（2，3）（1，4）、（2，4）表示结果了。

## 抽象对象化
如何从一个状态生成另一个状态？如果用上面的一个二维数组来做逻辑处理，是需要考虑比较多的，如：除了0，相同的值移动需要一起移动；移动向的领域不能超出4X5区域范围并且目标要是0；离开的区域，需要设置为0 等等。基于二维数组状态表做这些逻辑处理，略微复杂，我们将他们简化。

细想华容道游戏，包含一个面板，多个角色卡片，和两个空白位置这几种不同数据。我们如何把 面板、角色卡片、空白点 这三类有机的组合起来？
1、从卡片开始，我们定义一个Card 对象，它有角色值，有位置，有大小；

```python
class Card:
    def __init__(self, role, x, y, width, height):
        self.role = role

        self.x = x
        self.y = y
        self.width = width
        self.height = height

```

2、空白点好说，就是定义为（x，y） 这样的一个元组即可，不用过多设计。

3、面板上包含属性有卡片，和空白点。卡片角色值是唯一的，用一个dir(role:Card) 表示；还有两个空白点，由于空白点也是唯一的，为了运算方便，我们把它定义到集合set 里面。

代码：

```python
class Board:
    '''
    cards: dir{role:card}
    blanks:set((x,y))
    '''
    def __init__(self, cards, blanks):
        self.cards = {card.role:card for card in cards}
        self.blanks = blanks
```

对比目前的 Board 对象和前面的状态state数组，它们表示是完全等价的。但对象化之后，操作逻辑已经大大简化，例如面板上移动一个卡片，就是对card 进行x，y进行加减操作，对空白位置的替换，如提供 move 函数。

```python
class Card:
	# 若干代码
    def move(self, offset_x, offset_y):
        self.x = self.x + offset_x
        self.y = self.y + offset_y
```

对比要对state 数组操作，都会清晰明了很多。

还需要抽象一个game 来做游戏总控制
```python
class Game:
    def __init__(self):
```

## 主要逻辑
再来整理下建模游戏的主要逻辑，由于华容道答案是期望寻求最短路径的，所以需要一个广度优先算法。
从初始化局面（根局面）开始：
1 枚举每个卡片，对每个卡片进行上下左右可移动判断，并生成所有可能状态局面，记录到列表；
2 对每个生成状态局面进行判断，如果是答案，则返回“演化”历史；如果不是，则记录到“下一层”遍历列表；
3 对“下一层”遍历列表每个状态局面进行递归处理，回到步骤 1。


简单说说可移动判断逻辑，比如一个卡片想往上移动，它能往上移动的条件是什么？1）卡片本身不能在最贴顶部；2）卡片顶边的上方，每个格子都没有其他卡片，看状态二维数组，就是状态为“0”，在 Board 对象来看，就是上方的（x，y）点，都在 Board.blanks 内。清理好思路后，逻辑就简单了，如下：
```python
class Card:
	# 判断是否已经到顶部
	def isTopMost(self):
        return self.y == 0

	# 求顶边各个点
    def getTopLines(self):
        return [(self.x + i, self.y) for i in range(self.width)]

```
向上移动，如果是顶部了，则不能往上移动，否则，回去顶部各点的上方一格，并且判断上一个是空白，则可以移动了

```python
class Game:
    def moveUp(self, card, board):
        if card.isTopMost():
            return None

        # 进入区域为顶边偏移-1，离开区域为底边，偏移值得 为(0,-1)
        above_tops = [(x, y - 1) for (x, y) in card.getTopLines()]
        return self.move(card, board, above_tops, card.getBottomLines(), 0, -1)

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
```

递归算法
```python
    def dfs(self, forest, traversed):
        next_forest = []

        for tree in forest:
            child_boards = self.nextBoards(tree.board)
            for child_board in child_boards:
                child_tree = Tree(tree, child_board)

                if self.isAnswer(child_board):
                    return child_tree.sourceBoard()

                next_forest.append(child_tree)

        if len(next_forest) == 0:
            return []

        return self.dfs(next_forest, traversed)
```

由于答案需要记录演化历史，也就是需要从最后答案状态，需要往上回溯树父节点一直到根节点（初始状态），所以需要设计一种倒挂树——不记录子节点，而记录父亲节点

## 美化

## 完整代码分享

github 链接：https://github.com/yuccnx/klotski

