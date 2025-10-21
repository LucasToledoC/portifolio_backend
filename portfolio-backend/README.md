# Portfolio Backend API

A Flask-based REST API for managing a developer's portfolio, including projects, certificates, and visit tracking. The backend uses Supabase (PostgreSQL) as the database and includes a web-based CRUD admin interface.

## Features

- **Projects Management**: Create, read, update, and delete portfolio projects
- **Certificates Management**: Manage academic and course certificates with filtering by origin
- **Visit Tracking**: Track total visits to the portfolio
- **Admin CRUD Interface**: Web-based interface for managing data without direct database access
- **RESTful API**: Clean, well-documented endpoints for the frontend to consume
- **Authentication**: Simple password-based authentication for admin operations
- **CORS Support**: Enabled for cross-origin requests from the frontend

## Project Structure

```
portfolio-backend/
├── app.py                 # Main Flask API application
├── admin.py              # Admin CRUD interface
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── templates/           # HTML templates for admin interface
│   ├── login.html
│   └── admin_dashboard.html
├── static/              # Static files for admin interface
│   ├── css/
│   └── js/
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Supabase account and project

### Setup Steps

1. **Clone the repository** (or navigate to the backend directory)
   ```bash
   cd portfolio-backend
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ADMIN_PASSWORD=your_secure_password
   ```

5. **Set up Supabase database** (see Database Setup section below)

## Database Setup

### Create Tables in Supabase

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor and run the following SQL:

```sql
-- Create projetos table
CREATE TABLE projetos (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  titulo VARCHAR(255) NOT NULL,
  descricao TEXT NOT NULL,
  tecnologias TEXT NOT NULL,
  link_github VARCHAR(255),
  link_deploy VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create certificados table
CREATE TABLE certificados (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  nome VARCHAR(255) NOT NULL,
  instituicao VARCHAR(255) NOT NULL,
  origem VARCHAR(100),
  data_conclusao DATE NOT NULL,
  link_certificado VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create visitas table
CREATE TABLE visitas (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  total BIGINT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Running the Application

### Development

**Start the main API server:**
```bash
python app.py
```
The API will be available at `http://localhost:5000`

**Start the admin interface (in another terminal):**
```bash
python admin.py
```
The admin panel will be available at `http://localhost:5001/admin`

### Production

Use Gunicorn to run the application:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check

- **GET** `/health` - Check if API is running

### Projects

- **GET** `/api/projetos` - Get all projects
- **POST** `/api/projetos` - Create a new project (requires auth)
- **GET** `/api/projetos/<id>` - Get a specific project
- **PUT** `/api/projetos/<id>` - Update a project (requires auth)
- **DELETE** `/api/projetos/<id>` - Delete a project (requires auth)

### Certificates

- **GET** `/api/certificados` - Get all certificates
- **GET** `/api/certificados?origem=<name>` - Get certificates filtered by origin
- **POST** `/api/certificados` - Create a new certificate (requires auth)
- **GET** `/api/certificados/<id>` - Get a specific certificate
- **PUT** `/api/certificados/<id>` - Update a certificate (requires auth)
- **DELETE** `/api/certificados/<id>` - Delete a certificate (requires auth)

### Visits

- **GET** `/api/visitas` - Get total visit count
- **POST** `/api/visitas` - Increment visit counter

## Authentication

Protected endpoints require an `Authorization` header with the format:
```
Authorization: Bearer <admin_password>
```

Example using curl:
```bash
curl -X POST http://localhost:5000/api/projetos \
  -H "Authorization: Bearer your_admin_password" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "My Project", "descricao": "...", "tecnologias": "React, Node.js"}'
```

## Admin Interface

Access the admin panel at `http://localhost:5001/admin` and log in with your configured admin password. From there, you can:

- View all projects and certificates
- Create new projects and certificates
- Edit existing entries
- Delete entries
- Filter certificates by origin

## Deployment

### Render (Recommended for Flask)

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables in Render dashboard
5. Deploy

### Railway

1. Install Railway CLI
2. Connect your GitHub account
3. Run `railway init` and follow prompts
4. Set environment variables
5. Deploy with `railway up`

### Heroku (Legacy)

1. Install Heroku CLI
2. Run `heroku create` and `heroku config:set` for environment variables
3. Deploy with `git push heroku main`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Your Supabase API key | `eyJhbGc...` |
| `ADMIN_PASSWORD` | Password for admin operations | `secure_password_123` |
| `FLASK_ENV` | Flask environment | `development` or `production` |
| `FLASK_DEBUG` | Enable Flask debug mode | `True` or `False` |

## Testing

To test the API endpoints, you can use tools like:

- **Postman** - GUI for API testing
- **curl** - Command-line tool
- **Thunder Client** - VS Code extension

Example test request:
```bash
# Get all projects
curl http://localhost:5000/api/projetos

# Create a project
curl -X POST http://localhost:5000/api/projetos \
  -H "Authorization: Bearer admin123" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Portfolio Website",
    "descricao": "A modern portfolio website",
    "tecnologias": "React, Tailwind CSS",
    "link_github": "https://github.com/...",
    "link_deploy": "https://portfolio.com"
  }'
```

## Security Considerations

1. **Change the default admin password** in production
2. **Use environment variables** for sensitive data (never hardcode)
3. **Enable HTTPS** in production
4. **Implement rate limiting** for public endpoints
5. **Validate and sanitize** all user inputs
6. **Use strong Supabase API keys** with appropriate permissions
7. **Regularly update dependencies** for security patches

## Troubleshooting

### "ModuleNotFoundError: No module named 'supabase'"
- Make sure you've installed dependencies: `pip install -r requirements.txt`

### "Connection refused" when connecting to Supabase
- Check your `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Verify your Supabase project is active

### Admin interface not loading
- Make sure `admin.py` is running on port 5001
- Check browser console for errors
- Verify templates are in the correct directory

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue in the repository or contact the maintainer.

