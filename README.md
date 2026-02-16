# 围棋游戏后端服务器使用说明

## 📦 安装依赖

首先安装`websockets`库：

```bash
pip install websockets
```

## 🚀 启动服务器

在终端中运行：

```bash
cd /Users/zhouql1978/Documents/first_web
python server.py
```

你会看到：

```
[2025-01-15 10:30:00] 启动围棋游戏服务器...
[2025-01-15 10:30:00] 监听地址：ws://localhost:8080
[2025-01-15 10:30:00] 等待客户端连接...
```

## 🔧 修改前端配置

打开HTML文件，找到WebSocket配置部分（大约在第242行）：

```javascript
const WS_CONFIG = {
    url: 'ws://localhost:8080/ws',  // 修改这里
    reconnectInterval: 3000,
    debug: true
};
```

改为：

```javascript
const WS_CONFIG = {
    url: 'ws://localhost:8080',  // 去掉 /ws
    reconnectInterval: 3000,
    debug: true
};
```

## 📡 消息流程

### 1. 创建房间

**前端发送：**
```json
{
    "type": "create_room",
    "timestamp": 1736932200000
}
```

**后端处理：**
- 生成6位数房间ID（如：123456）
- 生成玩家ID（如：player_1）
- 创建房间，分配黑子（color=1）

**后端响应：**
```json
{
    "type": "room_created",
    "success": true,
    "roomId": "123456",
    "playerId": "player_1"
}
```

### 2. 加入房间

**前端发送：**
```json
{
    "type": "join_room",
    "roomId": "123456",
    "timestamp": 1736932200000
}
```

**后端处理：**
- 检查房间是否存在
- 检查房间是否已满
- 加入房间，分配白子（color=2）

**后端响应：**
```json
{
    "type": "room_joined",
    "success": true,
    "roomId": "123456",
    "playerId": "player_2",
    "playerColor": 2
}
```

### 3. 落子

**前端发送：**
```json
{
    "type": "place_stone",
    "roomId": "123456",
    "playerId": "player_1",
    "row": 3,
    "col": 15,
    "color": 1,
    "timestamp": 1736932200000
}
```

**后端处理：**
- 验证玩家是否在房间中
- 验证是否轮到该玩家
- 验证位置是否为空
- 落子，更新棋盘状态
- 切换到下一个玩家
- **广播**给房间内所有玩家

**后端响应（发送给所有玩家）：**
```json
{
    "type": "move_placed",
    "success": true,
    "row": 3,
    "col": 15,
    "color": 1,
    "nextPlayer": 2
}
```

## 🔍 调试技巧

### 查看后端日志

服务器会打印所有收到的消息：

```
[2025-01-15 10:30:05] 新客户端连接：('127.0.0.1', 52341)
[2025-01-15 10:30:06] 收到消息：create_room
[2025-01-15 10:30:06] 收到创建房间请求
[2025-01-15 10:30:06] 房间 123456 创建成功，玩家 player_1
```

### 查看前端日志

打开浏览器的开发者工具（F12），切换到Console标签，你会看到：

```
[GoGame] 页面加载完成，WebSocket初始化中...
[GoGame] WebSocket连接成功
[GoGame] 发送: {"type":"create_room","timestamp":1736932200000}
[GoGame] 收到: {"type":"room_created","success":true,"roomId":"123456","playerId":"player_1"}
```

## 📝 数据结构说明

### rooms（房间字典）

```python
{
    "123456": {
        "roomId": "123456",
        "players": {
            "player_1": {"color": 1, "websocket": <websocket对象>},
            "player_2": {"color": 2, "websocket": <websocket对象>}
        },
        "boardState": [
            [0, 0, 0, ..., 0],  # 第0行
            [0, 0, 0, ..., 0],  # 第1行
            ...
            [0, 0, 0, ..., 0]   # 第18行
        ],
        "currentPlayer": 1,  # 当前轮到谁（1=黑，2=白）
        "moveCount": 5,      # 已落子数量
        "createdAt": "2025-01-15T10:30:00"
    }
}
```

### boardState（棋盘状态）

- `0`：空位
- `1`：黑子
- `2`：白子

## 🧪 测试步骤

1. **启动后端**
   ```bash
   python server.py
   ```

2. **打开前端**
   - 在浏览器中打开HTML文件
   - 打开浏览器开发者工具（F12）→ Console

3. **创建房间**
   - 点击"Make a new room"
   - 后端日志：`房间 123456 创建成功`
   - 前端日志：`收到: {"type":"room_created",...}`

4. **加入房间**（用另一个浏览器窗口）
   - 输入房间ID：123456
   - 点击"Join Room"
   - 后端日志：`玩家 player_2 加入房间 123456`

5. **开始下棋**
   - 点击棋盘交叉点落子
   - 后端日志：`落子成功：(3, 15), 颜色1`
   - 两个浏览器窗口都应该同步显示棋子

## ❗ 常见问题

### 1. 连接失败

**错误：** `WebSocket连接失败`

**解决：**
- 确认后端服务器正在运行
- 确认端口8080未被占用
- 检查防火墙设置

### 2. 消息发送失败

**错误：** `WebSocket未连接，无法发送数据`

**解决：**
- 等待几秒让WebSocket完成连接
- 查看后端日志确认服务器正常

### 3. 落子失败

**错误：** `还没轮到你` 或 `这个位置已经有棋子了`

**解决：**
- 等待对手落子后再下
- 选择空白位置落子

## 🎮 下一步改进

1. **添加提子规则**：实现围棋的提子逻辑
2. **添加计时器**：每步棋限时
3. **添加悔棋功能**：允许撤销上一步
4. **添加观战模式**：允许其他人观看对局
5. **添加存档功能**：保存棋局到数据库

## 📞 需要帮助？

如果遇到问题，检查以下几点：
1. 后端是否正在运行
2. 前端的WebSocket URL是否正确
3. 浏览器Console是否有错误
4. 后端终端是否有错误信息
