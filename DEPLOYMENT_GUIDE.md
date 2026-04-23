# AriTyper Deployment Guide

## Overview
- **Frontend Website**: Host on Vercel (static files)
- **Admin Panel**: Host on Render (Flask web app)
- **Contact**: men777381@gmail.com | +256 760 730 254

## 1. Frontend Deployment (Vercel)

### Setup
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy website
cd website
vercel --prod
```

### Configuration
- Domain: Configure custom domain in Vercel dashboard
- Build: Static site (no build process)
- Environment: Not needed for static site

### Files Deployed
- `index.html` - Main website
- `style.css` - Embedded in HTML
- `script.js` - Embedded in HTML
- `vercel.json` - Vercel configuration

## 2. Admin Panel Deployment (Render)

### Setup
```bash
# Install Render CLI (optional)
npm install -g render-cli

# Deploy admin panel
cd admin_webapp
git init
git add .
git commit -m "Initial admin panel"
git remote add origin https://github.com/yourusername/arityper-admin.git
git push -u origin main

# Or use Render dashboard:
# 1. Go to render.com
# 2. Connect GitHub repository
# 3. Select admin_webapp folder
# 4. Configure service
```

### Service Configuration
- **Type**: Web Service
- **Runtime**: Python 3.9+
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Port**: 10000 (Render provides $PORT)
- **Health Check**: `/api/stats`

### Environment Variables
```
FLASK_ENV=production
PORT=10000
```

### Database
- SQLite database (`arityper_admin.db`) auto-created
- Persistent storage configured in `render.yaml`
- Backups: Configure in Render dashboard

## 3. Application Configuration

### Update Contact Information
Already updated in `website/index.html`:
- Email: men777381@gmail.com
- Phone/WhatsApp: +256 760 730 254

### Payment Configuration
Update in `payment_window.py`:
```python
PAYMENT_INFO = {
    "airtel_number": "+256760730254",  # Your Airtel number
    "mtn_number": "+256760730254",      # Your MTN number
    "amount": "10000",                  # UGX
    "currency": "UGX",
    "business_name": "AriTyper Uganda",
    "payment_reason": "AriTyper License Purchase"
}
```

## 4. Domain Configuration

### Frontend (Vercel)
1. Go to Vercel dashboard
2. Select project
3. Go to Domains
4. Add custom domain (e.g., arityper.ug)
5. Update DNS records as instructed

### Admin Panel (Render)
1. Go to Render dashboard
2. Select service
3. Go to Custom Domains
4. Add domain (e.g., admin.arityper.ug)
5. Update DNS records

## 5. Security Considerations

### Admin Panel
- Change default admin password
- Use HTTPS (automatic on Render)
- Monitor access logs
- Regular backups

### Frontend
- HTTPS enabled on Vercel
- No sensitive data exposed
- Contact forms handled securely

## 6. Monitoring & Maintenance

### Admin Panel
- Monitor device registrations
- Approve payments promptly
- Check system stats regularly
- Review activity logs

### Website
- Monitor download stats
- Update content as needed
- Check contact form submissions
- SEO optimization

## 7. File Structure After Cleanup

```
arityper/
├── website/                 # Frontend (Vercel)
│   ├── index.html
│   ├── vercel.json
│   └── assets/
├── admin_webapp/            # Admin panel (Render)
│   ├── app.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── templates/
├── payment_window.py        # Payment handling
├── license_manager.py       # License system
├── modern_ui.py           # UI components
├── device_client.py       # Device communication
├── server_api.py         # Server API
└── DEPLOYMENT_GUIDE.md   # This file
```

## 8. Testing

### Before Going Live
1. Test admin panel login
2. Test device registration
3. Test payment approval flow
4. Test website functionality
5. Test mobile responsiveness

### Post-Deployment
1. Test all URLs
2. Test admin functionality
3. Test download process
4. Test contact forms
5. Monitor for any issues

## 9. Troubleshooting

### Common Issues
- **Admin panel not loading**: Check Render logs
- **Database errors**: Check file permissions
- **Payment issues**: Verify configuration
- **Website not updating**: Clear Vercel cache

### Support Contacts
- Email: men777381@gmail.com
- Phone/WhatsApp: +256 760 730 254
- Business Hours: Mon-Fri 9am-6pm, Sat 10am-4pm

## 10. Next Steps

1. Deploy frontend to Vercel
2. Deploy admin panel to Render
3. Configure custom domains
4. Test complete flow
5. Monitor and maintain
6. Update payment numbers with actual mobile money accounts
7. Set up automated backups
8. Configure monitoring alerts
