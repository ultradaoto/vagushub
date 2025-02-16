const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    res.render('home', { title: 'VagusHub.com - Learn About Vagus Nerve Stimulation' });
});

router.get('/about', (req, res) => {
    res.render('about', { title: 'About Us - VagusHub.com' });
});

router.get('/blog', (req, res) => {
    res.render('blog', { title: 'Blog - VagusHub.com' });
});

router.get('/contact', (req, res) => {
    res.render('contact', { title: 'Contact Us - VagusHub.com' });
});

router.get('/case-study', (req, res) => {
    res.render('case-study', { title: 'Free Case Study - VagusHub.com' });
});

router.get('/symptoms', (req, res) => {
    res.render('blog/symptoms', { 
        title: 'Common Symptoms of Vagus Nerve Dysfunction - VagusHub.com' 
    });
});

router.get('/getting-started', (req, res) => {
    res.render('blog/getting-started', { 
        title: 'Getting Started with Vagus Nerve Stimulation - VagusHub.com' 
    });
});

router.get('/vns-benefits', (req, res) => {
    res.render('blog/vns-benefits', { 
        title: 'Benefits of Vagus Nerve Stimulation - VagusHub.com' 
    });
});

// Add these new routes
router.get('/sleep', (req, res) => {
    res.render('blog/sleep', { 
        title: 'Sleep Better with Vagus Nerve Techniques - VagusHub.com' 
    });
});

router.get('/priming', (req, res) => {
    res.render('blog/priming', { 
        title: 'Vagus Nerve Morning Priming - VagusHub.com' 
    });
});

router.get('/theory', (req, res) => {
    res.render('blog/theory', { 
        title: 'Understanding Polyvagal Theory - VagusHub.com' 
    });
});

router.get('/planner', (req, res) => {
    res.render('blog/planner', { 
        title: 'Daily Vagus Nerve Planner - VagusHub.com' 
    });
});

// Handle contact form submissions
router.post('/contact', (req, res) => {
    // TODO: Add contact form handling logic
    res.redirect('/contact?message=success');
});

module.exports = router; 