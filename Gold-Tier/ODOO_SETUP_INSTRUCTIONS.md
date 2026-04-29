# Odoo Web Setup Instructions
**Quick Reference Guide**

---

## 🌐 Step 1: Open Odoo

**URL:** http://localhost:8069

Open this in your browser now.

---

## 📝 Step 2: Fill Database Creation Form

You should see a form titled "Create a new database"

### Fill in these exact values:

| Field | Value |
|-------|-------|
| **Master Password** | `master_password_2026` |
| **Database Name** | `ai_employee_db` |
| **Email** | `pinkyshergill1986@gmail.com` (or your email) |
| **Password** | `admin_password_2026` |
| **Phone Number** | (optional - leave blank or fill) |
| **Language** | English |
| **Country** | Pakistan (or your country) |
| **Demo Data** | ❌ **UNCHECK THIS BOX** |

### Important:
- Master password is for database management
- Admin password is for logging in
- Demo data should be UNCHECKED (we want clean data)

---

## ⏳ Step 3: Create Database

1. Click the **"Create Database"** button
2. Wait 1-2 minutes (be patient, it's setting up)
3. You'll be automatically logged in when done

---

## 📦 Step 4: Install Apps

After login, you'll see the Odoo dashboard.

### Install Accounting App:
1. Click **"Apps"** in the top menu
2. Search for **"Accounting"**
3. Click **"Install"** on "Invoicing & Accounting"
4. Wait 2-3 minutes for installation

### Install Contacts App:
1. Still in Apps menu
2. Search for **"Contacts"**
3. Click **"Install"** on "Contacts" (CRM)
4. Wait 1-2 minutes

---

## ✅ Step 5: Verify Installation

### Check Menu Bar:
You should now see these in the top menu:
- Accounting
- Contacts
- (and other default apps)

### Create Test Partner:
1. Click **"Contacts"** in top menu
2. Click **"Create"** button
3. Fill in:
   - Name: `Test Client Inc`
   - Email: `test@client.com`
   - Phone: `+92-300-1234567`
4. Click **"Save"**

### Create Test Invoice:
1. Click **"Accounting"** in top menu
2. Click **"Customers"** → **"Invoices"**
3. Click **"Create"** button
4. Fill in:
   - Customer: Select "Test Client Inc"
   - Invoice Lines: Click "Add a line"
     - Product: Type "Service"
     - Quantity: 1
     - Unit Price: 100
5. Click **"Save"**

---

## 🎉 Step 6: Confirm Completion

Once you've completed all steps above, come back here and type:

```
Odoo setup complete
```

I will then automatically run all tests and verify the integration!

---

## 🔧 Troubleshooting

### "Cannot connect to database"
- Wait 30 more seconds and refresh
- Check containers: `docker compose ps` in odoo-docker folder

### "Master password incorrect"
- Use: `master_password_2026` (from .env file)

### "Database already exists"
- Good! Just log in with:
  - Email: admin
  - Password: `admin_password_2026`

### Apps not installing
- Wait longer (can take 3-5 minutes)
- Check browser console for errors
- Refresh page and try again

### Can't find Accounting app
- Make sure you're in "Apps" menu
- Remove any search filters
- Look for "Invoicing & Accounting"

---

## 📸 What You Should See

### Database Creation Screen:
- Form with fields for master password, database name, etc.
- "Create Database" button at bottom

### After Login:
- Odoo dashboard with app icons
- Top menu bar with "Apps", "Discuss", etc.

### After Installing Apps:
- "Accounting" and "Contacts" in top menu
- Can create partners and invoices

---

## ⏱️ Expected Time

- Database creation: 1-2 minutes
- Accounting app install: 2-3 minutes
- Contacts app install: 1-2 minutes
- Creating test records: 2-3 minutes

**Total: ~10 minutes**

---

## 🆘 Need Help?

If stuck, provide:
1. What step you're on
2. What you see on screen
3. Any error messages

I'll help troubleshoot!

---

**Ready?** Open http://localhost:8069 and start! 🚀
