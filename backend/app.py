"""
LinkBeam Backend Server
Handles device discovery and file sharing on LAN
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socket
import threading
import os
import json
import time
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
UPLOAD_FOLDER = 'uploads'
DISCOVERY_PORT = 12346
FILE_PORT = 12345
BUFFER_SIZE = 4096

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Device information
DEVICE_ID = str(uuid.uuid4())
DEVICE_NAME = socket.gethostname()

# Store discovered devices
discovered_devices = {}


def get_local_ip():
    """Get the local IP address of the machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class DeviceDiscovery:
    """Handles device discovery on LAN using UDP broadcast"""
    
    def __init__(self):
        self.running = False
        self.broadcast_thread = None
        self.listen_thread = None
        
    def start(self):
        """Start device discovery service"""
        if self.running:
            return
            
        self.running = True
        self.broadcast_thread = threading.Thread(target=self._broadcast_presence, daemon=True)
        self.listen_thread = threading.Thread(target=self._listen_for_devices, daemon=True)
        self.broadcast_thread.start()
        self.listen_thread.start()
        print("Device discovery started")
        
    def stop(self):
        """Stop device discovery service"""
        self.running = False
        
    def _broadcast_presence(self):
        """Broadcast device presence on LAN"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        message = json.dumps({
            'device_id': DEVICE_ID,
            'device_name': DEVICE_NAME,
            'ip': get_local_ip(),
            'port': FILE_PORT,
            'type': 'announce'
        })
        
        while self.running:
            try:
                sock.sendto(message.encode(), ('<broadcast>', DISCOVERY_PORT))
                time.sleep(5)  # Broadcast every 5 seconds
            except Exception as e:
                print(f"Broadcast error: {e}")
                
        sock.close()
        
    def _listen_for_devices(self):
        """Listen for device announcements"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', DISCOVERY_PORT))
        sock.settimeout(1.0)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                device_info = json.loads(data.decode())
                
                # Don't add ourselves
                if device_info['device_id'] != DEVICE_ID:
                    device_info['last_seen'] = time.time()
                    discovered_devices[device_info['device_id']] = device_info
                    
                    # Notify connected clients
                    socketio.emit('device_discovered', device_info)
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")
                
        sock.close()
        
    def cleanup_old_devices(self):
        """Remove devices not seen in the last 30 seconds"""
        current_time = time.time()
        to_remove = []
        
        for device_id, device_info in discovered_devices.items():
            if current_time - device_info.get('last_seen', 0) > 30:
                to_remove.append(device_id)
                
        for device_id in to_remove:
            del discovered_devices[device_id]
            socketio.emit('device_lost', {'device_id': device_id})


# Initialize discovery service
discovery_service = DeviceDiscovery()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'LinkBeam'})


@app.route('/api/device/info', methods=['GET'])
def get_device_info():
    """Get information about this device"""
    return jsonify({
        'device_id': DEVICE_ID,
        'device_name': DEVICE_NAME,
        'ip': get_local_ip(),
        'port': FILE_PORT
    })


@app.route('/api/devices', methods=['GET'])
def get_discovered_devices():
    """Get list of discovered devices on LAN"""
    discovery_service.cleanup_old_devices()
    return jsonify(list(discovered_devices.values()))


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Add timestamp if file exists
    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(time.time())}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'filepath': filepath,
        'size': os.path.getsize(filepath)
    })


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Handle file download"""
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
        
    return send_file(filepath, as_attachment=True)


@app.route('/api/files', methods=['GET'])
def list_files():
    """List available files"""
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            files.append({
                'filename': filename,
                'size': os.path.getsize(filepath),
                'modified': os.path.getmtime(filepath)
            })
    return jsonify(files)


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"Client connected")
    emit('connected', {'device_id': DEVICE_ID})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"Client disconnected")


@socketio.on('request_devices')
def handle_device_request():
    """Client requests device list"""
    discovery_service.cleanup_old_devices()
    emit('devices_list', list(discovered_devices.values()))


if __name__ == '__main__':
    # Start device discovery
    discovery_service.start()
    
    print(f"LinkBeam Server Starting...")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Device Name: {DEVICE_NAME}")
    print(f"IP Address: {get_local_ip()}")
    print(f"Server Port: 5000")
    print(f"Discovery Port: {DISCOVERY_PORT}")
    
    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
