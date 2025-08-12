
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

- Docker and Docker Compose installed
- Google Gemini API key (or compatible LLM API key)  
- SMTP email account with app password (for sending notifications)  

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/Khanhtkp/company-access-control.git
   cd company-access-control
   ```

2. **Configure environment variables**

  Fill at `.env` file inside the `config/` folder with the following variables:

   ```dotenv
   # config/.env
   SMTP_USERNAME=your_email@example.com
   SMTP_PASSWORD=your_email_app_password
   LLM_API_KEY=your_llm_api_key
   ```

3. **Run with Docker Compose**

   The project includes a `docker-compose.yml` at the root to run all services (backend, frontend, MySQL, Kafka) together:

   ```bash
   docker-compose up --build
   ```

4. **Access services**

   - Frontend Admin Panel: [http://localhost:3000](http://localhost:5173)  
   - Backend API: [http://localhost:8000](http://localhost:8000)  
   - Kafka and MySQL run inside the Docker network and are accessible to backend

---

## Usage

- Manage users via the frontend
- Use camera interface to verify access with face recognition
- View logs and attendance reports
- Verified users receive automatic attendance notification emails once per day

---

## Project Structure

```
attendance-access-control/
├── backend/          # FastAPI backend code and Dockerfile
├── frontend/         # React admin panel frontend and Dockerfile
├── config/           # Configuration files (credentials, .env)
├── docker-compose.yml# Docker Compose file for running all services
└── README.md         # Project overview and instructions
```

---

## Environment Configuration

- Store sensitive credentials securely in `config/.env`  
- Docker Compose will load these variables for backend and frontend services  
- Make sure to **never commit `.env`** with real credentials to public repos

---

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

---

## License

MIT License

---

## Contact

For questions or support, please contact [merikatori02@gmail.com].
