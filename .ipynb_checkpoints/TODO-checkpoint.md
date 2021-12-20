# 基本想法

每个节点代表的是一种变量激活方式，根节点表示所有变量都激活(即都有概率被选择)。根据实际被选择变量采样样本和补样本(补样本很重要，因为这样保证了每个变量被采样次数相等)，然后累加各个维度的估值，对维度进行分类，找到好的维度(即f值更高的维度)。根节点的左节点表示

在被选择的节点，根据节点表示的变量选择方式，

# 任务

0. 方法本身超参数的调优。主要是Cp调整，使得前后两项的量级接近，其他超参数可以顺便当做消融实验来做
2. 和lamcts对比。结论是Lamcts不适合高维问题。lamcts效果好的原因是迭代的将搜索空间划分成了非常小的部分，在非常小的搜索空间采样，所以新样本质量高，所以性能很好。扩展到高维空间，1是空间指数增大，需要更多(指数多)次的划分才能取得效果，2是划分越多，意味着树越深，即需要训练的分类器越多，加上样本维度高，训练的时间代价巨大。

其他不太急的事情
1. 用平均排名的变化图展示算法性能。之前大组会上的hyperband，[hyperband](https://arxiv.org/pdf/2105.09821.pdf)。或者像edo cs中，用平均排名，然后画一个优势最大的图
4. bestk好像还是容易陷入局部最优，相比于lamcts达不到更高的值，所以应该还能改进

# 具体实验细节

与BO集合：
lvs-bo，
lamcts-bo，
dropout-bo，
[x] bo，
rembo
与turbo结合，lvs-turbo，lamcts-turbo，dropout-turbo，turbo，alebo，cmaes，学习embedding的方法

## 消融实验

1. split时的依据：mean、median、kmeans。目前：mean
2. 重要的值确定方式：bo、turbo。目前：bo
3. 不重要值确定方式：random，bestk。目前：bestk，也许还可以对比dropout的所以值都从同一个变量中选择的方法
4. uct计算时，max、mean。目前：max
5. 选择右侧的值的次数计算，是用单次选择的次数还是累计选择的次数

画图，在plot-util的363和413行加入

## 需要思考的

计算get_axis_score时使用feature采样的样本的最大值还是均值，目前是max

dynamic_treeify时是否需要建立一颗完整的树

backpropogate时，需要更新哪些东西，是否要向上传递所有的样本点

变量数量过小时，则把节点的估值变得特别低，不选择他，因为会引起gpr的bug，这个可不可以通过聚类选择代表的方式解决

会不会因为选择不重要变量后，每次重要变量都是选择的best，反而使得f比较高

为什么在优化有更多冗余变量的函数时表现反而更好

# 目前的结论

dropout中的维度d是一个很难调的超参数，不是在d=实际维度或略大于略小于实际维度时效果最好，而是在比较奇怪的情况下效果很好。这个可以作为额外发现，放在附录或正文中

Effectiveness

# 真实世界实验

人造函数，beanin，ackley，rosenbrock

alebo：
1. Nasbench101，D=36，限制训练时间小于30m。包含输入输出共7个节点的CNN网络，最多不能超过9条边。7个节点邻接矩阵共21个参数，除了输入输出层外，5个中间层各可以选择3种操作，所以共36个参数。优化时，对于每个层种类的3个参数，选择最大的，对于边连接方式参数，找最大数量非零(也许可以设一个阈值)的添加到图中，直到保证连通输入输入的子图(因为有可能存在不连通的点)的边数不超过9条边(可以通过捕捉不同的异常实现)。
2. Policy search for robot locomotion：六足，每足3电机控制问题，控制器共72个参数，HDBO表现效果整体不好，文中分析是因为函数存在突变点(某些区域经过小的调整后，机器人会直接摔倒)，如果我们尝试每次只优化一部分变量，会不会好一些(更稳定，不容易摔倒)。

vs：
1. rover：60d，vs在这个上面效果很好，不知道靠不靠谱
2. MOPTA08：124d，

turbo（实验采集的样本量都很大）：
robot pushing，16d，可以通过turbo中的处理将问题变为无噪声问题
rover：60d，优化2维空间中的30个点（一条轨迹），
lunar：12d

ebo：rover

hesbo中有一个神经网络参数优化的问题，100d

暂定：
1. nasbench101
2. 神经网络参数优化，在hesbo中只评估了100次
3. rover、robot pushing，但在turbo中，评估次数是2w和1w
4. lunar，不一定比得过
5. rl问题

应该选一个采样数量稍微多一点的