## 说明文档

状态预测数据处理以及可视化查询后段接口说明文档。

## 运行方式

```
# 克隆内容到本地
git clone git@github.com:hijiangtao/statePrediction.git

# 进入该文件
cd PATH

# 在原始数据上清洗成分天存储的数据，并添加属性
# -d 输入文件夹
# -p 输出文件夹
# -i 原始文件个数（从0开始编号）
python segRawData.py -d /datahouse/zhtan/datasets/VIS-rawdata-region-c-sample  -p /datahouse/tao.jiang -i 3999

# 在分天存储的基础上作了进一步处理
python segDayDataForTripFlow.py

# trip 切分与聚类以及种子方向挑选工作
# -d 输入文件夹
# -p 输出文件夹
# -e 密度数
# -m 最小聚类个数
python tripFlowCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -e 2 -m 10

# 生成 treeMap 脚本
# -d 输入文件夹
# -p 输出文件夹
# -x 处理的小时 ID
# -n treeMap 个数
# -a search_angle
# -s seed_strength
# -w tree_width
python treeMapCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -x 9 -n 150 -a 60 -s 0.1 -w 1

```

## 联系

Github @hijiangtao