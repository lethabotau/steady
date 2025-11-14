import React, { useState } from 'react';
import { User, Target, Bell, Shield, LogOut, ChevronRight } from 'lucide-react';

interface ProfileScreenProps {
  weeklyGoal: number;
  onUpdateGoal: (goal: number) => void;
}

export function ProfileScreen({ weeklyGoal, onUpdateGoal }: ProfileScreenProps) {
  const [tempGoal, setTempGoal] = useState(weeklyGoal);
  const [notifications, setNotifications] = useState({
    insights: true,
    goals: true,
    weekly: false
  });

  const handleSaveGoal = () => {
    onUpdateGoal(tempGoal);
  };

  return (
    <div className="pb-20 px-6 pt-8" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-1" style={{ color: '#222' }}>Profile & Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ backgroundColor: '#F0F5F3' }}>
            <User size={32} style={{ color: '#1E4E40' }} />
          </div>
          <div>
            <p className="mb-1" style={{ color: '#222' }}>Alex Rodriguez</p>
            <p className="text-sm text-gray-500">San Francisco, CA</p>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
          <div>
            <p className="text-sm text-gray-500 mb-1">Joined</p>
            <p style={{ color: '#1E4E40' }}>Jan 2024</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Total Trips</p>
            <p style={{ color: '#1E4E40' }}>1,247</p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Rating</p>
            <p style={{ color: '#1E4E40' }}>4.92 ⭐</p>
          </div>
        </div>
      </div>

      {/* Weekly Goal */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Target size={20} style={{ color: '#E09447' }} />
          <h2 style={{ color: '#222' }}>Weekly Income Goal</h2>
        </div>
        <div className="mb-4">
          <div className="text-center mb-4">
            <div className="mb-1" style={{ color: '#1E4E40' }}>${tempGoal}</div>
            <p className="text-sm text-gray-500">per week</p>
          </div>
          <input
            type="range"
            min="400"
            max="2000"
            step="50"
            value={tempGoal}
            onChange={(e) => setTempGoal(Number(e.target.value))}
            className="w-full h-2 rounded-full appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #1E4E40 0%, #1E4E40 ${((tempGoal - 400) / 1600) * 100}%, #E5E5E5 ${((tempGoal - 400) / 1600) * 100}%, #E5E5E5 100%)`
            }}
          />
          <div className="flex justify-between text-sm text-gray-400 mt-2">
            <span>$400</span>
            <span>$2,000</span>
          </div>
        </div>
        {tempGoal !== weeklyGoal && (
          <button
            onClick={handleSaveGoal}
            className="w-full py-3 rounded-xl text-white transition-colors"
            style={{ backgroundColor: '#1E4E40' }}
          >
            Save Changes
          </button>
        )}
      </div>

      {/* Notifications */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Bell size={20} style={{ color: '#6CA58E' }} />
          <h2 style={{ color: '#222' }}>Notifications</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1" style={{ color: '#222' }}>New Insights</p>
              <p className="text-sm text-gray-500">Get notified of new earning tips</p>
            </div>
            <button
              onClick={() => setNotifications(prev => ({ ...prev, insights: !prev.insights }))}
              className="w-12 h-6 rounded-full transition-colors relative"
              style={{ backgroundColor: notifications.insights ? '#6CA58E' : '#E5E5E5' }}
            >
              <div
                className="w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform"
                style={{ transform: notifications.insights ? 'translateX(24px)' : 'translateX(2px)' }}
              />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1" style={{ color: '#222' }}>Goal Reminders</p>
              <p className="text-sm text-gray-500">Track your weekly progress</p>
            </div>
            <button
              onClick={() => setNotifications(prev => ({ ...prev, goals: !prev.goals }))}
              className="w-12 h-6 rounded-full transition-colors relative"
              style={{ backgroundColor: notifications.goals ? '#6CA58E' : '#E5E5E5' }}
            >
              <div
                className="w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform"
                style={{ transform: notifications.goals ? 'translateX(24px)' : 'translateX(2px)' }}
              />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1" style={{ color: '#222' }}>Weekly Summary</p>
              <p className="text-sm text-gray-500">Sunday evening recap email</p>
            </div>
            <button
              onClick={() => setNotifications(prev => ({ ...prev, weekly: !prev.weekly }))}
              className="w-12 h-6 rounded-full transition-colors relative"
              style={{ backgroundColor: notifications.weekly ? '#6CA58E' : '#E5E5E5' }}
            >
              <div
                className="w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform"
                style={{ transform: notifications.weekly ? 'translateX(24px)' : 'translateX(2px)' }}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Data & Privacy */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Shield size={20} style={{ color: '#1E4E40' }} />
          <h2 style={{ color: '#222' }}>Data & Privacy</h2>
        </div>
        <div className="space-y-3">
          <button className="w-full flex items-center justify-between py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors">
            <span style={{ color: '#222' }}>Manage Uber Connection</span>
            <ChevronRight size={20} className="text-gray-400" />
          </button>
          <button className="w-full flex items-center justify-between py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors">
            <span style={{ color: '#222' }}>Download My Data</span>
            <ChevronRight size={20} className="text-gray-400" />
          </button>
          <button className="w-full flex items-center justify-between py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors">
            <span className="text-red-500">Delete All Data</span>
            <ChevronRight size={20} className="text-gray-400" />
          </button>
        </div>
      </div>

      {/* Sign Out */}
      <button className="w-full py-4 rounded-xl border-2 flex items-center justify-center gap-2 transition-colors hover:bg-gray-50" style={{ borderColor: '#E5E5E5', color: '#666' }}>
        <LogOut size={20} />
        <span>Sign Out</span>
      </button>
    </div>
  );
}
