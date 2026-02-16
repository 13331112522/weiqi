# 围棋游戏部署指南

## 📋 目录
1. [方案1：本地测试](#方案1本地测试)
2. [方案2：内网穿透（推荐给朋友测试）](#方案2内网穿透推荐给朋友测试)
3. [方案3：云服务器部署（正式上线）](#方案3云服务器部署正式上线)
4. [方案4：免费云平台（适合学习）](#方案4免费云平台适合学习)

---

## 方案1：本地测试

### 适用场景
- 自己测试功能
- 局域网内其他设备访问

### 步骤

1. **启动后端**
   ```bash
   cd /Users/zhouql1978/Documents/first_web
   python server.py
   ```

2. **获取本机IP地址**
   ```bash
   # macOS
   ifconfig | grep "inet "

   # 或者在终端运行
   ipconfig getifaddr en0
   ```

3. **修改HTML文件**
   ```javascript
   const WS_CONFIG = {
       url: 'ws://你的本机IP:8080',  // 例如：ws://192.168.1.100:8080
       reconnectInterval: 3000,
       debug: true
   };
   ```

4. **局域网内其他设备访问**
   - 手机/电脑连接同一WiFi
   - 浏览器打开HTML文件

---

## 方案2：内网穿透（推荐给朋友测试）

### 使用ngrok（推荐）

#### 1. 安装ngrok

```bash
# macOS
brew install ngrok

# 或下载：https://ngrok.com/download
```

#### 2. 注册ngrok账号

访问：https://ngrok.com/signup

#### 3. 启动服务

**终端1：启动后端**
```bash
cd /Users/zhouql1978/Documents/first_web
python server.py
```

**终端2：启动ngrok**
```bash
ngrok http 8080
```

#### 4. 修改HTML配置

```javascript
const WS_CONFIG = {
    url: 'wss://abc123.ngrok.io',  // 使用ngrok提供的地址
    reconnectInterval: 3000,
    debug: true
};
```

#### 5. 分享链接

将ngrok提供的URL分享给朋友

---

## 方案3：云服务器部署（正式上线）

### 推荐云服务商

| 服务商 | 适合人群 | 价格 |
|--------|---------|------|
| **阿里云** | 国内用户 | ¥100-200/年 |
| **腾讯云** | 国内用户 | ¥100-200/年 |
| **AWS** | 国际用户 | $5-10/月 |

### 完整部署步骤（以阿里云为例）

#### 第一步：购买服务器

1. 访问：https://www.aliyun.com
2. 购买ECS云服务器
   - 操作系统：Ubuntu 20.04
   - 配置：1核2GB
   - 费用：约¥100-200/年

#### 第二步：登录服务器

```bash
ssh root@你的公网IP
# 输入密码
```

#### 第三步：安装环境

```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install websockets
```

#### 第四步：上传代码

```bash
# 在本地Mac执行
scp server.py root@你的公网IP:/root/weiqi/
```

#### 第五步：配置防火墙

在阿里云控制台添加安全组规则：
- 端口：8080
- 协议：TCP

#### 第六步：修改server.py

```python
# 改成监听所有网络接口
async with websockets.serve(handle_client, "0.0.0.0", 8080):
```

#### 第七步：启动服务

```bash
# 直接运行
python3 server.py

# 或使用systemd（推荐）
sudo systemctl start weiqi
```

---

## 方案4：免费云平台（适合学习）

### Render.com

1. 注册：https://render.com
2. 连接GitHub仓库
3. 自动部署

### Railway.app

1. 注册：https://railway.app
2. 部署Python服务
3. 自动获得公网URL

---

## 🚀 推荐方案

**给朋友测试：** → 使用ngrok（方案2）

**正式上线：** → 阿里云服务器（方案3）

**学习部署：** → Render.com（方案4）
