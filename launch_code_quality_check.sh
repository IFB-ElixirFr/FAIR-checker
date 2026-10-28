# Strict check (fails the script, like the GitHub CI), then advisory report.
gate_status=0

echo "---------------------------------------------------------------------------------------"
echo "flake8 . --exclude=.venv,.git,.ipynb_checkpoints,notebooks --count --select=E9,F63,F7,F82,E262,F841,E265,E266,E712,E713,F401,F403,F405,F811 --show-source --statistics"
echo "---------------------------------------------------------------------------------------"
flake8 . --exclude=.venv,.git,.ipynb_checkpoints,notebooks --count --select=E9,F63,F7,F82,E262,F841,E265,E266,E712,E713,F401,F403,F405,F811 --show-source --statistics || gate_status=$?
echo ""
echo "--------------------------------------------------------------------------------------------------------"
echo "flake8 . --exclude=.venv,.git,.ipynb_checkpoints,notebooks --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics"
echo "--------------------------------------------------------------------------------------------------------"
flake8 . --exclude=.venv,.git,.ipynb_checkpoints,notebooks --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

exit $gate_status
