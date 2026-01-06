# Webhook Server Deployment Guide

This guide explains how to deploy the GitHub webhook server that runs code quality checks and blocks PR merges if checks fail.

## Overview

The webhook server:
- ✅ Receives GitHub push/PR events via webhooks
- ✅ Clones the repository and runs code quality checks
- ✅ Updates PR status via GitHub Status API
- ✅ **Blocks merging** if checks fail
- ✅ Posts detailed review comments to PRs

## Architecture

```
GitHub Repository
    ↓ (webhook on push/PR)
Webhook Server
    ↓ (clone repo)
Run Code Checks (Ruff, pytest)
    ↓ (update status)
GitHub Status API
    ↓ (block/allow merge)
Pull Request
```

## Prerequisites

- Server with public IP or domain (for GitHub to reach)
- Docker and Docker Compose installed
- GitHub Personal Access Token
- Repository admin access (to configure webhooks)

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### Step 1: Prepare Server

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Clone your repository
git clone https://github.com/your-org/your-repo.git
cd your-repo/webhook_server
```

#### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

Set these values:
```bash
GITHUB_TOKEN=ghp_your_token_here
WEBHOOK_SECRET=your_generated_secret
PORT=5000
```

Generate webhook secret:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 3: Build and Run

```bash
# Build the Docker image
docker compose build

# Start the server
docker compose up -d

# Check logs
docker compose logs -f

# Check health
curl http://localhost:5000/health
```

#### Step 4: Expose Server (Choose One)

**Option A: Using ngrok (for testing)**
```bash
# Install ngrok
snap install ngrok

# Expose port 5000
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Using Nginx (for production)**
```bash
# Install Nginx
sudo apt-get install nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/webhook
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Option C: Using Cloud Services**
- AWS EC2 + Elastic IP
- Google Cloud Run
- Azure Container Instances
- DigitalOcean Droplet

### Option 2: Direct Python (Without Docker)

```bash
# Install dependencies
cd webhook_server
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN='your_token'
export WEBHOOK_SECRET='your_secret'

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 app:app
```

## GitHub Configuration

### Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Code Review Webhook"
4. Select scopes:
   - ✅ `repo` (full control - required for status API)
   - ✅ `repo:status` (commit status)
5. Generate and copy the token

### Step 2: Configure Webhook in Repository

1. Go to your repository on GitHub
2. Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: `https://your-server.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: (paste your WEBHOOK_SECRET)
   - **Events**: Select individual events:
     - ✅ Pull requests
     - ✅ Pushes
   - ✅ Active

4. Click "Add webhook"

### Step 3: Enable Branch Protection

1. Go to Settings → Branches
2. Add rule for `main` (or your default branch)
3. Configure:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Search and select: `code-review`
   - ✅ Do not allow bypassing the above settings

4. Save changes

## Testing

### Test 1: Health Check

```bash
curl http://your-server.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "github_token_set": true,
  "webhook_secret_set": true
}
```

### Test 2: Create Test PR

```bash
# Create a branch with intentional issues
git checkout -b test-webhook

# Add bad code
cat > test_file.py << 'EOF'
def bad():
    unused = 5
    return 1
EOF

git add test_file.py
git commit -m "Test: Add bad code"
git push origin test-webhook
```

Create PR on GitHub and check:
1. ⏳ Status shows "Pending" initially
2. ❌ Status changes to "Failed" after checks
3. 💬 Comment posted with detailed errors
4. 🚫 Merge button is blocked

### Test 3: Fix and Verify

```bash
# Fix the code
cat > test_file.py << 'EOF'
def good():
    """A good function."""
    return 1
EOF

git add test_file.py
git commit -m "Fix: Remove unused variable"
git push origin test-webhook
```

Check PR:
1. ⏳ Status shows "Pending"
2. ✅ Status changes to "Success"
3. ✅ Merge button is enabled

## Monitoring

### View Logs

```bash
# Docker Compose
docker compose logs -f webhook-server

# Direct Python
tail -f /var/log/webhook-server.log
```

### Check Server Status

```bash
# Health endpoint
curl http://localhost:5000/health

# Docker status
docker compose ps

# Resource usage
docker stats
```

### Common Log Messages

```
✅ Good:
- "Received push event"
- "Status updated: success"
- "All checks passed"

⚠️ Warning:
- "No Python files changed"
- "Ignoring action: labeled"

❌ Error:
- "Failed to clone repository"
- "Cannot update status: GITHUB_TOKEN not set"
- "Invalid signature"
```

## Troubleshooting

### Webhook Not Receiving Events

**Check:**
1. Server is publicly accessible
2. Webhook URL is correct
3. GitHub webhook shows recent deliveries
4. Firewall allows incoming connections

**Test:**
```bash
# From another machine
curl https://your-server.com/health
```

### Status Not Updating

**Check:**
1. GITHUB_TOKEN is set correctly
2. Token has `repo:status` scope
3. Check server logs for API errors

**Test:**
```bash
# Check token permissions
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### Checks Taking Too Long

**Solutions:**
1. Increase worker timeout in docker-compose.yml
2. Add more workers
3. Optimize check scripts
4. Use faster server

### Repository Clone Fails

**Check:**
1. Repository is accessible
2. Token has repo access
3. Disk space available

**Fix:**
```bash
# Clear repo cache
docker compose exec webhook-server rm -rf /tmp/review-bot-repos/*
```

## Security Best Practices

### 1. Secure Secrets

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use environment variables
export GITHUB_TOKEN='...'
export WEBHOOK_SECRET='...'
```

### 2. Enable HTTPS

```bash
# Use Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Restrict Access

```bash
# Firewall rules (allow only GitHub IPs)
sudo ufw allow from 140.82.112.0/20 to any port 5000
sudo ufw allow from 143.55.64.0/20 to any port 5000
```

### 4. Rotate Tokens

- Rotate GitHub token every 90 days
- Update webhook secret periodically
- Monitor token usage

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  webhook-server:
    deploy:
      replicas: 3
    # ... rest of config
```

### Load Balancer

```nginx
upstream webhook_servers {
    server webhook1:5000;
    server webhook2:5000;
    server webhook3:5000;
}

server {
    location / {
        proxy_pass http://webhook_servers;
    }
}
```

## Maintenance

### Update Server

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
cd webhook_server
docker compose down
docker compose build
docker compose up -d
```

### Backup

```bash
# Backup environment config
cp .env .env.backup

# Backup logs
docker compose logs > logs-backup.txt
```

### Clean Up

```bash
# Remove old repo clones
docker compose exec webhook-server \
  find /tmp/review-bot-repos -mtime +7 -delete

# Prune Docker
docker system prune -a
```

## Cost Estimation

### Cloud Hosting Options

| Provider | Service | Cost/Month | Notes |
|----------|---------|------------|-------|
| DigitalOcean | Droplet (2GB) | $12 | Simple, reliable |
| AWS | t3.small EC2 | ~$15 | Scalable |
| Google Cloud | Cloud Run | ~$5-20 | Pay per use |
| Azure | Container Instance | ~$10-30 | Easy deployment |
| Heroku | Hobby Dyno | $7 | Simple setup |

### Free Options (for testing)

- ngrok (temporary URLs)
- GitHub Codespaces (limited hours)
- Oracle Cloud (always free tier)
- Railway.app (free tier)

## Support

For issues:
1. Check server logs
2. Verify GitHub webhook deliveries
3. Test health endpoint
4. Review GitHub token permissions

## Next Steps

After deployment:
1. ✅ Test with a sample PR
2. ✅ Configure branch protection
3. ✅ Train team on new workflow
4. ✅ Monitor for first week
5. ✅ Set up alerts/monitoring