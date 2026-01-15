import React, { useState, useEffect } from 'react';
import { generateContent, saveAssignment } from '../services/geminiService';
import { AssignmentType, Difficulty } from '../types';
import { useLocation } from 'react-router-dom';

const AssignmentCreator: React.FC = () => {
  const location = useLocation();
  const [topic, setTopic] = useState('');
  const [type, setType] = useState<AssignmentType>('MCQ');
  const [difficulty, setDifficulty] = useState<Difficulty>('Medium');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<any[]>([]);
  
  // State to store the saved ID
  const [savedId, setSavedId] = useState<string | null>(null);
  
  // --- NEW: Handle Personalization Data from Insights Page ---
  useEffect(() => {
    if (location.state) {
      const { prefillTopic, prefillDifficulty, forStudent } = location.state as any;
      
      if (prefillTopic) {
        setTopic(prefillTopic);
      }
      
      if (prefillDifficulty) {
        // Ensure the difficulty matches one of our valid types (capitalize if needed)
        const formattedDiff = prefillDifficulty.charAt(0).toUpperCase() + prefillDifficulty.slice(1).toLowerCase();
        setDifficulty(formattedDiff as Difficulty);
      }
      
      // Visual feedback that personalization is active
      if (forStudent) {
        console.log(`✨ Personalizing assignment for ${forStudent}`);
      }
    }
  }, [location]);
  // -----------------------------------------------------------

  const handleGenerate = async () => {
    setIsLoading(true);
    setSavedId(null); // Reset previous ID
    const questions = await generateContent(topic, type, difficulty);
    setGeneratedQuestions(questions);
    setIsLoading(false);
  };

  const handleSave = async () => {
    if (generatedQuestions.length === 0) return;
    
    // Create the assignment object
    const assignment = {
      id: crypto.randomUUID(),
      title: `${topic} - ${difficulty} (${type})`,
      subject: "General", 
      topic,
      type,
      difficulty,
      questions: generatedQuestions,
      status: 'Published'
    };

    try {
      await saveAssignment(assignment);
      setSavedId(assignment.id); 
      alert("Assignment Saved Successfully!");
    } catch (e) {
      alert("Error saving assignment");
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Create New Assignment</h1>
      
      {/* Personalization Banner (Optional) */}
      {location.state?.forStudent && (
        <div className="mb-6 bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-lg animate-fade-in">
          <div className="flex items-center">
            <span className="text-indigo-600 font-bold mr-2">✨ Personalizing for:</span>
            <span className="text-gray-800">{location.state.forStudent}</span>
          </div>
          <p className="text-sm text-indigo-700 mt-1">
            Topic and difficulty have been auto-set based on their learning history.
          </p>
        </div>
      )}

      {/* Copy ID Section */}
      {savedId && (
        <div className="mb-8 p-4 bg-green-50 border border-green-200 rounded-lg flex flex-col items-center animate-fade-in">
          <p className="text-green-800 font-semibold mb-2">✅ Assignment Created Successfully!</p>
          <div className="flex items-center gap-2 bg-white p-2 border rounded shadow-sm w-full max-w-lg">
            <code className="flex-1 text-center font-mono text-gray-700 select-all">
              {savedId}
            </code>
            <button 
              onClick={() => navigator.clipboard.writeText(savedId)}
              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
            >
              Copy
            </button>
          </div>
          <p className="text-xs text-green-600 mt-2">Share this ID with your students.</p>
        </div>
      )}

      {/* Input Form */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Topic</label>
          <input 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)}
            className="w-full p-2 border rounded mt-1 outline-none focus:ring-2 focus:ring-indigo-500 transition" 
            placeholder="e.g. Photosynthesis, Linear Algebra"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Type</label>
            <select 
              value={type} 
              onChange={(e) => setType(e.target.value as AssignmentType)}
              className="w-full p-2 border rounded mt-1 outline-none focus:ring-2 focus:ring-indigo-500 transition"
            >
              <option value="MCQ">Multiple Choice</option>
              <option value="WRITTEN">Written / Subjective</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Difficulty</label>
            <select 
              value={difficulty} 
              onChange={(e) => setDifficulty(e.target.value as Difficulty)}
              className="w-full p-2 border rounded mt-1 outline-none focus:ring-2 focus:ring-indigo-500 transition"
            >
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
        </div>

        <button 
          onClick={handleGenerate} 
          disabled={isLoading || !topic}
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Generating Questions with AI...' : 'Generate Assignment'}
        </button>
      </div>

      {/* Preview Section */}
      {generatedQuestions.length > 0 && (
        <div className="mt-8 animate-fade-in">
          <h2 className="text-xl font-bold mb-4 text-gray-800">Preview ({generatedQuestions.length} Questions)</h2>
          <div className="space-y-4">
            {generatedQuestions.map((q, i) => (
              <div key={i} className="bg-white p-5 rounded-lg shadow-sm border-l-4 border-indigo-500 relative">
                <span className="absolute top-2 right-2 text-xs font-mono text-gray-400">ID: {q.id?.slice(0,8)}</span>
                
                {/* Question Text */}
                <p className="font-semibold text-lg text-gray-900 mb-2">
                  Q{i+1}: {q.text}
                </p>

                {/* Options (MCQ) */}
                {q.options && q.options.length > 0 && (
                  <ul className="grid grid-cols-1 gap-2 mb-3">
                    {q.options.map((opt: string, idx: number) => (
                      <li key={idx} className="bg-gray-50 px-3 py-2 rounded text-gray-700 text-sm border border-gray-100">
                        {opt}
                      </li>
                    ))}
                  </ul>
                )}

                {/* Answer Key & Rubric */}
                <div className="mt-3 pt-3 border-t border-gray-100 bg-green-50 -mx-5 -mb-5 px-5 py-3 rounded-b-lg">
                  <p className="text-sm text-green-800">
                    <span className="font-bold">Correct Answer:</span> {q.correctAnswer}
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    <span className="font-bold">Rubric/Explanation:</span> {q.rubric}
                  </p>
                </div>

              </div>
            ))}
          </div>
          
          <button 
            onClick={handleSave}
            className="mt-8 w-full bg-green-600 text-white py-4 rounded-xl text-lg font-bold hover:bg-green-700 shadow-lg transition transform hover:scale-[1.01]"
          >
            Save & Publish Assignment
          </button>
        </div>
      )}
    </div>
  );
};

export default AssignmentCreator;