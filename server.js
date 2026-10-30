// ========== УНИВЕРСАЛЬНАЯ ПОЧТА ==========
if (data.type === 'mail_message') {
    console.log('📧 Почта: пришло новое сообщение!');
    
    // Пересылаем письмо всем, кто подключен к почте
    wss.clients.forEach(c => {
        if (c.readyState === 1) {
            c.send(JSON.stringify({
                type: 'mail_message',
                subject: data.subject || 'Без темы',
                body: data.body || 'Пустое сообщение',
                from: data.from || 'Аноним'
            }));
        }
    });
}