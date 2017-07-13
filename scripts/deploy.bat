@echo off
set base_dir=%~dp0
"%base_dir%\merge.to.staging.bat" && python "%base_dir%\..\manage.py" makemigrations && (^
git add -A & git commit -am"committing migrations before deployment" & git push heroku HEAD:master & echo :D) || ^
echo "Deployment failed. Check for merge issues or server status."