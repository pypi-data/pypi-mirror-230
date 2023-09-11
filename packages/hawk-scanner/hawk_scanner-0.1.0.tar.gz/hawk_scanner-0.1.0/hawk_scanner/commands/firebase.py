import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from rich.console import Console
from hawk_scanner.internals import system
import os

def connect_firebase(credentials_file, bucket_name):
    try:
        cred = credentials.Certificate(credentials_file)
        firebase_admin.initialize_app(cred)
        bucket = storage.bucket(bucket_name)
        system.print_info(f"Connected to Firebase bucket: {bucket_name}")
        return bucket
    except Exception as e:
        print(f"Failed to connect to Firebase bucket: {e}")

def execute(args):
    results = []
    shouldDownload = True
    connections = system.get_connection()

    if 'sources' in connections:
        sources_config = connections['sources']
        firebase_config = sources_config.get('firebase')

        if firebase_config:
            for key, config in firebase_config.items():
                credentials_file = config.get('credentials_file')
                bucket_name = config.get('bucket_name')
                exclude_patterns = config.get(key, {}).get('exclude_patterns', [])

                if credentials_file and bucket_name:
                    bucket = connect_firebase(credentials_file, bucket_name)
                    if bucket:
                        for blob in bucket.list_blobs():
                            file_name = blob.name
                            ## get unique etag or hash of file
                            remote_etag = blob.etag
                            system.print_debug(f"Remote etag: {remote_etag}")

                            if system.should_exclude_file(file_name, exclude_patterns):
                                continue

                            file_path = f"data/firebase/{remote_etag}-{file_name}"
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)

                            if config.get("cache") == True:
                                if os.path.exists(file_path):
                                    shouldDownload = False
                                    local_etag = file_path.split('/')[-1].split('-')[0]
                                    system.print_debug(f"Local etag: {local_etag}")
                                    system.print_debug(f"File already exists in cache, using it. You can disable cache by setting 'cache: false' in connection.yml")
                                    if remote_etag != local_etag:
                                        system.print_debug(f"File in firebase bucket has changed, downloading it again...")
                                        shouldDownload = True
                                    else:
                                        shouldDownload = False

                            if shouldDownload:
                                file_path = f"data/firebase/{remote_etag}-{file_name}"
                                system.print_debug(f"Downloading file: {file_name} to {file_path}...")
                                blob.download_to_filename(file_path)
                            
                            matches = system.read_match_strings(file_path, 'google_cloud_storage')
                            if matches:
                                for match in matches:
                                    results.append({
                                        'bucket': bucket_name,
                                        'file_path': file_name,
                                        'pattern_name': match['pattern_name'],
                                        'matches': match['matches'],
                                        'sample_text': match['sample_text'],
                                        'profile': key,
                                        'data_source': 'firebase'
                                    })

                    else:
                        system.print_error(f"Failed to connect to Firebase bucket: {bucket_name}")
                else:
                    system.print_error(f"Incomplete Firebase configuration for key: {key}")
        else:
            system.print_error("No Firebase connection details found in connection.yml")
    else:
        system.print_error("No 'sources' section found in connection.yml")
    
    if config.get("cache") == False:
        os.system("rm -rf data/firebase")
    return results
