# Hamro Aawaz

A citizen-municipality collaboration platform for Nepal.

## Features

- 🔔 Priority-based complaint system
- 🏛️ Municipality activity tracking
- 🗣️ Bilingual support (नेपाली / English)
- 📊 Municipality performance leaderboard
- 🔒 Secure authentication system

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- Database: JSON-based storage
- Authentication: JWT tokens

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/rewqeas/hamro_awaz.git
cd hamro_awaz
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend:
```bash
cd backend
uvicorn main:app --reload
```

4. Run the frontend:
```bash
cd frontend
streamlit run streamlit_login.py
```

## Project Structure

```
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── data/ # JSON-based storage
│ │ ├── complains.json
│ │ ├── municipality.json
│ │ └── users.json
│ ├── routes/ # API endpoints
│ │ ├── auth.py
│ │ ├── complaints.py
│ │ └── municipality.py
│ ├── uploads/ # Uploaded files (organized per module)
│ │ ├── complaints/
│ │ └── municipality/
│ └── utils/ # Helper utilities
│ ├── auth_utils.py
│ ├── file_handler.py
│ ├── security.py
│ └── dependency.py
│
├── frontend/
│ └── streamlit_login.py # Streamlit-based demo frontend
│
├── tests/ # Test cases
│
├── venv/ # Virtual environment
│
├── pytest.ini # Pytest configuration
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── SECURITY.md # Security guidelines
└── sonar-project.properties # SonarQube configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with ❤️ for Nepal's communities

- Powered by FastAPI and Streamlit

