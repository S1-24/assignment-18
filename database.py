import json
import os

DB_FILE = "Legendary01_data.json"

def _init_db():
    """Creates the JSON file if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            # Initialize with an empty list to ensure valid JSON structure
            json.dump([], f)

def get_all_items():
    """Reads all items from the JSON file."""
    _init_db()
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        # Return empty list on read error
        return []

def add_item(title, creator, category, year, image_filename):
    """
    Adds a new item to the database.
    
    Arguments:
        title (str)
        creator (str)
        category (str)
        year (str)
        image_filename (str/None): The filename saved on the server.
    """
    items = get_all_items()
    
    # Generate a new ID based on the highest existing ID
    new_id = 1
    if items:
        # Find the max ID and increment it
        new_id = max(i['id'] for i in items) + 1
        
    new_item = {
        "id": new_id,
        "title": title,
        "creator": creator,
        "category": category,
        "year": year,
         # <-- NEW FIELD to store the image reference
    }
    
    items.append(new_item)
    _save(items)
    return new_item

def delete_item(item_id):
    """Deletes an item by its ID."""
    items = get_all_items()
    # Ensure item_id is an integer for comparison
    try:
        item_id = int(item_id)
    except ValueError:
        return False # Invalid ID format
        
    # Keep only items that DO NOT match the ID
    new_list = [i for i in items if i['id'] != item_id]
    
    # If the list size changed, we successfully deleted something
    if len(new_list) < len(items):
        _save(new_list)
        return True
    return False

def search_items(query):
    """Searches for items by Title or Creator (Case-insensitive)."""
    items = get_all_items()
    query = query.lower()
    return [i for i in items if query in i['title'].lower() or query in i['creator'].lower()]

def _save(data):
    """Helper to write data back to the file."""
    with open(DB_FILE, 'w') as f:
        # Use indent=4 for human-readable JSON formatting
        json.dump(data, f, indent=4)