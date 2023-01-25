echo "---------------------------------------------------------------------------------------"
echo "flake8 . --exclude=.venv,.git --count --select=E9,F63,F7,F82 --show-source --statistics"
echo "---------------------------------------------------------------------------------------"
flake8 . --exclude=.venv,.git --count --select=E9,F63,F7,F82 --show-source --statistics
echo ""
echo "--------------------------------------------------------------------------------------------------------"
echo "flake8 . --exclude=.venv,.git --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics"
echo "--------------------------------------------------------------------------------------------------------"
flake8 . --exclude=.venv,.git --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics