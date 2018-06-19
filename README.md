# M3: Multifaceted Microcirculation Map in Cities 

## Introduction

Can we understand the detailed movement of population in cities effectively through visualization? In this work, we study a densely sampled urban localization data that covers millions of city residents and has a fine resolution in space and time. While most related literature focus on displaying the high-level movement patterns among cities or municipal/functional regions, we seek to visualize the microscopic population movement in the metropolitan scale. This paper presents $M^3$, the multifaceted microcirculation map, which integrates movement abstraction techniques with the wind map visual metaphor to illustrate both global and local patterns in the population movement. On the algorithm side, we introduce a suite of methods to infer human movements from their raw location data, smooth and aggregate them into local movement clusters, and finally connect the clusters to generate movement flows using a tractography algorithm. On the visualization side, the design of wind map is improved to reduce the visual clutter caused by the nature of human movements. Multifaceted visual analytics methods are proposed for users to examine the different aspects of the complex behavior of population movements. We conducted two case studies with technical and domain experts in urban planning and public safety analysis. The result demonstrates the significance and effectiveness of the $M^3$ system in helping to complete their key tasks such as commute analysis and emergency detection.

## 目录

本项目存储在 M3 项目中用到的状态预测、旅途树结构生成等数据处理以及可视化查询后端接口涉及到的代码，此 README 为该部分的说明文档，包含 treeMap 等数据与分析结果的 python 处理脚本。

其中，运行部分只披露现有在用的脚本细节，已废弃的脚本文件或未在 M3 展示系统中使用的代码只在脚本依赖关系说明中涉及，作为备份与参考，不推荐实际使用。

除以上部分，该项目中还存储有约定数据格式 sample 文件以及一些有用的地理位置数据。需要注意的是该部分代码不包含**异常检测**等后续添加的新功能代码。

1. [使用方法](#使用方法)
    * 项目代码运行流程
    * 离线处理部分
    * 在线调用部分
2. [脚本依赖关系说明](#脚本依赖关系说明)
    * 部分类说明
3. [数据格式说明](#数据格式说明)
4. [联系](#联系)
5. [LICENSE](#LICENSE)

## 1. 使用方法

### 1.1 项目代码运行流程

项目文件结构如下所示：

```
M3/
├── datasets # 约定的各项数据格式样本均存放在该文件夹中，可参考，主要用于后端服务构建
├── SQL # 数据库构建批量脚本文件的存放处，后期由于数据处理逻辑进行了更新，所以该部分脚本也未继续使用
├── util # 各类分析模型、人流树（treeMap）、人流点线（tripFlow）结构生成脚本的原始类文件存放处，其中 tripFlow 文件夹下主要存放和 treeMap 以及在线服务调用有关的类
└── ... # 离线或在线调用的各个脚本文件，除此外还包括 README、.gitignore 等等
```

代码下载与本地运行流程如下所示：

```
# 克隆内容到本地（使用 SSH 或者 HTTPS 方式下载）
git clone git@github.com:hijiangtao/statePrediction.git
# 或者
git pull https://github.com/hijiangtao/M3.git

# 进入该文件
cd M3

# 开发模式前请确认在 dev 分支上操作
git checkout dev

# 传参并实际调用脚本进行计算
python ExactScriptFile -param P1 ...
```

### 1.2 离线处理部分

由于 M3 的项目过于庞大，无法将所有功能都通过实时脚本调用进行处理，于是非常耗时的这部分计算任务被分配到离线处理部分，包括对原始数据进行标记和按时间单位的切分与存储、对切分后的数据进行 triflow 的信息提取工作、对不同旅程（trip）进行切分与聚类计算、对 M3 前端展示进行种子挑选等任务。具体调用文件以及传参形式如下所示，参数实际含义见注释或各文件实际调用的类文件头部说明（包含输入数据格式、输入目录格式、类功能说明、输出数据格式、输出目录格式等）。

#### 1.2.1 segRawData.py

```
# 在原始数据上清洗成分天存储的数据，并添加属性
# 通过引入 FileSegByHour 类对原始文件进行切分处理，并将计算后的结果合并，存储至按天分的数据文件中。本部分采用了多进程进行处理，须确保 CPU 可调用核心数在 20 及以上

# ------ 调用示例 ------
python segRawData.py -d /datahouse/zhtan/datasets/VIS-rawdata-region-c-sample  -p /datahouse/tao.jiang -i 3999
```

* 参数说明

| 参数 | 用途 |
|---| ---------- |
| d | 输入数据所在文件夹 |
| p | 输出数据所在文件夹 |
| i | 原始文件个数（从0开始编号） |

#### 1.2.2 segDayDataForTripFlow.py

```
# 在分天存储的基础上作了进一步处理
# 将切分成天的数据按照小时进行切分存储，且只保留 travel 状态数据，该部分逻辑在 segRawData 中实现，不包含在本脚本中
# 运行依赖： rawdata-%d 已经在脚本 segRawData.py 中处理完毕

# ------ 调用示例 ------
python segDayDataForTripFlow.py
```

#### 1.2.3 tripFlowCal.py

```
# trip 切分与聚类以及种子方向挑选工作

# ------ 调用示例 ------
python tripFlowCal.py -d /tripflow/spaceInterval/ -p /tripflow/spaceInterval/ -e 2 -x 9 -k 24000
```

* 参数说明

| 参数 | 用途 |
|---| ---------- |
| d | 输入数据所在文件夹 |
| p | 输出数据所在文件夹 |
| [spaceInterval] | spaceInterval 为实际的距离参数，选择包括0, 200, 400, 800, 1600, 3200六种选择 |
| e | 角度密度数，默认为2，用于控制种子挑选条件 |
| x | 时段编号，表示从7.6零时开始的绝对小时编号，例如9 |
| k | 总边数除以该值得到 min_samples |

### 1.3 在线调用部分

在线调用部分的文件代码和离线处理的文件代码结构一致，命令行运行的调用方式也一致。唯一区别在于，在线调用部分的脚本文件同时可以通过 M3 前端界面交互进行控制调用。具体实现为通过前端交互向 M3 后端服务传传送 JSONP 请求，后端解析请求具体参数后在本地通过命令行调用数据处理 python 脚本，待计算完成后端检查是否正常生成结果文件，如果正常则读取结果并包成 JSON 格式返回给前端，否则将错误信息包成 JSON 返回给前端。

本部分涉及到的功能包括根据给定筛选条件生成 treemap 结构、根据指定 trip 筛选条件计算角度聚类结果。

#### 1.3.1 treeMapCal.py

```
# 生成 treeMap 脚本

# ------ 调用示例 ------
python treeMapCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.01 60 0.1 1 3 basic -1
```

* 参数说明（本脚本运行不再设置提示参数名，直接从参数数组中顺序读取；参数意义如下，按顺序填入，不可空缺）

| 顺序 | 用途 |
|---| ---------- |
| 1 | 输入数据所在文件夹 |
| 2 | 输出数据所在文件夹 |
| 3 | 处理的小时 ID |
| 4 | treeMap 比例，即需要利用数据生成 TOP 多少的 treemap，浮点数表示，例如 0.01 |
| 5 | search_angle，搜索角度范围 |
| 6 | seed_strength，搜索迭代强度，若下一条边的强度未超过首条边的强度值，则将后续数据丢弃，例如 0.1 表示丢弃所有未达到首条边强度 10% 的数据 |
| 7 | tree_width，控制树的分支数 |
| 8 | jump_length，控制每次搜索的网格单位，例如 3 表示每次向前搜索三个单位的网格内数据 |
| 9 | seed_unit，表明种子生成的方式，默认传参为 basic |
| 10 | grid_dirnum，控制 treemap 的分支数量， -1 表示不添加任何限制 |

#### 1.3.2 angleClusterCal.py

```
# 在线生成 angleCluster 脚本
# 角度聚类中存在两个关键的参数用于控制聚类具体的结果，实际上我们是自己设计的类似 DBScan 的角度聚类方法，参数同样取名为 eps 和 min_samples，用途类似 DBScan 线型聚类。

# ------ 调用示例 ------
python angleClusterCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.01 100
```

* 参数说明（本脚本运行不再设置提示参数名，直接从参数数组中顺序读取；参数意义如下，按顺序填入，不可空缺）

| 顺序 | 用途 |
|---| ---------- |
| 1 | 输入数据所在文件夹 |
| 2 | 输出数据所在文件夹 |
| 3 | 处理的小时 ID |
| 4 | eps |
| 5 | min_samples |


### 2. 脚本依赖关系说明

在 M3 最初的尝试中，我们设计过不同行政区划、不同小区、不同街道等空间单位之间的点/边 trip 信息，该部分脚本在后续讨论中已不再使用，但考虑到该部分思路可以被进一步借鉴，本部分将这部分脚本的依赖关系进行详细说明。其中包含各文件的作用、传参说明、调用进程数、前序步骤等信息，若遇到实际文件与描述文件不符，则以最新文件内代码逻辑为准。

#### 2.1 部分类说明

该部分主要的文件包含关系如下，实际实现均位于 util 文件夹内：

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

以下分文件进行描述：

* `FileSegClass.py` - 按照日期对文件进行分类重写存储，相关字段预先处理，包括 gid/aid/from\_gid/to\_aid/seg/hour/wday 等等必要字段，结果供后续多种 Matrix 聚集计算使用

| 属性 | 说明 |
|---| ---------- |
| 前序步骤 | 无 |
| 后续步骤 | （具体）聚集计算方案 |
| 依赖项 | 无 |
| 输入 | 未经任何处理 result 中的原始数据 |
| 输出 | bj-byday-sg 中分天存储的 rawdata- 数据 |
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
| 外部调用 | uniGridDistribution-speedup.py |
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
* `uniAdmDisBasic.py` - 空
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


### 3. 数据格式说明

本部分存储在数据处理、后端计算、前端通信中涉及到的各类数据格式说明 sample，以及一些有用的数据文件比如北京行政区划围栏信息。以下为该部分数据文件结构：

```
datasets/
├── beijingAdmin.csv
├── beijingBoundary.json
├── bejingStats.json
├── Mongo.edge.sample.js
├── Mongo.node.sample.js
├── originDataset.js
└── RESTful.sample.js

0 directories, 7 files
```

以下分点描述各文件作用，实际情况在各数据处理脚本文件头部中也进行了说明。

* `beijingAdmin.csv` - 北京各行政区划中心点经纬度位置数据
* `beijingBoundary.json` - 北京市围栏数据，按照海淀区、朝阳区类似划分，每个区域是一个 geojson 对象，其中 cp 属性存储的是中心点经纬度信息， name 属性存储的是其中文名字
* `beijingStats.json` - 北京市人文属性数据，包括合计 GDP, 人口, 区域面积, 人均 GDP 以及房价，按照行政区划存储
* `RESTful.sample.js` - 前后端交互标准数据格式
* `Mongo.edge.sample.js` - MongoDB 数据库数据格式说明（边存储）
* `Mongo.node.sample.js` - MongoDB 数据库数据格式说明（点存储）
* `originDataset.js` - 原始数据以及处理后输出数据格式说明

例如，MongoDB 中存储的边信息格式为：

```javascript
{
    "grid": {},
    "poi": {},
    "ppedge": { // 
        "from_nid": String(16), // 来源 POI 编号
        "to_nid": String(16), // 目的地 POI 编号
        "dev_num": 1, // 
        "rec_num": 1,
        "segid": 4, // 时间段编号
    }
};
```

原始数据与处理后输出数据格式为：

```javascript
const data = {
    originDataset: {
        'uid': 'String',
        'time': 'timestamp',
        'lat': 'double',
        'lng': 'double',
        'state': 'S/T/U',
        'stateID': 'number',
        'admin': 'text',
        'example': ['1', 12312321312, 39, 110, T, 1, '海淀区']
    },
    outputRawData: {
        id: 'String',
        seg: 'Number',
        hour: 'Number', // 0-23
        wday: 'Number', // 0-6
        gid: 'Number',
        state: 'S/T',
        admin: 'Number', // 1-16
        from_gid: 'Number',
        to_gid: 'Number',
        from_aid: 'Number',
        to_aid: 'Number'
    }
}
```

具体见各文件。


## 4. 联系

Github [@hijiangtao](https://github.com/hijiangtao)

## LICENSE

Apache License V2.0
