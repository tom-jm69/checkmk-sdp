# 🛠️ Checkmk Setup Guide

## 🔐 API User Configuration

---

### 🆕 Create New User

1. 🌐 Open the **Checkmk Web UI**
2. ⚙️ Click on the **settings icon** (middle left)
3. 👥 Navigate to **`Users`**

   - 👤 Click **`Users`**
     - ➕ Click **`Add user`**
       - ✍️ Fill out the following:
         - **Username**
         - **Full name**
         - ☑️ Tick **`Automation secret for machine accounts`**
         - 🔐 Either set a **custom strong password** or let Checkmk generate one
         - 👤 **Roles** – A normal monitoring user should be sufficient, but this depends on your specific role/permission setup

---

✅ Once created, fill out the following in your `conf.py` file:

```python
CHECKMK_USERNAME = "your_automation_username"
CHECKMK_SECRET = "your_automation_secret"
```
