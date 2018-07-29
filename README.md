# Send It Once
Simple Google App Engine application for creating single-use file downloads.

# How To Use This
1. Deploy the app.yaml at the root of this project to your App Engine project
2. Create an App Engine project and enable the default GCS bucket.
3. Create a "downloads" directory in the GCS bucket.
4. Upload the file you want to deliver into the downloads directory.
5. Create a key file named the same as the above file with ".key.txt" added to the end of the file name. (see below for format of this file)
6. Upload this key file into the downloads directory.


# Key File Format
Key files are plain text files in this form:
```
key|ttl
```
* key: Any string without pipe characters.
* ttl: Time in seconds that the download will be valid for after it is first used.

# Accessing Download Links
Download links are in this form:

https://APP_ID.appspot.com/downloads/filename?key=key

Once a download link is used for the first time, the key file in GCS will be rewritten with a expiration timestamp in place of the TTL value.

# Example
In default GCS bucket:
```
downloads
├── some_file.jpg
└── some_file.jpg.key.txt
```

Contents of some_file.jpg.key.txt:
```
c17a852292ae482eaf2cd4decfbf23d1|900
```

This link will be active for 15 minutes after it is first used:

https://APP_ID.appspot.com/downloads/some_file.jpg?key=c17a852292ae482eaf2cd4decfbf23d1