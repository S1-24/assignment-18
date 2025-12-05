from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import database
import os

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'uploads'
# Set the maximum allowed content length (e.g., 16 megabytes)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- API ROUTES ---

# 1. GET all items (with optional search)
@app.route('/api/items', methods=['GET'])
def get_items():
    """
    Fetch all items. Supports optional 'q' query for search (by name/author).
    """
    query = request.args.get('q')
    if query:
        return jsonify(database.search_items(query))
    return jsonify(database.get_all_items())

# 2. ADD new item (Handles the metadata and the saved image filename)
@app.route('/api/items', methods=['POST'])
def add_item():
    """
    Add a new item to the collection.
    Expects JSON: { "title": "...", "creator": "...", "image_filename": "..." }
    """
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Missing title"}), 400
    
    # Required metadata fields
    title = data['title']
    creator = data.get('creator', 'Unknown')
    category = data.get('category', 'Book')
    year = data.get('year', '2025')
    image_filename = data.get('image_filename', None) # New field
    
    new_item = database.add_item(title, creator, category, year, image_filename)
    
    return jsonify(new_item), 201

# 3. DELETE item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Delete an item by its ID.
    """
    success = database.delete_item(item_id)
    if success:
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

# --- IMAGE HANDLER ROUTES ---

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    """
    Receives an image file, saves it to the UPLOAD_FOLDER, and returns the filename.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        # Use secure_filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        # Simple file type check (for common image types)
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            # Return the filename so the frontend can store it with the metadata
            return jsonify({"filename": filename}), 200
        
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/images/<filename>')
def get_image(filename):
    """
    Serves the image file when requested (though the Tkinter frontend currently
    only stores the path and doesn't display the image without Pillow).
    """
    # Use safe method to send files from a specified directory
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    print("--- MyLibrary Server Running on port 5000 ---")
    app.run(port=5000, debug=True)