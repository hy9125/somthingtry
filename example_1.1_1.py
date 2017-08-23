# coding:utf-8
'''
 一摞有序的纸牌
'''
import collections

# 构造一个简单的类来表示纸牌
Card = collections.namedtuple('Card', ['rank', 'suit'])
# namedtuple 构造只有少数属性但是没有方法的对象

class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamods clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits]
        self.suit_value = dict(spades=3, hearts=2, diamods=1, clubs=0)

    def __len__(self):
        return len(self._cards)

    # 提供数组取值
    def __getitem__(self, position):
        return self._cards[position]

    def spades_high(self, card):
        rank_vaule = FrenchDeck.ranks.index(card.rank)
        return rank_vaule * len(self.suit_value) + self.suit_value[card.suit]

    def run(self):
        for card in sorted(deck, key=self.spades_high):
            print card

if __name__ == '__main__':
    deck = FrenchDeck()
    #print len(deck)
    # 此时的deck 是一个数组，可以进行数组操作

    print deck.run()

## 洗牌功能待实现

## python 内置函数pepr能把一个对象用字符串表达出来