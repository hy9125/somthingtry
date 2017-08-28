# coding:utf-8


# for关键词复制操作可能会影响列表推导式的值，这种在python3中不会出现

#  for 循环的先后影响结果的先后

#  tshirts = [(color,size) for color in colors for size in sizes]

# tuple 可以把他当做记录信息的东西

t = (1, 2, [30, 40])
t[2] += [50, 60]

# 会有两个结果，报错的同时会加上 t=(1,2,[30,40,50,60])

# list.sort 会返回NONE 而sorted会返回新列表

