const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

// Default Open Graph / Twitter card metadata
router.use((req, res, next) => {
    const baseTitle = 'VagusHub - Vagus Nerve Stimulation Resources';
    const baseDesc = 'Covering Ultrasound Vagus Nerve Stimulation guidance, electrical VNS, breathing, nutrition, and research.';
    const imagePath = '/images/vagushub-opengraph.jpg';
    const absoluteUrl = `${req.protocol}://${req.get('host')}${req.originalUrl}`;
    const absoluteImage = `${req.protocol}://${req.get('host')}${imagePath}`;

    res.locals.ogTitle = baseTitle;
    res.locals.ogDescription = baseDesc;
    res.locals.ogUrl = absoluteUrl;
    res.locals.ogImage = absoluteImage;
    next();
});

router.get('/', (req, res) => {
    res.render('home', { title: 'VagusHub.com - Learn About Vagus Nerve Stimulation' });
});

router.get('/about', (req, res) => {
    res.render('about', { title: 'About Us - VagusHub.com' });
});

router.get('/blog', (req, res) => {
    res.render('blog', { title: 'Blog - VagusHub.com' });
});

router.get('/contact', async (req, res) => {
    // Attempt to fetch current Ultra Skool price from public about page
    let ultraPrice = 'Monthly Subscription';
    try {
        const ultraUrl = 'https://www.skool.com/ultra/about';
        const r = await fetch(ultraUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
        });
        if (r.ok) {
            const html = await r.text();
            // Try multiple patterns
            const patterns = [
                /\$\s*\d+(?:\.\d{1,2})?\s*\/?\s*month/i,
                /\$\s*\d+\s*per\s*month/i,
                /\$\s*\d+\s*\/month/i
            ];
            for (const rx of patterns) {
                const m = html.match(rx);
                if (m && m[0]) { ultraPrice = m[0].replace(/\s{2,}/g, ' ').trim(); break; }
            }
        }
    } catch (e) {
        // keep fallback value
    }

    res.render('contact', { 
        title: 'Contact Us - VagusHub.com',
        ultraPrice
    });
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
    res.redirect(301, '/benefits');
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
        title: 'The Nemertean Vagus Nerve Origin Theory - VagusHub.com' 
    });
});

router.get('/planner', (req, res) => {
    res.render('blog/planner', { 
        title: 'Daily Vagus Nerve Planner - VagusHub.com' 
    });
});

router.get('/ultrasound', (req, res) => {
    res.render('blog/ultrasound', { 
        title: 'Benefits of Vagus Nerve Ultrasound Stimulation - VagusHub.com' 
    });
});

router.get('/citations', (req, res) => {
    res.render('blog/citations', { 
        title: 'Citations & Research Papers Covering Vagus Nerve Stimulation Protocols, Technology, Etc. - VagusHub.com' 
    });
});

router.get('/top-products', (req, res) => {
    res.render('blog/top-products', { 
        title: 'Top Resources for Vagus Nerve Health - VagusHub.com' 
    });
});

router.get('/media', (req, res) => {
    res.render('blog/media', { 
        title: 'Sterling Cooley Media Appearances - VagusHub.com' 
    });
});

router.get('/testimonials', (req, res) => {
    res.render('blog/testimonials', { 
        title: 'Vagus Nerve Program Testimonials - VagusHub.com' 
    });
});

router.get('/benefits', (req, res) => {
    res.render('blog/benefits', { 
        title: 'Benefits of Vagus Nerve Stimulation - VagusHub.com' 
    });
});

router.get('/stay-in-touch', (req, res) => {
    res.render('blog/stay-in-touch', { 
        title: 'Stay Connected with VagusHub - VagusHub.com' 
    });
});

// Handle contact form submissions
router.post('/contact', (req, res) => {
    // TODO: Add contact form handling logic
    res.redirect('/contact?message=success');
});

router.post('/api/skool-webhook', async (req, res) => {
    try {
        const { email } = req.body;
        if (!email) {
            return res.status(400).json({ error: 'Email is required' });
        }

        console.log('Attempting to send email:', email);
        const webhookUrl = 'https://api.skool.com/groups/vagus/webhooks/cfe03756891a47f684cae361ce0fab1c';
        const response = await fetch(`${webhookUrl}?email=${encodeURIComponent(email)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        // Log the response details
        console.log('Webhook Response Status:', response.status);
        const responseText = await response.text();
        console.log('Webhook Response Body:', responseText);

        if (!response.ok) {
            throw new Error(`Webhook failed with status ${response.status}: ${responseText}`);
        }

        res.json({ success: true });
    } catch (error) {
        console.error('Detailed webhook error:', {
            message: error.message,
            stack: error.stack,
            email: req.body.email
        });
        res.status(500).json({ 
            error: 'Failed to process webhook',
            details: error.message
        });
    }
});

// Private style prototype routes (not linked in nav)
router.get('/_style1', (req, res) => {
    res.render('style1', {
        title: 'Style Prototype 1 - VagusHub.com'
    });
});

router.get('/_style2', (req, res) => {
    res.render('style2', {
        title: 'Style Prototype 2 - VagusHub.com'
    });
});

router.get('/_style3', (req, res) => {
    res.render('style3', {
        title: 'Style Prototype 3 - VagusHub.com'
    });
});

router.get('/_style4', (req, res) => {
    res.render('style4', {
        title: 'Style Prototype 4 - VagusHub.com'
    });
});

module.exports = router; 