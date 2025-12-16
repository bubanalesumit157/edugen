import React, { useState } from 'react';
import { autoGradeSubmission, getAssignment } from '../services/geminiService';
import { getCurrentUser } from '../services/authService';

const StudentPortal = () => {
  const [step, setStep] = useState(1); // 1 = Search, 2 = Answer
  const [assignmentId, setAssignmentId] = useState('');
  const [assignmentData, setAssignmentData] = useState<any>(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Step 1: Fetch the Assignment Details
  const handleLoadAssignment = async () => {
    if (!assignmentId) return alert("Please enter an ID");
    setLoading(true);
    try {
      const data = await getAssignment(assignmentId);
      setAssignmentData(data);
      setStep(2); // Move to next screen
    } catch (error) {
      alert("Assignment not found! Check the ID.");
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Submit the Answer
  const handleSubmit = async () => {
    const user = getCurrentUser();
    if (!user) return alert("Please login first");

    setLoading(true);
    try {
      const result = await autoGradeSubmission(assignmentId, user.id, answer);
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

      {/* --- STEP 1: LOAD ASSIGNMENT --- */}
      {step === 1 && (
        <div className="bg-white p-8 rounded-xl shadow-md border border-gray-100">
          <h2 className="text-xl font-semibold mb-4">Load Assignment</h2>
          <div className="flex gap-4">
            <input 
              className="flex-1 border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none" 
              placeholder="Paste Assignment ID here (e.g., 550e84...)" 
              value={assignmentId}
              onChange={(e) => setAssignmentId(e.target.value.trim())}
            />
            <button 
              onClick={handleLoadAssignment} 
              disabled={loading}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Load'}
            </button>
          </div>
        </div>
      )}

      {/* --- STEP 2: VIEW & ANSWER --- */}
      {step === 2 && assignmentData && (
        <div className="space-y-6">
          {/* Assignment Header */}
          <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-100">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold text-indigo-900">{assignmentData.title}</h2>
                <p className="text-indigo-600 mt-1">Topic: {assignmentData.topic} • Difficulty: {assignmentData.difficulty}</p>
              </div>
              <button onClick={() => setStep(1)} className="text-sm text-gray-500 underline">Change Assignment</button>
            </div>
          </div>

          {/* Question Display */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-3">Question:</h3>
            <div className="prose bg-gray-50 p-4 rounded-lg text-gray-800">
              {/* Display the first question text (simplification for demo) */}
              {assignmentData.questions && assignmentData.questions[0] ? (
                <p>{assignmentData.questions[0].text}</p>
              ) : (
                <p>No questions found in this assignment data.</p>
              )}
            </div>
          </div>

          {/* Answer Input */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">Your Answer</label>
            <textarea 
              className="w-full border border-gray-300 p-4 rounded-lg h-40 focus:ring-2 focus:ring-indigo-500 outline-none" 
              placeholder="Type your answer here..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
            />
            <div className="mt-4 flex justify-end">
              <button 
                onClick={handleSubmit} 
                disabled={loading}
                className="bg-green-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-green-700 transition shadow-lg disabled:opacity-50"
              >
                {loading ? 'Grading...' : 'Submit & Grade'}
              </button>
            </div>
          </div>

          {/* AI Feedback Result */}
          {feedback && (
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-300 mt-6 animate-fade-in">
              <div className="flex items-center gap-4 mb-4">
                <div className={`text-4xl font-bold ${feedback.score >= 70 ? 'text-green-600' : 'text-orange-500'}`}>
                  {feedback.score}%
                </div>
                <div className="text-gray-600 font-medium">AI Grading Result</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <p className="whitespace-pre-wrap text-gray-700 leading-relaxed">{feedback.feedback}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StudentPortal;