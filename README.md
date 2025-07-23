# ArXiv论文转发工具

一个自动化工具，每天搜索ArXiv上的最新计算机科学论文，使用Gemini AI分析摘要内容，并将结果通过邮件发送。

## 功能特点

- 🔍 **智能搜索**：基于关键词自动搜索ArXiv计算机科学领域的最新论文
- 🤖 **AI分析**：使用Google Gemini API智能分析论文摘要，生成中文概括
- 📧 **邮件推送**：自动发送包含论文信息、首页截图和AI分析的精美邮件
- 📱 **可配置性**：支持自定义关键词、论文数量、运行时间等参数
- ⏰ **定时运行**：支持定时任务，每天自动运行
- 📊 **日志记录**：详细的运行日志，便于监控和调试

## 快速开始

### 1. 环境要求

- Python 3.8+
- Gmail邮箱（用于发送邮件）
- Google Gemini API密钥

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制`.env.example`文件为`.env`：

```bash
cp .env.example .env
```

编辑`.env`文件，填入你的配置信息：

```env
# ArXiv搜索配置
ARXIV_KEYWORDS=machine learning,artificial intelligence,deep learning
MAX_PAPERS=5

# Gemini API配置
GEMINI_API_KEY=your_gemini_api_key_here

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient@email.com

# 其他设置
PDF_DOWNLOAD_DIR=./downloads
SCHEDULE_TIME=09:00
```

### 4. 获取必要的API密钥和密码

#### Google Gemini API密钥
1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 创建新项目或选择现有项目
3. 生成API密钥
4. 将密钥填入`.env`文件的`GEMINI_API_KEY`字段

#### Gmail应用专用密码
1. 登录你的Gmail账户
2. 进入 [Google账户安全设置](https://myaccount.google.com/security)
3. 启用两步验证（如果未启用）
4. 生成应用专用密码
5. 将密码填入`.env`文件的`SENDER_PASSWORD`字段

### 5. 运行程序

#### 单次运行（测试）
```bash
python main.py once
```

#### 定时运行
```bash
python main.py
```

程序会按照配置的时间每天自动运行。

## 配置说明

### 环境变量详解

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `ARXIV_KEYWORDS` | 搜索关键词，用逗号分隔 | `machine learning,artificial intelligence` |
| `MAX_PAPERS` | 每天最大论文数量 | `5` |
| `GEMINI_API_KEY` | Google Gemini API密钥 | 必填 |
| `SMTP_SERVER` | SMTP服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP端口 | `587` |
| `SENDER_EMAIL` | 发送方邮箱 | 必填 |
| `SENDER_PASSWORD` | 发送方邮箱密码（应用专用密码） | 必填 |
| `RECIPIENT_EMAIL` | 接收方邮箱 | 必填 |
| `PDF_DOWNLOAD_DIR` | PDF下载目录 | `./downloads` |
| `SCHEDULE_TIME` | 每天运行时间（24小时格式） | `09:00` |

### 关键词配置建议

可以根据你的研究兴趣配置关键词，例如：

```env
# 机器学习相关
ARXIV_KEYWORDS=machine learning,deep learning,neural network,reinforcement learning

# 计算机视觉相关
ARXIV_KEYWORDS=computer vision,image recognition,object detection,segmentation

# 自然语言处理相关
ARXIV_KEYWORDS=natural language processing,transformer,large language model,chatbot

# 多领域混合
ARXIV_KEYWORDS=machine learning,computer vision,nlp,robotics,ai
```

## 项目结构

```
arxiv_to_mail/
├── main.py                 # 主程序入口
├── config.py               # 配置管理
├── arxiv_search.py         # ArXiv搜索模块
├── pdf_processor.py        # PDF处理模块
├── gemini_analyzer.py      # Gemini AI分析模块
├── email_sender.py         # 邮件发送模块
├── requirements.txt        # 依赖包列表
├── .env.example           # 环境变量示例文件
├── .env                   # 环境变量文件（需要创建）
├── README.md              # 说明文档
├── downloads/             # 下载目录
└── arxiv_to_mail.log      # 运行日志
```

## 邮件内容示例

发送的邮件包含以下内容：

- **邮件标题**：【AI论文分享】日期-论文题目
- **论文信息**：ArXiv编号、作者、发布日期、链接
- **首页截图**：论文PDF的首页预览图
- **AI分析**：包括研究领域、核心贡献、技术方法、实验结果、意义价值

## 常见问题

### Q: 邮件发送失败怎么办？
A: 请检查以下几点：
1. Gmail账户是否启用了两步验证
2. 是否使用了应用专用密码而不是账户密码
3. 网络连接是否正常
4. SMTP服务器和端口配置是否正确

### Q: Gemini API调用失败怎么办？
A: 程序包含了fallback机制，如果Gemini API不可用，会使用简化的分析。请检查：
1. API密钥是否正确
2. 是否有API配额限制
3. 网络是否能访问Google服务

### Q: 如何修改论文搜索范围？
A: 编辑`arxiv_search.py`文件中的`cs_categories`列表，添加或删除ArXiv分类代码。

### Q: 可以部署到服务器上吗？
A: 可以。建议使用systemd、cron或Docker等方式部署到Linux服务器上。

## 部署建议

### Linux服务器部署

1. 使用cron定时任务：
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天9点运行）
0 9 * * * /path/to/python /path/to/main.py once
```

2. 使用systemd服务：
```ini
# 创建 /etc/systemd/system/arxiv-to-mail.service
[Unit]
Description=ArXiv to Mail Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/arxiv_to_mail
ExecStart=/path/to/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 更新日志

- v1.0.0: 初始版本，实现基本功能
  - ArXiv论文搜索
  - Gemini AI分析
  - 邮件发送
  - 定时任务