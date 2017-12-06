const data = {
    "grid": { // 
        "nid": 1, // 代表节点的唯一编号，在网格划分不改变的情况下不同时间单位下同一位置网格编号不变
        "pid": String(16), // poi 编号
        "lng": 30.0, // 经度
        "lat": 30.0, // 纬度
        "x": 1, // 经度编号
        "y": 1 // 纬度编号
    },
    "poi": { // 
        "pid": String(16), // poi 编号
        "coordinates": [], // 围栏信息
        "properties": {
            "district": "海淀区",
            "ptype": 00001, // type
            "name": "gg",
            "business_area": "",
            "address": "",
            "cp": []
        }
    },
    "matrix": { // 
        "pid": String(16), // POI 编号
        "segid": 4, // 时间段编号
        "dev_num": 1, // 
        "rec_num": 1
    }
};

export default data;