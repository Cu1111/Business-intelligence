# 加入数据
def load_dataset():
    dataSet = [['bread', 'milk', 'vegetable', 'fruit', 'eggs'],
               ['noodle', 'beef', 'pork', 'water', 'socks', 'gloves', 'shoes', 'rice'],
               ['socks', 'gloves'],
               ['bread', 'milk', 'shoes', 'socks', 'eggs'],
               ['socks', 'shoes', 'sweater', 'cap', 'milk', 'vegetable', 'gloves'],
               ['eggs', 'bread', 'milk', 'fish', 'crab', 'shrimp', 'rice']]
    return dataSet


# 转化为frozenset使之可以为字典的key便于之后操作
def transfer_to_frozenset(data_set):
    frozen_data_set = {}
    for elem in data_set:
        frozen_data_set[frozenset(elem)] = 1
    return frozen_data_set


class TreeNode:
    def __init__(self, nodeName, count, nodeParent):
        self.nodeName = nodeName
        self.count = count
        self.nodeParent = nodeParent
        self.nextSimilarItem = None
        self.children = {}

    def increaseC(self, count):
        self.count += count

    def disp(self, ind=1):
        print('  ' * ind, self.nodeName, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


def createFPTree(frozenDataSet, minSupport):
    headPointTable = {}
    for items in frozenDataSet:
        for item in items:
            headPointTable[item] = headPointTable.get(item, 0) + frozenDataSet[items]
    headPointTable = {k: v for k, v in headPointTable.items() if v >= minSupport}
    frequentItems = set(headPointTable.keys())
    if len(frequentItems) == 0: return None, None

    for k in headPointTable:
        headPointTable[k] = [headPointTable[k], None]
    fptree = TreeNode("null", 1, None)
    # scan dataset at the second time, filter out items for each record
    for items, count in frozenDataSet.items():
        frequentItemsInRecord = {}
        for item in items:
            if item in frequentItems:
                frequentItemsInRecord[item] = headPointTable[item][0]
        if len(frequentItemsInRecord) > 0:
            orderedFrequentItems = [v[0] for v in
                                    sorted(frequentItemsInRecord.items(), key=lambda v: v[1], reverse=True)]
            updateFPTree(fptree, orderedFrequentItems, headPointTable, count)

    return fptree, headPointTable


def updateFPTree(fptree, orderedFrequentItems, headPointTable, count):
    # handle the first item
    if orderedFrequentItems[0] in fptree.children:
        fptree.children[orderedFrequentItems[0]].increaseC(count)
    else:
        fptree.children[orderedFrequentItems[0]] = TreeNode(orderedFrequentItems[0], count, fptree)

        # update headPointTable
        if headPointTable[orderedFrequentItems[0]][1] == None:
            headPointTable[orderedFrequentItems[0]][1] = fptree.children[orderedFrequentItems[0]]
        else:
            updateHeadPointTable(headPointTable[orderedFrequentItems[0]][1], fptree.children[orderedFrequentItems[0]])
    # handle other items except the first item
    if (len(orderedFrequentItems) > 1):
        updateFPTree(fptree.children[orderedFrequentItems[0]], orderedFrequentItems[1::], headPointTable, count)


def updateHeadPointTable(headPointBeginNode, targetNode):
    while (headPointBeginNode.nextSimilarItem != None):
        headPointBeginNode = headPointBeginNode.nextSimilarItem
    headPointBeginNode.nextSimilarItem = targetNode


def mineFPTree(headPointTable, prefix, frequentPatterns, minSupport):
    headPointItems = [v[0] for v in sorted(headPointTable.items(), key=lambda v: v[1][0])]
    if (len(headPointItems) == 0): return

    for headPointItem in headPointItems:
        newPrefix = prefix.copy()
        newPrefix.add(headPointItem)
        support = headPointTable[headPointItem][0]
        frequentPatterns[frozenset(newPrefix)] = support

        prefixPath = getPrefixPath(headPointTable, headPointItem)
        if (prefixPath != {}):
            conditionalFPtree, conditionalHeadPointTable = createFPTree(prefixPath, minSupport)
            if conditionalHeadPointTable != None:
                mineFPTree(conditionalHeadPointTable, newPrefix, frequentPatterns, minSupport)


def getPrefixPath(headPointTable, headPointItem):
    prefixPath = {}
    beginNode = headPointTable[headPointItem][1]
    prefixs = ascendTree(beginNode)
    if ((prefixs != [])):
        prefixPath[frozenset(prefixs)] = beginNode.count

    while (beginNode.nextSimilarItem != None):
        beginNode = beginNode.nextSimilarItem
        prefixs = ascendTree(beginNode)
        if (prefixs != []):
            prefixPath[frozenset(prefixs)] = beginNode.count
    return prefixPath


def ascendTree(treeNode):
    prefixs = []
    while ((treeNode.nodeParent != None) and (treeNode.nodeParent.nodeName != 'null')):
        treeNode = treeNode.nodeParent
        prefixs.append(treeNode.nodeName)
    return prefixs


def rulesGenerator(frequentPatterns, minConf, rules, data_length):
    for frequentset in frequentPatterns:
        if (len(frequentset) > 1):
            getRules(frequentset, frequentset, rules, frequentPatterns, minConf, data_length)


def remove_str(set, str):
    tempSet = []
    for elem in set:
        if (elem != str):
            tempSet.append(elem)
    tempFrozenSet = frozenset(tempSet)
    return tempFrozenSet


def getRules(frequentset, currentset, rules, frequentPatterns, minConf, data_length):
    for frequentElem in currentset:
        subSet = remove_str(currentset, frequentElem)
        confidence = frequentPatterns[frequentset] / frequentPatterns[subSet]
        lift = frequentPatterns[frequentset] / (
                frequentPatterns[subSet] * (frequentPatterns[frozenset([frequentElem])] / data_length))
        if confidence >= minConf and lift > 1:
            flag = False
            for rule in rules:
                if rule[0] == subSet and rule[1] == frequentset - subSet:
                    flag = True
            if not flag:
                rules.append((subSet, frequentset - subSet, confidence))
            if len(subSet) >= 2:
                getRules(frequentset, subSet, rules, frequentPatterns, minConf, data_length)


def take_num(elem):
    return len(elem)


if __name__ == '__main__':
    print("fptree:")
    dataSet = load_dataset()
    frozenDataSet = transfer_to_frozenset(dataSet)
    minSupport = 3
    fptree, headPointTable = createFPTree(frozenDataSet, minSupport)
    fptree.disp()
    frequentPatterns = {}
    prefix = set([])
    mineFPTree(headPointTable, prefix, frequentPatterns, minSupport)
    print("频繁项集：")
    pattern_list = []
    for pattern in frequentPatterns:
        pattern_list.append(list(set(pattern)))
    pattern_list.sort(key=take_num)
    for list_item in pattern_list:
        print(list_item, end=" ")
    minConf = 0.6
    rules = []
    rulesGenerator(frequentPatterns, minConf, rules, len(dataSet))
    print("\n关联规则：")
    for rule in rules:
        print(set(rule[0]), '-->', set(rule[1]), "置信度为：", rule[2])
