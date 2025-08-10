import os
from flask import Flask, render_template, request, jsonify
from nebula_hash import NebulaHash
import hashlib

# Configure absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Verify template directory exists
    if not os.path.exists(TEMPLATE_DIR):
        return "Template directory not found. Expected at: " + TEMPLATE_DIR, 500
    
    if request.method == 'POST':
        input_text = request.form.get('input_text', '')
        hash_length = int(request.form.get('hash_length', 32))
        
        try:
            nebula = NebulaHash.compute(input_text, hash_length)
            sha256 = hashlib.sha256(input_text.encode()).hexdigest()
            
            # Calculate similarity
            nebula_bin = bin(int.from_bytes(nebula.encode(), 'big'))[2:]
            sha256_bin = bin(int.from_bytes(sha256.encode(), 'big'))[2:]
            min_len = min(len(nebula_bin), len(sha256_bin))
            matches = sum(1 for a, b in zip(nebula_bin[:min_len], sha256_bin[:min_len]) if a == b)
            similarity = (matches / min_len) * 100
            
            return render_template('index.html',
                               input_text=input_text,
                               hash_length=hash_length,
                               nebula_hash=nebula,
                               sha256_hash=sha256,
                               similarity=f"{similarity:.2f}%")
        except Exception as e:
            return render_template('index.html',
                               error=str(e),
                               input_text=input_text,
                               hash_length=hash_length)
    
    return render_template('index.html')

@app.route('/debug')
def debug():
    return jsonify({
        "base_dir": BASE_DIR,
        "template_dir": TEMPLATE_DIR,
        "template_exists": os.path.exists(TEMPLATE_DIR),
        "files": os.listdir(BASE_DIR),
        "templates": os.listdir(TEMPLATE_DIR) if os.path.exists(TEMPLATE_DIR) else "Missing"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
