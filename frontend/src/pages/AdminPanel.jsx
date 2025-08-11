import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState("addUser");
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [userForm, setUserForm] = useState({
    user_id: "",
    name: "",
    department: "",
    role: "",
    email: "",
    phone: "",
    face_file: null
  });

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Fetch users
  const fetchUsers = async () => {
    const res = await axios.get("http://localhost:8000/users");
    setUsers(res.data);
  };

  // Fetch logs
  const fetchLogs = async () => {
    const res = await axios.get("http://localhost:8000/logs");
    setLogs(res.data);
  };

  // Add user
  const handleAddUser = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    Object.keys(userForm).forEach((key) => {
      formData.append(key, userForm[key]);
    });

    await axios.post("http://localhost:8000/users", formData);
    alert("User added successfully!");
    fetchUsers();
  };

  // Delete user
  const handleDeleteUser = async (userId) => {
    await axios.delete(`http://localhost:8000/users/${userId}`);
    fetchUsers();
  };

  // Start camera for verification
  const startCamera = () => {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      videoRef.current.srcObject = stream;
    });
  };

  // Capture image and verify
  const captureAndVerify = async () => {
    const ctx = canvasRef.current.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, 300, 200);
    canvasRef.current.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("face_file", blob, "capture.jpg");
      const res = await axios.post("http://localhost:8000/verify_access", formData);
      alert(`Access ${res.data.status} for ${res.data.user_id}`);
    });
  };

  // Tab rendering
  const renderTab = () => {
    switch (activeTab) {
      case "addUser":
        return (
          <form onSubmit={handleAddUser}>
            <input placeholder="User ID" onChange={(e) => setUserForm({ ...userForm, user_id: e.target.value })} />
            <input placeholder="Name" onChange={(e) => setUserForm({ ...userForm, name: e.target.value })} />
            <input placeholder="Department" onChange={(e) => setUserForm({ ...userForm, department: e.target.value })} />
            <input placeholder="Role" onChange={(e) => setUserForm({ ...userForm, role: e.target.value })} />
            <input placeholder="Email" onChange={(e) => setUserForm({ ...userForm, email: e.target.value })} />
            <input placeholder="Phone" onChange={(e) => setUserForm({ ...userForm, phone: e.target.value })} />
            <input type="file" onChange={(e) => setUserForm({ ...userForm, face_file: e.target.files[0] })} />
            <button type="submit">Add User</button>
          </form>
        );
      case "viewUsers":
        return (
          <div>
            <button onClick={fetchUsers}>Refresh</button>
            <table>
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Name</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.user_id}>
                    <td>{u.user_id}</td>
                    <td>{u.name}</td>
                    <td>
                      <button onClick={() => handleDeleteUser(u.user_id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      case "verifyAccess":
        return (
          <div>
            <video ref={videoRef} autoPlay width="300" height="200" />
            <canvas ref={canvasRef} width="300" height="200" style={{ display: "none" }} />
            <div>
              <button onClick={startCamera}>Start Camera</button>
              <button onClick={captureAndVerify}>Verify</button>
            </div>
          </div>
        );
      case "viewLogs":
        return (
          <div>
            <button onClick={fetchLogs}>Refresh Logs</button>
            <ul>
              {logs.map((log, idx) => (
                <li key={idx}>
                  {log.timestamp} - {log.user_id} - {log.status}
                </li>
              ))}
            </ul>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <h1>Admin Panel</h1>
      <nav>
        <button onClick={() => setActiveTab("addUser")}>Add User</button>
        <button onClick={() => setActiveTab("viewUsers")}>View Users</button>
        <button onClick={() => setActiveTab("verifyAccess")}>Verify Access</button>
        <button onClick={() => setActiveTab("viewLogs")}>View Logs</button>
      </nav>
      <hr />
      {renderTab()}
    </div>
  );
}
