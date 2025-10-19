# findPublicMedia

A project to find and manage public media resources.

## 🚀 Quick Setup

### 1. Authentication Setup (One-time only)
Run the authentication setup script to securely store your GitHub credentials:
```bash
./scripts/setup-auth.sh
```

This will configure your system to automatically handle GitHub authentication without requiring you to enter your token each time.

### 2. Test Your Setup
After configuring authentication, test it:
```bash
./scripts/test-push.sh
```

## 📋 Getting Started

This project is set up with Git flow branching:
- `main` - Production-ready code
- `develop` - Integration branch for features
- Feature branches - Individual features branched off develop

## 🔄 Development Workflow

1. Create feature branches from `develop`
2. Merge completed features back to `develop`
3. When ready for release, merge `develop` to `main`
