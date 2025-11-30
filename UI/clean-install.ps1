# Clean and reinstall UI dependencies
Write-Host "Cleaning up old dependencies and build files..."

# Remove node_modules if it exists
if (Test-Path "node_modules") {
    Write-Host "Removing node_modules..."
    Remove-Item -Recurse -Force "node_modules"
}

# Remove lock files
if (Test-Path "pnpm-lock.yaml") {
    Write-Host "Removing pnpm-lock.yaml..."
    Remove-Item -Force "pnpm-lock.yaml"
}

if (Test-Path "package-lock.json") {
    Write-Host "Removing package-lock.json..."
    Remove-Item -Force "package-lock.json"
}

# Remove .next build directory
if (Test-Path ".next") {
    Write-Host "Removing .next build directory..."
    Remove-Item -Recurse -Force ".next"
}

Write-Host "Cleanup complete!"
Write-Host ""
Write-Host "Installing dependencies with pnpm..."

# Install dependencies
pnpm install

Write-Host ""
Write-Host "Installation complete!"

