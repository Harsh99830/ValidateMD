from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import traceback
import logging
import numpy as np
from werkzeug.utils import secure_filename
from npi_matcher import validate_providers_from_csv, get_validation_summary

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/validate', methods=['POST'])
def validate_csv():
    """Validate CSV file against NPI registry"""
    
    logger.info("=== NEW VALIDATION REQUEST STARTED ===")
    
    # Check if file is present
    if 'file' not in request.files:
        logger.error("No file provided in request")
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    logger.info(f"File received: {file.filename}, Size: {len(file.read())} bytes")
    file.seek(0)  # Reset file pointer after reading size
    
    # Check if file is selected
    if file.filename == '':
        logger.error("Empty filename provided")
        return jsonify({"error": "No file selected"}), 400
    
    # Check file type
    if not allowed_file(file.filename):
        logger.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Only CSV files are allowed"}), 400
    
    file_path = None
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(f"{file_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"Saving file to: {file_path}")
        
        # Save file
        file.save(file_path)
        logger.info("File saved successfully")
        
        # Get parameters
        use_ai = request.form.get('use_ai', 'true').lower() == 'true'
        limit = request.form.get('limit', type=int)
        
        logger.info(f"Validation parameters - use_ai: {use_ai}, limit: {limit}")
        
        # Validate providers
        logger.info("Starting provider validation...")
        results = validate_providers_from_csv(file_path, use_ai=use_ai, limit=limit)
        logger.info(f"Validation completed. Processed {len(results)} providers")
        
        summary = get_validation_summary(results)
        logger.info(f"Summary: {summary}")
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("Temporary file cleaned up")
        
        # Ensure JSON serializable output: convert any NaN/Infinity to None
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(v) for v in obj]
            if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            return obj
        
        safe_results = sanitize(results)
        safe_summary = sanitize(summary)
        
        logger.info("=== VALIDATION REQUEST COMPLETED SUCCESSFULLY ===")
        
        return jsonify({
            "success": True,
            "summary": safe_summary,
            "results": safe_results,
            "total_processed": len(results)
        })
        
    except Exception as e:
        logger.error(f"VALIDATION FAILED: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Clean up file in case of error
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Cleaned up temporary file after error")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up file: {cleanup_error}")
        
        return jsonify({"error": f"Validation failed: {str(e)}"}), 500

@app.route('/api/validate-sample', methods=['GET'])
def validate_sample():
    """Validate a sample set of providers (for testing)"""
    logger.info("Sample validation request received")
    try:
        # Use a sample CSV file path - you'll need to adjust this
        sample_file_path = 'sample_data.csv'
        
        if not os.path.exists(sample_file_path):
            logger.error("Sample file not found")
            return jsonify({"error": "Sample file not found"}), 404
        
        use_ai = request.args.get('use_ai', 'true').lower() == 'true'
        limit = request.args.get('limit', 5, type=int)
        
        logger.info(f"Sample validation - use_ai: {use_ai}, limit: {limit}")
        
        results = validate_providers_from_csv(sample_file_path, use_ai=use_ai, limit=limit)
        logger.info(f"Sample validation completed: {len(results)} providers")
        
        summary = get_validation_summary(results)
        
        return jsonify({
            "success": True,
            "summary": summary,
            "results": results,
            "total_processed": len(results)
        })
        
    except Exception as e:
        logger.error(f"Sample validation failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Sample validation failed: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("Starting NPI Validation API Server...")
    app.run(debug=True, port=5000)