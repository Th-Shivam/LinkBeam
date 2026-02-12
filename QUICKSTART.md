# Quick Start Guide - LinkBeam

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.7+
- Node.js 14+
- Two or more devices on the same LAN (for testing)

---

## 📦 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Th-Shivam/LinkBeam.git
cd LinkBeam
```

### Step 2: Start the Application

**Option A: Using the Start Script (Recommended)**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual Start**

1. **Start Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

2. **Start Frontend (in a new terminal):**
```bash
cd frontend
npm install
npm start
```

---

## 🎯 First Time Use

### On Device 1 (Sender):

1. Open browser to `http://localhost:3000`
2. You'll see your device info at the top
3. Click the **📤 Send** tab
4. Click **Choose File** and select a file
5. Wait for Device 2 to appear in "Available Devices"
6. Click on Device 2's card to select it
7. Click **Send File**
8. Watch the progress bar!

### On Device 2 (Receiver):

1. Open browser to `http://localhost:3000`
2. Note your IP address shown at the top
3. Click the **📥 Receive** tab
4. Wait for the file transfer to complete
5. Your received file will appear in the "Received Files" list
6. Click **⬇️ Download** to save it to your device

---

## 🔍 Troubleshooting

### "No devices found"
- ✅ Make sure both devices are on the same network
- ✅ Check that the backend is running on both devices
- ✅ Verify firewall allows UDP broadcast on port 12346
- ✅ Wait 10-15 seconds for device discovery

### "Error sending file"
- ✅ Verify the receiver's backend is running on port 5000
- ✅ Check network connectivity between devices
- ✅ Make sure you selected both a file and a device

### "Cannot connect to backend"
- ✅ Ensure backend server is running
- ✅ Check that port 5000 is not in use by another application
- ✅ Try restarting the backend server

---

## 📱 Access from Other Devices

### To access LinkBeam from another device on your network:

1. Find your server's IP address (shown in the device info)
2. On another device, open browser to:
   - Backend API: `http://<server-ip>:5000`
   - Frontend UI: `http://<server-ip>:3000`

**Example:**
If server IP is `192.168.1.100`:
- Frontend: `http://192.168.1.100:3000`
- Backend API: `http://192.168.1.100:5000/api/health`

---

## 🎨 Features Overview

### Send Mode
- 📁 Select any file from your device
- 👀 See all available devices on your network
- 📊 Real-time upload progress
- ✅ Success/error notifications

### Receive Mode
- 📥 Automatically receive files from other devices
- 📋 View list of all received files
- 💾 Download files to your device
- 📊 See file size and timestamp

### Device Discovery
- 🔍 Automatic discovery of devices on LAN
- 🔄 Real-time updates when devices join/leave
- 💻 Shows device name and IP address
- ⚡ Fast and efficient using UDP broadcast

---

## 🔧 Configuration

### Change Backend Port
Edit `backend/app.py`:
```python
socketio.run(app, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

### Change Frontend API URL
Create `frontend/.env`:
```
REACT_APP_API_URL=http://your-server:5000
```

### Change Upload Directory
Edit `backend/app.py`:
```python
UPLOAD_FOLDER = 'uploads'  # Change to your preferred directory
```

---

## 🏗️ Building for Production

### Backend
The backend runs the same in development and production:
```bash
cd backend
python app.py
```

### Frontend
Build optimized production files:
```bash
cd frontend
npm run build
```

Serve the built files:
```bash
npm install -g serve
serve -s build -p 3000
```

Or use the backend to serve frontend:
Copy `frontend/build/*` to `backend/static/` and configure Flask to serve static files.

---

## 📚 Next Steps

- [ ] Read the full [README.md](README.md) for detailed documentation
- [ ] Check the [API.md](API.md) for API documentation
- [ ] Test file transfers between multiple devices
- [ ] Customize the UI colors and styling
- [ ] Wait for Phase 2: Hand gesture file sharing!

---

## 💡 Tips

1. **Keep both devices on the same network**: Device discovery only works on LAN
2. **Firewall**: Make sure ports 5000 and 12346 are allowed
3. **File size**: Large files work fine but may take time depending on network speed
4. **Multiple files**: You can send files one at a time
5. **Browser compatibility**: Works best on modern browsers (Chrome, Firefox, Safari, Edge)

---

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review the [API.md](API.md) for API details
- Open an issue on GitHub
- Make sure all prerequisites are installed

---

## 🎉 Enjoy LinkBeam!

You're all set! Start sharing files seamlessly on your local network.
