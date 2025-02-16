const express = require('express');
const path = require('path');
const app = express();
const homeRoutes = require('./routes/homeRoutes');

// Set EJS as templating engine
app.set('view engine', 'ejs');

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Use routes
app.use('/', homeRoutes);

const PORT = 3300;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
}); 