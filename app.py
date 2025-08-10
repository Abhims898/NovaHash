import os
from flask import Flask, render_template, request, jsonify
from nebula_hash import NebulaHash
import hashlib
import math

# Get absolute path to templates directory
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

@app.before_first_request
def verify_setup():
    """Debugging function to verify paths on deployment"""
    print("\n=== Startup Verification ===")
    print(f"Base directory: {base_dir}")
    print(f"Template directory: {template_dir}")
    print(f"Templates exists: {os.path.exists(template_dir)}")
    if os.path.exists(template_dir):
        print(f"Template files: {os.listdir(template_dir)}")
    print("=========================\n")

@app.route('/', methods=['GET', 'POST'])
def home():
    # Debug output for every request
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Template path verification: {os.path.exists(template_dir)}")
    
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
            print(f"Error during hash computation: {str(e)}")
            return render_template('index.html',
                               error=str(e),
                               input_text=input_text,
                               hash_length=hash_length)
    
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Endpoint for health checks"""
    return jsonify({
        "status": "healthy",
        "service": "NebulaHash API",
        "template_dir": template_dir,
        "template_exists": os.path.exists(template_dir)
    })

@app.route('/debug')
def debug():
    """Debug endpoint to check file structure"""
    import os
    return jsonify({
        "current_directory": os.getcwd(),
        "base_directory": base_dir,
        "template_directory": template_dir,
        "directory_contents": os.listdir(base_dir),
        "templates_contents": os.listdir(template_dir) if os.path.exists(template_dir) else "Missing"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server with template directory: {template_dir}")
    app.run(host='0.0.0.0', port=port)
