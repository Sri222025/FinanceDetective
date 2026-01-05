@echo off
echo Starting Financial Detective UI...
echo.
echo Make sure you have:
echo 1. Installed dependencies: pip install -r requirements_financial_detective.txt
echo 2. Set GROQ_API_KEY or OPENAI_API_KEY environment variable
echo.
echo Starting Streamlit app...
python -m streamlit run financial_detective_app.py --server.port 8502
pause

