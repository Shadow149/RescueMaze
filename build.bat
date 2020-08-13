@echo off
if not exist %~dp0build\ mkdir %~dp0build\
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
For /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set "build_name=RescueMaze_Build_%mydate%_%mytime%"
python %~dp0build.py ^"%~dp0build\%build_name%^"
pause