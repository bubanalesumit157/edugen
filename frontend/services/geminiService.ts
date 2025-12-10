// src/services/geminiService.ts
import axios from 'axios';
import { Assignment, AssignmentType, Difficulty } from '../types';

const API_URL = 'http://localhost:8000';

export const generateContent = async (topic: string, type: AssignmentType, difficulty: Difficulty) => {
  try {
    // Calls Backend Member 2 -> who calls Member 3 (RAG)
    const response = await axios.post(`${API_URL}/assignments/generate`, {
      topic,
      type,
      difficulty
    });
    return response.data;
  } catch (error) {
    console.error("API Error", error);
    return [];
  }
};

export const autoGradeSubmission = async (question: string, answer: string, rubric: string) => {
  try {
    // Calls Backend Member 2 -> who calls Member 4 (ML)
    const response = await axios.post(`${API_URL}/student/grade`, {
      question,
      answer,
      rubric
    });
    return response.data;
  } catch (error) {
    console.error("Grading Error", error);
    return { score: 0, feedback: "Error connecting to AI grading service." };
  }
};

export const analyzeAssignment = async (assignment: Assignment) => {
  try {
    const response = await axios.post(`${API_URL}/assignments/${assignment.id}/analyze`);
    return response.data.text;
  } catch (error) {
    return "Could not perform audit at this time.";
  }
};