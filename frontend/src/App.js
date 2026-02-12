import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [mode, setMode] = useState('send');
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [socket, setSocket] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    // API_URL is from process.env and is static, safe to omit from deps
    // Fetch device info
    axios.get(`${API_URL}/api/device/info`)
      .then(response => {
        setDeviceInfo(response.data);
      })
      .catch(error => {
        console.error('Error fetching device info:', error);
      });

    // Initialize socket connection
    const newSocket = io(API_URL);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      newSocket.emit('request_devices');
    });

    newSocket.on('device_discovered', (device) => {
      setDevices(prev => {
        const exists = prev.find(d => d.device_id === device.device_id);
        if (!exists) {
          return [...prev, device];
        }
        return prev;
      });
    });

    newSocket.on('devices_list', (devicesList) => {
      setDevices(devicesList);
    });

    newSocket.on('device_lost', (data) => {
      setDevices(prev => prev.filter(d => d.device_id !== data.device_id));
    });

    // Fetch available files
    fetchFiles();

    // Refresh devices every 10 seconds
    const interval = setInterval(() => {
      newSocket.emit('request_devices');
      fetchFiles();
    }, 10000);

    return () => {
      clearInterval(interval);
      newSocket.disconnect();
    };
  }, []);

  const fetchFiles = () => {
    axios.get(`${API_URL}/api/files`)
      .then(response => {
        setAvailableFiles(response.data);
      })
      .catch(error => {
        console.error('Error fetching files:', error);
      });
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setStatus(file ? `Selected: ${file.name}` : '');
  };

  const handleSendFile = async () => {
    if (!selectedFile) {
      setStatus('Please select a file first');
      return;
    }

    if (!selectedDevice) {
      setStatus('Please select a device');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setStatus('Uploading file...');
      const response = await axios.post(
        `http://${selectedDevice.ip}:5000/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadProgress(percentCompleted);
          },
        }
      );

      setStatus(`File sent successfully to ${selectedDevice.device_name}!`);
      setUploadProgress(0);
      setSelectedFile(null);
    } catch (error) {
      setStatus(`Error sending file: ${error.message}`);
      setUploadProgress(0);
    }
  };

  const handleDownloadFile = async (filename) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/download/${filename}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setStatus(`Downloaded: ${filename}`);
    } catch (error) {
      setStatus(`Error downloading file: ${error.message}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔗 LinkBeam</h1>
        <p className="subtitle">LAN File Sharing</p>
      </header>

      <div className="device-info">
        {deviceInfo && (
          <div>
            <strong>Your Device:</strong> {deviceInfo.device_name} | 
            <strong> IP:</strong> {deviceInfo.ip}
          </div>
        )}
      </div>

      <div className="mode-switcher">
        <button 
          className={mode === 'send' ? 'active' : ''}
          onClick={() => setMode('send')}
        >
          📤 Send
        </button>
        <button 
          className={mode === 'receive' ? 'active' : ''}
          onClick={() => setMode('receive')}
        >
          📥 Receive
        </button>
      </div>

      {mode === 'send' ? (
        <div className="send-mode">
          <h2>Send File</h2>
          
          <div className="file-selector">
            <input 
              type="file" 
              onChange={handleFileSelect}
              id="file-input"
            />
            <label htmlFor="file-input" className="file-input-label">
              {selectedFile ? selectedFile.name : 'Choose File'}
            </label>
          </div>

          <div className="devices-list">
            <h3>Available Devices ({devices.length})</h3>
            {devices.length === 0 ? (
              <p className="no-devices">No devices found. Make sure other devices are running LinkBeam.</p>
            ) : (
              <div className="devices-grid">
                {devices.map((device) => (
                  <div 
                    key={device.device_id}
                    className={`device-card ${selectedDevice?.device_id === device.device_id ? 'selected' : ''}`}
                    onClick={() => setSelectedDevice(device)}
                  >
                    <div className="device-icon">💻</div>
                    <div className="device-name">{device.device_name}</div>
                    <div className="device-ip">{device.ip}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button 
            className="send-button"
            onClick={handleSendFile}
            disabled={!selectedFile || !selectedDevice}
          >
            Send File
          </button>

          {uploadProgress > 0 && (
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
              <span className="progress-text">{uploadProgress}%</span>
            </div>
          )}
        </div>
      ) : (
        <div className="receive-mode">
          <h2>Receive Files</h2>
          <p className="receive-status">
            Ready to receive files. Share your IP with other devices.
          </p>

          <div className="received-files">
            <h3>Received Files ({availableFiles.length})</h3>
            {availableFiles.length === 0 ? (
              <p className="no-files">No files received yet.</p>
            ) : (
              <div className="files-list">
                {availableFiles.map((file, index) => (
                  <div key={index} className="file-item">
                    <div className="file-info">
                      <div className="file-icon">📄</div>
                      <div>
                        <div className="file-name">{file.filename}</div>
                        <div className="file-details">
                          {formatFileSize(file.size)} • {formatDate(file.modified)}
                        </div>
                      </div>
                    </div>
                    <button 
                      className="download-button"
                      onClick={() => handleDownloadFile(file.filename)}
                    >
                      ⬇️ Download
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {status && (
        <div className={`status-message ${status.includes('Error') ? 'error' : 'success'}`}>
          {status}
        </div>
      )}
    </div>
  );
}

export default App;
