const express = require('express');
const path = require('path');
const app = express();
const homeRoutes = require('./routes/homeRoutes');

// Add these middleware lines before your routes
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Set EJS as templating engine
app.set('view engine', 'ejs');

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Use routes
app.use('/', homeRoutes);

const PORT = process.env.PORT || 3300;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
}); 