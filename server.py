"""
围棋游戏后端服务器 - WebSocket实现
功能：接收前端发送的JSON数据，处理游戏逻辑

安装依赖：
    pip install websockets

运行服务器：
    python server.py

前端会连接到：ws://localhost:8080

Render部署会自动使用环境变量PORT
"""

import asyncio
import websockets
import json
import os
from datetime import datetime
from typing import Dict, Set

# ==================== 配置 ====================

# Render.com 提供环境变量 PORT，默认使用 8080
PORT = int(os.environ.get("PORT", 8080))

# Render.com 需要监听 0.0.0.0 才能接受外部连接
HOST = os.environ.get("HOST", "0.0.0.0")

# ==================== 数据结构 ====================

# 存储所有连接的客户端
# Dict[websocket, player_info]
# player_info 包含：player_id, room_id, color等
connected_clients: Dict = {}

# 存储房间信息
# Dict[room_id, room_info]
# room_info 包含：players, board_state, current_player等
rooms: Dict = {}

# 玩家ID计数器
player_id_counter = 0


# ==================== 辅助函数 ====================


def generate_player_id():
    """生成唯一的玩家ID"""
    global player_id_counter
    player_id_counter += 1
    return f"player_{player_id_counter}"


def generate_room_id():
    """生成随机的房间ID（6位数字）"""
    import random
    return str(random.randint(100000, 999999))


def log(message: str):
    """打印日志（带时间戳）"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# ==================== 消息处理函数 ====================

async def handle_create_room(websocket, data: dict):
    """
    处理创建房间请求

    前端发送：
        {
            "type": "create_room",
            "timestamp": 1234567890
        }

    后端响应：
        {
            "type": "room_created",
            "success": true,
            "roomId": "123456",
        }
    """
    log(f"收到创建房间请求")

    # 生成房间ID和玩家ID
    room_id = generate_room_id()
    player_id = generate_player_id()

    # 创建新房间
    rooms[room_id] = {
        "roomId": room_id,
        "players": {
            player_id: {
                "color": 1,  # 创建者执黑
                "websocket": websocket
            }
        },
        "boardState": [[0 for _ in range(19)] for _ in range(19)],  # 19×19棋盘
        "currentPlayer": 1,  # 当前玩家：1=黑，2=白
        "moveCount": 0,
        "createdAt": datetime.now().isoformat()
    }

    # 保存客户端信息
    connected_clients[websocket] = {
        "playerId": player_id,
        "roomId": room_id,
        "color": 1  # 创建房间者执黑
    }

    # 发送成功响应
    response = {
        "type": "room_created",
        "success": True,
        "roomId": room_id,
        "playerId": player_id,
        "playerColor": 1  # 创建房间者执黑
    }

    await websocket.send(json.dumps(response))
    log(f"房间 {room_id} 创建成功，玩家 {player_id} 加入（黑棋）")


async def handle_join_room(websocket, data: dict):
    """
    处理加入房间请求

    前端发送：
        {
            "type": "join_room",
            "roomId": "123456",
            "playerId": "player_1",
            "timestamp": 1234567890
        }

    后端响应：
        {
            "type": "room_joined",
            "success": true,
            "roomId": "123456",
            "playerId": "player_1",
            "playerColor": 2
        }
    """
    room_id = data.get("roomId")
    log(f"收到加入房间请求：{room_id}")

    # 检查房间是否存在
    if room_id not in rooms:
        response = {
            "type": "room_joined",
            "success": False,
            "message": "房间不存在"
        }
        await websocket.send(json.dumps(response))
        log(f"加入失败：房间 {room_id} 不存在")
        return

    room = rooms[room_id]

    # 检查房间是否已满（最多2人）
    if len(room["players"]) > 2:
        response = {
            "type": "room_joined",
            "success": False,
            "message": "房间已满"
        }
        await websocket.send(json.dumps(response))
        log(f"加入失败：房间 {room_id} 已满")
        return

    # 生成玩家ID
    player_id = generate_player_id()

    # 加入房间（第二个玩家是白子）
    player_color = 2 if len(room["players"]) == 1 else 1
    room["players"][player_id] = {
        "color": player_color,
        "websocket": websocket
    }

    # 保存客户端信息
    connected_clients[websocket] = {
        "playerId": player_id,
        "roomId": room_id,
        "color": player_color
    }

    # 发送成功响应
    response = {
        "type": "room_joined",
        "success": True,
        "roomId": room_id,
        "playerId": player_id,
        "playerColor": player_color
    }

    await websocket.send(json.dumps(response))
    log(f"玩家 {player_id} 加入房间 {room_id}，颜色：{player_color}")


# ==================== 围棋提子辅助函数 ====================

def get_group_and_liberties(board, row, col):
    """
    计算指定位置棋子所在的棋串和气的数量

    使用BFS（广度优先搜索）算法：
    1. 从指定位置出发，找到所有相连的同色棋子（形成一个棋串）
    2. 统计这个棋串周围的所有空位（气）

    参数:
        board: 棋盘状态（19×19二维数组）
        row, col: 棋子位置

    返回:
        stones: 棋串中所有棋子的坐标列表 [(row1, col1), (row2, col2), ...]
        liberties: 气的坐标集合 {(row1, col1), (row2, col2), ...}
    """
    color = board[row][col]
    if color == 0:
        return [], set()

    stones = []
    liberties = set()
    visited = set()
    queue = [(row, col)]
    visited.add((row, col))

    while queue:
        r, c = queue.pop(0)
        stones.append((r, c))

        # 检查四个方向：上下左右
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc

            # 越界检查
            if nr < 0 or nr >= 19 or nc < 0 or nc >= 19:
                continue

            # 空位 = 气
            if board[nr][nc] == 0:
                liberties.add((nr, nc))
            # 同色棋子 = 加入棋串
            elif board[nr][nc] == color and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))

    return stones, liberties


def check_and_remove_captures(board, row, col, color):
    """
    检查并提走落子后应该被提走的对手棋子

    落子后，检查落子点四周的对手棋子：
    1. 对每个相邻的对手棋子，计算其所在棋串的气
    2. 如果气为0，提走整个棋串
    3. 返回所有被提走的棋子位置

    参数:
        board: 棋盘状态（会被修改）
        row, col: 落子位置
        color: 落子的颜色（1=黑，2=白）

    返回:
        captured_stones: 被提走的棋子坐标列表 [(row1, col1), ...]
    """
    opponent_color = 2 if color == 1 else 1
    captured = []

    # 检查四个方向的对手棋子
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc

        # 越界检查
        if nr < 0 or nr >= 19 or nc < 0 or nc >= 19:
            continue

        # 如果是对手棋子
        if board[nr][nc] == opponent_color:
            stones, liberties = get_group_and_liberties(board, nr, nc)

            # 如果没有气，提走整个棋串
            if len(liberties) == 0:
                for (r, c) in stones:
                    board[r][c] = 0
                    captured.append((r, c))
                    log(f"  提子: ({r}, {c})")

    return captured


async def handle_place_stone(websocket, data: dict):
    """
    处理落子请求

    前端发送：
        {
            "type": "place_stone",
            "roomId": "123456",
            "playerId": "player_1",
            "row": 3,
            "col": 15,
            "color": 1,
            "timestamp": 1234567890
        }

    后端响应：
        {
            "type": "move_placed",
            "success": true,
            "row": 3,
            "col": 15,
            "color": 1,
            "nextPlayer": 2
        }
    """
    room_id = data.get("roomId")


    player_id = data.get("playerId")   #dict
    row = data.get("row")
    col = data.get("col")

    # 检查房间是否存在（必须在访问之前检查）
    if room_id not in rooms:
        response = {
            "type": "move_placed",
            "success": False,
            "message": "房间不存在"
        }
        await websocket.send(json.dumps(response))
        log(f"落子失败：房间 {room_id} 不存在")
        return

    room = rooms[room_id]

    # 验证房间结构
    if "boardState" not in room or "players" not in room:
        response = {
            "type": "move_placed",
            "success": False,
            "message": "房间数据损坏，请重新创建房间"
        }
        await websocket.send(json.dumps(response))
        log(f"落子失败：房间 {room_id} 数据结构不完整")
        return

    # 现在可以安全地访问房间数据
    color = room["players"][player_id]["color"]  # 使用服务器记录的颜色，忽略前端传来的颜色
    log(f"收到落子请求：房间{room_id}, 玩家{player_id}, 位置({row},{col}), 颜色{color}")

    # 检查玩家是否在房间中
    if player_id not in room["players"]:
        response = {
            "type": "move_placed",
            "success": False,
            "message": "你不是这个房间的玩家"
        }
        await websocket.send(json.dumps(response))
        return

    # 检查是否轮到该玩家
    if room["currentPlayer"] != color:
        response = {
            "type": "move_placed",
            "success": False,
            "message": "还没轮到你"
        }
        await websocket.send(json.dumps(response))
        return

    # 检查位置是否已有棋子
    if room["boardState"][row][col] != 0:
        response = {
            "type": "move_placed",
            "success": False,
            "message": "这个位置已经有棋子了"
        }
        await websocket.send(json.dumps(response))
        return



    # 落子
    room["boardState"][row][col] = color
    room["moveCount"] += 1

    # 自动提子：检查并移除气尽的对手棋子
    captured_stones = check_and_remove_captures(
        room["boardState"],
        row,
        col,
        color
    )

    # 切换玩家
    room["currentPlayer"] = 2 if color == 1 else 1

    # 发送成功响应给所有玩家
    response = {
        "type": "move_placed",
        "success": True,
        "row": row,
        "col": col,
        "color": color,
        "nextPlayer": room["currentPlayer"]
    }

    # 如果有提子，添加到响应中
    if captured_stones:
        response["captured"] = [{"row": r, "col": c} for r, c in captured_stones]
        log(f"提掉了 {len(captured_stones)} 颗子")

    # 广播给房间内所有玩家
    for player_info in room["players"].values():
        player_ws = player_info["websocket"]
        try:
            await player_ws.send(json.dumps(response))
        except Exception as e:
            log(f"发送消息失败：{e}")



# ==================== WebSocket主处理函数 ====================

async def handle_client(websocket, path):
    """
    处理客户端连接的主函数
    每当有新客户端连接时，websocket库会自动调用这个函数

    参数：
        websocket: WebSocket连接对象
        path: 连接路径（暂时不用）
    """
    client_address = websocket.remote_address
    log(f"新客户端连接：{client_address}")

    try:
        # 持续接收客户端消息
        async for message in websocket:
            try:
                # 解析JSON数据
                # 类似前端的数据格式：
                # {"type": "create_room", "timestamp": ...}
                data = json.loads(message)

                log(f"收到消息：{data.get('type')}")

                # 根据消息类型分发到不同的处理函数
                message_type = data.get("type")

                if message_type == "create_room":
                    await handle_create_room(websocket, data)

                elif message_type == "join_room":
                    await handle_join_room(websocket, data)

                elif message_type == "place_stone":
                    await handle_place_stone(websocket, data)

                else:
                    # 未知消息类型
                    response = {
                        "type": "error",
                        "message": f"未知消息类型：{message_type}"
                    }
                    await websocket.send(json.dumps(response))
                    log(f"未知消息类型：{message_type}")

            except json.JSONDecodeError as e:
                # JSON解析错误
                log(f"JSON解析错误：{e}")
                response = {
                    "type": "error",
                    "message": "JSON格式错误"
                }
                await websocket.send(json.dumps(response))

            except Exception as e:
                # 其他错误
                log(f"处理消息时出错：{e}")
                response = {
                    "type": "error",
                    "message": str(e)
                }
                await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        log(f"客户端断开连接：{client_address}")

    finally:
        # 清理断开的客户端
        if websocket in connected_clients:
            client_info = connected_clients[websocket]
            player_id = client_info["playerId"]
            room_id = client_info["roomId"]

            log(f"清理客户端：玩家 {player_id}, 房间 {room_id}")

            # 从房间中移除玩家
            if room_id in rooms and player_id in rooms[room_id]["players"]:
                del rooms[room_id]["players"][player_id]

                # 如果房间空了，删除房间
                if len(rooms[room_id]["players"]) == 0:
                    del rooms[room_id]
                    log(f"房间 {room_id} 已删除（无玩家）")

            # 从连接列表中移除
            del connected_clients[websocket]


# ==================== 启动服务器 ====================

async def main():
    """
    启动WebSocket服务器
    本地开发：监听地址 0.0.0.0:8080
    Render部署：自动使用环境变量 PORT
    """
    log("启动围棋游戏服务器...")
    log(f"监听地址：{HOST}:{PORT}")
    log("等待客户端连接...")

    # 创建WebSocket服务器
    async with websockets.serve(handle_client, HOST, PORT):
        # 持续运行，直到手动停止（Ctrl+C）
        await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    try:
        # 运行服务器
        asyncio.run(main())
    except KeyboardInterrupt:
        log("\n服务器已停止")
