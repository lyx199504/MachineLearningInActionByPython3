#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/1/17 15:54
# @Author : LYX-夜光

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print(' '*ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind+1)

# 初始化数据
def createInitSet(dataSet):
    dataDict = {}
    for trans in dataSet:
        dataDict[frozenset(trans)] = 1
    return dataDict

# 创建FP树
def createTree(dataDict, minSup=1):
    headerTable = {}
    for trans in dataDict:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataDict[trans]
    for item in list(headerTable.keys()):  # 去掉小于支持量的元素
        if headerTable[item] < minSup:
            del headerTable[item]
    freqItemSet = set(headerTable.keys())  # 满足支持量的元素集合
    if len(freqItemSet) == 0:
        return None, None
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]
    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataDict.items():
        localD = {}
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0]  # 每组数据满足支持量的元素
        if len(localD) > 0:
            # 根据每个元素出现的次数大小进行排序，组合成元素列表
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda x: x[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable

def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:  # 子节点包含第一个元素
        inTree.children[items[0]].inc(count)
    else:  # 子节点不包含第一个元素，则构造子树
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] is None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:  # 继续构造子节点的子节点
        updateTree(items[1:], inTree.children[items[0]], headerTable, count)

# 找出所有同名节点
def updateHeader(nodeToTest, targetNode):
    while nodeToTest.nodeLink is not None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

# 递归获取双亲名称
def ascendTree(leafNode, prefixPath):
    if leafNode.parent is not None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

# 获取所有双亲集合
def findPrefixPath(treeNode):
    condPats = {}
    while treeNode is not None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

# 递归查找频繁项集
def mineTree(headerTable, minSup, prefix, freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda x: x[1][0])]
    for basePat in bigL:
        newFreqSet = prefix.copy()
        newFreqSet.add(basePat)  # 关联元素加到集合中
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(headerTable[basePat][1])  # 获取所有双亲集合
        _, myHead = createTree(condPattBases, minSup)  # 再用双亲集合构造树
        if myHead is not None:  # 用双亲集合构造的树再递归查找，最终freqItemList得到所有关联集合
            mineTree(myHead, minSup, newFreqSet, freqItemList)

if __name__ == "__main__":
    dataSet = [['r', 'z', 'h', 'j', 'p'],
               ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
               ['z'],
               ['r', 'x', 'n', 'o', 's'],
               ['y', 'r', 'x', 'z', 'q', 't', 'p'],
               ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    dataDict = createInitSet(dataSet)
    FPtree, headerTable = createTree(dataDict, 3)
    FPtree.disp()
    freqItems = []
    mineTree(headerTable, 3, set([]), freqItems)
    print(freqItems)