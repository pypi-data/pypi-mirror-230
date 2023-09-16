# mupy 使用指南

mupy，An many/more extension/utils for python，是 python 语言下的多工具集合。

## 基本

- glb

  全局变量。

- istuple
- islist
- isndarray
- isdict
- isfunc
- isvalue
- isbool

- reverseTuple
- rndStr
- toBool
- toValue
- toStr
- 

## clipboard

## disk

## mp

## socket

## 函数是类？

有些函数实际上是类。

因 python 实例化一个类不需要 new，使用起来跟函数差不多。

但类的 `__init__` 可以多次重载，就实现了函数参数的多样化，且不需要用 `*args,**kwargs` 这样的结构，更方便，注释文档也更好写。

其实 python 内部也有很多这种做法，比如常见的 range 函数，其实就是一个类。