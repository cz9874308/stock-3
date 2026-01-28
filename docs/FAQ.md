# ❓ FAQ 常见问题解答

> **📚 文档说明**: 收集 InStock 使用过程中的常见问题和解决方案  
> **🔄 更新频率**: 持续更新中

---

## 📋 问题分类导航

```
┌─────────────────────────────────────────────────────────────────┐
│                     FAQ 快速导航                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🔧 安装配置问题    ──▶  第1节                                  │
│   📊 数据采集问题    ──▶  第2节                                  │
│   📈 指标策略问题    ──▶  第3节                                  │
│   🌐 Web服务问题     ──▶  第4节                                  │
│   🐳 Docker部署问题  ──▶  第5节                                  │
│   🤖 自动交易问题    ──▶  第6节                                  │
│   💡 使用技巧       ──▶  第7节                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ 安装配置问题

### Q1.1: Python 版本要求是什么？

**A:** 推荐使用 Python 3.11 或更高版本。

```bash
# 检查 Python 版本
python --version
```

如果版本过低，请到 [python.org](https://www.python.org/downloads/) 下载最新版本。

---

### Q1.2: pip install 报错，下载很慢或失败？

**A:** 配置国内镜像源可解决。

```bash
# 设置阿里云镜像 (推荐)
pip config --global set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 或临时使用
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

**常用国内镜像:**
- 阿里云: `https://mirrors.aliyun.com/pypi/simple/`
- 清华: `https://pypi.tuna.tsinghua.edu.cn/simple/`
- 豆瓣: `https://pypi.douban.com/simple/`

---

### Q1.3: TA-Lib 安装失败？

**A:** TA-Lib 需要先安装 C 语言库。

**Windows:**
```bash
# 方法1: 从官网下载安装器
# https://ta-lib.org/install/
# 选择 "Windows Executable Installer"

# 方法2: 使用 conda
conda install -c conda-forge ta-lib
```

**Linux (Ubuntu/Debian):**
```bash
# 安装依赖
sudo apt-get install build-essential

# 下载并安装 TA-Lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# 然后安装 Python 包
pip install TA-Lib
```

**Mac:**
```bash
brew install ta-lib
pip install TA-Lib
```

---

### Q1.4: 数据库连接失败？

**A:** 检查以下几点：

1. **MySQL 服务是否启动？**
```bash
# Windows
net start mysql

# Linux
sudo systemctl start mysql
```

2. **密码是否正确？**
```python
# 检查 instock/lib/database.py
db_password = "你的密码"  # 确保与 MySQL 安装时设置的一致
```

3. **端口是否被占用？**
```bash
# Windows
netstat -an | findstr 3306

# Linux
sudo lsof -i :3306
```

4. **测试连接:**
```bash
mysql -u root -p
# 输入密码，能进入即可
```

---

### Q1.5: 如何更新依赖库？

**A:**

```bash
# 方法1: 修改 requirements.txt 中的 "==" 为 ">="，然后执行
pip install -r requirements.txt --upgrade

# 方法2: 单独更新某个库
pip install pandas --upgrade
```

---

## 2️⃣ 数据采集问题

### Q2.1: 数据抓取被限制/封 IP？

**A:** 配置代理或 Cookie。

**配置代理:**
```bash
# 编辑 instock/config/proxy.txt
# 每行一个代理，格式: IP:端口 或 用户名:密码@IP:端口
192.168.1.1:8080
user:pass@192.168.1.2:8080
```

**配置东方财富 Cookie:**
1. 打开浏览器访问东方财富
2. F12 打开开发者工具
3. Network 选项卡，找到包含 `push2.eastmoney.com` 的请求
4. 复制 Cookie 值
5. 配置方式:
```bash
# 方式一: 环境变量
setx EAST_MONEY_COOKIE "你的Cookie值"

# 方式二: 配置文件
# 编辑 instock/config/eastmoney_cookie.txt
```

---

### Q2.2: 数据为空或不完整？

**A:** 可能原因及解决方法：

| 原因 | 解决方法 |
|------|----------|
| 非交易时间 | 收盘后运行，数据更完整 |
| 网络问题 | 检查网络，配置代理 |
| 数据源限制 | 配置 Cookie |
| 首次运行 | 多等待一会，首次需要时间 |

```bash
# 手动重新抓取
python basic_data_daily_job.py
```

---

### Q2.3: 如何抓取历史数据？

**A:** 使用批量作业命令。

```bash
cd instock/job

# 单个日期
python execute_daily_job.py 2024-01-15

# 多个日期
python execute_daily_job.py 2024-01-15,2024-01-16,2024-01-17

# 日期范围
python execute_daily_job.py 2024-01-01 2024-01-31
```

> ⚠️ 注意：批量抓取历史数据需要较长时间，建议在非交易时段执行。

---

### Q2.4: 支持港股/美股吗？

**A:** 目前主要支持 A 股市场。

InStock 的数据源（东方财富、新浪等）主要提供 A 股数据。如需港股/美股支持，需要：
1. 添加新的数据源接口
2. 修改数据结构适配
3. 调整指标计算参数

---

## 3️⃣ 指标策略问题

### Q3.1: 指标计算结果和其他软件不一致？

**A:** InStock 的指标计算已针对同花顺、通达信进行校准，大部分应该一致。

如发现差异，可能原因：
1. **数据源差异**: 不同软件数据源可能略有差异
2. **复权方式**: 检查是否使用相同的复权方式
3. **参数设置**: 确认指标参数一致

---

### Q3.2: 如何添加自定义指标？

**A:** 在 `instock/core/indicator/calculate_indicator.py` 中添加。

```python
def calculate_my_indicator(close, high, low, volume):
    """
    我的自定义指标
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        volume: 成交量序列
        
    Returns:
        指标值
    """
    # 你的计算逻辑
    result = ...
    return result
```

---

### Q3.3: 策略回测胜率很低，怎么优化？

**A:** 几个优化方向：

1. **调整参数**: 修改策略中的阈值参数
2. **增加过滤条件**: 排除不适合的股票（如 ST、次新股）
3. **组合策略**: 多个策略共同验证
4. **分析失败案例**: 找出规律进行改进

```python
# 示例: 添加过滤条件
def check(stock_data, end_date=None):
    # 原有策略逻辑
    basic_condition = ...
    
    # 新增过滤: 排除成交额太小的
    latest = stock_data.iloc[-1]
    volume_filter = latest['amount'] > 100000000  # 1亿以上
    
    return basic_condition and volume_filter
```

---

### Q3.4: 如何查看策略选中的股票？

**A:** 多种方式查看：

**方式一: Web 界面**
访问 `http://localhost:9988/`，点击"策略选股"菜单

**方式二: 数据库查询**
```sql
SELECT strategy_name, code, name 
FROM cn_stock_strategy_YYYYMMDD
ORDER BY strategy_name;
```

**方式三: 查看日志**
```bash
cat instock/log/stock_execute_job.log | grep "策略"
```

---

## 4️⃣ Web 服务问题

### Q4.1: 无法访问 localhost:9988？

**A:** 排查步骤：

1. **检查服务是否启动**
```bash
# 查看是否有 Python 进程
ps aux | grep python
```

2. **检查端口是否被占用**
```bash
# Windows
netstat -an | findstr 9988

# Linux
sudo lsof -i :9988
```

3. **检查防火墙**
```bash
# Windows: 关闭防火墙或添加例外
# Linux
sudo ufw allow 9988
```

4. **尝试指定 IP**
```
http://127.0.0.1:9988/
```

---

### Q4.2: 页面加载很慢？

**A:** 可能原因及解决：

| 原因 | 解决方法 |
|------|----------|
| 数据量大 | 分页加载，减少单页数据量 |
| 数据库慢 | 添加索引，优化查询 |
| 网络问题 | 检查网络连接 |
| 服务器配置低 | 增加内存，使用 SSD |

---

### Q4.3: 如何修改端口号？

**A:** 修改 `instock/web/web_service.py`：

```python
# 找到端口配置
PORT = 9988  # 修改为你想要的端口

# 或通过环境变量
import os
PORT = int(os.environ.get('INSTOCK_PORT', 9988))
```

---

## 5️⃣ Docker 部署问题

### Q5.1: Docker 镜像下载很慢？

**A:** 配置 Docker 镜像加速器。

```bash
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

# 重启 Docker
sudo systemctl restart docker
```

---

### Q5.2: Docker 容器启动后立即退出？

**A:** 查看日志排查：

```bash
# 查看容器日志
docker logs InStock

# 查看退出状态
docker ps -a
```

常见原因：
- 数据库连接失败
- 端口被占用
- 配置文件错误

---

### Q5.3: 如何备份 Docker 数据？

**A:** 备份数据卷：

```bash
# 备份数据库
docker exec InStockDbService mysqldump -u root -proot instockdb > backup.sql

# 恢复数据库
docker exec -i InStockDbService mysql -u root -proot instockdb < backup.sql
```

---

## 6️⃣ 自动交易问题

### Q6.1: 自动交易不执行？

**A:** 检查以下几点：

1. **同花顺客户端是否打开？**
2. **账户密码是否正确？**
3. **券商类型配置是否正确？**
4. **Tesseract 是否安装？**

```bash
# 测试 Tesseract
tesseract --version
```

---

### Q6.2: 如何禁用自动打新？

**A:** 两种方法：

**方法一:** 不启动交易服务
```bash
# 不运行 run_trade.bat
```

**方法二:** 删除或重命名打新策略文件
```bash
# 重命名
mv instock/trade/strategies/stagging.py instock/trade/strategies/stagging.py.bak
```

---

### Q6.3: 支持哪些券商？

**A:** 支持使用同花顺客户端的券商：

- 广发证券 (`gf_client`)
- 华泰证券 (`ht_client`)
- 银河证券 (`yh_client`)
- 通用同花顺 (`universal_client`)
- 更多请参考 easytrader 文档

---

## 7️⃣ 使用技巧

### Q7.1: 如何快速上手？

**A:** 推荐学习路径：

```
1. 阅读 快速开始.md       (5分钟)
2. 完成环境安装           (30分钟)
3. 运行一次数据作业       (5分钟)
4. 访问 Web 界面浏览功能  (10分钟)
5. 阅读其他教程深入学习   (按需)
```

---

### Q7.2: 数据多久更新一次？

**A:** 建议的更新频率：

| 数据类型 | 更新时机 | 命令 |
|----------|----------|------|
| 实时行情 | 交易时段每30分钟 | `basic_data_daily_job.py` |
| 完整数据 | 每日 17:30 | `execute_daily_job.py` |
| 指标计算 | 收盘后 | `indicators_data_daily_job.py` |

---

### Q7.3: 如何关注特定股票？

**A:** 在 Web 界面使用"关注"功能：

1. 找到目标股票
2. 点击"关注"按钮
3. 关注的股票会在列表中置顶、标红显示

---

### Q7.4: 日志文件太大怎么办？

**A:** 定期清理或配置日志轮转：

```bash
# 手动清理
rm instock/log/*.log

# 或只保留最近的日志
tail -10000 stock_execute_job.log > stock_execute_job.log.new
mv stock_execute_job.log.new stock_execute_job.log
```

---

### Q7.5: 如何贡献代码？

**A:** 欢迎贡献！步骤如下：

1. Fork 项目到你的 GitHub
2. 创建功能分支 `git checkout -b feature/my-feature`
3. 提交更改 `git commit -m "Add my feature"`
4. 推送分支 `git push origin feature/my-feature`
5. 创建 Pull Request

---

## 📞 获取更多帮助

如果以上问题没有解决你的困惑：

1. **📖 阅读教程**: 查看 [tutorials/](./tutorials/) 目录下的详细教程
2. **🐛 提交 Issue**: [GitHub Issues](https://github.com/myhhub/stock/issues)
3. **💬 社区讨论**: GitHub Discussions
4. **📧 联系作者**: 查看项目 README

---

> 💡 **提示**: 遇到问题先搜索已有 Issue，可能已经有解决方案！

**祝你使用愉快！** 🎉
