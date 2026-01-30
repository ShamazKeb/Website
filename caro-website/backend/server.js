const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Basic endpoint examples
app.get('/api/info', (req, res) => {
  res.json({ message: "Caro Website API" });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
