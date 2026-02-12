# LinkBeam API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Health Check
Check if the server is running.

```
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "LinkBeam"
}
```

---

### Get Device Info
Get information about the current device.

```
GET /api/device/info
```

**Response:**
```json
{
  "device_id": "8bc1eea3-87d1-4cbf-8a3f-557826d307d5",
  "device_name": "MyComputer",
  "ip": "192.168.1.100",
  "port": 12345
}
```

---

### Get Discovered Devices
Get a list of all devices discovered on the LAN.

```
GET /api/devices
```

**Response:**
```json
[
  {
    "device_id": "abc123...",
    "device_name": "Device1",
    "ip": "192.168.1.101",
    "port": 12345,
    "type": "announce",
    "last_seen": 1234567890.123
  },
  {
    "device_id": "def456...",
    "device_name": "Device2",
    "ip": "192.168.1.102",
    "port": 12345,
    "type": "announce",
    "last_seen": 1234567891.456
  }
]
```

---

### Upload File
Upload a file to the server.

```
POST /api/upload
```

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field

**cURL Example:**
```bash
curl -X POST -F "file=@/path/to/file.txt" http://localhost:5000/api/upload
```

**Response:**
```json
{
  "success": true,
  "filename": "file.txt",
  "filepath": "uploads/file.txt",
  "size": 1024
}
```

**Error Response:**
```json
{
  "error": "No file provided"
}
```

---

### Download File
Download a file from the server.

```
GET /api/download/<filename>
```

**Parameters:**
- `filename` (path parameter): Name of the file to download

**Example:**
```
GET /api/download/test.txt
```

**Response:**
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename=<filename>`
- Body: File contents

**Error Response:**
```json
{
  "error": "File not found"
}
```

---

### List Files
Get a list of all files available for download.

```
GET /api/files
```

**Response:**
```json
[
  {
    "filename": "file1.txt",
    "size": 1024,
    "modified": 1234567890.123
  },
  {
    "filename": "file2.pdf",
    "size": 2048,
    "modified": 1234567891.456
  }
]
```

---

## WebSocket Events

### Connect
Client connects to the WebSocket server.

**Event:** `connect`

**Server Response:**
```json
{
  "device_id": "8bc1eea3-87d1-4cbf-8a3f-557826d307d5"
}
```

---

### Request Devices
Client requests the current list of discovered devices.

**Event:** `request_devices`

**Client Emits:**
```javascript
socket.emit('request_devices')
```

**Server Response:**
Event: `devices_list`
```json
[
  {
    "device_id": "abc123...",
    "device_name": "Device1",
    "ip": "192.168.1.101",
    "port": 12345
  }
]
```

---

### Device Discovered
Server notifies clients when a new device is discovered.

**Event:** `device_discovered`

**Server Emits:**
```json
{
  "device_id": "abc123...",
  "device_name": "NewDevice",
  "ip": "192.168.1.103",
  "port": 12345,
  "type": "announce",
  "last_seen": 1234567890.123
}
```

---

### Device Lost
Server notifies clients when a device is no longer available.

**Event:** `device_lost`

**Server Emits:**
```json
{
  "device_id": "abc123..."
}
```

---

## Configuration

### Backend Configuration (backend/app.py)

```python
UPLOAD_FOLDER = 'uploads'      # Directory for uploaded files
DISCOVERY_PORT = 12346         # UDP port for device discovery
FILE_PORT = 12345              # TCP port for file transfers  
BUFFER_SIZE = 4096             # Buffer size for file operations
```

### Frontend Configuration (frontend/.env)

```env
REACT_APP_API_URL=http://localhost:5000
```

---

## Error Codes

- `400 Bad Request`: Invalid request (e.g., no file provided)
- `404 Not Found`: Requested resource not found (e.g., file doesn't exist)
- `500 Internal Server Error`: Server error

---

## Device Discovery Protocol

LinkBeam uses UDP broadcast for device discovery:

1. Each device broadcasts its presence every 5 seconds on port `12346`
2. Broadcast message format:
```json
{
  "device_id": "unique-id",
  "device_name": "hostname",
  "ip": "192.168.1.100",
  "port": 12345,
  "type": "announce"
}
```

3. Devices listen for broadcasts from other devices
4. Devices not seen for 30 seconds are removed from the list

---

## File Transfer Protocol

1. Client uploads file via POST to `/api/upload`
2. Server stores file in `uploads/` directory
3. Server responds with file metadata
4. File can be downloaded via GET from `/api/download/<filename>`

---

## CORS

The backend has CORS enabled for all origins to allow cross-origin requests during development.

For production, you should restrict CORS to specific origins:

```python
CORS(app, resources={r"/api/*": {"origins": "http://yourdomain.com"}})
```
