# Amazon Linux Deployment Notes

## Amazon Linux Specific Considerations

### User Account
- **Default user**: `ec2-user` (not `ubuntu`)
- All scripts default to `ec2-user` for Amazon Linux

### Package Manager
- **Amazon Linux 2**: Uses `yum`
- **Amazon Linux 2023**: Uses `dnf` (yum is alias)
- **Nginx**: Use `amazon-linux-extras install nginx1` for Amazon Linux 2

### Python Installation
Amazon Linux 2 comes with Python 3.7 by default. The setup script will:
1. Install build dependencies
2. Compile Python 3.12 from source (if not available via package manager)
3. Create symlinks for `python3.12` and `pip3.12`

**Note**: Python 3.12 compilation may take 10-15 minutes on smaller instances.

### Node.js Installation
- Uses NodeSource RPM repository
- Installs Node.js 20.x LTS
- Automatically configured for Amazon Linux

### Firewall Configuration
Amazon Linux uses `firewalld` (not `ufw`):
- SSH: `sudo firewall-cmd --permanent --add-service=ssh`
- HTTP: `sudo firewall-cmd --permanent --add-service=http`
- HTTPS: `sudo firewall-cmd --permanent --add-service=https`
- Reload: `sudo firewall-cmd --reload`

**Note**: AWS Security Groups are the primary firewall. Ensure ports 22, 80, and 443 are open.

### Systemd Services
Systemd works the same on Amazon Linux as on Ubuntu:
- Service files: `/etc/systemd/system/`
- Commands: `systemctl start|stop|restart|status`
- Logs: `journalctl -u service-name`

### Nginx Configuration
- Configuration file: `/etc/nginx/nginx.conf` or `/etc/nginx/conf.d/`
- Sites: `/etc/nginx/conf.d/` (Amazon Linux doesn't use sites-available/sites-enabled)
- Logs: `/var/log/nginx/`

### Paths and Permissions
- Application directory: `/opt/trading-api`
- Logs: `/var/log/trading-api`
- User: `ec2-user`
- Group: `ec2-user`

### Common Issues

#### Issue: Python 3.12 not found
**Solution**: The setup script compiles Python 3.12 from source. This takes time but ensures compatibility.

#### Issue: Permission denied
**Solution**: 
```bash
sudo chown -R ec2-user:ec2-user /opt/trading-api
sudo chown -R ec2-user:ec2-user /var/log/trading-api
```

#### Issue: Nginx not starting
**Solution**:
```bash
# Check if nginx is installed
sudo amazon-linux-extras list | grep nginx

# Install if needed
sudo amazon-linux-extras install nginx1

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### Issue: Node.js version too old
**Solution**: The setup script installs Node.js 20.x from NodeSource. If issues persist:
```bash
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
```

### Quick Commands for Amazon Linux

```bash
# Check OS version
cat /etc/os-release

# Update system
sudo yum update -y

# Install build tools
sudo yum groupinstall -y "Development Tools"

# Check Python version
python3 --version
python3.12 --version  # If installed

# Check Node.js version
node --version
npm --version

# Check Nginx
nginx -v
sudo systemctl status nginx

# Check firewall
sudo firewall-cmd --list-all
```

### Deployment Example for Amazon Linux

```bash
# 1. Initial setup
ssh -i ~/.ssh/key.pem ec2-user@ec2-ip
./setup-ec2.sh

# 2. Deploy from local
./deploy/aws-deploy.sh ec2-ip ec2-user

# 3. Configure and start
ssh -i ~/.ssh/key.pem ec2-user@ec2-ip
sudo ./deploy/scripts/setup-systemd.sh
sudo ./deploy/scripts/configure-nginx.sh
sudo systemctl start trading-api-backend trading-api-frontend
```

### Environment Variables

Amazon Linux uses the same environment variable configuration as other Linux distributions. The `.env` files work the same way.

### SSL/TLS with Let's Encrypt

Amazon Linux uses the same certbot installation:
```bash
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Monitoring

Same commands work on Amazon Linux:
```bash
# Service status
sudo systemctl status trading-api-backend
sudo systemctl status trading-api-frontend

# Logs
sudo journalctl -u trading-api-backend -f
sudo journalctl -u trading-api-frontend -f

# System resources
htop  # Install with: sudo yum install -y htop
df -h
free -h
```

### Performance Tips for Amazon Linux

1. **Enable EPEL repository** (for additional packages):
   ```bash
   sudo yum install -y epel-release
   ```

2. **Install Performance Monitoring Tools**:
   ```bash
   sudo yum install -y htop iotop
   ```

3. **Optimize Python**:
   - Use virtual environments (done automatically)
   - Python 3.12 is compiled with optimizations

4. **Node.js Optimization**:
   - Use production build: `npm run build`
   - Enable PM2 for process management (optional)

### Troubleshooting

#### Python Virtual Environment Issues
```bash
cd /opt/trading-api/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### Node.js Build Issues
```bash
cd /opt/trading-api/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm run build
```

#### Systemd Service Issues
```bash
# Check service status
sudo systemctl status trading-api-backend

# View detailed logs
sudo journalctl -u trading-api-backend -n 100 --no-pager

# Test service manually
cd /opt/trading-api/backend
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8501
```

### Security Best Practices

1. **Update regularly**:
   ```bash
   sudo yum update -y
   ```

2. **Use Security Groups**: Configure AWS Security Groups instead of relying on firewalld

3. **SSH Key Security**: Use SSH keys, disable password authentication

4. **Regular Backups**: Backup `/opt/trading-api/backend/privatedata/` and `.env` files

5. **Monitor Logs**: Set up CloudWatch Logs for centralized logging

### Additional Resources

- [Amazon Linux 2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/amazon-linux-2.html)
- [Amazon Linux 2023 User Guide](https://docs.aws.amazon.com/linux/al2023/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

