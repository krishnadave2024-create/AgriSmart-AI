import os
import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

# Add states in TopNav
if 'const [notifications, setNotifications] = useState([])' not in c:
    c = c.replace('const [showNotif, setShowNotif] = useState(false)',
                  'const [showNotif, setShowNotif] = useState(false)\n  const [notifications, setNotifications] = useState([])\n  const [unreadCount, setUnreadCount] = useState(0)\n  const [weatherData, setWeatherData] = useState(null)\n  const [weatherLoading, setWeatherLoading] = useState(true)\n  const [weatherError, setWeatherError] = useState(null)')

# Add useEffect in TopNav
new_effect = """
  useEffect(() => {
    if (user) {
      fetchNotifications();
      fetchWeather();
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      if (res.data.success) {
        setNotifications(res.data.notifications);
        setUnreadCount(res.data.unread_count);
      }
    } catch (err) {
      console.error('Failed to fetch notifications');
    }
  };

  const fetchWeather = async () => {
    setWeatherLoading(true);
    setWeatherError(null);
    try {
      const res = await api.get('/weather/navbar/');
      if (res.data.success) {
        setWeatherData(res.data);
      } else {
        setWeatherError(res.data.error || 'Weather unavailable');
      }
    } catch (err) {
      setWeatherError('Weather unavailable');
    } finally {
      setWeatherLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.post(`/notifications/${id}/read/`);
      fetchNotifications();
    } catch (err) {}
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/read-all/');
      fetchNotifications();
    } catch (err) {}
  };
"""
if 'const fetchNotifications = async () => {' not in c:
    c = c.replace('const initials = getInitials(user?.full_name, user?.username);', new_effect + '\n  const initials = getInitials(user?.full_name, user?.username);')

# Replace breadcrumb
c = re.sub(
    r'\{\/\* Breadcrumb demo \*\/\}.*?<span>Overview</span>\s*</div>',
    '{/* Breadcrumb */}\n      <div className="hidden sm:flex items-center gap-1.5 text-sm text-forest-500 dark:text-forest-400 font-medium">\n        <Leaf size={14} className="text-forest-600 dark:text-forest-400" />\n        <span className="text-forest-700 dark:text-forest-300">{displayFarmName}</span>\n      </div>',
    c, flags=re.DOTALL
)

# Replace weather badge
weather_badge_replacement = """
      {/* Weather badge */}
      <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-1.5 rounded-lg bg-forest-50 dark:bg-forest-900 border border-forest-200 dark:border-forest-700 text-xs text-forest-700 dark:text-forest-300 font-medium">
        {weatherLoading ? (
            <span>Loading...</span>
        ) : weatherError ? (
            <span className="text-red-500">{weatherError === 'Farm city not set.' ? 'Set farm city' : 'Weather unavailable'}</span>
        ) : weatherData ? (
            <>
                <span>{weatherData.temp.toFixed(1)}°C</span>
                <span className="capitalize hidden lg:inline">· {weatherData.description}</span>
            </>
        ) : (
            <span>Unavailable</span>
        )}
      </div>
"""
c = re.sub(
    r'\{\/\* Weather demo badge \*\/\}.*?</div>',
    weather_badge_replacement.strip(),
    c, flags=re.DOTALL
)

# Replace Notifications
notif_replacement = """
        {/* Notifications */}
        <button 
          className="p-2 rounded-lg text-forest-600 dark:text-forest-400 hover:bg-forest-100 dark:hover:bg-forest-800 relative" 
          aria-label="Open notifications"
          onClick={() => setShowNotif(!showNotif)}
        >
          <Bell size={18} />
          {unreadCount > 0 && <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />}
        </button>

        {showNotif && (
          <div className="absolute top-12 right-10 w-80 bg-white dark:bg-forest-900 border border-forest-100 dark:border-forest-700 rounded-xl shadow-agri-md p-4 z-50 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold text-forest-900 dark:text-forest-100">Notifications</h3>
              {unreadCount > 0 && (
                  <button onClick={markAllAsRead} className="text-xs text-forest-600 dark:text-forest-400 hover:underline">Mark all read</button>
              )}
            </div>
            <ul className="space-y-2 text-sm text-forest-700 dark:text-forest-300">
              {notifications.length === 0 ? (
                  <li className="text-center py-4 text-forest-500 dark:text-forest-400">You're all caught up</li>
              ) : (
                  notifications.map(n => (
                      <li key={n.id} onClick={() => { if(!n.is_read) markAsRead(n.id); }} className={`p-2 rounded-lg border-l-4 cursor-pointer ${n.is_read ? 'bg-transparent border-gray-300 dark:border-gray-700 opacity-70' : 'bg-forest-50 dark:bg-forest-950 border-forest-500'}`}>
                          <div className="font-semibold">{n.title}</div>
                          <div className="text-xs mt-0.5">{n.message}</div>
                      </li>
                  ))
              )}
            </ul>
          </div>
        )}
"""

c = re.sub(
    r'\{\/\* Notifications \*\/\}.*?\{\/\* Theme toggle \*\/\}',
    notif_replacement.strip() + '\n\n        {/* Theme toggle */}',
    c, flags=re.DOTALL
)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(c)

print("App.jsx updated")
