# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time Go (Weiqi) game implementation using WebSocket for client-server communication. Players can create rooms, join existing rooms, and play Go on a 19×19 board with real-time synchronization.

### Architecture

- **Frontend**: Single HTML file (`index.html`) with embedded JavaScript, CSS, and SVG-based board rendering
- **Backend**: Python WebSocket server (`server.py`) using `websockets` library
- **Protocol**: JSON-based WebSocket messages for all game actions

The architecture follows a simple message-passing pattern:
1. Frontend sends JSON messages via WebSocket
2. Backend processes messages and updates game state
3. Backend broadcasts state changes to all players in a room
4. Frontend renders updates received from server

## Development Commands

### Start the backend server
```bash
python server.py
```
Server runs on `ws://localhost:8080` by default.

### Open the frontend
Open `index.html` directly in a browser. The WebSocket connection is configured at line ~292:
```javascript
const WS_CONFIG = {
    url: 'ws://localhost:8080/ws',  // Note: should be 'ws://localhost:8080' (no /ws)
    reconnectInterval: 3000,
    debug: true
};
```

### Install dependencies
```bash
pip install -r requirements.txt
```
Only dependency is `websockets>=12.0`.

## Key Implementation Details

### Backend (`server.py`)

**Data structures:**
- `rooms: Dict[room_id, room_info]` - Stores all active rooms with board state, players, and move count
- `connected_clients: Dict[websocket, client_info]` - Tracks all active connections
- Room structure includes: `players` dict, `boardState` (19×19 array), `moveCount`, `createdAt`

**Message handlers:**
- `handle_create_room()` - Generates 6-digit room ID, initializes board
- `handle_join_room()` - Validates room, assigns player color (black=1, white=2)
- `handle_place_stone()` - Validates move, updates board, broadcasts to all players

**Important:** The server maintains authoritative game state. Player colors are assigned by the server and stored in `room["players"][player_id]["color"]`. The server ignores color values sent by clients and uses its own records.

### Frontend (`index.html`)

**Board rendering:**
- SVG-based 19×19 grid (lines drawn with SVG)
- Intersection points as clickable div elements positioned with absolute CSS
- Stones rendered as div elements with radial gradients for 3D effect
- Board size: 580×580px with 20px padding

**WebSocket flow:**
1. `initWebSocket()` - Establishes connection with auto-reconnect
2. `sendToServer()` - Sends JSON messages
3. `onmessage()` handler - Dispatches to specific handlers based on `message.type`
4. Handlers: `handleRoomCreated()`, `handleRoomJoined()`, `handleMovePlaced()`

**State management:**
- `current_room_id` - Active room ID
- `my_player_id` - Current player's ID
- `myColor` - Assigned color (1=black, 2=white)
- `currentPlayer` - Whose turn it is (server-tracked)

### Message Protocol

**Create room:**
```json
{"type": "create_room", "timestamp": 1234567890}
```

**Join room:**
```json
{"type": "join_room", "roomId": "123456", "timestamp": 1234567890}
```

**Place stone:**
```json
{"type": "place_stone", "roomId": "123456", "playerId": "player_1", "row": 3, "col": 15, "color": 1, "timestamp": 1234567890}
```

**Response (room_created):**
```json
{"type": "room_created", "success": true, "roomId": "123456", "playerId": "player_1"}
```

**Response (move_placed):** Broadcast to ALL players in room
```json
{"type": "move_placed", "success": true, "row": 3, "col": 15, "color": 1, "nextPlayer": 2}
```

## Common Issues

### WebSocket URL mismatch
The frontend config at line ~292 has `/ws` suffix but server runs on root path. When debugging connection issues, verify `WS_CONFIG.url` matches server endpoint.

### Turn validation
Server validates turns using `currentPlayer` variable. Currently hardcoded to `1` in `handle_place_stone()` - this needs to be moved to room state for proper turn alternation.

### Color assignment
First player to create/join gets black (1), second player gets white (2). Server maintains authoritative color assignment in `room["players"]`.

## Code Structure Notes

- `server.py:453` lines total - single file with all backend logic
- `index.html:957` lines - self-contained frontend with embedded CSS/JS
- No external frontend frameworks - vanilla JavaScript only
- No database - all state in-memory, lost on server restart
- `room manage.py` exists but is empty - appears to be unused placeholder

## Future Improvements

The README and DEPLOYMENT docs mention several planned features:
- Capture/removal logic (提子规则) - Not implemented
- Move timer - Not implemented
- Undo functionality - Not implemented
- Spectator mode - Not implemented
- Game persistence - Not implemented
