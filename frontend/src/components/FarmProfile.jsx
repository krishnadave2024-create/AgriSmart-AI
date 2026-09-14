import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { MapPin, Loader2 } from 'lucide-react';

export default function FarmProfile() {
  const [farm, setFarm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const farmRes = await api.get('farm/');
        setFarm(farmRes.data.farm);
      } catch (error) {
        setMessage({ type: 'error', text: 'Failed to load farm data.' });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleFarmChange = (e) => {
    setFarm({ ...farm, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      await api.put('farm/', farm);
      setMessage({ type: 'success', text: 'Farm profile saved successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save farm profile.' });
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
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-forest-900 dark:text-white">Farm Profile</h1>
        <p className="text-forest-600 dark:text-forest-400 mt-1">Manage your farm details</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl border ${message.type === 'success' ? 'bg-green-50 border-green-100 text-green-700' : 'bg-red-50 border-red-100 text-red-600'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white dark:bg-forest-900 rounded-2xl border border-forest-100 dark:border-forest-800 overflow-hidden">
          <div className="p-4 bg-forest-50 dark:bg-forest-950 border-b border-forest-100 dark:border-forest-800 flex items-center gap-3">
            <MapPin size={20} className="text-forest-600 dark:text-forest-400" />
            <h2 className="font-semibold text-forest-900 dark:text-white">Farm Details</h2>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Farm Name</label>
              <input
                type="text"
                name="farm_name"
                value={farm?.farm_name || ''}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Location</label>
              <input
                type="text"
                name="location"
                value={farm?.location || ''}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">State</label>
              <input
                type="text"
                name="state"
                value={farm?.state || ''}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Country</label>
              <input
                type="text"
                name="country"
                value={farm?.country || 'India'}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Farm Area</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  step="0.1"
                  name="farm_area"
                  value={farm?.farm_area || ''}
                  onChange={handleFarmChange}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
                />
                <select
                  name="area_unit"
                  value={farm?.area_unit || 'acres'}
                  onChange={handleFarmChange}
                  className="w-32 px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
                >
                  <option value="acres">Acres</option>
                  <option value="hectares">Hectares</option>
                  <option value="sq_meters">Sq Meters</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Soil Type</label>
              <select
                name="soil_type"
                value={farm?.soil_type || ''}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              >
                <option value="">Select Soil Type</option>
                <option value="Clay">Clay</option>
                <option value="Sandy">Sandy</option>
                <option value="Silty">Silty</option>
                <option value="Loam">Loam</option>
                <option value="Peaty">Peaty</option>
                <option value="Saline">Saline</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Irrigation Method</label>
              <select
                name="irrigation_method"
                value={farm?.irrigation_method || ''}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
              >
                <option value="">Select Method</option>
                <option value="Drip">Drip</option>
                <option value="Sprinkler">Sprinkler</option>
                <option value="Surface">Surface</option>
                <option value="Manual">Manual</option>
                <option value="Rainfed">Rainfed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-forest-700 dark:text-forest-300 mb-1.5">Main Crops</label>
              <input
                type="text"
                name="main_crops"
                value={farm?.main_crops || ''}
                onChange={handleFarmChange}
                className="w-full px-4 py-2.5 rounded-xl border border-forest-200 dark:border-forest-700 bg-white dark:bg-forest-950 text-forest-900 dark:text-white focus:ring-2 focus:ring-harvest-500 outline-none"
                placeholder="e.g. Wheat, Rice, Cotton"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl bg-harvest-500 hover:bg-harvest-600 text-white font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Farm Profile'}
          </button>
        </div>
      </form>
    </div>
  );
}
