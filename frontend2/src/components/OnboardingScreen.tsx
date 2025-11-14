import React, { useState } from 'react';
import { ArrowRight, DollarSign, Clock, MapPin } from 'lucide-react';

interface OnboardingScreenProps {
  onComplete: (data: OnboardingData) => void;
}

export interface OnboardingData {
  weeklyGoal: number;
  averageHours: string;
  preferredZones: string[];
  workDays: string[];
}

export function OnboardingScreen({ onComplete }: OnboardingScreenProps) {
  const [step, setStep] = useState(1);
  const [weeklyGoal, setWeeklyGoal] = useState(1000);
  const [averageHours, setAverageHours] = useState('20-30');
  const [preferredZones, setPreferredZones] = useState<string[]>([]);
  const [workDays, setWorkDays] = useState<string[]>([]);

  const zones = ['Downtown', 'Airport', 'Suburbs', 'University District'];
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const handleComplete = () => {
    onComplete({ weeklyGoal, averageHours, preferredZones, workDays });
  };

  const toggleZone = (zone: string) => {
    setPreferredZones(prev =>
      prev.includes(zone) ? prev.filter(z => z !== zone) : [...prev, zone]
    );
  };

  const toggleDay = (day: string) => {
    setWorkDays(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  return (
    <div className="min-h-screen flex flex-col px-6 py-8" style={{ backgroundColor: '#FAF8F5' }}>
      {/* Progress */}
      <div className="mb-8">
        <div className="flex gap-2 mb-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className="h-1 flex-1 rounded-full transition-all"
              style={{ backgroundColor: s <= step ? '#1E4E40' : '#E5E5E5' }}
            />
          ))}
        </div>
        <p className="text-sm text-gray-500">Step {step} of 3</p>
      </div>

      {/* Step 1: Weekly Goal */}
      {step === 1 && (
        <div className="flex-1 flex flex-col">
          <div className="mb-8">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4" style={{ backgroundColor: '#E09447' }}>
              <DollarSign size={24} style={{ color: '#FFF' }} />
            </div>
            <h2 className="mb-2" style={{ color: '#222' }}>What's your weekly income goal?</h2>
            <p className="text-gray-600">We'll help you track progress and optimize your earnings</p>
          </div>

          <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
            <div className="text-center mb-6">
              <div className="mb-2" style={{ color: '#1E4E40' }}>${weeklyGoal}</div>
              <p className="text-sm text-gray-500">per week</p>
            </div>
            <input
              type="range"
              min="400"
              max="2000"
              step="50"
              value={weeklyGoal}
              onChange={(e) => setWeeklyGoal(Number(e.target.value))}
              className="w-full h-2 rounded-full appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #1E4E40 0%, #1E4E40 ${((weeklyGoal - 400) / 1600) * 100}%, #E5E5E5 ${((weeklyGoal - 400) / 1600) * 100}%, #E5E5E5 100%)`
              }}
            />
            <div className="flex justify-between text-sm text-gray-400 mt-2">
              <span>$400</span>
              <span>$2,000</span>
            </div>
          </div>

          <button
            onClick={() => setStep(2)}
            className="py-4 rounded-xl text-white flex items-center justify-center gap-2 transition-colors"
            style={{ backgroundColor: '#1E4E40' }}
          >
            <span>Continue</span>
            <ArrowRight size={20} />
          </button>
        </div>
      )}

      {/* Step 2: Work Schedule */}
      {step === 2 && (
        <div className="flex-1 flex flex-col">
          <div className="mb-8">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4" style={{ backgroundColor: '#1E4E40' }}>
              <Clock size={24} style={{ color: '#FFF' }} />
            </div>
            <h2 className="mb-2" style={{ color: '#222' }}>When do you typically drive?</h2>
            <p className="text-gray-600">This helps us provide better forecasts and insights</p>
          </div>

          <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
            <div className="mb-6">
              <label className="block mb-3 text-sm text-gray-600">Average hours per week</label>
              <div className="grid grid-cols-3 gap-2">
                {['10-20', '20-30', '30-40', '40+'].map((hours) => (
                  <button
                    key={hours}
                    onClick={() => setAverageHours(hours)}
                    className="py-3 px-4 rounded-xl border-2 transition-all"
                    style={{
                      borderColor: averageHours === hours ? '#1E4E40' : '#E5E5E5',
                      backgroundColor: averageHours === hours ? '#F0F5F3' : 'transparent',
                      color: averageHours === hours ? '#1E4E40' : '#666'
                    }}
                  >
                    {hours}h
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block mb-3 text-sm text-gray-600">Days you usually work</label>
              <div className="grid grid-cols-7 gap-2">
                {days.map((day) => (
                  <button
                    key={day}
                    onClick={() => toggleDay(day)}
                    className="py-3 rounded-xl border-2 transition-all"
                    style={{
                      borderColor: workDays.includes(day) ? '#1E4E40' : '#E5E5E5',
                      backgroundColor: workDays.includes(day) ? '#F0F5F3' : 'transparent',
                      color: workDays.includes(day) ? '#1E4E40' : '#666'
                    }}
                  >
                    {day}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="py-4 px-6 rounded-xl border-2 transition-colors"
              style={{ borderColor: '#E5E5E5', color: '#666' }}
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              className="flex-1 py-4 rounded-xl text-white flex items-center justify-center gap-2 transition-colors"
              style={{ backgroundColor: '#1E4E40' }}
            >
              <span>Continue</span>
              <ArrowRight size={20} />
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Preferred Zones */}
      {step === 3 && (
        <div className="flex-1 flex flex-col">
          <div className="mb-8">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4" style={{ backgroundColor: '#6CA58E' }}>
              <MapPin size={24} style={{ color: '#FFF' }} />
            </div>
            <h2 className="mb-2" style={{ color: '#222' }}>Where do you prefer to drive?</h2>
            <p className="text-gray-600">We'll analyze patterns in your preferred zones</p>
          </div>

          <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
            <div className="space-y-3">
              {zones.map((zone) => (
                <button
                  key={zone}
                  onClick={() => toggleZone(zone)}
                  className="w-full py-4 px-5 rounded-xl border-2 transition-all text-left"
                  style={{
                    borderColor: preferredZones.includes(zone) ? '#1E4E40' : '#E5E5E5',
                    backgroundColor: preferredZones.includes(zone) ? '#F0F5F3' : 'transparent',
                    color: preferredZones.includes(zone) ? '#1E4E40' : '#666'
                  }}
                >
                  {zone}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="py-4 px-6 rounded-xl border-2 transition-colors"
              style={{ borderColor: '#E5E5E5', color: '#666' }}
            >
              Back
            </button>
            <button
              onClick={handleComplete}
              className="flex-1 py-4 rounded-xl text-white flex items-center justify-center gap-2 transition-colors"
              style={{ backgroundColor: '#1E4E40' }}
            >
              <span>Get Started</span>
              <ArrowRight size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
