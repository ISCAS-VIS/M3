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

## 类说明

```
util/
├── csvToMatrixJson.py
├── dbopts.py # 各类数据库连接，查询等操作函数
├── FileSegClass.py
├── GridPropSup.py
├── __init__.py
├── POITrans.py
├── preprocess.py # 文件读写，数据转换、计算等公共函数
├── UniGridDisBasic.py
├── UniGridDisOnlyPoints.py
└── UniPOIDisBasic.py
```


* `FileSegClass.py` - 按照日期对文件进行分类重写存储，相关字段预先处理，结果供 Matrix 聚集计算使用

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | 无 |
| 后续步骤 | （具体）聚集计算方案 |
| 依赖项 | 无 |
| 输入 | 未经任何处理 result 中的原始数据 |
| 输出 | bj-byday-sg 中分天存储的数据 |
| 外部调用 | segRawData.py |
| 使用进程 | 20 |

* `POITrans.py` - 将原始 JSON 文件转化成预定格式、适合导入 mongoDB 的 GeoJSON 格式

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | 无 |
| 后续步骤 | 结果导入 mongoDB.pois |
| 依赖项 | 无 |
| 输入 | 分类的多个 POI 数组文件 |
| 输出 | 与输入在同一文件下的 POI Json 数组文件 |
| 外部调用 | genNewPoiJson.py |
| 使用进程 | 1 |

* `GridPropSup.py` - 遍历 POI, 将从属的有意义网格挑出，并添加与 POI 的绑定信息，构成有效网格映射关系表

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | mongoDB.pois 已存在 |
| 后续步骤 | 结果导入 mongoDB.grids |
| 依赖项 | 无 |
| 输入 | POI Geojson 数据 |
| 输出 | BJ-MID-SQL 中分进程的有效网格以及汇总网格文件 |
| 外部调用 | genGridSubProp.py |
| 使用进程 | 20 |

* `UniGridDisBasic.py` - 初始计算脚本，适用于空间精度 0.05 划分结构下 node 和 edge 的统一计算

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | 无 |
| 后续步骤 | 结果存入 MySQL |
| 依赖项 | 无 |
| 输入 | 未经任何处理 result 中的原始数据 |
| 输出 | bj-newvis 中分小时的 nodes 和 edges CSV 文件 |
| 外部调用 | uniGridDistribution.py |
| 使用进程 | 20 |

* `UniGridDisOnlyPoints.py` - 改进后计算脚本，适用于 0.003 精度 Grid 映射 POI 的聚集数据计算方案

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | 按日期分类的原始数据已经处理完毕 |
| 后续步骤 | 无 |
| 依赖项 | 无 |
| 输入 | bj-byday 中按天分的预处理后的数据文件 |
| 输出 | bj-newvis 中 nodes 文件 |
| 外部调用 | ugd-speedup.py |
| 使用进程 | 20 |

* `UniPOIDisBasic.py` - 改进后计算脚本，适用于 0.0005 精度 Grid 映射 POI 的聚集数据计算方案

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | 按日期分类的原始数据已经处理完毕 |
| 后续步骤 | 无 |
| 依赖项 | 无 |
| 输入 | bj-byday-sg 中按天分的预处理后的数据文件 |
| 输出 | bj-newvis-sg 中按进程分的 matrix 结果文件 [hares-j] |
| 外部调用 | uniPOIDistribution.py |
| 使用进程 | 20 |

* `csvToMatrixJson.py` - 将 POI 分时段的聚集分布 CSV 文件转化为 JSON 文件

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | Uni- 类脚本已经将 POI 分时段分布数据跑完 |
| 后续步骤 | 结果存入 mongoDB.matrix |
| 依赖项 | 无 |
| 输入 | bj-newvis-sg 中分进程的 Matrix 文件 |
| 输出 | bj-newvis-sg 中统一的 JSON 文件 [hares-jat] |
| 外部调用 | convPOICSVToJSON.py |
| 使用进程 | 1 |

* `GridPropMatchAdmin.py` - 废弃，由原始数据提供商处理完加入到原始数据字段中
* `UniAdmDisBasic.py` - 空

* `UniPOIEdgeBasic.py` - POI 到 POI 的边权聚集脚本

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | Uni- 类脚本已经将 POI 分时段分布数据跑完 |
| 后续步骤 | 结果转化为 JSON 后存入 mongoDB.ppedge |
| 依赖项 | 无 |
| 输入 | bj-byday-sg 中按天分的预处理后的数据文件 |
| 输出 | bj-newvis-sg 中按进程分的 ppedge- 结果文件 |
| 外部调用 | 类 convPOICSVToJSON.py 脚本 |
| 使用进程 | 20 |


## 约定数据格式

```
datasets/
├── beijingBoundary.json
├── bejingStats.json
├── Mongo.sample.js
└── RESTful.sample.js

```

* `/beijingBoundary.json` - 北京市围栏数据，按照海淀区、朝阳区类似划分，每个区域是一个 geojson 对象，其中 cp 属性存储的是中心点经纬度信息， name 属性存储的是其中文名字
* `/beijingStats.json` - 北京市人文属性数据，包括合计 GDP, 人口, 区域面积, 人均 GDP 以及房价，按照行政区划存储
* `/RESTful.sample.js` - 前后端交互标准数据格式
* `/Mongo.sample.js` - MongoDB 数据库数据格式说明


## 联系

Github @hijiangtao