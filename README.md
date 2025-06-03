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

## 📊 Admin Interface

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