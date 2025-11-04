# Clean Ransomware Detection Project

Steps:
1. Open `backend` in VS Code.
2. Create venv and install requirements.
3. Run:
   ```powershell
   python dataset_generator.py
   python train_model.py
   python app.py
   ```
4. Open browser at http://127.0.0.1:5000
5. Use UI to scan file or folder.

MongoDB logs results under DB `ransomware_demo`.
All data synthetic & safe.