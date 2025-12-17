import React, { useState } from 'react';
import { generateContent, saveAssignment } from '../services/geminiService';
import { AssignmentType, Difficulty } from '../types';

const AssignmentCreator: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [type, setType] = useState<AssignmentType>('MCQ');
  const [difficulty, setDifficulty] = useState<Difficulty>('Medium');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<any[]>([]);
  
  // NEW: State to store the saved ID
  const [savedId, setSavedId] = useState<string | null>(null);

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
      // NEW: Set the ID so it displays on screen
      setSavedId(assignment.id); 
      alert("Assignment Saved Successfully!");
    } catch (e) {
      alert("Error saving assignment");
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Create New Assignment</h1>
      
      {/* NEW: Copy ID Section */}
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
            className="w-full p-2 border rounded mt-1" 
            placeholder="e.g. Photosynthesis, Linear Algebra"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Type</label>
            <select 
              value={type} 
              onChange={(e) => setType(e.target.value as AssignmentType)}
              className="w-full p-2 border rounded mt-1"
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
              className="w-full p-2 border rounded mt-1"
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
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Generating Questions with AI...' : 'Generate Assignment'}
        </button>
      </div>

      {/* Preview Section */}
      {generatedQuestions.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Preview ({generatedQuestions.length} Questions)</h2>
          <div className="space-y-4">
            {generatedQuestions.map((q, i) => (
              <div key={i} className="bg-white p-4 rounded shadow border-l-4 border-indigo-500">
                <p className="font-medium text-gray-900">Q{i+1}: {q.text}</p>
                {/* Preview Options if they exist */}
                {q.options && q.options.length > 0 && (
                  <ul className="mt-2 space-y-1 ml-4 list-disc text-gray-600">
                    {q.options.map((opt: string, idx: number) => (
                      <li key={idx}>{opt}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
          <button 
            onClick={handleSave}
            className="mt-6 w-full bg-green-600 text-white py-3 rounded text-lg font-bold hover:bg-green-700"
          >
            Save & Publish Assignment
          </button>
        </div>
      )}
    </div>
  );
};

export default AssignmentCreator;