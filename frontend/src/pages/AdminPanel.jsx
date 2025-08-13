import React, { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState("addUser");
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editUserId, setEditUserId] = useState(null);
  const [userForm, setUserForm] = useState({
    user_id: "",
    name: "",
    department: "",
    role: "",
    email: "",
    phone: "",
    face_file: null
  });
  const [reportText, setReportText] = useState("");
  const [todayReportText, setTodayReportText] = useState("");
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const logIntervalRef = useRef(null);
  const cameraIntervalRef = useRef(null);
  const cameraStreamRef = useRef(null);
  const fetchUsers = async () => {
    const res = await axios.get("http://localhost:8000/users");
    const todayStr = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    const usersWithAttendance = res.data.map(user => ({
      ...user,
      attendance_today: user.last_verified_date === todayStr
    }));
    setUsers(usersWithAttendance);
  };
  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/logs");
      setLogs(res.data);
    } catch (err) {
      console.error("Error fetching logs:", err);
    }
  };
  React.useEffect(() => {
    fetchUsers();
  }, []);
  React.useEffect(() => {
    if (activeTab === "viewLogs") {
      fetchLogs();
      logIntervalRef.current = setInterval(fetchLogs, 3000);
    }
    return () => {
      if (logIntervalRef.current){
        clearInterval(logIntervalRef.current);
        logIntervalRef.current = null;
      }
    };
  }, [activeTab]);

  const fetchReport = async () => {
    try {
      const res = await axios.get("http://localhost:8000/report");
      setReportText(res.data.report || "No report available");
    } catch (err) {
      setReportText("Failed to fetch report");
    }
  };

  const fetchTodayReport = async () => {
    try {
      const res = await axios.get("http://localhost:8000/report/today");
      setTodayReportText(res.data.report || "No report available");
    } catch (err) {
      setTodayReportText("Failed to fetch today's report");
    }
  };
  const handleAddUser = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    Object.keys(userForm).forEach((key) => {
      formData.append(key, userForm[key]);
    });

    await axios.post("http://localhost:8000/users", formData);
    alert("User added successfully!");

    setUserForm({
      user_id: "",
      name: "",
      department: "",
      role: "",
      email: "",
      phone: "",
      face_file: null
    });

    fetchUsers();
  };


  const handleDeleteUser = async (userId) => {
    await axios.delete(`http://localhost:8000/users/${userId}`);
    fetchUsers();
  };
  const handleModifyUser = async (userId) => {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("name", userForm.name || "");
    formData.append("department", userForm.department || "");
    formData.append("role", userForm.role || "");
    formData.append("email", userForm.email || "");
    formData.append("phone", userForm.phone || "");
    if (userForm.face_file) {
      formData.append("face_file", userForm.face_file);
    }

    try {
      await axios.patch(`http://localhost:8000/users/${userId}`, formData);
      alert("User updated successfully!");
      fetchUsers(); // refresh instantly
    } catch (err) {
      alert("Failed to update user: " + err.response?.data?.detail);
    }
  };

  const startCamera = () => {
    if (cameraIntervalRef.current) return;

    let cancelled = false;
    videoRef.current.cancelCamera = () => { cancelled = true; };

    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (cancelled) {
          stream.getTracks().forEach(track => track.stop()); // stop right away
          return;
        }
        cameraStreamRef.current = stream; // store for stopping later
        videoRef.current.srcObject = stream;
        cameraIntervalRef.current = setInterval(captureAndVerify, 2000);
      })
      .catch(err => {
        console.error("Camera error:", err);
      });
  };

  const stopCamera = () => {
    if (videoRef.current?.cancelCamera) {
      videoRef.current.cancelCamera();
      delete videoRef.current.cancelCamera;
    }

    // Stop the stored stream if it exists
    if (cameraStreamRef.current) {
      cameraStreamRef.current.getTracks().forEach(track => track.stop());
      cameraStreamRef.current = null;
    }

    // Stop whatever is in videoRef as well
    const stream = videoRef.current?.srcObject;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }

    if (cameraIntervalRef.current) {
      clearInterval(cameraIntervalRef.current);
      cameraIntervalRef.current = null;
    }
  };

  React.useEffect(() => {
    if (activeTab === "verifyAccess") {
      startCamera();
    } else {
      stopCamera();
    }
  }, [activeTab]);
  const captureAndVerify = async () => {
    const ctx = canvasRef.current.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, 300, 200);
    canvasRef.current.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("face_file", blob, "capture.jpg");

      try {
        const res = await axios.post("http://localhost:8000/verify_access", formData);
        if (res.data.status === "granted") {
          alert(`✅ Access granted for ${res.data.user_id}`);

          setUsers(prevUsers =>
            prevUsers.map(user =>
              user.user_id === res.data.user_id
                ? { ...user, attendance_today: true, last_verified_date: new Date().toISOString().slice(0, 10)}
                : user
            )
          );

          clearInterval(cameraIntervalRef.current);
          cameraIntervalRef.current = null;
        } else {
          console.log("Access denied");
        }
      } catch (err) {
        console.error("Verification error:", err);
      }
    });
  };


  const renderTab = () => {
    switch (activeTab) {
      case "addUser":
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Add New User</h2>
            <form onSubmit={handleAddUser} className="grid gap-3">
              {["user_id", "name", "department", "role", "email", "phone"].map((field) => (
                <input
                  key={field}
                  value={userForm[field]}
                  placeholder={field.replace("_", " ").toUpperCase()}
                  className="border border-gray-300 rounded p-2 text-sm"
                  onChange={(e) => setUserForm({ ...userForm, [field]: e.target.value })}
                />
              ))}
              <input
                type="file"
                className="border border-gray-300 rounded p-2 text-sm"
                onChange={(e) => setUserForm({ ...userForm, face_file: e.target.files[0] })}
              />
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm"
              >
                Add User
              </button>
            </form>
          </div>
        );

      case "viewUsers":
        return (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Users</h2>
                <button
                    onClick={fetchUsers}
                    className="bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded text-sm"
                >
                  Refresh
                </button>
              </div>
              <table className="min-w-full border-collapse border border-gray-300">
                <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 px-4 py-2 text-center">User ID</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Name</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Phone</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Email</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Attendance</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Action</th>
                </tr>
                </thead>
                <tbody>
                {users.map((user) => (
                    <tr key={user.user_id}>
                      <td className="border border-gray-300 px-4 py-2 text-center">{user.user_id}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{user.name}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{user.phone}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{user.email}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {user.attendance_today ? (
                            <span className="text-green-500 text-lg">✔</span>
                        ) : (
                            ""
                        )}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        <div className="flex justify-center items-center space-x-2">
                          <button
                              onClick={() => handleDeleteUser(user.user_id)}
                              className="px-3 py-1 rounded-lg bg-red-100 text-red-600 font-medium hover:bg-red-200 transition"
                          >
                            Delete
                          </button>
                          <button
                              onClick={() => {
                                setEditUserId(user.user_id);
                                setUserForm({
                                  user_id: user.user_id,
                                  name: user.name || "",
                                  department: user.department || "",
                                  role: user.role || "",
                                  email: user.email || "",
                                  phone: user.phone || "",
                                  face_file: null
                                });
                                setIsEditing(true);
                              }}
                              className="px-3 py-1 rounded-lg bg-blue-100 text-blue-600 font-medium hover:bg-blue-200 transition"
                          >
                            Modify
                          </button>
                        </div>
                      </td>
                    </tr>
                ))}
                </tbody>
              </table>
              {isEditing && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
                    <div className="bg-white rounded-lg p-6 w-96 shadow-lg">
                      <h2 className="text-lg font-semibold mb-4">Edit User</h2>
                      <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            handleModifyUser(editUserId);
                            setIsEditing(false);
                          }}
                          className="grid gap-3"
                      >
                        {["name", "department", "role", "email", "phone"].map((field) => (
                            <input
                                key={field}
                                placeholder={field.replace("_", " ").toUpperCase()}
                          className="border border-gray-300 rounded p-2 text-sm"
                          value={userForm[field]}
                          onChange={(e) => setUserForm({ ...userForm, [field]: e.target.value })}
                        />
                      ))}
                      <input
                        type="file"
                        className="border border-gray-300 rounded p-2 text-sm"
                        onChange={(e) => setUserForm({ ...userForm, face_file: e.target.files[0] })}
                      />
                      <div className="flex justify-end space-x-2">
                        <button
                          type="button"
                          onClick={() => setIsEditing(false)}
                          className="bg-gray-200 px-4 py-2 rounded text-sm"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm"
                        >
                          Save
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
        );

      case "verifyAccess":
        return (
          <div className="flex flex-col items-center space-y-4">
            <video
              ref={videoRef}
              autoPlay
              width="300"
              height="200"
              className="border rounded"
            />
            <canvas
              ref={canvasRef}
              width="300"
              height="200"
              style={{ display: "none" }}
            />
            <div className="flex space-x-4">
              <button
                onClick={startCamera}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded shadow"
              >
                Start Camera
              </button>
              <button
                onClick={stopCamera}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded shadow"
              >
                Stop Camera
              </button>
            </div>
          </div>
        );

      case "viewLogs":
        return (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Access Logs</h2>
                <button
                    onClick={fetchLogs}
                    className="bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded text-sm"
                >
                  Refresh Logs
                </button>
              </div>
              <ul className="space-y-2 text-sm">
                {logs.map((log, idx) => (
                    <li key={idx} className="border-b pb-1">
                      <span className="font-medium">{log.user_id}</span> — {log.status} —{" "}
                      <span className="text-gray-500">{log.timestamp}</span>
                    </li>
              ))}
            </ul>
          </div>
        );
      case "report":
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Reports</h2>
            <div className="mb-6">
              <h3 className="font-medium mb-2">General Attendance Report</h3>
              <button
                  onClick={fetchReport}
                  className="mb-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm"
              >
                Get Monthly Report
              </button>
              <div className="bg-gray-50 p-4 rounded h-48 overflow-auto prose max-w-full">
                <ReactMarkdown>{reportText}</ReactMarkdown>
              </div>
            </div>

            <div>
              <h3 className="font-medium mb-2">Today's Attendance Report</h3>
              <button
                  onClick={fetchTodayReport}
                  className="mb-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm"
              >
                Get Today's Report
              </button>
              <div className="bg-gray-50 p-4 rounded h-48 overflow-auto prose max-w-full">
                <ReactMarkdown>{todayReportText}</ReactMarkdown>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
      <div className="min-h-screen bg-gray-100 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow fixed top-0 left-0 w-full z-50 flex items-center">
          {/* Logo */}
          <div className="pl-4">
            <img
                src="/uet-logo.png"
                alt="Logo"
                className="h-12 w-auto object-contain"
            />
          </div>

          {/* Title */}
          <h1 className="ml-4 text-lg font-semibold text-gray-900">
            Admin Panel
          </h1>
        </header>

        {/* Main */}
        <div className="flex flex-1 pt-16">
          {/* Sidebar */}
          <nav className="w-56 bg-white border-r p-4 space-y-2">
            {[
              { key: "addUser", label: "Add User" },
              { key: "viewUsers", label: "View Users" },
              { key: "verifyAccess", label: "Verify Access" },
              { key: "viewLogs", label: "View Logs" },
              { key: "report", label: "Report" }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`block w-full text-left px-3 py-2 rounded text-sm ${
                  activeTab === tab.key
                    ? "bg-indigo-100 text-indigo-700 font-medium"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Content Area */}
          <main className="flex-1 p-6">{renderTab()}</main>
        </div>
      </div>
  );
}
