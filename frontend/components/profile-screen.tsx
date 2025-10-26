import { Card } from "./ui/card";
import { Switch } from "./ui/switch";
import { Slider } from "./ui/slider";
import { Button } from "./ui/button";
import { ArrowLeft, User, Target, Bell, Shield, Trash2, LogOut } from "lucide-react";
import { useState } from "react";

interface ProfileScreenProps {
  onBack: () => void;
  onLogout: () => void;
}

export function ProfileScreen({ onBack, onLogout }: ProfileScreenProps) {
  const [weeklyGoal, setWeeklyGoal] = useState([900]);
  const [notifications, setNotifications] = useState({
    weeklyRecap: true,
    goalReminders: true,
    insights: false
  });

  return (
    <div className="pb-24 bg-background min-h-screen">
      {/* Header */}
      <div className="px-6 pt-12 pb-6">
        <div className="flex items-center gap-3 mb-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="space-y-1">
            <h1 className="text-xl font-semibold text-foreground">Profile & Settings</h1>
            <p className="text-sm text-muted-foreground">Manage your account and preferences</p>
          </div>
        </div>
      </div>

      <div className="px-6 space-y-6">
        {/* Driver Profile */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center">
                <User className="w-6 h-6 text-primary-foreground" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-medium text-foreground">Alex Chen</h3>
                <p className="text-sm text-muted-foreground">Driver since March 2024</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 pt-2">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">City</p>
                <p className="font-medium text-foreground">Sydney</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Trips</p>
                <p className="font-medium text-foreground">1,247</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Weekly Goal Setting */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-secondary" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-medium text-foreground">Weekly Income Goal</h3>
                <p className="text-sm text-muted-foreground">Set your target weekly earnings</p>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Current goal</span>
                <span className="text-lg font-semibold text-foreground">${weeklyGoal[0]}</span>
              </div>
              
              <Slider
                value={weeklyGoal}
                onValueChange={setWeeklyGoal}
                max={1500}
                min={500}
                step={50}
                className="w-full"
              />
              
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>$500</span>
                <span>$1,500</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Notification Preferences */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-accent" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-medium text-foreground">Notifications</h3>
                <p className="text-sm text-muted-foreground">Choose what updates you receive</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="font-medium text-foreground">Weekly summary</p>
                  <p className="text-sm text-muted-foreground">Get a recap every Sunday</p>
                </div>
                <Switch 
                  checked={notifications.weeklyRecap}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, weeklyRecap: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="font-medium text-foreground">Goal reminders</p>
                  <p className="text-sm text-muted-foreground">Alerts when behind target</p>
                </div>
                <Switch 
                  checked={notifications.goalReminders}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, goalReminders: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="font-medium text-foreground">Smart insights</p>
                  <p className="text-sm text-muted-foreground">New earning opportunities</p>
                </div>
                <Switch 
                  checked={notifications.insights}
                  onCheckedChange={(checked) => 
                    setNotifications(prev => ({ ...prev, insights: checked }))
                  }
                />
              </div>
            </div>
          </div>
        </Card>

        {/* Privacy & Security */}
        <Card className="p-6 bg-card border-border">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-primary" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-medium text-foreground">Privacy & Security</h3>
                <p className="text-sm text-muted-foreground">Manage your data and connections</p>
              </div>
            </div>
            
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start h-12">
                <Shield className="w-4 h-4 mr-2" />
                Manage Uber connection
              </Button>
              
              <Button variant="outline" className="w-full justify-start h-12 text-red-600 border-red-200 hover:bg-red-50">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete all data
              </Button>
            </div>
          </div>
        </Card>

        {/* Logout */}
        <Card className="p-6 bg-card border-border">
          <Button 
            onClick={onLogout}
            variant="outline" 
            className="w-full justify-center h-12"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign out
          </Button>
        </Card>

        {/* App Info */}
        <div className="text-center space-y-2 pb-8">
          <p className="text-sm text-muted-foreground">Steady for Sydney Drivers</p>
          <p className="text-xs text-muted-foreground">Version 1.2.0 • Made with ❤️ for drivers</p>
        </div>
      </div>
    </div>
  );
}
