# GitHub Webhook Server for Code Review

A Flask-based webhook server that automatically runs code quality checks on GitHub PRs and blocks merging if checks fail.

## Features

✅ **Automatic PR Status Checks** - Runs on every push to PR
✅ **Blocks Merging** - PR cannot be merged until checks pass
✅ **Line-by-Line Comments** - Posts detailed review comments
✅ **GitHub Status API** - Updates commit status (pending/success/failure)
✅ **No GitHub Actions Required** - Works without CI/CD
✅ **Docker Support** - Easy deployment with Docker Compose

## How It Works

```
1. Developer pushes code to PR branch
   ↓
2. GitHub sends webhook event to server
   ↓
3. Server clones repo and runs checks:
   - Ruff linting
   - Code formatting
   - pytest tests
   ↓
4. Server updates PR status via GitHub API:
   - ✅ Success → Merge allowed
   - ❌ Failure → Merge blocked
   ↓
5. Server posts review comments with errors
```

## Quick Start

### 1. Deploy Server

```bash
# Clone repository
git clone https://github.com/your-org/your-repo.git
cd your-repo/webhook_server

# Configure environment
cp .env.example .env
nano .env  # Add your GITHUB_TOKEN and WEBHOOK_SECRET

# Start with Docker Compose
docker compose up -d

# Check health
curl http://localhost:5000/health
```

### 2. Configure GitHub Webhook

1. Go to repository Settings → Webhooks → Add webhook
2. Set:
   - **Payload URL**: `https://your-server.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: (your WEBHOOK_SECRET)
   - **Events**: Pull requests, Pushes
3. Save

### 3. Enable Branch Protection

1. Go to Settings → Branches → Add rule
2. Select branch: `main`
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Select: `code-review`
4. Save

## Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=ghp_your_token_here        # GitHub Personal Access Token
WEBHOOK_SECRET=your_secret_here         # Webhook secret for security

# Optional
PORT=5000                               # Server port (default: 5000)
```

### GitHub Token Scopes

Required scopes:
- `repo` (full control) - for private repos
- `repo:status` - to update commit status
- `public_repo` - for public repos only

Create token at: https://github.com/settings/tokens

## API Endpoints

### POST /webhook
Receives GitHub webhook events (push, pull_request)

### GET /health
Health check endpoint

Response:
```json
{
  "status": "healthy",
  "github_token_set": true,
  "webhook_secret_set": true
}
```

## Code Checks

The server runs these checks:

1. **Ruff Linting** - Checks for code errors and style issues
2. **Ruff Formatting** - Verifies code is properly formatted
3. **pytest** - Runs all tests

## PR Status Updates

### Pending
```
⏳ Running code quality checks...
```
Shown while checks are running.

### Success
```
✅ All checks passed
```
PR can be merged.

### Failure
```
❌ Found X issue(s)
```
PR cannot be merged. Review comments posted with details.

## Example PR Comment

When checks fail, the server posts:

```markdown
## 🔍 Code Review Results for commit `abc1234`

Found 2 issue(s):

### 📄 `src/calculator.py`

🔴 **Line 15:5** - `F841`
   Local variable `unused_var` is assigned but never used

⚠️ **Line 20:1** - `E225`
   Missing whitespace around operator

---
💡 **Fix these issues to pass the status check**
```

## Deployment Options

### Docker Compose (Recommended)
```bash
docker compose up -d
```

### Direct Python
```bash
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:5000 app:app
```

### Cloud Platforms
- AWS EC2
- Google Cloud Run
- Azure Container Instances
- DigitalOcean Droplet
- Heroku

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## Development

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN='your_token'
export WEBHOOK_SECRET='your_secret'

# Run Flask development server
python app.py
```

### Test Webhook

```bash
# Use ngrok for local testing
ngrok http 5000

# Copy the HTTPS URL and use it in GitHub webhook settings
```

## Monitoring

### View Logs

```bash
# Docker Compose
docker compose logs -f

# Check specific container
docker compose logs webhook-server
```

### Health Check

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Webhook Not Receiving Events

1. Check server is publicly accessible
2. Verify webhook URL in GitHub settings
3. Check GitHub webhook delivery logs
4. Ensure firewall allows incoming connections

### Status Not Updating

1. Verify GITHUB_TOKEN is set
2. Check token has correct scopes
3. Review server logs for API errors

### Checks Failing

1. Check server logs for error details
2. Verify ruff and pytest are installed
3. Ensure repository can be cloned

## Security

- ✅ Webhook signature verification
- ✅ HTTPS recommended for production
- ✅ Environment variables for secrets
- ✅ Token rotation recommended every 90 days

## Architecture

```
┌─────────────────┐
│  GitHub Repo    │
└────────┬────────┘
         │ webhook
         ↓
┌─────────────────┐
│ Webhook Server  │
│  - Flask App    │
│  - Code Checks  │
│  - Status API   │
└────────┬────────┘
         │ status update
         ↓
┌─────────────────┐
│  Pull Request   │
│  ✅ or ❌       │
└─────────────────┘
```

## Files

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image configuration
- `docker-compose.yml` - Docker Compose setup
- `.env.example` - Environment variables template
- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions

## Support

For issues or questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review server logs
3. Verify GitHub webhook deliveries
4. Check token permissions

## License

MIT License