from flask import Flask, request, render_template, jsonify
from nebula_hash import NebulaHash
import hashlib
import os
import math

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_text = request.form.get('input_text', '')
        hash_length = int(request.form.get('hash_length', 32))
        
        try:
            # Compute hashes
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

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "NebulaHash API"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
