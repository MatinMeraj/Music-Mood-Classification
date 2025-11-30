@echo off
echo Cleaning up old dependencies and build files...

if exist node_modules (
    echo Removing node_modules...
    rmdir /s /q node_modules
)

if exist pnpm-lock.yaml (
    echo Removing pnpm-lock.yaml...
    del /q pnpm-lock.yaml
)

if exist package-lock.json (
    echo Removing package-lock.json...
    del /q package-lock.json
)

if exist .next (
    echo Removing .next build directory...
    rmdir /s /q .next
)

echo Cleanup complete!
echo.
echo Installing dependencies with pnpm...

pnpm install

if errorlevel 1 (
    echo.
    echo pnpm not found, trying npm...
    npm install --legacy-peer-deps
)

echo.
echo Installation complete!
pause

