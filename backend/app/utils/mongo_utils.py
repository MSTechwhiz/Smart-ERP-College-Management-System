from bson import ObjectId

def clean_mongo_doc(data):
    """Recursively convert ObjectId to string in nested dictionaries/lists"""
    if isinstance(data, list):
        return [clean_mongo_doc(i) for i in data]
    elif isinstance(data, dict):
        return {k: clean_mongo_doc(v) for k, v in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    return data
