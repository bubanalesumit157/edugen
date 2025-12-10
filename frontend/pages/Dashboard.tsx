import React from 'react';
import { 
  Users, 
  FileCheck, 
  TrendingUp, 
  Clock,
  PlusCircle,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const stats = [
    { label: 'Active Students', value: '124', icon: Users, color: 'bg-blue-500' },
    { label: 'Pending Reviews', value: '18', icon: FileCheck, color: 'bg-amber-500' },
    { label: 'Avg. Class Score', value: '87%', icon: TrendingUp, color: 'bg-emerald-500' },
    { label: 'Avg. Completion Time', value: '45m', icon: Clock, color: 'bg-purple-500' },
  ];

  const recentAssignments = [
    { id: 1, title: 'Quantum Physics Basics', course: 'Physics 101', status: 'Published', submissions: 24 },
    { id: 2, title: 'Macbeth: Character Analysis', course: 'Literature', status: 'Draft', submissions: 0 },
    { id: 3, title: 'Calculus: Derivatives', course: 'Math 202', status: 'Closed', submissions: 112 },
  ];

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div>
        <h2 className="text-3xl font-bold text-slate-900">Educator Dashboard</h2>
        <p className="text-slate-500 mt-2">Welcome back. Here's what's happening in your classrooms today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg text-white`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Assignments */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h3 className="font-semibold text-lg text-slate-900">Recent Assignments</h3>
            <Link to="/assignments" className="text-indigo-600 text-sm hover:underline">View All</Link>
          </div>
          <div className="divide-y divide-slate-100">
            {recentAssignments.map((assignment) => (
              <div key={assignment.id} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div>
                  <h4 className="font-medium text-slate-900">{assignment.title}</h4>
                  <p className="text-sm text-slate-500">{assignment.course}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    assignment.status === 'Published' ? 'bg-emerald-100 text-emerald-700' :
                    assignment.status === 'Draft' ? 'bg-slate-100 text-slate-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {assignment.status}
                  </span>
                  <span className="text-sm text-slate-500">{assignment.submissions} submissions</span>
                  <button className="text-slate-400 hover:text-indigo-600">
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-xl shadow-lg p-6 text-white flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-lg mb-2">AI Generator</h3>
            <p className="text-indigo-100 text-sm mb-6">
              Create comprehensive assignments, quizzes, and study guides in seconds using our Gemini-powered engine.
            </p>
          </div>
          <Link to="/create" className="w-full">
            <button className="w-full bg-white text-indigo-700 py-3 rounded-lg font-semibold hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2">
              <PlusCircle className="w-5 h-5" />
              Create New Assignment
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;