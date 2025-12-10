import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { Brain, TrendingUp, AlertTriangle } from 'lucide-react';

const AnalyticsDashboard: React.FC = () => {
  // Mock Data for "Member 4" ML requirements
  const performanceData = [
    { name: 'Week 1', avgScore: 65, predicted: 68 },
    { name: 'Week 2', avgScore: 72, predicted: 70 },
    { name: 'Week 3', avgScore: 78, predicted: 75 },
    { name: 'Week 4', avgScore: 74, predicted: 79 },
    { name: 'Week 5', avgScore: 82, predicted: 81 },
    { name: 'Week 6', avgScore: 88, predicted: 85 },
  ];

  const topicMasteryData = [
    { subject: 'Algebra', A: 120, fullMark: 150 },
    { subject: 'Geometry', A: 98, fullMark: 150 },
    { subject: 'Calculus', A: 86, fullMark: 150 },
    { subject: 'Statistics', A: 99, fullMark: 150 },
    { subject: 'Trigonometry', A: 85, fullMark: 150 },
    { subject: 'Physics', A: 65, fullMark: 150 },
  ];

  const studentStrengthData = [
    { name: 'Reasoning', val: 80 },
    { name: 'Memory', val: 90 },
    { name: 'Application', val: 60 },
    { name: 'Analysis', val: 70 },
    { name: 'Evaluation', val: 50 },
    { name: 'Creation', val: 40 }, // Bloom's Taxonomy levels
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
       <div className="flex items-center justify-between">
         <div>
            <h2 className="text-3xl font-bold text-slate-900">Performance Analytics</h2>
            <p className="text-slate-500 mt-2">ML-powered insights into student performance and curriculum efficacy.</p>
         </div>
         <div className="bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 border border-indigo-100">
            <Brain className="w-4 h-4" />
            Predictive Model v2.4 Active
         </div>
       </div>

       <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         {/* Performance Trend & Prediction */}
         <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
           <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
             <TrendingUp className="w-5 h-5 text-emerald-500" />
             Class Performance Trajectory
           </h3>
           <div className="h-80 w-full">
             <ResponsiveContainer width="100%" height="100%">
               <LineChart data={performanceData}>
                 <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                 <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                 <YAxis stroke="#64748b" fontSize={12} />
                 <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                 />
                 <Legend />
                 <Line type="monotone" dataKey="avgScore" name="Actual Avg." stroke="#6366f1" strokeWidth={3} activeDot={{ r: 8 }} />
                 <Line type="monotone" dataKey="predicted" name="ML Prediction" stroke="#94a3b8" strokeWidth={2} strokeDasharray="5 5" />
               </LineChart>
             </ResponsiveContainer>
           </div>
           <p className="text-sm text-slate-500 mt-4 text-center">
             Dashed line represents ML-predicted outcomes based on engagement metrics.
           </p>
         </div>

         {/* Topic Mastery Radar */}
         <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
           <h3 className="font-bold text-slate-800 mb-6">Bloom's Taxonomy Breakdown</h3>
           <div className="h-80 w-full">
             <ResponsiveContainer width="100%" height="100%">
               <RadarChart cx="50%" cy="50%" outerRadius="80%" data={studentStrengthData}>
                 <PolarGrid stroke="#e2e8f0" />
                 <PolarAngleAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} />
                 <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                 <Radar name="Class Average" dataKey="val" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
                 <Tooltip />
               </RadarChart>
             </ResponsiveContainer>
           </div>
           <p className="text-sm text-slate-500 mt-4 text-center">
             Analysis of student capabilities across cognitive levels.
           </p>
         </div>

         {/* At Risk Students - Recommendation Engine */}
         <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Intervention Required
            </h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="bg-slate-50 text-slate-600 text-sm">
                            <th className="p-3 font-medium">Student Name</th>
                            <th className="p-3 font-medium">Current Grade</th>
                            <th className="p-3 font-medium">Risk Factor</th>
                            <th className="p-3 font-medium">Suggested Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        <tr>
                            <td className="p-3 text-slate-800 font-medium">Alex Johnson</td>
                            <td className="p-3 text-red-600 font-bold">62%</td>
                            <td className="p-3">
                                <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">High Risk</span>
                            </td>
                            <td className="p-3 text-sm text-slate-600">Assign remedial "Algebra Basics" module.</td>
                        </tr>
                        <tr>
                            <td className="p-3 text-slate-800 font-medium">Sam Smith</td>
                            <td className="p-3 text-amber-600 font-bold">71%</td>
                            <td className="p-3">
                                <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs">Moderate</span>
                            </td>
                            <td className="p-3 text-sm text-slate-600">Schedule 1:1 review session for Geometry.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
         </div>
       </div>
    </div>
  );
};

export default AnalyticsDashboard;