const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcrypt');
const fs = require('fs');

// Ensure data directory exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

const dbPath = process.env.DATABASE_PATH || path.join(dataDir, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    // Users table
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )`);

    // Reviews table
    db.run(`CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        content TEXT,
        rating INTEGER,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        approved INTEGER DEFAULT 0
    )`);

    // Initialize Admin User if not exists
    const adminUser = process.env.ADMIN_USERNAME || 'admin';
    const adminPass = process.env.ADMIN_PASSWORD || 'admin'; // Default fallback, should be set in env

    db.get("SELECT * FROM users WHERE username = ?", [adminUser], (err, row) => {
        if (!row) {
            const salt = bcrypt.genSaltSync(10);
            const hash = bcrypt.hashSync(adminPass, salt);
            db.run("INSERT INTO users (username, password_hash) VALUES (?, ?)", [adminUser, hash]);
            console.log(`Admin user '${adminUser}' initialized.`);
        }
    });

    // Content table
    db.run(`CREATE TABLE IF NOT EXISTS content (
        key TEXT PRIMARY KEY,
        value TEXT,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    // Seed Content if empty
    db.get("SELECT count(*) as count FROM content", [], (err, row) => {
        if (err) return console.error(err.message);
        if (row.count === 0) {
            console.log("Seeding content database...");
            const seedData = require('./data/content_seed.json');
            const stmt = db.prepare("INSERT INTO content (key, value) VALUES (?, ?)");
            seedData.forEach(item => {
                stmt.run(item.key, item.value);
            });
            stmt.finalize();
            console.log("Content seeded.");
        }
    });
});

module.exports = db;
