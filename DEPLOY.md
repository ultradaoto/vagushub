# VagusHub Deployment

## GitHub Actions (Auto-deploy on push)

Pushes to `main` automatically deploy to the production server via GitHub Actions.

### Required Secrets

Add these in **Settings → Secrets and variables → Actions** (repo: `ultradaoto/vagushub`):

| Secret | Value | Description |
|--------|-------|-------------|
| `REMOTE_HOST` | `143.198.103.15` | Server IP |
| `REMOTE_USER` | `deployer` | SSH user |
| `REMOTE_PORT` | `22` | SSH port (optional, defaults to 22) |
| `SSH_PRIVATE_KEY` | *(contents of your SSH private key)* | Key that can SSH as deployer@143.198.103.15 |

Use the same key you use for `ssh deployer@143.198.103.15` (e.g. `~/.ssh/id_ed25519`).

### Manual deploy (if Actions unavailable)

```bash
ssh deployer@143.198.103.15 "cd ~/vagushub && git pull origin main && npm install --production && pm2 reload vagushub && pm2 save"
```
