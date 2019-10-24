from numpy import *


def load_data():
    dataSet = [['bread', 'milk', 'vegetable', 'fruit', 'eggs'],
               ['noodle', 'beef', 'pork', 'water', 'socks', 'gloves', 'shoes', 'rice'],
               ['socks', 'gloves'],
               ['bread', 'milk', 'shoes', 'socks', 'eggs'],
               ['socks', 'shoes', 'sweater', 'cap', 'milk', 'vegetable', 'gloves'],
               ['eggs', 'bread', 'milk', 'fish', 'crab', 'shrimp', 'rice']]
    return dataSet


# 扫描全部数据，产生c1
def create_c1(data):
    c1 = []
    for transaction in data:
        for item in transaction:
            if [item] not in c1:
                c1.append([item])
    c1.sort()
    return list(map(frozenset, c1))


# 由c（i）生成对应的l（i）
def c2l(data, ck, min_support):
    dict_sup = {}
    for i in data:
        for j in ck:
            if j.issubset(i):
                if j not in dict_sup:
                    dict_sup[j] = 1
                else:
                    dict_sup[j] += 1
    support_data = {}
    result_list = []
    for i in dict_sup:
        temp_sup = dict_sup[i] / len(data)
        if temp_sup >= min_support:
            result_list.append(i)
            support_data[i] = temp_sup
    return result_list, support_data


# 由l（k-1）生成c（k）
def get_next_c(Lk, k):
    result_list = []
    len_lk = len(Lk)
    for i in range(len_lk):
        for j in range(i + 1, len_lk):
            l1 = list(Lk[i])[:k]
            l2 = list(Lk[j])[:k]
            if l1 == l2:
                a = Lk[i] | Lk[j]
                a1 = list(a)
                b = []
                for q in range(len(a1)):
                    t = [a1[q]]
                    tt = frozenset(set(a1) - set(t))
                    b.append(tt)
                t = 0
                for w in b:
                    if w in Lk:
                        t += 1
                if t == len(b):
                    result_list.append(b[0] | b[1])
    return result_list


# 得到所有的l集
def get_all_l(data_set, min_support):
    c1 = create_c1(data_set)
    data = list(map(set, data_set))
    L1, support_data = c2l(data, c1, min_support)
    L = [L1]
    k = 2
    while (len(L[k - 2]) > 0):
        Ck = get_next_c(L[k - 2], k - 2)
        Lk, sup = c2l(data, Ck, min_support)
        support_data.update(sup)
        L.append(Lk)
        k += 1
    del L[-1]
    return L, support_data


# 得到所有L集的子集
def get_subset(from_list, result_list):
    for i in range(len(from_list)):
        t = [from_list[i]]
        tt = frozenset(set(from_list) - set(t))
        if tt not in result_list:
            result_list.append(tt)
            tt = list(tt)
            if len(tt) > 1:
                get_subset(tt, result_list)


# 计算置信度
def calc_conf(freqSet, H, supportData, min_conf):
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet - conseq]
        lift = supportData[freqSet] / (supportData[conseq] * supportData[freqSet - conseq])
        if conf >= min_conf and lift > 1:
            print(set(freqSet - conseq), '-->', set(conseq), '支持度', round(supportData[freqSet - conseq], 2), '置信度：',
                  conf)


# 生成规则
def gen_rule(L, support_data, min_conf=0.7):
    for i in range(len(L)):
        print("\n", i + 1, "-频繁项集为：")
        for freqSet in L[i]:
            print(set(freqSet), end="  ")
    print("\n")
    for i in range(1, len(L)):
        for freqSet in L[i]:
            H1 = list(freqSet)
            all_subset = []
            get_subset(H1, all_subset)
            calc_conf(freqSet, all_subset, support_data, min_conf)


if __name__ == '__main__':
    dataSet = load_data()
    L, supportData = get_all_l(dataSet, 0.5)
    gen_rule(L, supportData, 0.6)
