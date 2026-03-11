# 🥒 HomeMade Pickles & Snacks – Taste the Best

**AWS Cloud-Based E-Commerce Platform | Academic Certification Project**

A full-stack e-commerce web application built with Flask and deployed on AWS EC2, demonstrating real-world cloud architecture using DynamoDB, CloudWatch, and scalable deployment patterns.

---

## 📐 System Architecture

```
                        ┌─────────────────────────────────┐
                        │          AWS Cloud               │
                        │                                 │
  User Browser  ────►  │  EC2 Instance (t2.micro)        │
                        │  ┌──────────┐  ┌────────────┐  │
                        │  │  Nginx   │  │  Gunicorn  │  │
                        │  │ (Port 80)│─►│ (Port 5000)│  │
                        │  └──────────┘  └─────┬──────┘  │
                        │                      │          │
                        │              ┌────────▼───────┐ │
                        │              │  Flask App     │ │
                        │              │  (Python 3.11) │ │
                        │              └────────┬───────┘ │
                        │                       │         │
                        │         ┌─────────────▼──────┐  │
                        │         │   AWS DynamoDB      │  │
                        │         │  ┌──────────────┐  │  │
                        │         │  │  Users        │  │  │
                        │         │  │  Products     │  │  │
                        │         │  │  Orders       │  │  │
                        │         │  │  Inventory    │  │  │
                        │         │  │  Subscriptions│  │  │
                        │         │  └──────────────┘  │  │
                        │         └────────────────────┘  │
                        │                                  │
                        │         ┌────────────────────┐   │
                        │         │  AWS CloudWatch     │   │
                        │         │  (Logs & Monitoring)│  │
                        │         └────────────────────┘   │
                        └──────────────────────────────────┘
```

### Cloud Scenarios Implemented

| Scenario | Implementation |
|---|---|
| Scalable Order Processing | Gunicorn multi-worker + DynamoDB conditional writes prevent conflicts |
| Real-Time Inventory Tracking | Atomic DynamoDB `UpdateItem` with `ConditionExpression` on every order |
| Personalized Experience | Recommendation engine reads order history + browsing history from DynamoDB |

---

## 📁 Project Structure

```
homemade_pickles/
│
├── app/
│   ├── __init__.py              # Flask app factory (Blueprint registration)
│   ├── routes/
│   │   ├── main_routes.py       # Home page
│   │   ├── auth_routes.py       # Register / Login / Logout
│   │   ├── product_routes.py    # Catalog, category filter, product detail
│   │   ├── cart_routes.py       # Session-based shopping cart
│   │   ├── order_routes.py      # Checkout, confirmation, history
│   │   ├── subscription_routes.py  # Subscription management
│   │   ├── admin_routes.py      # Admin monitoring dashboard
│   │   └── dashboard_routes.py  # User personal dashboard
│   │
│   ├── services/
│   │   ├── user_service.py      # User CRUD, browsing history tracking
│   │   ├── product_service.py   # Product catalog queries
│   │   ├── inventory_service.py # Real-time stock deduction (atomic)
│   │   ├── order_service.py     # Order creation and management
│   │   ├── subscription_service.py  # Subscription logic
│   │   └── recommendation_service.py # Personalized recommendations
│   │
│   ├── models/
│   │   ├── user_model.py        # User DynamoDB document schema
│   │   ├── order_model.py       # Order document schema
│   │   └── subscription_model.py # Subscription document schema
│   │
│   ├── utils/
│   │   ├── dynamodb_client.py   # boto3 DynamoDB connection
│   │   └── auth_helpers.py      # Password hashing, login decorators
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base layout with navbar/footer
│   │   ├── index.html           # Home page
│   │   ├── auth/                # Login, Register
│   │   ├── products/            # Catalog, Detail
│   │   ├── cart/                # Shopping cart
│   │   ├── orders/              # Confirmation, History
│   │   ├── subscriptions/       # List, New
│   │   ├── dashboard/           # User dashboard
│   │   └── admin/               # Admin monitoring panel
│   │
│   └── static/
│       ├── css/style.css        # Complete stylesheet
│       └── js/main.js           # Cart counter, auto-dismiss alerts
│
├── aws/
│   ├── dynamodb_setup.py        # Creates all 5 DynamoDB tables
│   └── seed_products.py         # Seeds 12 sample products + admin user
│
├── tests/
│   └── test_app.py              # 10 test cases (mocked DynamoDB)
│
├── run.py                       # Flask entry point
├── gunicorn_config.py           # Gunicorn production server config
├── nginx.conf                   # Nginx reverse proxy config
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## 🗄️ DynamoDB Table Design

### Users Table
| Attribute | Type | Notes |
|---|---|---|
| UserID (PK) | String | UUID |
| Name | String | Full name |
| Email | String | Unique email |
| Password | String | SHA-256 hashed |
| Address | String | Delivery address |
| Role | String | `customer` or `admin` |
| BrowsingHistory | List | ProductIDs viewed (max 20) |
| OrderHistory | List | OrderIDs placed |
| CreatedAt | String | ISO timestamp |

### Products Table
| Attribute | Type | Notes |
|---|---|---|
| ProductID (PK) | String | e.g. `prod-mango-001` |
| Name | String | Product name |
| Category | String | `Pickles` or `Snacks` |
| Price | String | In rupees |
| Stock | Number | Current quantity |
| Description | String | Product description |
| ImageURL | String | Product image URL |

### Orders Table
| Attribute | Type | Notes |
|---|---|---|
| OrderID (PK) | String | UUID |
| UserID | String | FK → Users |
| Products | List | [{ProductID, Name, Quantity, Price}] |
| TotalAmount | String | Total in rupees |
| OrderStatus | String | `Confirmed`, `Cancelled` |
| OrderDate | String | ISO timestamp |

### Inventory Table
| Attribute | Type | Notes |
|---|---|---|
| ProductID (PK) | String | FK → Products |
| Stock | Number | Current stock level |
| LastUpdated | String | ISO timestamp |

### Subscriptions Table
| Attribute | Type | Notes |
|---|---|---|
| SubscriptionID (PK) | String | UUID |
| UserID | String | FK → Users |
| ProductID | String | FK → Products |
| Frequency | String | `weekly` or `monthly` |
| NextDelivery | String | ISO timestamp |
| Status | String | `Active` or `Cancelled` |
| CreatedAt | String | ISO timestamp |

---

## ☁️ Deployment Guide – AWS EC2

### Step 1: Launch EC2 Instance

1. Log into AWS Console → EC2 → **Launch Instance**
2. Settings:
   - **AMI:** Amazon Linux 2023 (free tier)
   - **Instance Type:** t2.micro (free tier eligible)
   - **Key Pair:** Create new → download `.pem` file
   - **Security Group rules:**
     - SSH (port 22) – Your IP
     - HTTP (port 80) – Anywhere (0.0.0.0/0)
3. Launch instance and note the **Public IPv4 address**

### Step 2: Connect to EC2

```bash
# Make key file read-only (required)
chmod 400 your-key.pem

# SSH into the instance
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### Step 3: Install System Dependencies

```bash
# Update system packages
sudo yum update -y

# Install Python 3.11, pip, git, nginx
sudo yum install python3.11 python3.11-pip git nginx -y

# Verify installations
python3.11 --version
nginx -v
```

### Step 4: Clone / Upload Project

**Option A: If project is on GitHub:**
```bash
cd /home/ec2-user
git clone https://github.com/YOUR_USERNAME/homemade_pickles.git
cd homemade_pickles
```

**Option B: Upload from local machine:**
```bash
# Run this on your LOCAL machine
scp -i your-key.pem -r ./homemade_pickles ec2-user@YOUR_EC2_IP:/home/ec2-user/
```

### Step 5: Install Python Dependencies

```bash
cd /home/ec2-user/homemade_pickles

# Install all required packages
pip3.11 install -r requirements.txt
```

### Step 6: Configure Environment Variables

```bash
# Create .env from the template
cp .env.example .env

# Edit with your actual AWS credentials
nano .env
```

Fill in your values:
```
SECRET_KEY=your-random-secret-key-here
PASSWORD_SALT=your-unique-salt-here
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

> **Security note:** The EC2 instance role is the preferred method for production. For this academic project, `.env` variables are acceptable.

### Step 7: Set Up DynamoDB Tables

```bash
# Create all 5 DynamoDB tables
python3.11 aws/dynamodb_setup.py

# Seed sample products and admin user
python3.11 aws/seed_products.py
```

Expected output:
```
=== HomeMade Pickles & Snacks – DynamoDB Table Setup ===
  ✅ Table 'Users' is ACTIVE.
  ✅ Table 'Products' is ACTIVE.
  ✅ Table 'Orders' is ACTIVE.
  ✅ Table 'Inventory' is ACTIVE.
  ✅ Table 'Subscriptions' is ACTIVE.
=== All tables created successfully! ===
```

### Step 8: Configure Nginx

```bash
# Copy the nginx config
sudo cp nginx.conf /etc/nginx/conf.d/homemade_pickles.conf

# Edit server_name with your EC2 IP
sudo nano /etc/nginx/conf.d/homemade_pickles.conf
# Change: server_name _;
# To:     server_name YOUR_EC2_IP;

# Test config syntax
sudo nginx -t

# Start and enable nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 9: Run the Flask App with Gunicorn

```bash
cd /home/ec2-user/homemade_pickles

# Start the app (runs in background with nohup)
nohup gunicorn -c gunicorn_config.py run:app > /tmp/gunicorn.log 2>&1 &

# Check it's running
ps aux | grep gunicorn

# View logs
tail -f /tmp/gunicorn.log
```

### Step 10: Verify Deployment

Open a browser and visit:
```
http://YOUR_EC2_PUBLIC_IP
```

You should see the HomeMade Pickles & Snacks home page!

---

## 📊 CloudWatch Monitoring Setup

### Enable EC2 Detailed Monitoring
1. AWS Console → EC2 → Select your instance → **Actions → Monitor and troubleshoot → Enable detailed monitoring**

### View Application Logs in CloudWatch
```bash
# Install CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Create config file
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

Paste this config:
```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/tmp/gunicorn.log",
            "log_group_name": "homemade-pickles",
            "log_stream_name": "gunicorn-access"
          }
        ]
      }
    }
  }
}
```

```bash
# Start agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
```

### Set CloudWatch Alarms (Console)
1. AWS Console → CloudWatch → Alarms → Create Alarm
2. Recommended alarms:
   - **CPUUtilization > 80%** on EC2 instance
   - **StatusCheckFailed** on EC2 instance

---

## 🧪 Testing Instructions

### Run Unit Tests (no AWS required)

```bash
cd /home/ec2-user/homemade_pickles

# Install pytest
pip3.11 install pytest

# Run all tests
python -m pytest tests/ -v
```

Expected output:
```
tests/test_app.py::test_home_page_loads PASSED
tests/test_app.py::test_register_page_loads PASSED
tests/test_app.py::test_register_new_user PASSED
tests/test_app.py::test_register_duplicate_email PASSED
tests/test_app.py::test_login_page_loads PASSED
tests/test_app.py::test_login_success PASSED
tests/test_app.py::test_login_invalid_credentials PASSED
tests/test_app.py::test_product_catalog_loads PASSED
tests/test_app.py::test_product_detail_loads PASSED
tests/test_app.py::test_product_not_found PASSED
... (10 tests total)
```

### Manual Testing Checklist

#### 1. Product Browsing
- [ ] Visit `http://EC2_IP/` – Home page loads with products
- [ ] Visit `http://EC2_IP/products/` – Full catalog displays
- [ ] Click "Pickles" filter – shows only pickles
- [ ] Click any product → detail page with price and stock

#### 2. User Registration & Login
- [ ] Go to `/auth/register`, fill form, submit
- [ ] Check success message → redirected to login
- [ ] Login with credentials → redirected to home with welcome message
- [ ] Navbar shows "My Account" and "Cart"
- [ ] Go to `/auth/logout` → logged out

#### 3. Cart & Checkout
- [ ] Browse to a product → click "Add to Cart"
- [ ] Go to `/cart/` → item appears with correct price
- [ ] Cart total is calculated correctly
- [ ] Click "Place Order" → confirmation page appears
- [ ] Order ID shown on confirmation page

#### 4. Inventory Deduction
- [ ] Note product stock BEFORE order (e.g., 50)
- [ ] Place order for 2 units
- [ ] Go back to product page → stock shows 48
- [ ] Go to Admin Dashboard → inventory table updated

#### 5. Subscription Creation
- [ ] Go to `/subscriptions/new`
- [ ] Select a product and "Monthly" frequency
- [ ] Submit → subscription appears in list
- [ ] Dashboard shows active subscription

#### 6. Recommendation Display
- [ ] Place 2-3 orders for different products
- [ ] Visit home page → "Recommended for You" section appears
- [ ] Recommendations are related to ordered categories

#### 7. Admin Dashboard
- [ ] Login as: `admin@homemadepickles.com` / `admin123`
- [ ] Visit `/admin/dashboard`
- [ ] Stats cards show total orders, revenue, product count
- [ ] Low stock alerts show for products with ≤10 stock
- [ ] Inventory table shows all products with status badges
- [ ] Recent orders table shows latest orders

---

## 🌱 Sample Test Data

After running `seed_products.py`, these accounts are available:

### Admin Account
| Field | Value |
|---|---|
| Email | admin@homemadepickles.com |
| Password | admin123 |
| Role | admin |

### Sample Products Loaded

| Product | Category | Price | Stock |
|---|---|---|---|
| Traditional Mango Pickle | Pickles | ₹149 | 50 |
| Spicy Lemon Pickle | Pickles | ₹129 | 35 |
| Garlic Pickle | Pickles | ₹179 | 28 |
| Gongura Chutney Pickle | Pickles | ₹159 | 40 |
| Mixed Vegetable Pickle | Pickles | ₹139 | 60 |
| Tomato Pickle | Pickles | ₹119 | 8 ⚠️ |
| Crispy Rice Murukku | Snacks | ₹99 | 75 |
| Spicy Poha Chivda | Snacks | ₹89 | 90 |
| Wheat Chakli | Snacks | ₹109 | 55 |
| Karnataka Kodubale | Snacks | ₹119 | 45 |
| Masala Boondi | Snacks | ₹79 | 100 |
| Rajasthani Namkeen Mix | Snacks | ₹129 | 0 ❌ |

---

## 🔧 Troubleshooting

### Gunicorn not starting
```bash
# Check logs
tail -50 /tmp/gunicorn.log

# Test Flask directly
python3.11 run.py
```

### DynamoDB connection error
```bash
# Verify AWS credentials in .env
cat .env

# Test DynamoDB connection
python3.11 -c "from app.utils.dynamodb_client import get_table; t = get_table('Products'); print('✅ Connected')"
```

### Nginx 502 Bad Gateway
```bash
# Check if gunicorn is running
ps aux | grep gunicorn

# Restart gunicorn
pkill gunicorn
nohup gunicorn -c gunicorn_config.py run:app > /tmp/gunicorn.log 2>&1 &
```

---

## 📦 Technology Stack Summary

| Component | Technology | AWS Service |
|---|---|---|
| Backend | Python Flask + Gunicorn | EC2 |
| Frontend | HTML/CSS/JS (Jinja2) | EC2 |
| Database | boto3 DynamoDB SDK | DynamoDB |
| Web Server | Nginx (reverse proxy) | EC2 |
| Monitoring | CloudWatch Agent | CloudWatch |
| Deployment | EC2 + systemd | EC2 |

---

*Project developed for AWS Cloud Architecture academic certification submission.*
*All products and pricing are fictional for demonstration purposes.*
