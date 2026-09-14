import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { User, Loader2 } from 'lucide-react';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('profile/');
        setProfile(res.data.profile);
      } catch (error) {
        setMessage({ type: 'error', text: 'Failed to load profile data.' });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleProfileChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      await api.put('profile/', profile);
      setMessage({ type: 'success', text: 'Profile saved successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save profile.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin text-harvest-500" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-forest-900 dark:text-white">Account Profile</h1>
        <p className="text-forest-600 dark:text-forest-400 mt-1">Manage your personal details</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl border ${message.type === 'success' ? 'bg-green-50 border-green-100 text-green-700' : 'bg-red-50 border-red-100 text-red-600'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white dark:bg-forest-900 rounded-2xl border border-forest-100 dark:border-forest-800 overflow-hidden">
          <div className="p-4 bg-forest-50 dark:bg-forest-950 border-b border-forest-100 dark:border-forest-800 flex items-center gap-3">
            <User size={20} className="text-forest-600 dark:text-forest-400" />
            <h2 className="font-semibold text-forest-900 dark:text-white">Personal Information</h2>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Email Address</label>
              <input
                type="email"
                disabled
                value={profile?.user?.email || ''}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-forest-50 dark:bg-forest-950 text-forest-500 cursor-not-allowed outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Username</label>
              <input
                type="text"
                disabled
                value={profile?.user?.username || ''}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-forest-50 dark:bg-forest-950 text-forest-500 cursor-not-allowed outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Full Name</label>
              <input
                type="text"
                name="full_name"
                value={profile?.full_name || ''}
                onChange={handleProfileChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Preferred Language</label>
              <select
                name="preferred_language"
                value={profile?.preferred_language || 'en'}
                onChange={handleProfileChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              >
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="gu">Gujarati</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl bg-harvest-500 hover:bg-harvest-600 text-white font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  );
}
