## 说明文档

状态预测数据处理以及可视化查询后段接口说明文档。

## 目录

```
├── datasets
│   ├── beijingBoundary.json
│   ├── bejingStats.json
│   └── sample.vis.js
├── LICENSE
├── README.md
├── unigriddis.sh
├── uniGridDistribution.py
└── util
    ├── dbopts.py # 数据库操作类
    ├── FileSegClass.py # 按天切分原始数据
    ├── __init__.py
    ├── preprocess.py # 计算基础类
    ├── UniGridDisBasic.py # 按小时全量遍历数据类（形成点边信息的城市结果）
    └── UniGridDisOnlyPoints.py # 按天遍历（天内数据同时处理）数据类（点信息）
```

* `/datasets/beijingBoundary.json` - 北京市围栏数据，按照海淀区、朝阳区类似划分，每个区域是一个 geojson 对象，其中 cp 属性存储的是中心点经纬度信息， name 属性存储的是其中文名字
* `/datasets/beijingStats.json` - 北京市人文属性数据，包括合计 GDP, 人口, 区域面积, 人均 GDP 以及房价，按照行政区划存储
* `/datasets/sample.vis.js` - 前后端交互标准数据格式
* `/util` - 数据分析脚本工具类 


## 联系

Github @hijiangtao