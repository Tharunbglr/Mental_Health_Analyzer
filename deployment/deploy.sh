# Production deployment script
# Run as: bash deploy.sh yourdomain.com

set -e

if [ -z "$1" ]; then
    echo "Usage: bash deploy.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "Installing dependencies..."
sudo apt-get install -y python3-pip python3-venv nginx redis-server supervisor certbot python3-certbot-nginx

# Create production directory
echo "Setting up application directory..."
sudo mkdir -p /var/www/mental-health
sudo chown $USER:$USER /var/www/mental-health

# Clone repository
echo "Cloning repository..."
git clone https://github.com/yourusername/mental-health-analyzer.git /var/www/mental-health/current
cd /var/www/mental-health/current

# Set up Python environment
echo "Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn gevent

# Set up environment variables
echo "Setting up environment variables..."
sudo tee /etc/mental-health.env << EOL
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
RATELIMIT_STORAGE_URI=redis://localhost:6379/0
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
RATELIMIT_DEFAULT=100/day
EOL

# Configure Supervisor
echo "Configuring Supervisor..."
sudo cp deployment/supervisor.conf /etc/supervisor/conf.d/mental-health.conf
sudo supervisorctl reread
sudo supervisorctl update

# Configure Nginx
echo "Configuring Nginx..."
sudo cp deployment/nginx.conf /etc/nginx/sites-available/mental-health
sudo sed -i "s/yourmentalhealth.com/$DOMAIN/g" /etc/nginx/sites-available/mental-health
sudo ln -sf /etc/nginx/sites-available/mental-health /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# Set up SSL
echo "Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --redirect --non-interactive --agree-tos --email admin@$DOMAIN

# Set up Redis
echo "Configuring Redis..."
sudo sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
sudo systemctl restart redis-server

# Set up log rotation
echo "Configuring log rotation..."
sudo tee /etc/logrotate.d/mental-health << EOL
/var/log/mental-health/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        /usr/bin/supervisorctl restart mental-health > /dev/null
    endscript
}
EOL

# Set up monitoring (basic)
echo "Setting up basic monitoring..."
sudo apt-get install -y prometheus-node-exporter

# Final steps
echo "Starting services..."
sudo systemctl restart supervisor
sudo systemctl restart nginx

echo "Deployment complete! Site should be available at https://$DOMAIN"
echo "Next steps:"
echo "1. Configure monitoring (recommended: Datadog or Grafana)"
echo "2. Set up backup system"
echo "3. Configure email for error notifications"
echo "4. Set up CDN (recommended: Cloudflare)"