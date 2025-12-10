import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AssignmentCreator from './pages/AssignmentCreator';
import StudentPortal from './pages/StudentPortal';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AssignmentsList from './pages/AssignmentsList';

const App: React.FC = () => {
  return (
    <HashRouter>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="ml-64 flex-1 overflow-x-hidden">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<AssignmentCreator />} />
            <Route path="/assignments" element={<AssignmentsList />} />
            <Route path="/student-portal" element={<StudentPortal />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
};

export default App;