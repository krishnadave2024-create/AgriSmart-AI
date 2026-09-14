import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Leaf, Eye, EyeOff } from 'lucide-react';

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    fullName: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    setLoading(true);
    
    const result = await register(
      formData.username, 
      formData.email, 
      formData.fullName, 
      formData.password,
      formData.confirmPassword
    );
    
    if (result.success) {
      navigate('/');
    } else {
      if (typeof result.error === 'object' && result.error !== null) {
        // Format object errors nicely (e.g. {"email": ["A user with that email already exists."]})
        const errorMessages = Object.entries(result.error)
          .map(([field, msgs]) => {
            const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ');
            const msg = Array.isArray(msgs) ? msgs[0] : msgs;
            return `${fieldName}: ${msg}`;
          })
          .join('\n');
        setError(errorMessages || 'Registration failed');
      } else {
        setError(result.error || 'Registration failed');
      }
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-forest-50 dark:bg-forest-950 p-4">
      <div className="max-w-md w-full bg-white dark:bg-forest-900 rounded-2xl shadow-agri-lg border border-forest-100 dark:border-forest-800 p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-forest-500 flex items-center justify-center mb-4">
            <Leaf size={24} className="text-forest-950" />
          </div>
          <h1 className="text-2xl font-bold text-forest-950 dark:text-white">Create Account</h1>
          <p className="text-forest-500 dark:text-forest-400 text-sm mt-1">Join AgriSmart AI today</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-red-50 text-red-600 text-sm border border-red-100 whitespace-pre-line">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Full Name</label>
            <input
              type="text"
              name="fullName"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all"
              value={formData.fullName}
              onChange={handleChange}
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Username</label>
            <input
              type="text"
              name="username"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all"
              value={formData.username}
              onChange={handleChange}
              placeholder="johndoe123"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Email Address</label>
            <input
              type="email"
              name="email"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all"
              value={formData.email}
              onChange={handleChange}
              placeholder="farmer@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all pr-10"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                minLength="8"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-forest-400 hover:text-forest-600"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Confirm Password</label>
            <input
              type={showPassword ? "text" : "password"}
              name="confirmPassword"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="••••••••"
              minLength="8"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-harvest-500 hover:bg-harvest-600 text-white font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed mt-4"
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-forest-600 dark:text-forest-400">
          Already have an account?{' '}
          <Link to="/login" className="text-harvest-500 hover:text-harvest-600 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
