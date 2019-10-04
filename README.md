# Cache simulation

## 总结了我们工作的三个大点 希望大家多多整理代码和实验结果 补充报告

## *1* Behaviour comparison between monolithic cache and cache cluster

### Current work and findings

现有的实验是每次针对一个trace文件来做，而trace文件是磁盘请求，本身具有相当高的局部性，在10%大小时可以达到将近90%的命中次数。在计算机结构中也没有人做这种用同一级（与多级相对）小cache集群替换大cache的做法，说明在计算机结构（局部性相当强）的请求中，这种cache改进没有意义，这也解释了为什么之前实验中两种cache的表现变化难以捉摸（这种提升是随机性的）。

### Future work

我们是做 proxy cache，相当于有多个用户各自产生局部性很强的请求整合起来。应当把多个trace文件各自取出部分，融合成新的trace。融合中考虑到不同文件里的时间戳起止时间问题，可以重新自定义如何融合，要保证来自同一个文件的请求相对顺序不变且考虑到模拟的多个用户（提取出的trace文件）被公平地处理请求。

## *2* Trace locality aborbing in multi-level cache architecture

According to previous research ([Starobinski](https://github.com/Peixuan670/cache_simulation/blob/master/reference/Probabilistic%20Methods%20for%20Web%20Caching.pdf)). The off-the-self cache archetecture can be regard as multi-level, the client-end caches may absorb the locality hence the attribute of locality in the request trace recevied by higher cache will be less significent. However, the whole point about cacheing is the locality of the request pattern.  

## *3* Increasing the locality in cache cluster

Inspired by [Starobinski's](https://github.com/Peixuan670/cache_simulation/blob/master/reference/Probabilistic%20Methods%20for%20Web%20Caching.pdf) work, we may design a new caching methode in proxy cache.  

对之前提到的融合的请求文件，对比实验：
1、大cache LRU
2、小cache集群 每个小cache只对来自固定的用户处理，相当于以分割cache来把用户产生的总请求分割成更小的局部性更加强的请求。
在文件中标明请求来自哪个文件（用户），比如10个用户融合的文件，有5个小cache，每个cache固定处理来自某两个用户的请求。

(Comments from Peixuan: 
个人认为locality 分为两个方面, 时间和空间。
(1)空间涉及到缓存了一个文件之后也缓存与他相关联的文件, 这个在CDN中目前没有涉及。
(2)时间的话也就是一个文件缓存之后也可能被重复request，而这也是目前的CDN的实现。
思路可以是相关一类的文件放到一起(因为用户实在是太多了, 或者说对用户和request进行cluster分类)
)
