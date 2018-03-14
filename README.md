## 说明文档

状态预测数据处理以及可视化查询后段接口说明文档。

## 运行方式

### 初始化

```
# 克隆内容到本地
git clone git@github.com:hijiangtao/statePrediction.git

# 进入该文件
cd PATH

# 开发模式前请确认在 dev 分支上操作
```

### 离线处理部分

```
# 在原始数据上清洗成分天存储的数据，并添加属性
# -d 输入文件夹
# -p 输出文件夹
# -i 原始文件个数（从0开始编号）
python segRawData.py -d /datahouse/zhtan/datasets/VIS-rawdata-region-c-sample  -p /datahouse/tao.jiang -i 3999

# 在分天存储的基础上作了进一步处理
python segDayDataForTripFlow.py

# trip 切分与聚类以及种子方向挑选工作
# [spaceInterval 为实际的距离参数，选择包括0, 200, 400, 800, 1600, 3200]
# -d 输入文件夹
# -p 输出文件夹
# -e 密度数
# -m 最小聚类个数
python tripFlowCal.py -d /tripflow/spaceInterval/ -p /tripflow/spaceInterval/ -e 2 -m 10
```

### 在线调用部分

```
# 生成 treeMap 脚本
# [本脚本运行不再设置提示参数名 直接从参数数组中顺序读取]
# [参数意义如下，按顺序填入，不可空缺]
# 输入文件夹
# 输出文件夹
# 处理的小时 ID
# treeMap 个数
# search_angle
# seed_strength
# tree_width
# jump_length
python /datahouse/tripflow/200 /datahouse/tripflow/200 treeMapCal.py 9 30 60 0.1 1 3

```

## 联系

Github @hijiangtao