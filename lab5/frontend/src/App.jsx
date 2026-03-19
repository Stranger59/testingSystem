import React, { useState, useEffect } from 'react';

const API = 'http://localhost:8000';

const styles = {
  container: { fontFamily: 'Arial, sans-serif', maxWidth: 800, margin: '0 auto', padding: 24 },
  h1: { color: '#2c5f2e', borderBottom: '2px solid #2c5f2e', paddingBottom: 8 },
  h2: { color: '#388e3c', marginTop: 32 },
  card: { background: '#f9fbe7', border: '1px solid #c5e1a5', borderRadius: 8, padding: 16, marginBottom: 12 },
  input: { padding: '8px 12px', border: '1px solid #aed581', borderRadius: 4, marginRight: 8, fontSize: 14 },
  btn: { padding: '8px 16px', borderRadius: 4, border: 'none', cursor: 'pointer', fontSize: 14, marginRight: 6 },
  btnGreen: { background: '#4caf50', color: '#fff' },
  btnBlue: { background: '#1976d2', color: '#fff' },
  btnRed: { background: '#e53935', color: '#fff' },
  status: { padding: '8px 12px', borderRadius: 4, marginTop: 8, fontSize: 13 },
  ok: { background: '#e8f5e9', color: '#2e7d32', border: '1px solid #a5d6a7' },
  err: { background: '#ffebee', color: '#c62828', border: '1px solid #ef9a9a' },
  tag: { display: 'inline-block', background: '#c8e6c9', color: '#1b5e20', borderRadius: 12, padding: '2px 10px', fontSize: 12, marginRight: 4 },
};

export default function App() {
  const [topics, setTopics] = useState([]);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [editId, setEditId] = useState('');
  const [editTitle, setEditTitle] = useState('');
  const [status, setStatus] = useState(null);
  const [health, setHealth] = useState(null);

  const showStatus = (msg, ok = true) => setStatus({ msg, ok });

  // GET /health
  const checkHealth = async () => {
    try {
      const r = await fetch(`${API}/health`);
      const d = await r.json();
      setHealth(d.status);
      showStatus('Сервер работает ✓');
    } catch {
      setHealth('error');
      showStatus('Сервер недоступен', false);
    }
  };

  // GET /topics
  const fetchTopics = async () => {
    try {
      const r = await fetch(`${API}/topics`);
      setTopics(await r.json());
      showStatus(`Загружено тем: ${topics.length}`);
    } catch {
      showStatus('Ошибка загрузки тем', false);
    }
  };

  // POST /topics
  const createTopic = async () => {
    if (!newTitle.trim()) return showStatus('Введите название темы', false);
    try {
      const r = await fetch(`${API}/topics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, description: newDesc }),
      });
      if (!r.ok) throw new Error();
      const d = await r.json();
      showStatus(`Тема "${d.title}" создана (ID: ${d.id})`);
      setNewTitle(''); setNewDesc('');
      fetchTopics();
    } catch {
      showStatus('Ошибка создания темы', false);
    }
  };

  // PUT /topics/:id
  const updateTopic = async () => {
    if (!editId || !editTitle.trim()) return showStatus('Заполните ID и название', false);
    try {
      const r = await fetch(`${API}/topics/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editTitle }),
      });
      if (!r.ok) throw new Error();
      showStatus(`Тема #${editId} обновлена`);
      setEditId(''); setEditTitle('');
      fetchTopics();
    } catch {
      showStatus(`Тема #${editId} не найдена`, false);
    }
  };

  // DELETE /topics/:id
  const deleteTopic = async (id) => {
    try {
      const r = await fetch(`${API}/topics/${id}`, { method: 'DELETE' });
      if (!r.ok) throw new Error();
      showStatus(`Тема #${id} удалена`);
      fetchTopics();
    } catch {
      showStatus(`Ошибка удаления темы #${id}`, false);
    }
  };

  useEffect(() => { checkHealth(); fetchTopics(); }, []);

  return (
    <div style={styles.container}>
      <h1 style={styles.h1}> Система тестирования биологов</h1>


      {/* GET Topics */}
      <h2 style={styles.h2}> Темы (GET /topics)</h2>
      <button style={{ ...styles.btn, ...styles.btnBlue }} onClick={fetchTopics}>Обновить список</button>
      <div style={{ marginTop: 12 }}>
        {topics.length === 0
          ? <p style={{ color: '#757575' }}>Нет тем</p>
          : topics.map(t => (
              <div key={t.id} style={styles.card}>
                <span style={styles.tag}>#{t.id}</span>
                <b>{t.title}</b>
                {t.description && <span style={{ color: '#555', marginLeft: 8 }}>— {t.description}</span>}
                <button
                  style={{ ...styles.btn, ...styles.btnRed, float: 'right', padding: '4px 10px' }}
                  onClick={() => deleteTopic(t.id)}
                >✕</button>
              </div>
            ))
        }
      </div>

      {/* POST Topic */}
      <h2 style={styles.h2}> Создать тему (POST /topics)</h2>
      <div style={styles.card}>
        <input style={styles.input} placeholder="Название*" value={newTitle} onChange={e => setNewTitle(e.target.value)} />
        <input style={styles.input} placeholder="Описание" value={newDesc} onChange={e => setNewDesc(e.target.value)} />
        <button style={{ ...styles.btn, ...styles.btnGreen }} onClick={createTopic}>Создать</button>
      </div>

      {/* PUT Topic */}
      <h2 style={styles.h2}> Обновить тему (PUT /topics/:id)</h2>
      <div style={styles.card}>
        <input style={{ ...styles.input, width: 60 }} placeholder="ID" value={editId} onChange={e => setEditId(e.target.value)} />
        <input style={styles.input} placeholder="Новое название" value={editTitle} onChange={e => setEditTitle(e.target.value)} />
        <button style={{ ...styles.btn, ...styles.btnGreen }} onClick={updateTopic}>Обновить</button>
      </div>

      <p style={{ color: '#9e9e9e', fontSize: 12, marginTop: 32 }}>
        Swagger API: <a href={`${API}/docs`} target="_blank" rel="noreferrer">{API}/docs</a>
      </p>
    </div>
  );
}
