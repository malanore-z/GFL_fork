# GFL Features

## 目前实现

### Job Config

1. 自定义Train Config用于训练    
    + trainer  
    + model
    + loss function
    + function
    + optimizer
    + ...
    
2. 自定义Aggregate Config用于聚合
    + aggregator
    + ...
    
3. 自定义Dataset Config用于加载数据集  
    + dataset
    + val_dataset
    + ...
    
4. 自定义Job Config用于生成Job  
    + round
    + owner
    + ...

### 训练和聚合

1. 自定义Trainer
    + parse_job_config
    + parse_train_config
    + parse_dataset_config
    + pre_train
    + train
    + post_train
    
    实现以上过程用于训练模型  
    
    + validate
    实现以上过程用于验证模型(训练完成后对全局模型进行验证)  
    
2. 自定义Aggregator
    + parse_train_config
    + parse_aggregate_config
    + load_client_parameters
    + aggregate
    + save_aggregate_parameters
    
    实现以上过程用于聚合参数  
    
    + aggregate_validation_results  
     
    实现以上过程用于聚合客户端对全局模型的验证结果
    
### 通信

1. 内置Http和区块链两种通信方式
    
    
## 待实现

### 训练和聚合

1. Aggregator执行更灵活的功能， 如模型的统计参数

2. 实现常用算法的Trainer和Aggregator， 添加算法库

3. 添加易用可读的训练日志

### 测试和评估

1. 添加评估模型性能的接口和指标

2. 在训练完成之后生成Job的性能评估报告

### 数据集

1. 添加数据集划分工具包（算法库）
2. 添加数据集评估的接口和指标
3. 添加常用数据集

### 去中心化

1. 针对区块链和智能合约去中心化的特性，添加去中心化环境下执行的联邦学习算法。  

## 长久计划

### 纵向联邦

1. 添加模型训练过程中节点间通信交换数据的方法

2. 实现纵向联邦算法

### 安全

1. 添加同态加密和MPC

### 多设备支持

1. 构建light node用于在物联网/嵌入式设备上收集数据和训练  

### 数据定价

1. 在Trainer中添加对数据集的评分
