# LinkBeam - LAN File Sharing

LinkBeam is a modern web-based file sharing application that works on your local network (LAN) without requiring internet connectivity. It features automatic device discovery and seamless file transfers between devices.

## Features

✨ **Phase 1 - Current Features:**
- 🌐 Web-based React UI with modern design
- 🔍 Automatic device discovery on LAN using UDP broadcast
- 📤 Send files to discovered devices
- 📥 Receive files from other devices
- 📊 Real-time progress tracking for file transfers
- 💻 Cross-platform support (works on any device with a web browser)
- 🔒 No internet required - works entirely on local network
- 🔄 Real-time device list updates using WebSockets

🚀 **Phase 2 - Coming Soon:**
- 👋 Hand gesture-based file sharing
- Camera-based gesture detection
- Gesture-triggered file transfers

## Architecture

### Backend (Python + Flask)
- **Flask**: Web server and REST API
- **Flask-SocketIO**: Real-time communication with WebSockets
- **UDP Broadcast**: Device discovery on LAN
- **File Upload/Download**: Secure file transfer endpoints

### Frontend (React)
- **React**: Modern, component-based UI
- **Socket.IO Client**: Real-time device updates
- **Axios**: HTTP requests for file operations
- **Responsive Design**: Works on desktop and mobile

## Installation

### Prerequisites
- Python 3.7 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
python app.py
```

The backend will start on `http://0.0.0.0:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will open in your browser at `http://localhost:3000`

## Usage

### Sending Files

1. Start LinkBeam on both devices
2. Click the **📤 Send** tab
3. Click **Choose File** to select a file
4. Wait for devices to appear in the "Available Devices" list
5. Click on the device you want to send to
6. Click **Send File**
7. Watch the progress bar as your file uploads

### Receiving Files

1. Start LinkBeam on your device
2. Click the **📥 Receive** tab
3. Share your IP address with the sender
4. Received files will appear in the "Received Files" list
5. Click **⬇️ Download** to save files to your device

### Device Discovery

- Devices automatically broadcast their presence every 5 seconds
- Devices not seen for 30 seconds are removed from the list
- The device list updates in real-time via WebSockets

## Configuration

### Backend Configuration (backend/app.py)
```python
UPLOAD_FOLDER = 'uploads'      # Where received files are stored
DISCOVERY_PORT = 12346         # UDP port for device discovery
FILE_PORT = 12345              # TCP port for file transfers
```

### Frontend Configuration
Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:5000
```

## Network Requirements

- All devices must be on the same local network (LAN)
- Firewall should allow:
  - Port 5000 (HTTP/WebSocket)
  - Port 12346 (UDP broadcast)
  - Port 12345 (File transfers)

## Troubleshooting

### Devices Not Appearing
- Check that all devices are on the same network
- Verify firewall settings allow UDP broadcast on port 12346
- Ensure the backend server is running on all devices

### File Transfer Fails
- Verify the receiving device's backend is running
- Check network connectivity between devices
- Ensure port 5000 is accessible on the receiving device

### Cannot Access from Other Devices
- Make sure the backend is binding to `0.0.0.0` not `127.0.0.1`
- Check your firewall settings
- Verify you're using the correct IP address

## Project Structure

```
LinkBeam/
├── backend/
│   ├── app.py              # Flask server with device discovery
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Received files storage
├── frontend/
│   ├── public/             # Static files
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styling
│   │   └── index.js       # React entry point
│   └── package.json       # Node dependencies
├── gesture_detect.py       # Gesture detection (Phase 2)
└── link_beam.py           # Original desktop app
```

## Technology Stack

### Backend
- Python 3.x
- Flask 3.0.0
- Flask-CORS 4.0.0
- Flask-SocketIO 5.3.5
- python-socketio 5.11.0

### Frontend
- React 18.x
- Socket.IO Client
- Axios
- Modern CSS with animations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Roadmap

- [x] Phase 1: React UI and Python backend
  - [x] Device discovery
  - [x] File sharing
  - [x] Real-time updates
- [ ] Phase 2: Hand gesture file sharing
  - [ ] Integrate gesture detection
  - [ ] Camera access in React
  - [ ] Gesture-triggered actions

## Author

Shivam Singh

## Acknowledgments

- Inspired by Huawei's hand gesture file share feature
- Built for seamless LAN file sharing
