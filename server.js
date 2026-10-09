// ============================================
// 🖥️ СЕРВЕР ГРОМ ТАНКОВ · v1.0
// ============================================
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
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

// ========== 🏠 ГЛАВНАЯ ==========
app.get('/', (req, res) => {
  res.send('🚜 Grom Tankov Server OK · Игроков: ' + scores.length);
});

// ========== 📥 ПОЛУЧИТЬ ТОП-20 ==========
app.get('/leaderboard', (req, res) => {
  const top = scores
    .sort((a, b) => b.score - a.score)
    .slice(0, 20);
  res.json(top);
});

// ========== 📤 ОТПРАВИТЬ СЧЁТ ==========
app.post('/score', (req, res) => {
  const { nickname, score, wave } = req.body;

  // Проверка
  if(!nickname || typeof nickname !== 'string' || nickname.length < 3){
    return res.status(400).json({ error: 'Ник минимум 3 буквы' });
  }
  if(typeof score !== 'number' || score < 0){
    return res.status(400).json({ error: 'Счёт должен быть числом ≥ 0' });
  }
  if(nickname.length > 15){
    return res.status(400).json({ error: 'Ник максимум 15 букв' });
  }

  // Ищем игрока
  const existing = scores.find(s => s.nickname.toLowerCase() === nickname.toLowerCase());

  if(existing){
    // Обновляем если счёт больше
    if(score > existing.score){
      existing.score = score;
      existing.wave = wave || existing.wave;
      existing.updated = Date.now();
    }
  } else {
    // Новый игрок
    scores.push({
      nickname: nickname,
      score: score,
      wave: wave || 1,
      created: Date.now(),
      updated: Date.now()
    });
  }

  // Сортируем и оставляем только топ-100
  scores.sort((a, b) => b.score - a.score);
  scores = scores.slice(0, 100);

  saveScores(scores);

  console.log('📥 ' + nickname + ': ' + score + ' очков');
  res.json({ ok: true, rank: scores.findIndex(s => s.nickname.toLowerCase() === nickname.toLowerCase()) + 1 });
});

// ========== 🏆 СТАТИСТИКА ==========
app.get('/stats', (req, res) => {
  res.json({
    totalPlayers: scores.length,
    topScore: scores.length > 0 ? scores[0].score : 0,
    topPlayer: scores.length > 0 ? scores[0].nickname : '—'
  });
});

// ========== 🚀 ЗАПУСК ==========
app.listen(PORT, () => {
  console.log('🚜 Сервер Гром Танков запущен на порту ' + PORT);
  console.log('📊 Игроков в базе: ' + scores.length);
});