import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Leaf, Eye, EyeOff } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    const result = await login(username, password);
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
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
          <h1 className="text-2xl font-bold text-forest-950 dark:text-white">Welcome Back</h1>
          <p className="text-forest-500 dark:text-forest-400 text-sm mt-1">Sign in to your AgriSmart account</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-red-50 text-red-600 text-sm border border-red-100">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Username</label>
            <input
              type="text"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="farmer123"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none transition-all pr-10"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
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

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-harvest-500 hover:bg-harvest-600 text-white font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-forest-600 dark:text-forest-400">
          Don't have an account?{' '}
          <Link to="/register" className="text-harvest-500 hover:text-harvest-600 font-medium">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}
