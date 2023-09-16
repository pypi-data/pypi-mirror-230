import hashlib

def calculate_file_hash(hashed_results):
    """
    Calculate the SHA-256 hash of a file.
    args:
       hashed_results: 
    
    """
    sha256_hash = hashlib.sha256(hashed_results.rstrip()).hexdigest()
    return sha256_hash
