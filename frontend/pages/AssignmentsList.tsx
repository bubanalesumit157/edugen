import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Plus, Search, Filter, FileText, Calendar, Sparkles, Loader2, Trash2, Copy, Check 
} from 'lucide-react';
// 1. IMPORT REACT-MARKDOWN
import ReactMarkdown from 'react-markdown'; 

import { Assignment } from '../types';
import { analyzeAssignment, fetchAssignments } from '../services/geminiService';

const AssignmentsList: React.FC = () => {
  // ... (Keep all your existing state and functions: assignments, loading, loadAssignments, etc.) ...
  
  // (I am omitting the state/functions here to save space, keep them exactly as they were)
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<{id: string, text: string} | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => { loadAssignments(); }, []);

  const loadAssignments = async () => {
    setLoading(true);
    const data = await fetchAssignments();
    setAssignments(data);
    setLoading(false);
  };
  
  // ... (Keep handleAnalyze, handleCopyId, deleteAssignment, etc.) ...

  const handleAnalyze = async (assignment: Assignment) => {
    setAnalyzingId(assignment.id);
    setAnalysisResult(null);
    try {
      const result = await analyzeAssignment(assignment);
      setAnalysisResult({ id: assignment.id, text: result });
    } catch (error) {
      console.error("Analysis failed", error);
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleCopyId = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const deleteAssignment = (id: string) => {
    if(confirm('Are you sure you want to delete this assignment?')) {
      setAssignments(prev => prev.filter(a => a.id !== id));
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'No Date';
    return new Date(dateString).toLocaleDateString();
  };
  
  const filteredAssignments = assignments.filter(a => {
    const title = a.title || "";
    const subject = a.subject || "";
    const matchesSearch = title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || a.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* ... (Header and Controls remain the same) ... */}
      
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Assignments</h2>
          <p className="text-slate-500 mt-2">Manage, review, and grade your course assessments.</p>
        </div>
        <Link to="/create">
          <button className="bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2 shadow-sm">
            <Plus className="w-5 h-5" />
            Create New
          </button>
        </Link>
      </div>

       {/* Controls */}
       <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search by title or subject..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
          />
        </div>
        
        <div className="flex items-center gap-3 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="text-sm text-slate-600 font-medium">Status:</span>
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="p-2 border border-slate-300 rounded-lg text-sm outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="All">All Statuses</option>
            <option value="Draft">Draft</option>
            <option value="Published">Published</option>
            <option value="Archived">Archived</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center py-20">
          <Loader2 className="w-10 h-10 text-indigo-600 animate-spin" />
        </div>
      )}

      {/* List */}
      <div className="grid grid-cols-1 gap-4">
        {filteredAssignments.map((assignment) => (
          <div key={assignment.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-6 flex flex-col lg:flex-row gap-6 lg:items-center">
              
              {/* Icon & Info */}
              <div className="flex items-start gap-4 flex-1">
                <div className={`p-3 rounded-lg ${
                  assignment.type === 'MCQ' ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600'
                }`}>
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{assignment.title}</h3>
                  <p className="text-sm text-slate-500 mb-2">
                     {assignment.subject} • {Array.isArray(assignment.questions) ? assignment.questions.length : 0} Questions
                  </p>
                  
                  {/* ID Badge */}
                  <div 
                    onClick={() => handleCopyId(assignment.id)}
                    className="inline-flex items-center gap-2 bg-slate-100 px-2 py-1 rounded border border-slate-200 cursor-pointer hover:bg-slate-200 transition group"
                  >
                    <span className="text-xs font-mono text-slate-600 font-medium">ID: {assignment.id}</span>
                    {copiedId === assignment.id ? <Check className="w-3 h-3 text-green-600" /> : <Copy className="w-3 h-3 text-slate-400 group-hover:text-slate-600" />}
                  </div>

                  <div className="flex flex-wrap gap-2 mt-3">
                    <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-full">{assignment.type}</span>
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                      assignment.difficulty === 'Easy' ? 'bg-emerald-100 text-emerald-700' :
                      assignment.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>{assignment.difficulty}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 border-t lg:border-t-0 pt-4 lg:pt-0 border-slate-100 w-full lg:w-auto">
                 <div className="flex items-center gap-2 text-sm text-slate-500 min-w-[140px]">
                    <Calendar className="w-4 h-4" />
                    <span>Created: {formatDate(assignment.createdAt)}</span>
                 </div>

                 <div className="flex items-center gap-2 w-full sm:w-auto">
                    <button 
                      onClick={() => handleAnalyze(assignment)}
                      disabled={analyzingId === assignment.id}
                      className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors border border-indigo-100"
                    >
                      {analyzingId === assignment.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                      {analyzingId === assignment.id ? 'Auditing...' : 'AI Audit'}
                    </button>
                    <div className="h-8 w-px bg-slate-200 hidden sm:block"></div>
                    <button onClick={() => deleteAssignment(assignment.id)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                 </div>
              </div>
            </div>

            {/* --- AI Analysis Result Panel (UPDATED) --- */}
            {analysisResult?.id === assignment.id && (
              <div className="bg-indigo-900/5 p-6 border-t border-indigo-100 flex items-start gap-4 animate-fade-in-down">
                 <div className="bg-white p-2 rounded-full shadow-sm mt-1">
                    <Sparkles className="w-5 h-5 text-indigo-600" />
                 </div>
                 <div className="flex-1">
                    <h4 className="text-base font-bold text-indigo-900 mb-2">AI Pedagogical Audit</h4>
                    
                    {/* 2. USE REACT MARKDOWN HERE */}
                    <div className="prose prose-indigo prose-sm max-w-none text-slate-700 leading-relaxed">
                        <ReactMarkdown>
                            {analysisResult.text}
                        </ReactMarkdown>
                    </div>

                 </div>
                 <button onClick={() => setAnalysisResult(null)} className="text-xs text-indigo-500 hover:text-indigo-800 font-medium">
                    Dismiss
                 </button>
              </div>
            )}
            
          </div>
        ))}
      </div>
    </div>
  );
};

export default AssignmentsList;