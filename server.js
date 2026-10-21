// ============================================
// 🖥️ СЕРВЕР ГРОМ ТАНКОВ · v1.1 (С МУЛЬТИПЛЕЕРОМ)
// ============================================
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const http = require('http');         // НОВОЕ (для WebSocket)
const { WebSocketServer } = require('ws'); // НОВОЕ (для WebSocket)

const app = express();
const server = http.createServer(app); // НОВОЕ: оборачиваем express в http-сервер
const wss = new WebSocketServer({ server }); // НОВОЕ: создаем WebSocket сервер

const PORT = process.env.PORT || 3000;
const DB_FILE = path.join(__dirname, 'scores.json');

// Middleware
app.use(cors());
app.use(express.json());

// ========== 📁 БАЗА ДАННЫХ (файл) ==========
function loadScores(){
  try {
    if(fs.existsSync(DB_FILE)){
      return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
    }
  } catch(e){ console.error('Ошибка чтения:', e); }
  return [];
}

function saveScores(scores){
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(scores, null, 2));
  } catch(e){ console.error('Ошибка записи:', e); }
}

let scores = loadScores();

// ========== 🌐 МУЛЬТИПЛЕЕР (WebSocket) ==========
let onlinePlayers = {};

wss.on('connection', (ws) => {
  const id = Math.random().toString(36).substring(2, 9);
  onlinePlayers[id] = { x: 0, y: 0, angle: 0, turretAngle: 0, color: '#4caf50' };

  ws.send(JSON.stringify({ type: 'init', id: id }));

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      if (data.type === 'move') {
        onlinePlayers[id] = { 
          x: data.x, y: data.y, 
          angle: data.angle, turretAngle: data.turretAngle, 
          color: data.color 
        };
        broadcast({ type: 'update', id: id, player: onlinePlayers[id] });
      }
    } catch(e){}
  });

  ws.on('close', () => {
    delete onlinePlayers[id];
    broadcast({ type: 'remove', id: id });
  });
});

function broadcast(data) {
  const msg = JSON.stringify(data);
  wss.clients.forEach((client) => {
    if (client.readyState === 1) { // 1 = OPEN
      client.send(msg);
    }
  });
}

// ========== 🏠 ГЛАВНАЯ ==========
app.get('/', (req, res) => {
  res.send('🚜 Grom Tankov Server OK · Игроков в базе: ' + scores.length + ' · Онлайн: ' + Object.keys(onlinePlayers).length);
});

// ========== 📥 ПОЛУЧИТЬ ТОП-20 ==========
app.get('/leaderboard', (req, res) => {
  const top = [...scores]
    .sort((a, b) => b.score - a.score)
    .slice(0, 20);
  res.json(top);
});

// ========== 📤 ОТПРАВИТЬ СЧЁТ ==========
app.post('/score', (req, res) => {
  const { nickname, score, wave } = req.body;

  if(!nickname || typeof nickname !== 'string' || nickname.length < 3){
    return res.status(400).json({ error: 'Ник минимум 3 буквы' });
  }
  if(typeof score !== 'number' || score < 0){
    return res.status(400).json({ error: 'Счёт должен быть числом ≥ 0' });
  }
  if(nickname.length > 15){
    return res.status(400).json({ error: 'Ник максимум 15 букв' });
  }

  const existing = scores.find(s => s.nickname.toLowerCase() === nickname.toLowerCase());

  if(existing){
    if(score > existing.score){
      existing.score = score;
      existing.wave = wave || existing.wave;
      existing.updated = Date.now();
    }
  } else {
    scores.push({
      nickname: nickname,
      score: score,
      wave: wave || 1,
      created: Date.now(),
      updated: Date.now()
    });
  }

  scores.sort((a, b) => b.score - a.score);
  scores = scores.slice(0, 100);
  saveScores(scores);

  res.json({ ok: true, rank: scores.findIndex(s => s.nickname.toLowerCase() === nickname.toLowerCase()) + 1 });
});

// ========== 🏆 СТАТИСТИКА ==========
app.get('/stats', (req, res) => {
  res.json({
    totalPlayers: scores.length,
    topScore: scores.length > 0 ? scores[0].score : 0,
    topPlayer: scores.length > 0 ? scores[0].nickname : '—',
    online: Object.keys(onlinePlayers).length
  });
});

// ========== 🚀 ЗАПУСК ==========
server.listen(PORT, () => {
  console.log('🚜 Сервер Гром Танков (с мультиплеером) запущен на порту ' + PORT);
});