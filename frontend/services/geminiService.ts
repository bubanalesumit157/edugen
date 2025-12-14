// src/services/geminiService.ts
import axios from 'axios';
import { Assignment, AssignmentType, Difficulty } from '../types';

const API_URL = 'http://localhost:8000';

/**
 * Generates assignment questions using the Backend RAG Pipeline.
 */
export const generateContent = async (topic: string, type: AssignmentType, difficulty: Difficulty) => {
  try {
    const response = await axios.post(`${API_URL}/assignments/generate`, {
      topic,
      type,
      difficulty
    });
    // The backend returns a list of questions directly
    return response.data;
  } catch (error) {
    console.error("API Error generating content:", error);
    return [];
  }
};

/**
 * Submits a student answer for AI grading and database storage.
 * Updated to match schemas.SubmissionCreate on the backend.
 */
export const autoGradeSubmission = async (assignmentId: string, studentId: number, answerText: string) => {
  try {
    const response = await axios.post(`${API_URL}/student/grade`, {
      assignment_id: assignmentId, // Matches schemas.py: assignment_id
      student_id: studentId,       // Matches schemas.py: student_id
      answer_text: answerText      // Matches schemas.py: answer_text
    });
    return response.data; // Returns { score, feedback }
  } catch (error) {
    console.error("Grading Error:", error);
    return { score: 0, feedback: "Error connecting to grading service." };
  }
};

/**
 * Audit an assignment using the Pedagogical Validator.
 */
export const analyzeAssignment = async (assignment: Assignment) => {
  try {
    const response = await axios.post(`${API_URL}/assignments/${assignment.id}/analyze`);
    return response.data.text;
  } catch (error) {
    console.error("Audit Error:", error);
    return "Could not perform audit at this time.";
  }
};