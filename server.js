// ============================================
// 🚜 ГРОМ БРОНИ · СЕРВЕР ИГР
// ============================================

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const FILE_PATH = path.join(__dirname, 'games.json');

// Создаём файл, если нет
if (!fs.existsSync(FILE_PATH)) {
    fs.writeFileSync(FILE_PATH, JSON.stringify([]));
}

const server = http.createServer((req, res) => {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // ГЛАВНАЯ
    if (req.url === '/' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('🚜 Сервер ГРОМ БРОНИ работает!');
        return;
    }

    // 1. СПИСОК ИГР
    if (req.url === '/games' && req.method === 'GET') {
        fs.readFile(FILE_PATH, 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Ошибка чтения' }));
                return;
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(data);
        });
        return;
    }

    // 2. СОЗДАТЬ ИГРУ
    if (req.url === '/create' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const game = JSON.parse(body);
                if (!game.name || !game.host) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Нужно имя и хост' }));
                    return;
                }
                const games = JSON.parse(fs.readFileSync(FILE_PATH, 'utf8'));
                // Убираем старые игры (старше 1 часа)
                const now = Date.now();
                const fresh = games.filter(g => now - g.created < 3600000);
                // Добавляем новую
                game.id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
                game.created = now;
                game.players = [game.host];
                fresh.push(game);
                fs.writeFileSync(FILE_PATH, JSON.stringify(fresh, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, game }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Ошибка формата' }));
            }
        });
        return;
    }

    // 3. ПРИСОЕДИНИТЬСЯ К ИГРЕ
    if (req.url === '/join' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                if (!data.id || !data.player) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Нужен ID и игрок' }));
                    return;
                }
                const games = JSON.parse(fs.readFileSync(FILE_PATH, 'utf8'));
                const game = games.find(g => g.id === data.id);
                if (!game) {
                    res.writeHead(404, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Игра не найдена' }));
                    return;
                }
                if (!game.players.includes(data.player)) {
                    game.players.push(data.player);
                }
                fs.writeFileSync(FILE_PATH, JSON.stringify(games, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, game }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Ошибка формата' }));
            }
        });
        return;
    }

    // 4. УДАЛИТЬ ИГРУ
    if (req.url === '/delete' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                let games = JSON.parse(fs.readFileSync(FILE_PATH, 'utf8'));
                games = games.filter(g => g.id !== data.id);
                fs.writeFileSync(FILE_PATH, JSON.stringify(games, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Ошибка' }));
            }
        });
        return;
    }

    res.writeHead(404);
    res.end('Не найдено');
});

server.listen(PORT, () => {
    console.log('🚜 Сервер ГРОМ БРОНИ работает на порту ' + PORT);
});