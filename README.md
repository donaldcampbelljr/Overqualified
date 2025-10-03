# Overqualified 🎭
An absurd resume generator that creates overqualified fictional resumes using AI

## 🚀 Features

- **AI-Powered Generation**: Uses Google's Gemini API to create unique, absurd fictional resumes
- **Fallback System**: Displays cached fictional resumes when API key is not available

## 🛠️ Tech Stack

- **Frontend**: React 18, Tailwind CSS
- **Backend**: Python Flask, Google Gemini API
- **Infrastructure**: Docker, Docker Compose
- **Styling**: Tailwind CSS (loaded via CDN)

## 📦 Quick Start

### Prerequisites
- Docker and Docker Compose installed on your system
- (Optional) Google Gemini API key for AI-generated resumes

### 1. Clone the Repository
```bash
git clone https://github.com/donaldcampbelljr/Overqualified.git
cd Overqualified
```

### 2. Set Up Environment (Optional)
If you want AI-generated resumes, edit `docker-compose.yml` and uncomment the GEMINI_API_KEY line:
```yaml
environment:
  GEMINI_API_KEY: "your_actual_api_key_here"
```

**Note**: If you don't provide an API key, the app will automatically serve cached fictional resumes instead!

### 3. Build and Run
```bash
docker-compose up --build
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 🎯 Usage

1. Open your browser to `http://localhost:3000`
2. Click "Generate New Fictional Resume" to get a random resume
3. Each refresh or button click will show a different absurd professional profile
4. If the API key is not configured, you'll see one of the pre-made cached resumes

## 🐛 Troubleshooting

**Frontend can't connect to backend:**
- Ensure both containers are running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`

**API key issues:**
- Verify your API key in `docker-compose.yml`

**Docker issues:**
- Rebuild containers: `docker-compose down && docker-compose up --build`
- Clear Docker cache: `docker system prune`

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## Final Note

This is for fun, please don't use these to apply to real jobs.
