from math import log
import operator
import treePlotter
# 类别计数
def classCount(dataSet):
    # labelCount字典用来存放分类结果的标签----Y/N
    labelCount={}
    for one in dataSet:
        if one[-1] not in labelCount.keys():
            labelCount[one[-1]]=0
        labelCount[one[-1]]+=1
    return labelCount

# 计算信息熵
def calcShannonEntropy(dataSet):
    labelCount=classCount(dataSet)
    numEntries=len(dataSet)  # 元素的个数
    Entropy=0.0  # 存放信息熵的值
    for i in labelCount:
        prob=float(labelCount[i])/numEntries
        Entropy-=prob*log(prob,2)
    return Entropy

# 获得一个数据集中类别标签最多的类
def majorityClass(dataSet):
    labelCount=classCount(dataSet)
    # 以每个分类的数量进行排序(Y和N各自的数量),降序排列
    sortedLabelCount=sorted(labelCount.items(), key=operator.itemgetter(1), reverse=True)
    return sortedLabelCount[0][0]  # 找出为Y

def splitDataSet(dataSet,i,value):
    subDataSet=[] # 用来存储筛选后的结果
    for one in dataSet:
        if one[i]==value:
            reduceData=one[:i]
            reduceData.extend(one[i+1:])
            subDataSet.append(reduceData)  # 选择出符合条件的行
    return subDataSet

# 分裂连续数据集
def splitContinuousDataSet(dataSet,i,value,direction):
    subDataSet=[] # 用来存储筛选后的结果
    for one in dataSet:
        if direction==0:
            if one[i]>value:
                reduceData=one[:i]
                reduceData.extend(one[i+1:])
                subDataSet.append(reduceData)  # 选出>value的行
        if direction==1:
            if one[i]<=value:
                reduceData=one[:i]
                reduceData.extend(one[i+1:])
                subDataSet.append(reduceData)   # 选出<=value的行
    return subDataSet

# 选择最佳节点
def chooseBestFeat(dataSet,labels):
    baseEntropy=calcShannonEntropy(dataSet)  # 计算原始信息熵
    bestFeat=0    # 用来存储获取最大信息增益时所对应的特征
    baseGainRatio=-1  # 用来存储获取的最大信息增益
    numFeats=len(dataSet[0])-1   # 特征的数量
    bestSplitDic={}  # 用来存储特征以及相应的值
    i=0
    for i in range(numFeats):
        featVals=[example[i] for example in dataSet]  # 遍历每一个特征
        # 判断特征的类型
        if type(featVals[0]).__name__=='float' or type(featVals[0]).__name__=='int':  # 特征为数值
            j=0
            sortedFeatVals=sorted(featVals)  # 对特征进行排序
            splitList=[]
            for j in range(len(featVals)-1):
                splitList.append((sortedFeatVals[j]+sortedFeatVals[j+1])/2.0)  # 求两两之间的中间值(数值型的特征要离散化为标称型)
            for j in range(len(splitList)):
                newEntropy=0.0  # 存储新的信息熵
                gainRatio=0.0   # 信息增益
                splitInfo=0.0   # 特征的信息熵
                value=splitList[j]
                subDataSet0=splitContinuousDataSet(dataSet,i,value,0)  # 子数据集0
                subDataSet1=splitContinuousDataSet(dataSet,i,value,1)  # 子数据集1
                prob0=float(len(subDataSet0))/len(dataSet)  # 子数据集0的占比
                newEntropy-=prob0*calcShannonEntropy(subDataSet0)  # 子集的信息熵
                prob1=float(len(subDataSet1))/len(dataSet)  # 子数据集1的占比
                newEntropy-=prob1*calcShannonEntropy(subDataSet1)  # 子集的信息熵
                splitInfo-=prob0*log(prob0,2)
                splitInfo-=prob1*log(prob1,2)  # 使用该特征划分数据的信息熵
                gainRatio=float(baseEntropy-newEntropy)/splitInfo  # 该特征划分数据集的信息增益

                if gainRatio>baseGainRatio:  # 判断是否为最大信息增益
                    baseGainRatio=gainRatio
                    bestSplit=j
                    bestFeat=i
            bestSplitDic[labels[i]]=splitList[bestSplit]
        else:  # 特征为标称（挑选过程基本相同）
            uniqueFeatVals=set(featVals)  # 创建集合
            GainRatio=0.0  # 信息增益
            splitInfo=0.0  # 特征的信息熵
            newEntropy=0.0  # 存储新的信息熵
            for value in uniqueFeatVals:
                subDataSet=splitDataSet(dataSet,i,value)
                prob=float(len(subDataSet))/len(dataSet)
                splitInfo-=prob*log(prob,2)
                newEntropy-=prob*calcShannonEntropy(subDataSet)
            gainRatio=float(baseEntropy-newEntropy)/splitInfo
            if gainRatio > baseGainRatio:
                bestFeat = i
                baseGainRatio = gainRatio
    if type(dataSet[0][bestFeat]).__name__=='float' or type(dataSet[0][bestFeat]).__name__=='int':
        bestFeatValue=bestSplitDic[labels[bestFeat]]
    if type(dataSet[0][bestFeat]).__name__=='str':
        bestFeatValue=labels[bestFeat]
    return bestFeat,bestFeatValue


# 创建决策树
def createTree(dataSet,labels):
    classList=[example[-1] for example in dataSet]  # 最终判断的结果类型Y/N
    if len(set(classList))==1:  # 结果只有一种
        return classList[0][0]
    if len(dataSet[0])==1:  # 没有特征
        return majorityClass(dataSet)  # 显示概率最大的
    Entropy = calcShannonEntropy(dataSet)  # 计算信息熵
    bestFeat,bestFeatLabel=chooseBestFeat(dataSet,labels)  # 计算最优的节点

    myTree={labels[bestFeat]:{}}
    subLabels = labels[:bestFeat]
    subLabels.extend(labels[bestFeat+1:])  # 去除该节点后，剩余的特征

    # 判断特征类型
    if type(dataSet[0][bestFeat]).__name__=='str':
        featVals = [example[bestFeat] for example in dataSet]
        uniqueVals = set(featVals)  # 该特征值下的类型
         # 去除该特征后的部分训练集
        for value in uniqueVals:
            reduceDataSet=splitDataSet(dataSet,bestFeat,value)

            myTree[labels[bestFeat]][value]=createTree(reduceDataSet,subLabels)
    if type(dataSet[0][bestFeat]).__name__=='int' or type(dataSet[0][bestFeat]).__name__=='float':  # 与上述基本相同
        value=bestFeatLabel
        greaterDataSet=splitContinuousDataSet(dataSet,bestFeat,value,0)
        smallerDataSet=splitContinuousDataSet(dataSet,bestFeat,value,1)

        myTree[labels[bestFeat]]['>' + str(value)] = createTree(greaterDataSet, subLabels)

        myTree[labels[bestFeat]]['<=' + str(value)] = createTree(smallerDataSet, subLabels)
    return myTree
# 创建训练集
def createDataSet():
    # 输入训练集的数据
    dataSet = [['sunny',    '85', '85', 'FALSE', 'N'],
               ['sunny',    '80', '90', 'TRUE', 'N'],
               ['overcast', '83', '86', 'FALSE', 'Y'],
               ['rainy',    '70', '96', 'FALSE', 'Y'],
               ['rainy',    '68', '80', 'FALSE', 'Y'],
               ['rainy',    '65', '70', 'TRUE', 'N'],
               ['overcast', '64', '65', 'TRUE', 'Y'],
               ['sunny',    '72', '95', 'FALSE', 'N'],
               ['sunny',    '60', '70', 'FALSE', 'Y'],
               ['rainy',    '75', '80', 'FALSE', 'Y'],
               ['sunny',    '75', '70', 'TRUE', 'Y'],
               ['overcast', '72', '90', 'TRUE', 'Y'],
               ['overcast', '81', '75', 'FALSE', 'Y'],
               ['rainy',    '71', '91', 'TRUE', 'N']]
# 训练集各数据的含义
    labels = ['天气', '温度','湿度','刮风','适合运动']  # 四个特征
    return dataSet, labels
# 构建测试集
def createTestSet():
    testSet = [['overcast', '85', '85', 'FALSE'],
               ['rainy', '80', '90', 'TRUE'],
               ['overcast', '87', '91', 'FALSE'],
               ['rainy', '70', '96', 'TRUE'],
               ['rainy', '80', '80', 'FALSE'],
               ['rainy', '65', '70', 'FALSE'],
               ['overcast', '64', '65', 'TRUE'],
               ['sunny', '72', '95', 'FALSE'],
               ['sunny', '60', '70', 'FALSE'],
               ['rainy', '75', '80', 'TRUE']]

    return testSet
# 根据构建的树判断结果
def classify(inputTree,featLabels,testVec):
    global classLabel
    firstStr = list(inputTree.keys())[0]   #最顶层的特征
    secondDict = inputTree[firstStr]    #该特征下的子节点
    featIndex = featLabels.index(firstStr)  #判断该特征是否为已有特征之一
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':  # 若有其他判断条件继续划分
                classLabel = classify(secondDict[key], featLabels, testVec)
            else:
                classLabel = secondDict[key]
    return classLabel

# 将测试集拆分为单条数据
def classifyAll(inputTree,featLabels,testDataSet):
    classLabeAll=[]  # 存储测试集的结果
    for testVec in testDataSet:
        classLabeAll.append(classify(inputTree,featLabels,testVec))
    return classLabeAll

if __name__ == '__main__':
    dataSet, labels = createDataSet()
    labels_tmp = labels[:]
    myTree = createTree(dataSet, labels_tmp)
    treePlotter.createPlot(myTree)
    print(myTree)
    testSet = createTestSet()
print(classifyAll(myTree, labels, testSet))
