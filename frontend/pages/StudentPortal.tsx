import React, { useState } from 'react';
import { BookOpen, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { autoGradeSubmission } from '../services/geminiService';

const StudentPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'todo' | 'completed'>('todo');
  
  // Mock Active Assignment
  const assignment = {
    title: "Intro to ML Algorithms",
    description: "Explain the differences between Supervised and Unsupervised Learning.",
    type: "Short Essay",
    dueDate: "Tomorrow, 11:59 PM"
  };

  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<{score: number, feedback: string} | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!answer) return;
    setIsSubmitting(true);
    // Simulate AI Grading
    const result = await autoGradeSubmission(
        assignment.description, 
        answer, 
        "Supervised learning uses labeled data (input-output pairs) to train models (e.g., classification, regression), whereas unsupervised learning analyzes unlabeled data to find hidden patterns or structures (e.g., clustering, dimensionality reduction)."
    );
    setFeedback(result);
    setIsSubmitting(false);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Student Portal</h2>
          <p className="text-slate-500 mt-2">Track your progress and submit assignments.</p>
        </div>
        <div className="flex bg-slate-100 p-1 rounded-lg">
           <button 
             onClick={() => setActiveTab('todo')}
             className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'todo' ? 'bg-white shadow text-indigo-600' : 'text-slate-500'}`}
           >
             To Do
           </button>
           <button 
             onClick={() => setActiveTab('completed')}
             className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'completed' ? 'bg-white shadow text-indigo-600' : 'text-slate-500'}`}
           >
             Completed
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'todo' ? (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100 bg-indigo-50">
                  <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-xl font-bold text-slate-800">{assignment.title}</h3>
                        <span className="inline-block mt-2 px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full">
                            {assignment.type}
                        </span>
                    </div>
                    <div className="flex items-center gap-2 text-amber-600 bg-amber-50 px-3 py-1 rounded-full text-sm">
                        <Clock className="w-4 h-4" />
                        <span className="font-medium">{assignment.dueDate}</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 space-y-6">
                    <div>
                        <h4 className="font-medium text-slate-900 mb-2">Question:</h4>
                        <p className="text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
                            {assignment.description}
                        </p>
                    </div>

                    {!feedback ? (
                        <div>
                            <label className="block font-medium text-slate-900 mb-2">Your Answer:</label>
                            <textarea 
                                value={answer}
                                onChange={(e) => setAnswer(e.target.value)}
                                className="w-full h-40 p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
                                placeholder="Type your response here..."
                            />
                            <div className="mt-4 flex justify-end">
                                <button 
                                    onClick={handleSubmit}
                                    disabled={isSubmitting || !answer}
                                    className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50"
                                >
                                    {isSubmitting ? 'Grading...' : 'Submit Assignment'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 animate-fade-in">
                            <div className="flex items-center gap-3 mb-4">
                                <CheckCircle className="w-8 h-8 text-emerald-600" />
                                <div>
                                    <h4 className="font-bold text-emerald-900 text-lg">Submission Graded</h4>
                                    <p className="text-emerald-700 text-sm">AI Auto-Grading Complete</p>
                                </div>
                                <div className="ml-auto text-4xl font-bold text-emerald-600">
                                    {feedback.score}<span className="text-lg text-emerald-400">/100</span>
                                </div>
                            </div>
                            <div className="bg-white/60 p-4 rounded-lg">
                                <p className="font-medium text-emerald-800 mb-1">Feedback:</p>
                                <p className="text-emerald-700">{feedback.feedback}</p>
                            </div>
                            <button 
                                onClick={() => {setFeedback(null); setAnswer('');}}
                                className="mt-4 text-emerald-700 hover:underline text-sm"
                            >
                                Try another response (Demo)
                            </button>
                        </div>
                    )}
                </div>
              </div>
          ) : (
            <div className="text-center py-20 text-slate-400">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-slate-200" />
                <p className="text-lg">No completed assignments to show in this demo.</p>
            </div>
          )}
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-indigo-500" />
                    Course Material
                </h3>
                <ul className="space-y-3">
                    <li className="flex items-center justify-between text-sm p-2 hover:bg-slate-50 rounded cursor-pointer transition-colors">
                        <span className="text-slate-600">Lecture 1: Introduction</span>
                        <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Viewed</span>
                    </li>
                    <li className="flex items-center justify-between text-sm p-2 hover:bg-slate-50 rounded cursor-pointer transition-colors">
                        <span className="text-slate-600">Lecture 2: Supervised Learning</span>
                        <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Viewed</span>
                    </li>
                    <li className="flex items-center justify-between text-sm p-2 hover:bg-slate-50 rounded cursor-pointer transition-colors">
                        <span className="text-slate-600">Textbook: Chapter 4</span>
                        <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded">Unread</span>
                    </li>
                </ul>
            </div>

            <div className="bg-amber-50 border border-amber-200 p-6 rounded-xl">
                <h3 className="font-bold text-amber-900 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Upcoming Exam
                </h3>
                <p className="text-sm text-amber-800 mb-4">
                    Mid-term evaluation is scheduled for next Tuesday. Review your past assignments to prepare.
                </p>
                <button className="w-full bg-amber-200 text-amber-900 py-2 rounded font-medium hover:bg-amber-300 transition-colors">
                    View Study Guide
                </button>
            </div>
        </div>
      </div>
    </div>
  );
};

export default StudentPortal;