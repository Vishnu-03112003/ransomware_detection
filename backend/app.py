from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, joblib, pandas as pd, datetime
from pathlib import Path
from pymongo import MongoClient
from features import get_extension, sample_non_printable_pct, pseudo_entropy_from_bytes, file_size_kb

# === Setup ===
app = Flask(__name__, static_folder="frontend")
CORS(app)  # ✅ Enables CORS for frontend

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'model.joblib'

# === Load Model ===
model = None
model_columns = []
if MODEL_PATH.exists():
    model_data = joblib.load(str(MODEL_PATH))
    model = model_data['model']
    model_columns = model_data['columns']
else:
    print("⚠️ Warning: model.joblib not found, using dummy mode")

# === MongoDB Setup ===
MONGO_URI = os.environ.get(
    'MONGO_URI',
    'mongodb+srv://rengasankar2005:<db_password>@cluster0.jmfr98r.mongodb.net/?retryWrites=true&w=majority'
)
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client['ransomware_demo']
    logs = db['detections']
    mongo_ok = True
    print("✅ MongoDB connected")
except Exception as e:
    print("❌ Mongo failed:", e)
    mongo_ok = False
    logs = None

# === Helper Functions ===
def compute_features(p: Path):
    sz = file_size_kb(str(p))
    ext = get_extension(str(p))
    de = 1 if '.' in p.name[:-len(p.suffix)] else 0
    npct = sample_non_printable_pct(str(p))
    try:
        b = open(p, 'rb').read(1024)
        ent = pseudo_entropy_from_bytes(b)
    except:
        ent = 0.0
    return {
        'file_size_kb': sz,
        'ext': ext,
        'double_ext': de,
        'entropy_proxy': ent,
        'write_count_last_min': 0,
        'rename_flag': 0,
        'non_printable_pct': npct
    }

def predict(feats):
    if model is None:
        return {'prediction': 0, 'prob': 0.0}
    r = pd.DataFrame([feats])
    r = pd.get_dummies(r)
    for c in model_columns:
        if c not in r:
            r[c] = 0
    r = r[model_columns]
    pred = int(model.predict(r)[0])
    prob = float(model.predict_proba(r)[0][1])
    return {'prediction': pred, 'prob': prob}

# === Routes ===
@app.route('/')
def home():
    return "✅ Ransomware Detection Backend Running"

@app.route('/api/scan_file', methods=['POST'])
def scan_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    tmp = BASE_DIR / 'tmp'
    tmp.mkdir(exist_ok=True)
    fp = tmp / f.filename
    f.save(fp)

    feats = compute_features(fp)
    res = predict(feats)
    os.remove(fp)

    entry = {'file': f.filename, **res, 'features': feats, 'time': datetime.datetime.utcnow().isoformat()}
    if mongo_ok and logs:
        logs.insert_one(entry)
    return jsonify(entry)

@app.route('/api/scan_folder', methods=['POST'])
def scan_folder():
    data = request.get_json()
    folder = data.get('folder')
    if not folder:
        return jsonify({'error': 'Folder required'}), 400
    p = Path(folder)
    if not p.exists() or not p.is_dir():
        return jsonify({'error': 'Folder not found'}), 400
    results = []
    for f in p.iterdir():
        if f.is_file():
            feats = compute_features(f)
            res = predict(feats)
            results.append({'file': str(f), **res})
    return jsonify({'results': results})

# === Run App ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Let Render assign port
    app.run(host='0.0.0.0', port=port)
