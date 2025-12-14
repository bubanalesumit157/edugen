 import React, { useState } from 'react';
import { Sparkles, Save, Loader2, Download, RefreshCw } from 'lucide-react';
import { generateContent } from '../services/geminiService';
import { AssignmentType, Difficulty, Question } from '../types';

const AssignmentCreator: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [type, setType] = useState<AssignmentType>(AssignmentType.MCQ);
  const [difficulty, setDifficulty] = useState<Difficulty>(Difficulty.MEDIUM);
  const [loading, setLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<Question[]>([]);
  const [hasGenerated, setHasGenerated] = useState(false);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setHasGenerated(false);
    
    const questions = await generateContent(topic, type, difficulty);
    setGeneratedQuestions(questions);
    
    setLoading(false);
    setHasGenerated(true);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
          <Sparkles className="text-indigo-600 w-8 h-8" />
          Intelligent Assignment Creator
        </h2>
        <p className="text-slate-500 mt-2">
          Use generative AI to build curriculum-aligned assessments instantly.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configuration Panel */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit lg:col-span-1">
          <h3 className="font-semibold text-lg mb-6 text-slate-900">Configuration</h3>
          
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Topic / Curriculum Unit</label>
              <input 
                type="text" 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Photosynthesis, World War II"
                className="w-full p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Assignment Type</label>
              <div className="grid grid-cols-2 gap-2">
                {Object.values(AssignmentType).map((t) => (
                  <button
                    key={t}
                    onClick={() => setType(t)}
                    className={`p-2 text-sm rounded-md border transition-all ${
                      type === t 
                      ? 'bg-indigo-50 border-indigo-500 text-indigo-700' 
                      : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Difficulty Level</label>
              <select 
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value as Difficulty)}
                className="w-full p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                {Object.values(Difficulty).map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <button 
              onClick={handleGenerate}
              disabled={loading || !topic}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Generate Content
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 min-h-[500px] flex flex-col">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50 rounded-t-xl">
            <h3 className="font-semibold text-lg text-slate-900">Content Preview</h3>
            {hasGenerated && (
               <div className="flex gap-2">
                 <button className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="Regenerate">
                    <RefreshCw className="w-5 h-5" />
                 </button>
                 <button className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="Export PDF">
                    <Download className="w-5 h-5" />
                 </button>
                 <button className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 text-sm font-medium transition-colors">
                    <Save className="w-4 h-4" />
                    Save Assignment
                 </button>
               </div>
            )}
          </div>

          <div className="p-8 flex-1">
            {!hasGenerated && !loading && (
              <div className="h-full flex flex-col items-center justify-center text-slate-400">
                <Sparkles className="w-16 h-16 mb-4 text-slate-200" />
                <p className="text-lg font-medium">Ready to generate content</p>
                <p className="text-sm">Configure the parameters and hit generate to start.</p>
              </div>
            )}

            {loading && (
              <div className="h-full flex flex-col items-center justify-center text-indigo-600 space-y-4">
                 <div className="relative w-20 h-20">
                    <div className="absolute inset-0 border-4 border-indigo-200 rounded-full animate-pulse"></div>
                    <div className="absolute inset-0 border-4 border-t-indigo-600 rounded-full animate-spin"></div>
                 </div>
                 <p className="font-medium animate-pulse">Consulting the knowledge base...</p>
              </div>
            )}

            {hasGenerated && (
              <div className="space-y-6 animate-fade-in-up">
                <div className="border-b pb-4 border-slate-100">
                    <h1 className="text-2xl font-bold text-slate-800">{topic}</h1>
                    <div className="flex gap-4 mt-2 text-sm text-slate-500">
                        <span className="bg-slate-100 px-2 py-1 rounded">{difficulty}</span>
                        <span className="bg-slate-100 px-2 py-1 rounded">{type}</span>
                    </div>
                </div>

                {generatedQuestions.map((q, idx) => (
                  <div key={q.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex gap-3">
                      <span className="flex-shrink-0 w-8 h-8 bg-white border border-slate-300 rounded-full flex items-center justify-center font-bold text-slate-500 text-sm">
                        {idx + 1}
                      </span>
                      <div className="flex-1">
                        <p className="text-slate-900 font-medium mb-3">{q.text}</p>
                        
                        {type === AssignmentType.MCQ && q.options && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {q.options.map((opt, i) => (
                              <div key={i} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-md">
                                <div className="w-4 h-4 rounded-full border border-slate-300"></div>
                                <span className="text-slate-600 text-sm">{opt}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {type === AssignmentType.WRITTEN && (
                           <div className="w-full h-24 bg-white border border-dashed border-slate-300 rounded-md p-3 text-slate-400 text-sm">
                             Student answer space...
                           </div>
                        )}

                        <div className="mt-4 pt-3 border-t border-slate-200">
                           <p className="text-xs text-slate-500 font-mono">
                             <span className="font-bold text-indigo-600">AI Key:</span> {type === AssignmentType.MCQ ? q.correctAnswer : q.rubric}
                           </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignmentCreator;