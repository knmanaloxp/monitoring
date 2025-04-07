@echo off
echo Setting up Git repository...

REM Check if Git is available in PATH
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git not found in PATH, trying to use Git from Program Files...
    set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
) else (
    set "GIT_CMD=git"
)

REM Initialize Git repository
echo Initializing Git repository...
"%GIT_CMD%" init

REM Configure Git
echo.
echo Please enter your GitHub username:
set /p GIT_USERNAME="Username: "
echo Please enter your GitHub email:
set /p GIT_EMAIL="Email: "

"%GIT_CMD%" config user.name "%GIT_USERNAME%"
"%GIT_CMD%" config user.email "%GIT_EMAIL%"

REM Add files and create initial commit
echo.
echo Adding files to Git...
"%GIT_CMD%" add .

echo.
echo Creating initial commit...
"%GIT_CMD%" commit -m "Initial commit: Web Monitoring System"

echo.
echo Please enter your GitHub repository URL (e.g., https://github.com/username/repo.git):
set /p REPO_URL="Repository URL: "

echo.
echo Adding remote origin...
"%GIT_CMD%" remote add origin %REPO_URL%

echo.
echo Pushing to GitHub...
"%GIT_CMD%" push -u origin master

echo.
echo Setup complete! Press any key to exit.
pause > nul