import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical, 
  FileText, 
  Calendar, 
  Sparkles,
  Loader2,
  Trash2,
  Edit,
  Eye,
  CheckCircle
} from 'lucide-react';
import { Assignment, AssignmentType, Difficulty } from '../types';
import { analyzeAssignment } from '../services/geminiService';

// Mock Data
const MOCK_ASSIGNMENTS: Assignment[] = [
  {
    id: '1',
    title: 'Introduction to Photosynthesis',
    subject: 'Biology 101',
    type: AssignmentType.MCQ,
    difficulty: Difficulty.EASY,
    questions: Array(5).fill({ text: 'Sample question' }),
    createdAt: '2024-03-10',
    dueDate: '2024-03-20',
    status: 'Published'
  },
  {
    id: '2',
    title: 'Hamlet: Themes & Motifs',
    subject: 'English Lit',
    type: AssignmentType.WRITTEN,
    difficulty: Difficulty.HARD,
    questions: Array(3).fill({ text: 'Sample question' }),
    createdAt: '2024-03-12',
    dueDate: '2024-03-25',
    status: 'Draft'
  },
  {
    id: '3',
    title: 'Linear Algebra Midterm',
    subject: 'Math 202',
    type: AssignmentType.MCQ,
    difficulty: Difficulty.MEDIUM,
    questions: Array(10).fill({ text: 'Sample question' }),
    createdAt: '2024-02-28',
    dueDate: '2024-03-05',
    status: 'Archived'
  }
];

const AssignmentsList: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>(MOCK_ASSIGNMENTS);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  
  // Analysis State
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<{id: string, text: string} | null>(null);

  const filteredAssignments = assignments.filter(a => {
    const matchesSearch = a.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          a.subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || a.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

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

  const deleteAssignment = (id: string) => {
    if(confirm('Are you sure you want to delete this assignment?')) {
        setAssignments(prev => prev.filter(a => a.id !== id));
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
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

      {/* List */}
      <div className="grid grid-cols-1 gap-4">
        {filteredAssignments.map((assignment) => (
          <div key={assignment.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-6 flex flex-col lg:flex-row gap-6 lg:items-center">
              
              {/* Icon & Info */}
              <div className="flex items-start gap-4 flex-1">
                <div className={`p-3 rounded-lg ${
                  assignment.type === AssignmentType.MCQ ? 'bg-blue-50 text-blue-600' : 
                  assignment.type === AssignmentType.WRITTEN ? 'bg-amber-50 text-amber-600' : 'bg-purple-50 text-purple-600'
                }`}>
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{assignment.title}</h3>
                  <p className="text-sm text-slate-500">{assignment.subject} • {assignment.questions.length} Questions</p>
                  
                  <div className="flex flex-wrap gap-2 mt-3">
                    <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-full">
                      {assignment.type}
                    </span>
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                      assignment.difficulty === Difficulty.EASY ? 'bg-emerald-100 text-emerald-700' :
                      assignment.difficulty === Difficulty.MEDIUM ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {assignment.difficulty}
                    </span>
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                      assignment.status === 'Published' ? 'bg-emerald-50 text-emerald-600 border border-emerald-200' :
                      assignment.status === 'Draft' ? 'bg-slate-50 text-slate-600 border border-slate-200' :
                      'bg-gray-100 text-gray-500'
                    }`}>
                      {assignment.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Meta & Actions */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 border-t lg:border-t-0 pt-4 lg:pt-0 border-slate-100 w-full lg:w-auto">
                 <div className="flex items-center gap-2 text-sm text-slate-500 min-w-[140px]">
                    <Calendar className="w-4 h-4" />
                    <span>Due: {assignment.dueDate}</span>
                 </div>

                 <div className="flex items-center gap-2 w-full sm:w-auto">
                    {/* AI Audit Button */}
                    <button 
                      onClick={() => handleAnalyze(assignment)}
                      disabled={analyzingId === assignment.id}
                      className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors border border-indigo-100"
                    >
                      {analyzingId === assignment.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                      {analyzingId === assignment.id ? 'Auditing...' : 'AI Audit'}
                    </button>

                    <div className="h-8 w-px bg-slate-200 hidden sm:block"></div>
                    
                    <button className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-slate-50 rounded-lg transition-colors" title="View/Edit">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-slate-50 rounded-lg transition-colors" title="Submissions">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => deleteAssignment(assignment.id)}
                      className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" 
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                 </div>
              </div>

            </div>

            {/* AI Analysis Result Panel */}
            {analysisResult?.id === assignment.id && (
              <div className="bg-indigo-900/5 p-4 border-t border-indigo-100 flex items-start gap-3 animate-fade-in-down">
                 <div className="bg-white p-1.5 rounded-full shadow-sm mt-0.5">
                    <Sparkles className="w-4 h-4 text-indigo-600" />
                 </div>
                 <div>
                    <h4 className="text-sm font-bold text-indigo-900">AI Pedagogical Audit</h4>
                    <p className="text-sm text-indigo-800 mt-1 leading-relaxed">
                       {analysisResult.text}
                    </p>
                 </div>
                 <button 
                    onClick={() => setAnalysisResult(null)}
                    className="ml-auto text-xs text-indigo-500 hover:text-indigo-800"
                 >
                    Dismiss
                 </button>
              </div>
            )}
          </div>
        ))}

        {filteredAssignments.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-slate-200 border-dashed">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500 font-medium">No assignments found matching your criteria.</p>
            <button 
              onClick={() => {setSearchTerm(''); setStatusFilter('All');}}
              className="text-indigo-600 text-sm hover:underline mt-2"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssignmentsList;