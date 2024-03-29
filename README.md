# klotski

## 需求来源
某天娃拿着华容道板块来,喊她爹我求解，大概如图这样的一个东西，我：...,一把年纪了，和你玩这个破东西？自己一边玩去。

![avatar](images/views/source.jpg)

花了一支烟时间想了下，算了，帮你写一个程序来破解吧，后面别来烦我就行了。

## 初步建模
面板大小为 4 X 5 的数组，角色我们称为卡片。
我们观察角色有：曹操、关羽、张飞、黄忠、马超和4个卒（为了表示方便，四个卒我们认为是四个不同角色）。
用一个二维数组表示游戏状态，为每个角色定义一个值。
角色值定义，卒用小写字母表示（谁叫你不是大佬？），大将们用大写字母表示，空白用 0 表示。（其实如何定义都没关系，主要是为了方便阅读和同名不冲突）
如下：
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

除了 0 值，其他相邻的相同值，我们认为是不可分割的一块，根据定义，我们构造其中一个初始化局面如下：
```python
[
  ["H","C","C","Y"],
  ["H","C","C","Y"],
  ["Z","G","G","M"],
  ["Z","b","c","M"],
  ["a","0","0","d"]
]
```



从初始状态开始，遍历每个可以移动的卡片进行下一个状态生成，得到一个状态树:

![avatar](images/views/tree.png)

最终生成树下如果把“曹操”角色移动到（1，3）、（2，3）（1，4）、（2，4）（如下图,蓝色数据移动到红色位置）表示结束，拿到答案了:

![avatar](images/views/result_post.png)

## 抽象对象化
在状态树图中，如何从一个状态生成另一个状态？如果用上面的一个二维数组来做逻辑处理，比较复杂，如：
 1） 除了0，相同的值的移动需要一起移动；
 2） 移动向的领域不能超出4X5区域范围并且目标要是0（空白）；
 3） 离开的区域，需要设置为0 等等。

基于二维数组做这些状态表逻辑处理，略微复杂，将它们抽象简化下。

细想华容道游戏，包含一个面板，多个角色卡片，和两个空白位置这几种不同数据。我们如何把"面板"、"角色卡片"、"空白点"这三类有机的组合起来？步骤如下：

1）从卡片开始，我们定义一个Card 对象，它有角色值，有位置，有大小；

```python
class Card:
    def __init__(self, role, x, y, width, height):
        self.role = role

        self.x = x
        self.y = y
        self.width = width
        self.height = height

```

2）空白点较为简单，定义为（x，y） 这样的一个元组即可，不过多设计了。

3）面板上包含属性有卡片，和空白点。卡片角色值是唯一的，用一个dir(role:Card) 表示角色；还有两个空白点，由于空白点也是唯一的，为了运算方便，我们把它定义到集合set 里面。

面板模型代码：

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

目前的 Board 对象和前面的状态state数组，它们表示是完全等价的。对象化之后，操作逻辑大大简化了，例如面板上移动一个卡片，就是两个步骤：
1）对card 进行x，y进行加减操作（如Card提供 move 函数）；
2）对进入区域和离开区域的空白位置的替换。

```python
class Card:
    # 若干代码
    def move(self, offset_x, offset_y):
        self.x = self.x + offset_x
        self.y = self.y + offset_y
```

相对原来的要对 state 数组操作，清晰明了很多。

## 主要逻辑
再来整理下建模游戏的主要逻辑，由于华容道答案是期望寻求最短路径的，所以需要一个广度优先算法。
从初始化局面（根局面）开始：
 1）枚举每个卡片，对每个卡片进行上下左右可移动判断，并生成所有可能状态局面，记录到列表；
 2）对每个生成状态局面进行判断，如果是答案，则返回“演化”历史；如果不是，则记录到“下一层”遍历列表；
 3）对“下一层”遍历列表每个状态局面进行递归处理，回到步骤 1)。


简单说说可移动判断逻辑，比如一个卡片想往上移动，它能往上移动的条件是什么？
 1）卡片本身不能在最贴顶部；
 2）卡片顶边的上方，每个格子都没有其他卡片，看状态二维数组，就是状态为“0”，在 Board 对象来看，就是上方的（x，y）点，都在 Board.blanks 内。

 整理好思路后，逻辑就简单了：
```python
class Card:
    # 判断是否已经到顶部
    def isTopMost(self):
        return self.y == 0

    # 求顶边各个点
    def getTopLines(self):
        return [(self.x + i, self.y) for i in range(self.width)]

    # ... 其他很多代码

```

向上移动，如果是顶部了，则不能往上移动；否则，获取顶部各点的上方一格，并且判断上一个是空白，则可以移动了。
还需要抽象一个game 来做游戏总控制。

```python
class Game:
    def __init__(self):
        pass

    # 返回移动后的状态，None 表示非法移动
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

递归算法，采用广度优先遍历，枚举每个局面，核心代码就是这么一点了：
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

由于答案需要回缩演化历史，也就是需要从最后答案状态，需要往上回溯树父节点一直到根节点（初始状态），所以需要设计一种倒挂树——不记录子节点，而记录父亲节点：
```python
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
```

## 算法优化
1）由于移动卡片时候，移动先后两个卡片几次后，可能会出现两个面板是一样的，所以针对每个局面进行hash 记录，历史上出现过了，不需要再做便利，可以大大减少局面遍历量。
2）形状相同的两个卡片，如果出现了位置调换，两个盘面其实是等价的，我们认为两个卡片是等价的，所以他们hash 记录理应一样，省去不必要的遍历。

代码见Board.hash() 相关逻辑。
相同的两个状态，没有优化的情况下，跑一个小时还没有出结果，做了这两点优化后，约10秒出结果。优化效果是比较客观的。

## 输出界面
本来想简单偷懒点，用个文字替换输出的，这个样子：

![avatar](images/views/text_view.jpg)

但考虑娃看不懂这种“高级”的幽默，我不得不又花了她爸的一个多小时去抠图，然后编码...刷刷刷～弄了个6岁儿童能看得懂的界面效果：

![avatar](images/views/image_view.png)

## 完整代码分享
不多说了，上代码吧。

github 链接：https://github.com/yuccnx/klotski

