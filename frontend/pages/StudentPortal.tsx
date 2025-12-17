import React, { useState } from 'react';
import { autoGradeSubmission, getAssignment } from '../services/geminiService';
import { getCurrentUser } from '../services/authService';

const StudentPortal: React.FC = () => {
  const [step, setStep] = useState(1);
  const [assignmentId, setAssignmentId] = useState('');
  const [assignmentData, setAssignmentData] = useState<any>(null);
  
  // Stores answers as { "questionId": "User Answer" }
  const [answers, setAnswers] = useState<Record<string, string>>({});
  
  const [feedback, setFeedback] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // 1. Load Assignment
  const handleLoadAssignment = async () => {
    if (!assignmentId) return alert("Please enter an ID");
    setLoading(true);
    try {
      const data = await getAssignment(assignmentId.trim());
      setAssignmentData(data);
      // Initialize empty answers
      const initialAnswers: Record<string, string> = {};
      data.questions.forEach((q: any) => initialAnswers[q.id] = "");
      setAnswers(initialAnswers);
      setStep(2);
    } catch (error) {
      alert("Assignment not found! Check the ID.");
    } finally {
      setLoading(false);
    }
  };

  // 2. Handle Input Change
  const handleAnswerChange = (questionId: string, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  // 3. Submit
  const handleSubmit = async () => {
    const user = getCurrentUser();
    if (!user) return alert("Please login first");

    setLoading(true);
    
    // For this demo, we join all answers into one block to send to the current backend
    // In a production app, you would send the 'answers' object directly.
    const formattedSubmission = Object.entries(answers)
      .map(([qId, ans], idx) => `Q${idx + 1}: ${ans}`)
      .join("\n\n");

    try {
      const result = await autoGradeSubmission(assignmentId, user.id, formattedSubmission);
      setFeedback(result);
    } catch (error) {
      alert("Error submitting assignment.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Student Portal</h1>

      {/* STEP 1: LOAD */}
      {step === 1 && (
        <div className="bg-white p-8 rounded-xl shadow-md border border-gray-100">
          <h2 className="text-xl font-semibold mb-4">Start Assignment</h2>
          <div className="flex gap-4">
            <input 
              className="flex-1 border border-gray-300 p-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" 
              placeholder="Paste Assignment ID here..." 
              value={assignmentId}
              onChange={(e) => setAssignmentId(e.target.value)}
            />
            <button 
              onClick={handleLoadAssignment} 
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Start'}
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: TAKE QUIZ */}
      {step === 2 && assignmentData && (
        <div className="space-y-8 animate-fade-in">
          <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-blue-900">{assignmentData.title}</h2>
              <p className="text-blue-600">{assignmentData.topic} • {assignmentData.questions.length} Questions</p>
            </div>
            <button onClick={() => setStep(1)} className="text-sm text-gray-500 underline">Exit</button>
          </div>

          <div className="space-y-6">
            {assignmentData.questions.map((q: any, index: number) => (
              <div key={q.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  {index + 1}. {q.text}
                </h3>

                {/* LOGIC: Show Options if they exist, otherwise Show Text Area */}
                {q.options && q.options.length > 0 ? (
                  <div className="space-y-3 pl-2">
                    {q.options.map((opt: string) => (
                      <label key={opt} className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                        <input
                          type="radio"
                          name={q.id}
                          value={opt}
                          checked={answers[q.id] === opt}
                          onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                          className="w-5 h-5 text-blue-600"
                        />
                        <span className="text-gray-700">{opt}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <textarea 
                    className="w-full border border-gray-300 p-3 rounded-lg h-32 focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="Type your answer here..."
                    value={answers[q.id] || ''}
                    onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4">
            <button 
              onClick={handleSubmit} 
              disabled={loading}
              className="bg-green-600 text-white px-10 py-4 rounded-xl font-bold text-lg hover:bg-green-700 shadow-lg transition disabled:opacity-50"
            >
              {loading ? 'Grading...' : 'Submit Assignment'}
            </button>
          </div>

          {/* AI FEEDBACK */}
          {feedback && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold">Grading Report</h2>
                  <button onClick={() => setFeedback(null)} className="text-gray-500 hover:text-gray-700 text-xl">✕</button>
                </div>
                
                <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
                  <div className={`text-5xl font-bold ${feedback.score >= 70 ? 'text-green-600' : 'text-orange-500'}`}>
                    {Math.round(feedback.score)}%
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">Overall Score</div>
                    <div className="text-sm text-gray-500">AI Analysis Complete</div>
                  </div>
                </div>

                <div className="prose prose-blue max-w-none">
                  <h3 className="text-lg font-semibold mb-2">Detailed Feedback</h3>
                  <p className="whitespace-pre-wrap text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg border">
                    {feedback.feedback}
                  </p>
                </div>

                <button 
                  onClick={() => window.location.reload()} 
                  className="mt-8 w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700"
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StudentPortal;