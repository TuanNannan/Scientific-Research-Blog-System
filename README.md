# 构音障碍语音识别科研博客系统

## 项目概述
这是一个专为构音障碍语音识别研究设计的博客系统，用于记录科研工作、实验结果和进度。

## 技术栈
- **后端**: Flask 2.x + Flask-RESTful + SQLAlchemy
- **前端**: Vue 3 + TypeScript + Vite + Element Plus
- **数据库**: PostgreSQL (开发环境可使用SQLite)
- **音频处理**: Librosa, PyAudio
- **可视化**: Matplotlib, Plotly, ECharts
- **部署**: Docker + Nginx

## 系统架构

### 核心功能模块
1. **用户认证系统**
   - 注册/登录/个人资料管理
   - 角色权限管理（管理员、研究者、访客）

2. **博客文章管理**
   - Markdown编辑器
   - 文章分类和标签
   - 评论系统

3. **实验记录系统（定制化）**
   - 音频文件上传和管理
   - 实验参数记录（模型架构、超参数、数据集信息）
   - 实验结果可视化（准确率、损失函数、混淆矩阵等）
   - 进度时间线
   - 实验对比分析

4. **数据管理**
   - 构音障碍语音数据集管理
   - 数据预处理流水线
   - 数据增强工具

5. **待办事项系统**
   - 科研任务管理
   - 实验进度跟踪
   - 里程碑设定
   - 优先级和截止日期
   - 任务分类和标签

### 数据库设计
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'researcher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 博客文章表
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES users(id),
    category VARCHAR(50),
    tags TEXT[],
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 实验记录表
CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    researcher_id INTEGER REFERENCES users(id),
    model_architecture VARCHAR(100),
    hyperparameters JSONB,
    dataset_info JSONB,
    training_config JSONB,
    results JSONB,
    status VARCHAR(20) DEFAULT 'planning',
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 音频文件表
CREATE TABLE audio_files (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    duration FLOAT,
    sample_rate INTEGER,
    speaker_info JSONB,
    transcription TEXT,
    labels JSONB,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 实验结果指标表
CREATE TABLE experiment_metrics (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    epoch INTEGER,
    step INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 待办事项表
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 待办事项标签表
CREATE TABLE todo_tags (
    id SERIAL PRIMARY KEY,
    todo_id INTEGER REFERENCES todos(id),
    tag VARCHAR(50) NOT NULL
);
```

## 开发计划

### 阶段1: 项目基础搭建 (1-2天)
- [x] 创建项目结构
- [ ] 配置Flask项目
- [ ] 设置数据库模型
- [ ] 基础API端点

### 阶段2: 核心功能开发 (3-5天)
- [ ] 用户认证系统
- [ ] 博客文章CRUD
- [ ] 实验记录管理
- [ ] 音频文件上传

### 阶段3: 定制化功能 (2-3天)
- [ ] 实验参数模板
- [ ] 结果可视化组件
- [ ] 进度时间线
- [ ] 实验对比分析

### 阶段4: 前端开发 (3-4天)
- [ ] React项目搭建
- [ ] 用户界面设计
- [ ] 博客文章界面
- [ ] 实验记录界面
- [ ] 可视化图表

### 阶段5: 集成和测试 (2天)
- [ ] 前后端集成
- [ ] 功能测试
- [ ] 性能优化

### 阶段6: 部署和文档 (1天)
- [ ] Docker配置
- [ ] 部署文档
- [ ] 用户手册

## 快速开始

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置
```bash
# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. 运行开发服务器
```bash
flask run
```

### 4. 访问应用
- 后端API: http://localhost:5000/api/
- 管理后台: http://localhost:5000/admin/
- 前端界面: http://localhost:5173

## 特色功能

### 构音障碍语音识别定制化
1. **音频标注工具**: 支持对语音样本进行精细标注
2. **特征提取**: 自动提取MFCC、频谱图等声学特征
3. **模型评估**: 集成常用的评估指标（WER、CER、准确率等）
4. **数据增强**: 支持语音数据增强技术
5. **可视化分析**: 提供丰富的实验结果可视化

### 科研工作流支持
1. **实验模板**: 预定义常用实验配置模板
2. **版本控制**: 实验配置和结果的版本管理
3. **协作功能**: 支持多人协作和实验共享
4. **报告生成**: 自动生成实验报告
5. **数据导出**: 支持多种格式的数据导出

## 贡献指南
欢迎贡献代码、报告问题或提出改进建议。

## 许可证
MIT License