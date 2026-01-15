import React, { useEffect, useState } from 'react';
import { Users, AlertTriangle, TrendingUp, CheckCircle, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const StudentInsights: React.FC = () => {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // 1. Fetch Real Data from Backend
  useEffect(() => {
    const fetchInsights = async () => {
      try {
        // Calls the endpoint we created in analytics.py
        const response = await axios.get('http://localhost:8000/analytics/class-insights');
        setStudents(response.data);
      } catch (error) {
        console.error("Error fetching class insights:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, []);

  // 2. Smart Navigation Handler
  const handleCreateAssignment = (student: any) => {
    // Navigates to Creator Page with specific instructions
    navigate('/create', { 
      state: { 
        prefillTopic: student.recommended_topic,
        prefillDifficulty: student.recommended_difficulty,
        forStudent: student.name 
      } 
    });
  };

  const getTierColor = (tier: string) => {
    switch(tier) {
      case 'Struggling': return 'bg-red-100 text-red-700 border-red-200';
      case 'Below Average': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'Excellent': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-900">Student Insights</h2>
        <p className="text-slate-500 mt-2">AI-driven analysis of individual student learning paths.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-red-50 p-6 rounded-xl border border-red-100 flex items-center gap-4">
          <div className="p-3 bg-white rounded-full text-red-500 shadow-sm"><AlertTriangle /></div>
          <div>
            <h3 className="text-2xl font-bold text-red-900">
               {students.filter(s => s.tier === 'Struggling' || s.tier === 'Below Average').length}
            </h3>
            <p className="text-red-700 text-sm">Students Need Help</p>
          </div>
        </div>
        
        <div className="bg-green-50 p-6 rounded-xl border border-green-100 flex items-center gap-4">
          <div className="p-3 bg-white rounded-full text-green-600 shadow-sm"><TrendingUp /></div>
          <div>
            <h3 className="text-2xl font-bold text-green-900">
               {students.filter(s => s.tier === 'Excellent').length}
            </h3>
            <p className="text-green-700 text-sm">High Performers</p>
          </div>
        </div>

        <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 flex items-center gap-4">
          <div className="p-3 bg-white rounded-full text-blue-600 shadow-sm"><Users /></div>
          <div>
            <h3 className="text-2xl font-bold text-blue-900">{students.length}</h3>
            <p className="text-blue-700 text-sm">Total Students Analyzed</p>
          </div>
        </div>
      </div>

      {/* Insights Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h3 className="font-bold text-lg text-slate-800">Class Roster & Recommendations</h3>
        </div>
        
        {loading ? (
          <div className="p-12 flex justify-center"><Loader2 className="animate-spin text-indigo-600" /></div>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-slate-500 text-sm">
              <tr>
                <th className="p-4 font-medium">Student Name</th>
                <th className="p-4 font-medium">Performance Tier</th>
                <th className="p-4 font-medium">Accuracy</th>
                <th className="p-4 font-medium">Weak Topics</th>
                <th className="p-4 font-medium">AI Recommendation</th>
                <th className="p-4 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.map((student) => (
                <tr key={student.id} className="hover:bg-slate-50 transition">
                  <td className="p-4 font-medium text-slate-900 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600 uppercase">
                      {student.name.charAt(0)}
                    </div>
                    {student.name}
                  </td>
                  <td className="p-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getTierColor(student.tier)}`}>
                      {student.tier}
                    </span>
                  </td>
                  <td className="p-4 text-slate-600">{student.accuracy}</td>
                  <td className="p-4">
                    {student.weak_topics > 0 ? (
                      <span className="text-red-600 font-medium flex items-center gap-1 text-sm">
                        <AlertTriangle className="w-3 h-3" /> {student.weak_topics} Topics
                      </span>
                    ) : (
                      <span className="text-slate-400 text-sm flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> All Clear
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-sm text-slate-700">
                    <div className="flex flex-col">
                        <span className="font-medium">{student.needs}</span>
                        <span className="text-xs text-slate-500">Rec: {student.recommended_topic} ({student.recommended_difficulty})</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <button 
                        onClick={() => handleCreateAssignment(student)}
                        className="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 text-sm font-semibold hover:bg-indigo-50 px-3 py-2 rounded transition-colors"
                    >
                      <Sparkles className="w-4 h-4" />
                      Generate {student.recommended_difficulty} Assignment
                    </button>
                  </td>
                </tr>
              ))}
              
              {students.length === 0 && (
                <tr>
                    <td colSpan={6} className="p-8 text-center text-slate-500">
                        No student data available yet. Waiting for first submissions.
                    </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default StudentInsights;