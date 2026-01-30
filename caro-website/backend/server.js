const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const db = require('./database');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';

// Middleware to verify JWT
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.sendStatus(401);

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

// --- AUTH ---

app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;

  db.get("SELECT * FROM users WHERE username = ?", [username], async (err, user) => {
    if (err) return res.status(500).send("Database error");
    if (!user) return res.status(401).send("Invalid credentials");

    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) return res.status(401).send("Invalid credentials");

    const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '24h' });
    res.json({ token });
  });
});

// --- REVIEWS (PUBLIC) ---

app.get('/api/reviews', (req, res) => {
  // Only return approved reviews for public
  db.all("SELECT * FROM reviews WHERE approved = 1 ORDER BY date DESC", [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.post('/api/reviews', (req, res) => {
  const { name, content, rating } = req.body;
  // New reviews are not approved by default
  db.run("INSERT INTO reviews (name, content, rating, approved) VALUES (?, ?, ?, 0)",
    [name, content, rating],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id: this.lastID, message: "Review submitted for approval" });
    }
  );
});

// --- ADMIN (PROTECTED) ---

app.get('/api/admin/reviews', authenticateToken, (req, res) => {
  db.all("SELECT * FROM reviews ORDER BY date DESC", [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.delete('/api/admin/reviews/:id', authenticateToken, (req, res) => {
  db.run("DELETE FROM reviews WHERE id = ?", [req.params.id], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: "Deleted" });
  });
});

app.put('/api/admin/reviews/:id/approve', authenticateToken, (req, res) => {
  db.run("UPDATE reviews SET approved = 1 WHERE id = ?", [req.params.id], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: "Approved" });
  });
});

app.put('/api/admin/reviews/:id/approve', authenticateToken, (req, res) => {
  db.run("UPDATE reviews SET approved = 1 WHERE id = ?", [req.params.id], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: "Approved" });
  });
});

// --- CMS (CONTENT) ---

app.get('/api/content', (req, res) => {
  db.all("SELECT key, value FROM content", [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    // Convert array to object for easier frontend consumption
    const content = {};
    rows.forEach(row => content[row.key] = row.value);
    res.json(content);
  });
});

app.put('/api/admin/content/:key', authenticateToken, (req, res) => {
  const { value } = req.body;
  const key = req.params.key;

  // UPSERT logic: Insert or Update
  db.run(`INSERT INTO content (key, value, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, last_updated=excluded.last_updated`,
    [key, value],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ message: "Content updated" });
    }
  );
});

// Backup endpoint (for dev use to generate seed file)
app.get('/api/admin/backup/content', authenticateToken, (req, res) => {
  db.all("SELECT key, value FROM content", [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    // Return as array format matching seed.json
    res.json(rows.map(r => ({ key: r.key, value: r.value })));
  });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
