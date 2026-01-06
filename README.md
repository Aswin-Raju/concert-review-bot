# Code Review Bot - Automated PR Status Checks

A comprehensive code review system that automatically runs quality checks on Pull Requests and **blocks merging** until all checks pass. Works without GitHub Actions using a webhook server.

## 🎯 Key Features

✅ **Automatic PR Status Checks** - Runs on every push to PR
✅ **Blocks Merging** - PR cannot be merged until checks pass  
✅ **Line-by-Line Comments** - Posts detailed review comments with file paths and line numbers
✅ **No GitHub Actions Required** - Uses webhook server instead
✅ **Real-time Feedback** - Immediate status updates on commits
✅ **Comprehensive Checks** - Ruff linting, formatting, and pytest tests

## 📋 How It Works

```
Developer pushes code to PR
         ↓
GitHub webhook triggers server
         ↓
Server clones repo & runs checks
         ↓
Updates PR status via GitHub API
         ↓
✅ Success → Merge allowed
❌ Failure → Merge blocked + Comments posted
```

## 🚀 Quick Start

### 1. Deploy Webhook Server

```bash
cd webhook_server

# Configure environment
cp .env.example .env
nano .env  # Add GITHUB_TOKEN and WEBHOOK_SECRET

# Start server with Docker
docker compose up -d

# Verify it's running
curl http://localhost:5000/health
```

### 2. Configure GitHub

**A. Create GitHub Token**
- Go to: https://github.com/settings/tokens
- Create token with `repo` and `repo:status` scopes

**B. Add Webhook**
- Repository Settings → Webhooks → Add webhook
- Payload URL: `https://your-server.com/webhook`
- Content type: `application/json`
- Secret: (your WEBHOOK_SECRET)
- Events: Pull requests, Pushes

**C. Enable Branch Protection**
- Settings → Branches → Add rule for `main`
- ✅ Require status checks to pass before merging
- ✅ Select: `code-review`

### 3. Test It

```bash
# Create test PR with bad code
git checkout -b test-pr
echo "def bad(): unused=5; return 1" > test.py
git add test.py
git commit -m "Test PR"
git push origin test-pr
```

**Expected Result:**
- ⏳ Status shows "Pending" while checks run
- ❌ Status changes to "Failed" 
- 💬 Comment posted with line-by-line errors
- 🚫 Merge button is blocked

## 📁 Project Structure

```
.
├── webhook_server/          # Webhook server (main component)
│   ├── app.py              # Flask application
│   ├── Dockerfile          # Docker configuration
│   ├── docker-compose.yml  # Docker Compose setup
│   ├── requirements.txt    # Server dependencies
│   ├── README.md           # Server documentation
│   └── DEPLOYMENT_GUIDE.md # Detailed deployment guide
│
├── src/                    # Sample Python code
│   ├── calculator.py
│   └── string_utils.py
│
├── tests/                  # Sample tests
│   ├── test_calculator.py
│   └── test_string_utils.py
│
├── scripts/                # Helper scripts (optional)
│   ├── review_bot.py      # Local code review script
│   └── post_pr_comments.py # Manual PR comment poster
│
└── README.md              # This file
```

## 🔧 Configuration

### Webhook Server Environment

```bash
# Required
GITHUB_TOKEN=ghp_xxxxx      # GitHub Personal Access Token
WEBHOOK_SECRET=xxxxx        # Webhook secret for security

# Optional  
PORT=5000                   # Server port
```

### Code Quality Checks

The system runs:
1. **Ruff Linting** - Detects code errors and style issues
2. **Ruff Formatting** - Verifies proper code formatting
3. **pytest** - Runs all tests

Configuration in `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py312"
line-length = 100
fix = true

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B"]
```

## 📊 PR Status Examples

### ✅ All Checks Pass

```
Status: ✅ All checks passed
Merge: Allowed
Comment: None (no issues found)
```

### ❌ Checks Fail

```
Status: ❌ Found 3 issue(s)
Merge: Blocked
Comment:
  ## 🔍 Code Review Results for commit abc1234
  
  Found 3 issue(s):
  
  ### 📄 `src/calculator.py`
  
  🔴 **Line 15:5** - `F841`
     Local variable `unused_var` is assigned but never used
  
  ⚠️ **Line 20:1** - `E225`
     Missing whitespace around operator
```

## 🛠️ Deployment Options

### Docker Compose (Recommended)
```bash
cd webhook_server
docker compose up -d
```

### Cloud Platforms
- **AWS EC2** - t3.small instance (~$15/month)
- **DigitalOcean** - Droplet 2GB (~$12/month)
- **Google Cloud Run** - Pay per use (~$5-20/month)
- **Azure Container Instances** - (~$10-30/month)

### Free Options (Testing)
- ngrok (temporary URLs)
- Railway.app (free tier)
- Oracle Cloud (always free tier)

See [webhook_server/DEPLOYMENT_GUIDE.md](webhook_server/DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🔒 Security

- ✅ Webhook signature verification
- ✅ HTTPS required for production
- ✅ Environment variables for secrets
- ✅ Token rotation every 90 days recommended
- ✅ Firewall rules to restrict access

## 📚 Documentation

- **[webhook_server/README.md](webhook_server/README.md)** - Webhook server overview
- **[webhook_server/DEPLOYMENT_GUIDE.md](webhook_server/DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Local development setup
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration from pre-commit hooks

## 🧪 Testing

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run linting
ruff check src/ tests/

# Run formatting check
ruff format --check src/ tests/
```

### Test Webhook Locally

```bash
# Use ngrok to expose local server
ngrok http 5000

# Update GitHub webhook URL to ngrok URL
# Push code and watch the magic happen!
```

## 🐛 Troubleshooting

### Webhook Not Receiving Events
- Check server is publicly accessible
- Verify webhook URL in GitHub settings
- Check GitHub webhook delivery logs

### Status Not Updating
- Verify GITHUB_TOKEN has correct scopes
- Check server logs for API errors
- Ensure token hasn't expired

### Checks Failing Unexpectedly
- Review server logs
- Verify ruff and pytest are installed
- Check repository can be cloned

See [webhook_server/DEPLOYMENT_GUIDE.md](webhook_server/DEPLOYMENT_GUIDE.md) for more troubleshooting.

## 💡 Workflow Example

```bash
# 1. Developer creates feature branch
git checkout -b feature/new-feature

# 2. Makes changes (with some issues)
vim src/calculator.py

# 3. Commits and pushes
git commit -m "Add new feature"
git push origin feature/new-feature

# 4. Creates PR on GitHub
# → Webhook triggers automatically
# → Server runs checks
# → Status updated: ❌ Failed
# → Comment posted with errors
# → Merge button blocked

# 5. Developer fixes issues
vim src/calculator.py
git commit -m "Fix linting issues"
git push origin feature/new-feature

# 6. Webhook triggers again
# → Server runs checks
# → Status updated: ✅ Success
# → Merge button enabled
# → PR can be merged!
```

## 🎓 Benefits

### For Developers
- ✅ Immediate feedback on code quality
- ✅ Clear, actionable error messages
- ✅ No manual review needed for basic issues
- ✅ Learn best practices from automated feedback

### For Teams
- ✅ Consistent code quality standards
- ✅ Reduced manual review time
- ✅ Prevents bad code from being merged
- ✅ Automated enforcement of coding standards

### For Organizations
- ✅ No GitHub Actions required
- ✅ Works with disabled CI/CD
- ✅ Self-hosted solution
- ✅ Full control over checks

## 📈 Monitoring

```bash
# Check server health
curl http://your-server.com/health

# View logs
docker compose logs -f

# Check resource usage
docker stats
```

## 🔄 Updates

```bash
# Update webhook server
cd webhook_server
git pull origin main
docker compose down
docker compose build
docker compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and checks
5. Submit a pull request

## 📄 License

MIT License

## 🆘 Support

For issues or questions:
1. Check [webhook_server/DEPLOYMENT_GUIDE.md](webhook_server/DEPLOYMENT_GUIDE.md)
2. Review server logs
3. Verify GitHub webhook deliveries
4. Check token permissions

## 🎉 Success Criteria

Your setup is working correctly when:
- ✅ Webhook receives GitHub events
- ✅ Server runs checks on PR commits
- ✅ PR status updates automatically
- ✅ Comments posted when checks fail
- ✅ Merge blocked until checks pass
- ✅ Merge allowed when checks succeed

---

**Ready to get started?** Head to [webhook_server/DEPLOYMENT_GUIDE.md](webhook_server/DEPLOYMENT_GUIDE.md) for step-by-step deployment instructions!