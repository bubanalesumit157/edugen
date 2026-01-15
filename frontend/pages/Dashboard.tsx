import React, { useEffect, useState } from 'react';
import { 
  Users, 
  FileCheck, 
  TrendingUp, 
  Clock,
  PlusCircle,
  ArrowRight,
  Loader2,
  BookOpen
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchAssignments } from '../services/geminiService';
import { Assignment } from '../types';

const Dashboard: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  // Load Real Data
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchAssignments();
        setAssignments(data);
      } catch (error) {
        console.error("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Calculate Dynamic Stats
  const totalAssignments = assignments.length;
  const publishedCount = assignments.filter(a => a.status === 'Published').length;
  const draftCount = assignments.filter(a => a.status === 'Draft').length;

  // Stats Array (Mixed Real + Mock for demo purposes)
  const stats = [
    { label: 'Total Assignments', value: totalAssignments.toString(), icon: BookOpen, color: 'bg-blue-500' },
    { label: 'Published Active', value: publishedCount.toString(), icon: FileCheck, color: 'bg-emerald-500' },
    { label: 'Drafts Pending', value: draftCount.toString(), icon: Clock, color: 'bg-amber-500' },
    { label: 'Total Students', value: '12', icon: Users, color: 'bg-purple-500' }, // Mock for now
  ];

  // Get top 3 most recent assignments
  const recentAssignments = assignments.slice(0, 3);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader2 className="w-10 h-10 text-indigo-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div>
        <h2 className="text-3xl font-bold text-slate-900">Educator Dashboard</h2>
        <p className="text-slate-500 mt-2">Welcome back. Here is an overview of your content generation.</p>
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
        {/* Recent Assignments List */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h3 className="font-semibold text-lg text-slate-900">Recent Assignments</h3>
            <Link to="/assignments" className="text-indigo-600 text-sm hover:underline">View All</Link>
          </div>
          
          <div className="divide-y divide-slate-100">
            {recentAssignments.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                No assignments created yet.
              </div>
            ) : (
              recentAssignments.map((assignment) => (
                <div key={assignment.id} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div>
                    <h4 className="font-medium text-slate-900">{assignment.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-slate-500">{assignment.subject || "General"}</span>
                      <span className="text-xs text-slate-300">•</span>
                      <span className="text-sm text-slate-500">
                        {Array.isArray(assignment.questions) ? assignment.questions.length : 0} Questions
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      assignment.status === 'Published' ? 'bg-emerald-100 text-emerald-700' :
                      assignment.status === 'Draft' ? 'bg-slate-100 text-slate-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {assignment.status}
                    </span>
                    
                    {/* Copy ID Button for quick access */}
                    <button 
                      onClick={() => {navigator.clipboard.writeText(assignment.id); alert("ID Copied!")}}
                      className="text-slate-400 hover:text-indigo-600 transition-colors"
                      title="Copy ID"
                    >
                      <ArrowRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-xl shadow-lg p-6 text-white flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-lg mb-2">AI Generator</h3>
            <p className="text-indigo-100 text-sm mb-6">
              Create comprehensive assignments, quizzes, and study guides in seconds using our GenAI engine.
            </p>
          </div>
          <Link to="/create" className="w-full">
            <button className="w-full bg-white text-indigo-700 py-3 rounded-lg font-semibold hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2 shadow-lg">
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