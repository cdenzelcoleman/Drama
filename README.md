# 🎬 Drama - Social Movie Picker

A Django-based social movie discovery and gaming platform where users can challenge friends, discover movies, and play interactive games.

## ✨ Features

- **🎯 Movie Challenges**: Challenge friends to movie-picking games
- **🎮 Interactive Games**: Taps and Shake games with leaderboards
- **🎬 Movie Discovery**: Browse and discover movies using TMDB API
- **👥 Social Features**: Friend requests, user profiles, and notifications
- **📱 Mobile-First Design**: Responsive design optimized for mobile devices
- **👤 User Profiles**: Avatar uploads and customizable profiles

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Django 5.2
- TMDB API Key (get from [themoviedb.org](https://www.themoviedb.org/settings/api))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Drama
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your TMDB API key and other settings.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## 🏗️ Project Structure

```
Drama/
├── drama/                  # Main project settings
│   ├── settings.py         # Development settings
│   ├── settings_prod.py    # Production settings
│   └── urls.py
├── accounts/               # User authentication & profiles
├── movies/                 # Movie discovery & challenges
├── games/                  # Interactive games (Taps & Shake)
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads (avatars)
└── requirements.txt        # Python dependencies
```

## 🎮 Game Features

### Taps Game
- Tap as fast as you can in 10 seconds
- Leaderboard tracking
- Real-time score updates

### Shake Game
- Shake your mobile device rapidly
- Motion sensor detection
- Mobile-optimized gameplay

## 🎬 Movie Features

- **Discovery**: Browse popular and trending movies
- **Challenges**: Challenge friends to pick movies
- **Favorites**: Save favorite movies
- **Social**: Share movie preferences with friends

## 👥 Social Features

- **User Profiles**: Customizable profiles with avatar uploads
- **Friends System**: Send and accept friend requests
- **Challenges**: Create movie-picking challenges
- **Notifications**: Real-time challenge updates

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TMDB_API_KEY=your-tmdb-api-key
DATABASE_URL=postgresql://user:pass@localhost:5432/drama_db  # For production
```

### TMDB API Setup

1. Create account at [themoviedb.org](https://www.themoviedb.org)
2. Go to Settings → API
3. Generate API key
4. Add to your `.env` file

## 🚀 Deployment

### Heroku Deployment

1. **Install Heroku CLI**

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DJANGO_SETTINGS_MODULE=drama.settings_prod
   heroku config:set TMDB_API_KEY=your-api-key
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Manual Deployment

1. **Use production settings**
   ```bash
   export DJANGO_SETTINGS_MODULE=drama.settings_prod
   ```

2. **Run deployment script**
   ```bash
   ./deploy.sh
   ```

3. **Start with Gunicorn**
   ```bash
   gunicorn drama.wsgi --bind 0.0.0.0:8000
   ```

## 📱 Mobile Features

- **Responsive Design**: Works on all screen sizes
- **Touch Optimized**: Mobile-first touch interactions
- **Motion Sensors**: Shake game uses device motion
- **PWA Ready**: Can be installed as a mobile app

## 🛠️ Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

```bash
python manage.py check --deploy
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
```

## 📊 Admin Interface

Access the admin interface at `/admin/` with your superuser credentials to:

- Manage users and profiles
- View game results
- Monitor movie data
- Manage friend relationships

## 🔒 Security Features

- CSRF protection
- XSS protection
- Secure session handling
- Content type validation
- HSTS for HTTPS deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the admin interface for errors
2. Review Django logs
3. Ensure TMDB API key is valid
4. Verify all environment variables are set

## 🎯 Future Enhancements

- Real-time multiplayer games
- Movie recommendations AI
- Social media integration
- Advanced analytics
- Mobile app (React Native)
- WebSocket real-time features

---

Built with ❤️ using Django, TMDB API, and modern web technologies.