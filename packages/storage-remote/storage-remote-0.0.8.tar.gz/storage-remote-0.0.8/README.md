# RemoteCirclesStorage Class

The `RemoteCirclesStorage` class provides methods for interacting with the remote storage service.  
It allows you to upload and download files from the remote storage.

## Installation

```bash
pip install storage-remote
```

Usage Example:

```python
from storage_remote.remote_circles_storage import RemoteCirclesStorage

# Uploading a file
remote_storage = RemoteCirclesStorage()
remote_path = remote_storage.put("file.txt", "/local/path/file.txt", 1, 2, 3)
print(f"Uploaded file to remote path: {remote_path}")

# Downloading a file
downloaded_contents = remote_storage.download("file.txt", 2, 3, "/local/path/file.txt")
print(f"Downloaded file contents: {downloaded_contents}")
```