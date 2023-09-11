# JDWData

### DataAPI
初级数据接口
- db:  基于sql关系数据库接口，可根据不同表结构定义获取数据
- ddb: 基于DDB数据接口 
- mg:  基于MongoDB数据接口

### RetrievalAPI
基于配置文件读取接口
通过指定yaml文件即mapping关系，读取对应时间

### SurfaceAPI
高级封装接口
基于逻辑业务的联查数据接口，适用于复杂条件及多表联查