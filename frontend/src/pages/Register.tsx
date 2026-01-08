import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { toast } from 'react-hot-toast';
import { TrendingUp } from 'lucide-react';

export default function Register() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        company: '',
        role: 'borrower'
    });
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await register(
                formData.email,
                formData.password,
                formData.full_name,
                formData.company,
                formData.role
            );
            await new Promise(resolve => setTimeout(resolve, 100));
            navigate('/');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to register');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 mb-3">
                        <TrendingUp className="w-8 h-8" />
                        <h1 className="text-2xl font-bold">CovenantIQ</h1>
                    </div>
                    <p className="text-sm text-gray-500">Create your workspace</p>
                </div>

                {/* Form Card */}
                <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <Input
                            label="Full Name"
                            name="full_name"
                            placeholder="John Doe"
                            value={formData.full_name}
                            onChange={handleChange}
                            required
                        />

                        <Input
                            label="Company Name"
                            name="company"
                            placeholder="Acme Corp"
                            value={formData.company}
                            onChange={handleChange}
                        />

                        <Input
                            label="Work Email"
                            type="email"
                            name="email"
                            placeholder="name@company.com"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />

                        <Input
                            label="Password"
                            type="password"
                            name="password"
                            placeholder="Create a strong password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            helper="Must be at least 8 characters"
                        />

                        <div className="w-full mb-4">
                            <label className="block text-sm font-medium text-black mb-1.5">
                                Role
                            </label>
                            <select
                                name="role"
                                value={formData.role}
                                onChange={handleChange}
                                className="w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg transition-colors focus:outline-none focus:border-black focus:ring-1 focus:ring-black"
                            >
                                <option value="borrower">Borrower (Corporate)</option>
                                <option value="lender">Lender (Bank/Fund)</option>
                                <option value="analyst">Credit Analyst</option>
                            </select>
                        </div>

                        <Button
                            type="submit"
                            className="w-full"
                            size="lg"
                            loading={loading}
                        >
                            Create Account
                        </Button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-gray-600">
                            Already have an account?{' '}
                            <Link to="/login" className="font-semibold text-black hover:underline">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
