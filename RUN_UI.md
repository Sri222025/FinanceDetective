# How to Run Financial Detective UI

## Quick Start

### Option 1: Using the Batch File (Windows)
Double-click `run_financial_detective_ui.bat`

### Option 2: Manual Command

1. **Open PowerShell or Command Prompt** in this directory

2. **Install dependencies** (if not already installed):
   ```powershell
   pip install streamlit networkx matplotlib numpy requests
   ```

3. **Set your API key** (choose one):
   ```powershell
   $env:GROQ_API_KEY="your-groq-api-key"
   # OR
   $env:OPENAI_API_KEY="your-openai-api-key"
   ```

4. **Run the Streamlit app**:
   ```powershell
   python -m streamlit run financial_detective_app.py --server.port 8502
   ```

5. **Open your browser** to: http://localhost:8502

## Troubleshooting

### "Python was not found"
- Make sure Python is installed and in your PATH
- Try using `py` instead of `python`:
  ```powershell
  py -m streamlit run financial_detective_app.py --server.port 8502
  ```

### "Module not found"
- Install missing dependencies:
  ```powershell
  pip install streamlit networkx matplotlib numpy requests
  ```

### "Connection Refused"
- Make sure the Streamlit server started successfully
- Check the terminal for any error messages
- Try a different port:
  ```powershell
  python -m streamlit run financial_detective_app.py --server.port 8503
  ```

### Port Already in Use
- If port 8502 is busy, use a different port:
  ```powershell
  python -m streamlit run financial_detective_app.py --server.port 8503
  ```
- Or stop the other Streamlit app first

## Alternative: Use the Existing Samaahar App Port

If the Samaahar app is running on port 8501, you can run Financial Detective on a different port:

```powershell
python -m streamlit run financial_detective_app.py --server.port 8502
```

Then access it at: http://localhost:8502

