import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  BookOpen, 
  GraduationCap, 
  BarChart3, 
  Settings,
  BrainCircuit
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/create', icon: BrainCircuit, label: 'AI Generator' },
    { to: '/assignments', icon: BookOpen, label: 'Assignments' },
    { to: '/student-portal', icon: GraduationCap, label: 'Student Portal' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-900 text-white flex flex-col shadow-xl z-50">
      <div className="p-6 border-b border-slate-700 flex items-center gap-3">
        <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
          <BrainCircuit className="w-5 h-5 text-white" />
        </div>
        <h1 className="text-xl font-bold tracking-tight">EduGen AI</h1>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${
                isActive 
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/20' 
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-700">
        <button className="flex items-center gap-3 w-full px-4 py-3 text-slate-400 hover:text-white transition-colors">
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </button>
        <div className="mt-4 px-4 py-2 bg-slate-800 rounded text-xs text-slate-500">
          v1.0.0 • React + Gemini
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;