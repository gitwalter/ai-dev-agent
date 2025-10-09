@echo off
echo Starting Cursor AI integration...
C:\App\Anaconda\python.exe -c "import sys; sys.path.append('.'); from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration; print('Auto-starting Cursor integration...'); result = auto_initialize_cursor_integration(); print('Cursor integration started' if result else 'Cursor integration failed!')"
echo Cursor integration startup completed.
pause
