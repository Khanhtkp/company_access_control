import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function AdminPanel() {
    const [formData, setFormData] = useState({
        user_id: "",
        name: "",
        department: "",
        role: "",
        email: "",
        phone: "",
    });

    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSubmit = async () => {
        setLoading(true);
        const res = await fetch("http://localhost:8000/add_user", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(formData),
        });
        const data = await res.json();
        alert(data.message);
        setFormData({user_id: "", name: "", department: "", role: "", email: "", phone: ""});
        fetchUsers();
        setLoading(false);
    };

    const fetchUsers = async () => {
        const res = await fetch("http://localhost:8000/list_users");
        const data = await res.json();
        setUsers(data);
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    return (
        <div className="p-4 grid grid-cols-1 gap-4 max-w-xl mx-auto">
            <Card>
                <CardContent className="space-y-4 p-6">
                    <h2 className="text-xl font-semibold">Thêm người dùng</h2>
                    {Object.keys(formData).map((key) => (
                        <div key={key} className="space-y-1">
                            <Label htmlFor={key}>{key}</Label>
                            <Input id={key} name={key} value={formData[key]} onChange={handleChange}/>
                        </div>
                    ))}
                    <Button onClick={handleSubmit} disabled={loading}>
                        {loading ? "Đang thêm..." : "Thêm người dùng"}
                    </Button>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Danh sách người dùng</h2>
                    <div className="space-y-2">
                        {users.map((user) => (
                            <div key={user.user_id} className="border p-2 rounded shadow">
                                <strong>{user.name}</strong> ({user.user_id}) - {user.email}
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}