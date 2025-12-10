export enum AssignmentType {
  MCQ = 'Multiple Choice',
  WRITTEN = 'Written Response',
  PROJECT = 'Project Based'
}

export enum Difficulty {
  EASY = 'Elementary',
  MEDIUM = 'Intermediate',
  HARD = 'Advanced'
}

export interface Question {
  id: string;
  text: string;
  options?: string[]; // Only for MCQ
  correctAnswer?: string; // For auto-grading
  rubric?: string; // For written
}

export interface Assignment {
  id: string;
  title: string;
  subject: string;
  type: AssignmentType;
  difficulty: Difficulty;
  questions: Question[];
  createdAt: string;
  dueDate: string;
  status: 'Draft' | 'Published' | 'Archived';
}

export interface StudentSubmission {
  studentName: string;
  assignmentId: string;
  answers: { questionId: string; answer: string }[];
  grade?: number;
  feedback?: string;
  submittedAt: string;
}

export interface AnalyticsData {
  subject: string;
  score: number;
  fullMark: number;
  classAverage: number;
}