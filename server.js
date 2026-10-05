// ============================================
// 🚜 ГРОМ БРОНИ · СЕРВЕР v3.0
// HTTP + WebSocket + Рейтинг + Никнеймы
// ============================================

const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');

const PORT = process.env.PORT || 3000;
const FILE_PATH = path.join(__dirname, 'games.json');
const SCORES_PATH = path.join(__dirname, 'scores.json');

if (!fs.existsSync(FILE_PATH)) fs.writeFileSync(FILE_PATH, JSON.stringify([]));
if (!fs.existsSync(SCORES_PATH)) fs.writeFileSync(SCORES_PATH, JSON.stringify([]));

// ========== HTTP ==========
const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

    if (req.url === '/' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('🚜 Сервер ГРОМ БРОНИ v3.0 — WebSocket + Рейтинг + Никнеймы');
        return;
    }

    if (req.url === '/games' && req.method === 'GET') {
        fs.readFile(FILE_PATH, 'utf8', (err, data) => {
            if (err) { res.writeHead(500); res.end('[]'); return; }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(data);
        });
        return;
    }

    if (req.url === '/create' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            try {
                const game = JSON.parse(body);
                const games = JSON.parse(fs.readFileSync(FILE_PATH, 'utf8'));
                const now = Date.now();
                const fresh = games.filter(g => now - g.created < 3600000);
                game.id = now.toString(36) + Math.random().toString(36).slice(2, 6);
                game.created = now;
                game.players = [game.host];
                fresh.push(game);
                fs.writeFileSync(FILE_PATH, JSON.stringify(fresh, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, game }));
            } catch(e) { res.writeHead(400); res.end('{"error":"bad"}'); }
        });
        return;
    }

    if (req.url === '/join' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const games = JSON.parse(fs.readFileSync(FILE_PATH, 'utf8'));
                const game = games.find(g => g.id === data.id);
                if (!game) { res.writeHead(404); res.end('{"error":"not found"}'); return; }
                if (!game.players.includes(data.player)) game.players.push(data.player);
                fs.writeFileSync(FILE_PATH, JSON.stringify(games, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, game }));
            } catch(e) { res.writeHead(400); res.end('{"error":"bad"}'); }
        });
        return;
    }

    // 🏆 ТОП-20
    if (req.url === '/leaderboard' && req.method === 'GET') {
        fs.readFile(SCORES_PATH, 'utf8', (err, data) => {
            if (err) { res.writeHead(500); res.end('[]'); return; }
            try {
                const scores = JSON.parse(data);
                scores.sort((a, b) => b.score - a.score);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(scores.slice(0, 20)));
            } catch(e) { res.writeHead(500); res.end('[]'); }
        });
        return;
    }

    // 📊 ОТПРАВИТЬ СЧЁТ
    if (req.url === '/score' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                if (!data.nickname || data.score === undefined) {
                    res.writeHead(400); res.end('{"error":"no data"}'); return;
                }
                const scores = JSON.parse(fs.readFileSync(SCORES_PATH, 'utf8'));
                const existing = scores.find(s => s.nickname === data.nickname);
                if (existing) {
                    if (data.score > existing.score) {
                        existing.score = data.score;
                        existing.wave = data.wave || 0;
                        existing.date = new Date().toISOString();
                    }
                } else {
                    scores.push({
                        nickname: data.nickname,
                        score: data.score,
                        wave: data.wave || 0,
                        date: new Date().toISOString()
                    });
                }
                fs.writeFileSync(SCORES_PATH, JSON.stringify(scores, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch(e) { res.writeHead(400); res.end('{"error":"bad"}'); }
        });
        return;
    }

    // 👤 СОХРАНИТЬ НИК
    if (req.url === '/save-nick' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                if (!data.nickname) { res.writeHead(400); res.end('{"error":"no nick"}'); return; }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, nickname: data.nickname }));
            } catch(e) { res.writeHead(400); res.end('{"error":"bad"}'); }
        });
        return;
    }

    res.writeHead(404);
    res.end('Not found');
});

// ========== WEBSOCKET ==========
const wss = new WebSocketServer({ server });
const rooms = {};

wss.on('connection', (ws) => {
    ws.id = Math.random().toString(36).slice(2, 8);
    ws.roomId = null;
    ws.playerName = 'Игрок';

    console.log('🔌 Подключился: ' + ws.id);

    ws.on('message', (msg) => {
        try {
            const data = JSON.parse(msg);

            // ВХОД В КОМНАТУ
            if (data.type === 'join') {
                ws.roomId = data.roomId;
                ws.playerName = data.name || 'Игрок';
                if (!rooms[ws.roomId]) rooms[ws.roomId] = { players: {}, enemies: [], wave: 1, started: false };
                rooms[ws.roomId].players[ws.id] = {
                    id: ws.id, name: ws.playerName,
                    x: 0, y: 0, angle: 0, hp: 100, color: '#4caf50', score: 0
                };
                broadcast(ws.roomId, {
                    type: 'playerJoined',
                    player: rooms[ws.roomId].players[ws.id],
                    playersCount: Object.keys(rooms[ws.roomId].players).length
                });
                console.log('👤 ' + ws.playerName + ' вошёл в ' + ws.roomId);
                if (Object.keys(rooms[ws.roomId].players).length >= 2 && !rooms[ws.roomId].started) {
                    rooms[ws.roomId].started = true;
                    spawnRoomEnemies(ws.roomId);
                    broadcast(ws.roomId, {
                        type: 'gameStart',
                        enemies: rooms[ws.roomId].enemies,
                        wave: rooms[ws.roomId].wave
                    });
                }
                ws.send(JSON.stringify({
                    type: 'roomState',
                    players: rooms[ws.roomId].players,
                    enemies: rooms[ws.roomId].enemies,
                    wave: rooms[ws.roomId].wave,
                    started: rooms[ws.roomId].started,
                    yourId: ws.id
                }));
                return;
            }

            // ОБНОВЛЕНИЕ ПОЗИЦИИ
            if (data.type === 'update') {
                if (!ws.roomId || !rooms[ws.roomId]) return;
                const p = rooms[ws.roomId].players[ws.id];
                if (!p) return;
                p.x = data.x; p.y = data.y; p.angle = data.angle;
                p.hp = data.hp; p.score = data.score || p.score;
                broadcast(ws.roomId, {
                    type: 'playerUpdate',
                    id: ws.id, name: p.name,
                    x: p.x, y: p.y, angle: p.angle,
                    hp: p.hp, score: p.score
                }, ws.id);
                return;
            }

            // ВЫСТРЕЛ
            if (data.type === 'shoot') {
                if (!ws.roomId) return;
                broadcast(ws.roomId, {
                    type: 'playerShot',
                    id: ws.id, x: data.x, y: data.y, angle: data.angle
                }, ws.id);
                return;
            }

            // УБИЙСТВО ВРАГА
            if (data.type === 'enemyKilled') {
                if (!ws.roomId || !rooms[ws.roomId]) return;
                const room = rooms[ws.roomId];
                room.enemies = room.enemies.filter(e => e.id !== data.enemyId);
                const p = room.players[ws.id];
                if (p) p.score = (p.score || 0) + 1;
                broadcast(ws.roomId, {
                    type: 'enemyRemoved',
                    enemyId: data.enemyId,
                    byPlayer: ws.id,
                    byName: p ? p.name : '',
                    score: p ? p.score : 0
                });
                if (room.enemies.length === 0) {
                    room.wave++;
                    spawnRoomEnemies(ws.roomId);
                    broadcast(ws.roomId, { type: 'newWave', enemies: room.enemies, wave: room.wave });
                }
                return;
            }

        } catch(e) { console.log('❌ Ошибка:', e.message); }
    });

    ws.on('close', () => {
        console.log('❌ Отключился: ' + ws.id);
        if (ws.roomId && rooms[ws.roomId]) {
            delete rooms[ws.roomId].players[ws.id];
            broadcast(ws.roomId, {
                type: 'playerLeft',
                id: ws.id,
                playersCount: Object.keys(rooms[ws.roomId].players).length
            });
            if (Object.keys(rooms[ws.roomId].players).length === 0) delete rooms[ws.roomId];
        }
    });
});

function broadcast(roomId, message, exceptId) {
    if (!rooms[roomId]) return;
    const msgStr = JSON.stringify(message);
    wss.clients.forEach(client => {
        if (client.readyState === 1 && client.roomId === roomId && client.id !== exceptId) {
            client.send(msgStr);
        }
    });
}

function spawnRoomEnemies(roomId) {
    const room = rooms[roomId];
    if (!room) return;
    room.enemies = [];
    const count = Math.min(3 + room.wave, 10);
    for (let i = 0; i < count; i++) {
        room.enemies.push({
            id: 'e_' + Math.random().toString(36).slice(2, 8),
            x: Math.cos((Math.PI * 2 / count) * i) * 200,
            y: Math.sin((Math.PI * 2 / count) * i) * 200,
            angle: 0,
            hp: 30 + room.wave * 10,
            speed: 60 + room.wave * 5,
            color: '#c62828'
        });
    }
}

// ========== ЗАПУСК ==========
server.listen(PORT, () => {
    console.log('🚜 Сервер ГРОМ БРОНИ v3.0 запущен на порту ' + PORT);
    console.log('📡 WebSocket + Рейтинг + Никнеймы — готов!');
});