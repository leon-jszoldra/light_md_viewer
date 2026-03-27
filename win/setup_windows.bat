@echo off
:: Register MD Viewer as default .md handler with icon (no admin required)

set "VIEWER_DIR=%~dp0"
set "ICON=%VIEWER_DIR%md-viewer.ico"
set "BAT=%VIEWER_DIR%MD Viewer.bat"

echo Registering MD Viewer for current user...

:: Register under HKCU (no admin needed)
reg add "HKCU\Software\Classes\.md" /ve /d "MDViewer.Document" /f >nul
reg add "HKCU\Software\Classes\.markdown" /ve /d "MDViewer.Document" /f >nul
reg add "HKCU\Software\Classes\MDViewer.Document" /ve /d "Markdown Document" /f >nul
reg add "HKCU\Software\Classes\MDViewer.Document\DefaultIcon" /ve /d "\"%ICON%\"" /f >nul
reg add "HKCU\Software\Classes\MDViewer.Document\shell\open\command" /ve /d "\"%BAT%\" \"%%1\"" /f >nul

:: Refresh icon cache
ie4uinit.exe -show >nul 2>&1

echo.
echo Done! .md and .markdown files now use MD Viewer with the custom icon.
echo You may need to restart Explorer or log out/in for icons to update.
pause
