
# Attendance Access Control System

A comprehensive attendance and access control system featuring face recognition, Kafka-based logging, and AI-powered attendance reports.

---

## Features

- User management (add, modify, delete users)
- Real-time face recognition for access verification
- Kafka-based logging of access events
- AI-generated attendance reports with LLM integration
- Frontend admin panel for user management and reports
- Automatic email notifications for verified attendance

---

## Tech Stack

- **Backend:** FastAPI, MySQL, InsightFace (face recognition), Kafka, Python  
- **Frontend:** React, Axios, Tailwind CSS  
- **AI:** Google Gemini API (or other LLM services)  
- **Messaging:** Kafka for event streaming  
- **Email:** SMTP with app passwords for notifications  

---

## Getting Started

### Prerequisites

- Python 3.10+  
- Node.js 16+  
- MySQL Server  
- Kafka Broker  
- Google Gemini API key (or compatible LLM API key)  
- SMTP email account with app password (for sending notifications)  

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/attendance-access-control.git
   cd attendance-access-control
   ```

2. **Backend Setup**

   - Configure your environment variables or config files with credentials, including:
     - Database connection info
     - Kafka broker address
     - Email SMTP username and app password
     - LLM API key

   - Install backend dependencies:

     ```bash
     cd backend
     pip install -r requirements.txt
     ```

   - Run backend server:

     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000 --reload
     ```

3. **Frontend Setup**

   - Install frontend dependencies:

     ```bash
     cd frontend
     npm install
     ```

   - Run frontend server:

     ```bash
     npm start
     ```

4. **Kafka**

   - Ensure Kafka broker is running and accessible based on your configuration.

---

## Usage

- Open the frontend admin panel at [http://localhost:3000](http://localhost:3000)
- Manage users: add, edit, delete
- Use the camera interface to verify access by face recognition
- View logs and attendance reports
- Verified users will receive automatic attendance notification emails once per day

---

## Project Structure

```
attendance-access-control/
├── backend/          # FastAPI backend code and services
├── frontend/         # React admin panel frontend
├── config/           # Configuration files (credentials, keys)
├── scripts/          # Utility scripts (e.g., DB migrations, deployments)
├── docs/             # Project documentation and API specs
└── README.md         # Project overview and instructions
```

---

## Environment Configuration

Store sensitive credentials securely in the `config` folder or use environment variables, including:

- Email SMTP username and app password (for sending notifications)
- Google Gemini or other LLM API keys
- Database credentials
- Kafka broker URL

---

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

---

## License

MIT License

---

## Contact

For questions or support, please contact [your-email@example.com].
