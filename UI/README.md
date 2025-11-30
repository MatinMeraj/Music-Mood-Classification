# UI Setup Instructions

## Clean Install

To remove all dependencies and reinstall from scratch:

### Option 1: Using the PowerShell Script

```powershell
cd UI
.\clean-install.ps1
```

### Option 2: Manual Cleanup

```powershell
cd UI

# Remove old dependencies
Remove-Item -Recurse -Force node_modules
Remove-Item -Force pnpm-lock.yaml
Remove-Item -Force package-lock.json
Remove-Item -Recurse -Force .next

# Install dependencies
pnpm install
```

### Option 3: Using npm (if pnpm is not available)

```powershell
cd UI

# Remove old dependencies
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
Remove-Item -Recurse -Force .next

# Install dependencies
npm install --legacy-peer-deps
```

## Running the Development Server

```powershell
cd UI
pnpm dev
# or
npm run dev
```

The app will be available at `http://localhost:3000`

## Building for Production

```powershell
cd UI
pnpm build
pnpm start
```

