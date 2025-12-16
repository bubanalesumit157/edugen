// project_clean_archive/frontend/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../services/authService';

const Login = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isRegister) {
        await register(email, password, role);
        alert("Registered! Now log in.");
        setIsRegister(false); // Switch back to login mode
      } else {
        await login(email, password);
        navigate('/'); // Go to Dashboard
      }
    } catch (err: any) {
      console.error(err);
      alert("Error: " + (err.response?.data?.detail || "Login failed"));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">
          {isRegister ? 'Create Account' : 'Welcome Back'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input 
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md" 
              placeholder="name@example.com" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input 
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md" 
              type="password" 
              placeholder="••••••••" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required
            />
          </div>

          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Role</label>
              <select 
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md" 
                value={role} 
                onChange={e => setRole(e.target.value)}
              >
                <option value="student">Student</option>
                <option value="educator">Educator</option>
              </select>
            </div>
          )}

          <button 
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition"
          >
            {isRegister ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <p 
          onClick={() => setIsRegister(!isRegister)} 
          className="mt-4 text-center text-sm text-blue-600 cursor-pointer hover:underline"
        >
          {isRegister ? 'Already have an account? Login' : 'Need an account? Register'}
        </p>
      </div>
    </div>
  );
};

export default Login;