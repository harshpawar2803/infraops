# InfraOps

## Enterprise Linux Infrastructure Monitoring & Security Analytics Platform

InfraOps is a web-based Linux infrastructure monitoring solution developed using Python Flask. It provides real-time server monitoring, security event tracking, log analysis, service monitoring, and reporting through a centralized dashboard.

---

## Features

### Infrastructure Monitoring
- Real-time CPU Usage Monitoring
- Real-time Memory Usage Monitoring
- Real-time Disk Usage Monitoring
- Server Load Average Monitoring
- Hostname, IP Address and Uptime Display

### Security Monitoring
- SSH Login Tracking
- Failed Login Detection
- Authentication Log Monitoring
- Security Alert Notifications

### Log Analytics
- System Log Viewer
- SSH Authentication Logs
- Failed Login Reports
- Search Functionality for Logs

### Service Monitoring
- SSHD Status
- Firewalld Status
- Crond Status

### Reporting
- Historical Monitoring Data
- CSV Report Export
- Resource Utilization Tracking

### Dashboard
- Dark Theme UI
- Auto Refresh
- Real-Time Charts using Chart.js

---

## Technology Stack

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Chart.js
- RHEL Linux
- Systemd
- Firewalld

---

## Project Structure

```text
infraops/
├── app.py
├── monitor.db
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── README.md
```

---

## Installation

### Install Dependencies

```bash
dnf install python3 python3-pip firewalld -y
pip3 install flask psutil
```

### Run Application

```bash
cd /opt/infraops
python3 app.py
```

Application URL:

```text
http://SERVER-IP:8080
```

---

## Systemd Service

```bash
systemctl enable --now infraops
systemctl status infraops
```

---

## Firewall Configuration

```bash
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --reload
```

---

## Key Learning Outcomes

- Linux System Administration
- Infrastructure Monitoring
- Security Analytics
- Log Management
- Python Automation
- Flask Web Development
- Systemd Service Management
- Linux Performance Monitoring

---

## Developer

Harsh Pawar

Master of Computer Applications (MCA)

---

## License

This project is developed for educational and learning purposes.
