import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../components/layout/Layout';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';
import { User, Bell, Activity, Calendar } from 'lucide-react';
import api from '../lib/api';
import { toast } from 'react-hot-toast';

interface UserPreferences {
    email_alerts: boolean;
    weekly_reports: boolean;
    system_updates: boolean;
}

interface ActivityItem {
    id: string;
    action: string;
    description: string;
    created_at: string;
}

export default function Settings() {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const [fullName, setFullName] = useState(user?.full_name || '');
    const [company, setCompany] = useState(user?.company || '');

    // Fetch preferences
    const { data: preferences } = useQuery<UserPreferences>({
        queryKey: ['user-preferences'],
        queryFn: async () => {
            const res = await api.get('/api/user/preferences');
            return res.data;
        },
    });

    // Fetch activity
    const { data: activity } = useQuery<ActivityItem[]>({
        queryKey: ['user-activity'],
        queryFn: async () => {
            const res = await api.get('/api/user/activity?limit=10');
            return res.data;
        },
    });

    // Update profile mutation
    const updateProfileMutation = useMutation({
        mutationFn: async (data: { full_name?: string; company?: string }) => {
            const res = await api.put('/api/user/profile', data);
            return res.data;
        },
        onSuccess: () => {
            toast.success('Profile updated successfully');
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
        onError: () => {
            toast.error('Failed to update profile');
        },
    });

    // Update preferences mutation
    const updatePreferencesMutation = useMutation({
        mutationFn: async (data: UserPreferences) => {
            const res = await api.put('/api/user/preferences', data);
            return res.data;
        },
        onSuccess: () => {
            toast.success('Preferences updated');
            queryClient.invalidateQueries({ queryKey: ['user-preferences'] });
        },
        onError: () => {
            toast.error('Failed to update preferences');
        },
    });

    const handleProfileUpdate = () => {
        updateProfileMutation.mutate({
            full_name: fullName,
            company: company,
        });
    };

    const handlePreferenceToggle = (key: keyof UserPreferences) => {
        if (preferences) {
            updatePreferencesMutation.mutate({
                ...preferences,
                [key]: !preferences[key],
            });
        }
    };

    return (
        <Layout title="Settings" maxWidth="wide">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Account */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Account Information */}
                    <Card>
                        <div className="flex items-center gap-2 mb-6">
                            <User className="w-5 h-5" />
                            <h2 className="text-lg font-semibold text-black">Account Information</h2>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                                label="Full Name"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                            />
                            <Input
                                label="Email"
                                type="email"
                                value={user?.email || ''}
                                disabled
                            />
                            <Input
                                label="Company"
                                value={company}
                                onChange={(e) => setCompany(e.target.value)}
                            />
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-black mb-1.5">
                                    Role
                                </label>
                                <div className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg text-gray-600 capitalize">
                                    {user?.role || 'Not specified'}
                                </div>
                            </div>
                        </div>
                        <div className="mt-6 pt-6 border-t border-gray-200">
                            <Button
                                variant="secondary"
                                size="sm"
                                onClick={handleProfileUpdate}
                                loading={updateProfileMutation.isPending}
                            >
                                Update Profile
                            </Button>
                        </div>
                    </Card>

                    {/* Recent Activity */}
                    <Card>
                        <div className="flex items-center gap-2 mb-6">
                            <Activity className="w-5 h-5" />
                            <h2 className="text-lg font-semibold text-black">Recent Activity</h2>
                        </div>
                        <div className="space-y-3">
                            {activity && activity.length > 0 ? (
                                activity.map((item) => (
                                    <div key={item.id} className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
                                        <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
                                            <Calendar className="w-4 h-4 text-gray-600" />
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-black capitalize">
                                                {item.action.replace('_', ' ')}
                                            </p>
                                            {item.description && (
                                                <p className="text-xs text-gray-500 mt-0.5">
                                                    {item.description}
                                                </p>
                                            )}
                                            <p className="text-xs text-gray-400 mt-1">
                                                {new Date(item.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-8 text-sm text-gray-400">
                                    No activity yet
                                </div>
                            )}
                        </div>
                    </Card>
                </div>

                {/* Right Column - Preferences */}
                <div className="space-y-6">
                    {/* Notifications */}
                    <Card>
                        <div className="flex items-center gap-2 mb-6">
                            <Bell className="w-5 h-5" />
                            <h2 className="text-lg font-semibold text-black">Notifications</h2>
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-start justify-between py-3 border-b border-gray-100">
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-black">Email Alerts</p>
                                    <p className="text-xs text-gray-500 mt-0.5">Covenant breach notifications</p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer ml-3">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={preferences?.email_alerts || false}
                                        onChange={() => handlePreferenceToggle('email_alerts')}
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-black rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
                                </label>
                            </div>
                            <div className="flex items-start justify-between py-3 border-b border-gray-100">
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-black">Weekly Reports</p>
                                    <p className="text-xs text-gray-500 mt-0.5">Portfolio summaries</p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer ml-3">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={preferences?.weekly_reports || false}
                                        onChange={() => handlePreferenceToggle('weekly_reports')}
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-black rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
                                </label>
                            </div>
                            <div className="flex items-start justify-between py-3">
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-black">System Updates</p>
                                    <p className="text-xs text-gray-500 mt-0.5">New features  & improvements</p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer ml-3">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={preferences?.system_updates || false}
                                        onChange={() => handlePreferenceToggle('system_updates')}
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-black rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
                                </label>
                            </div>
                        </div>
                    </Card>

                    {/* Account Info */}
                    <Card className="bg-gray-50 border-gray-300">
                        <h2 className="text-sm font-semibold text-black mb-4">Account Info</h2>
                        <div className="space-y-3">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Member since</span>
                                <span className="font-medium text-black">
                                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'N/A'}
                                </span>
                            </div>
                            <div className="flex justify-between text-sm pt-3 border-t border-gray-200">
                                <span className="text-gray-600">Account type</span>
                                <span className="font-medium text-black capitalize">{user?.role || 'User'}</span>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </Layout>
    );
}
