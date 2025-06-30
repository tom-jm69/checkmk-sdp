# 🛠️ Service Desk Plus Setup Guide

## 🔐 API User Configuration

You have **two options** for setting up an API user:

---

### 👤 Use Existing User

1. 🔝 Click on the **avatar icon** (top right corner)
2. 🎛️ Go to **`Personalize`**
3. 🔑 Click **`Generate Authtoken`**

---

### 🆕 Create New User

1. ⚙️ Click on the **settings icon** (top right – second icon from the right)
2. 👥 Navigate to **`Users & Permission`**

   - 👤 Click **`Users`**
     - ➕ Click **`New`**
       - ✍️ Fill out:
         - **Display name**
         - **Login name**
         - 🔐 Set a **safe password**
       - 🔓 Under **`Authtoken details`**
         - ☑️ Enable **`Allow to generate their own authtoken`**

3. 🔁 Now **log in** with the newly created user and repeat the steps from **"Use Existing User"** above to generate their authtoken.

---

✅ Once created, fill out the following in your `conf.py` file:

```python
SDP_REQUESTER_NAME = "your_requester_login_name"
SDP_SECRET = "your_generated_authtoken"
SDP_REQUESTER_ID = "userId_from_edit_url"
```

🆔 To find the **`SDP_REQUESTER_ID`**, open the user's edit page and look at the URL. It will look like this:

```
https://localhost:8443/SetUpWizard.do?forwardTo=requester&isUser=true&viewType=details&userId=607
```

👉 In this example, the `SDP_REQUESTER_ID` would be: `607`

---

## 🧩 Fields Configuration

Before creating your templates, you must first define custom fields:

---

### 🔧 Create Additional Fields

1. ⚙️ Click on the **settings icon** (top right – second icon from the right)
2. 🧱 Navigate to **`Customization`**

   - 👤 Click **`Additional Field`**
     - ➕ Click **`New Field`**

3. 📝 For each field below, provide the **Field Name** and set the correct **Format**:

---

#### 🟢 Service Fields

- 📌 **Service state** → **Pick List** (Set the corresponding state IDs in the conf file)
- 🧩 **Service name** → **Single Line**
- 📝 **Service description** → **Single Line**
- ⏲️ **Service state last changed** → **Date/Time**
- 📄 **Service plugin output long** → **Multi Line**
- 🧾 **Service plugin output** → **Multi Line**
- 🧪 **Service check command** → **Single Line**
- 🌐 **Service URL** → **Single Line**

---

#### 🔵 Host Fields

- 🌐 **Host URL** → **Single Line**
- 📶 **Host state** → **Pick List** (Set the corresponding state IDs in the conf file)
- 🧭 **Host address 4** → **Single Line**
- 🖥️ **Host name** → **Single Line**
- 🏷️ **Host alias** → **Single Line**
- 📋 **Host output** → **Multi Line**
- 🕰️ **Host last state UP** → **Date/Time**
- 🧪 **Host check command** → **Single Line**

---

#### 📣 Notification Fields

- 👥 **Contacts** → **Single Line**
- ⏰ **Alarm time** → **Date/Time**

---

📝 **Note:** You can customize field names, but ensure the formats match the intended data.

---

## 🧾 Templates

Once your fields are created, use them to build your request templates:

---

### 🧰 Create New Incident Templates

1. ⚙️ Click on the **settings icon** (top right – second icon from the right)
2. 🧱 Navigate to **`Templates & Forms`**
   - 👤 Click **`Incident Template`**
     - ➕ Click **`New Template`**
       - ✍️ Fill out:
         - **Name** (e.g. `Checkmk Service Template` or `Checkmk Host Template`)

---

### 🧩 Add Fields to the Template

3. 🎛️ Go to **`Available Fields`** (left middle panel)

   - ➕ Click **`Add New Field`**
     - ➕ Choose a layout format, such as **`Double Column`**
     - 🧲 Drag and drop it into the main template area

4. 🧲 Now drag in the previously created fields into the new section

---

💡 **Important Notes:**

- 📄 **Create two separate templates:**

  - One for **services** (e.g. "Checkmk Service Template")
  - One for **hosts** (e.g. "Checkmk Host Template")

- 🎨 **Field orientation and section layout are flexible.**  
  Customize the layout however you prefer—single, double columns, grouped sections, etc.

---

### 🔗 Final Configuration

After creating both templates:

1. Locate each template's ID in the browser URL, which looks like:

```
https://localhost:8443/app#/admin/incident-templates/301
```

In this example, the template ID is `301`.

2. Open your `conf.py` file and set the following variables:

```python
SDP_SERVICE_TEMPLATE_ID = 301  # Replace with your actual service template ID
SDP_HOST_TEMPLATE_ID = 602     # Replace with your actual host template ID
```

3. Then, map each custom field’s `API Field Name` from the field settings into the config like this:

```python
SERVICE_NAME_API_FIELD = "udf_sline_906"
SERVICE_STATUS_API_FIELD = "udf_pick_1503"
SERVICE_OUTPUT_API_FIELD = "udf_mline_1501"
SERVICE_OUTPUT_LONG_API_FIELD = "udf_mline_1502"
SERVICE_DESCRIPTION_API_FIELD = "udf_sline_901"
SERVICE_LAST_STATE_CHANGE_API_FIELD = "udf_date_1201"
SERVICE_CHECK_COMMAND_API_FIELD = "udf_sline_610"
SERVICE_URL_API_FIELD = "udf_sline_907"
HOST_NAME_API_FIELD = "udf_sline_605"
HOST_ALIAS_API_FIELD = "udf_sline_606"
HOST_IPV4_API_FIELD = "udf_sline_902"
HOST_STATE_API_FIELD = "udf_pick_1509"
HOST_URL_API_FIELD = "udf_sline_612"
CONTACTS_API_FIELD = "udf_sline_1505"
ALARM_DATE_API_FIELD = "udf_date_613"
HOST_CHECK_COMMAND_API_FIELD = "udf_sline_1506"
HOST_LAST_STATE_CHANGE_API_FIELD = "udf_date_1507"
HOST_LAST_STATE_UP_API_FIELD = "udf_date_1508"
HOST_OUTPUT_API_FIELD = "udf_sline_904"
```

✅ These field IDs ensure the automation logic maps correctly to each field inside your configured templates.
