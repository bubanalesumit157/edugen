// project_clean_archive/frontend/App.tsx
import React from 'react';
import { HashRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AssignmentCreator from './pages/AssignmentCreator';
import StudentPortal from './pages/StudentPortal';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AssignmentsList from './pages/AssignmentsList';
import Login from './pages/login'; // <--- IMPORT LOGIN

// Layout component for authenticated pages (Sidebar + Content)
const MainLayout = () => (
  <div className="flex min-h-screen bg-slate-50">
    <Sidebar />
    <main className="ml-64 flex-1 overflow-x-hidden">
      <Outlet />
    </main>
  </div>
);

const App: React.FC = () => {
  return (
    <HashRouter>
      <Routes>
        {/* PUBLIC ROUTE: Login (No Sidebar) */}
        <Route path="/login" element={<Login />} />

        {/* PROTECTED ROUTES: (With Sidebar) */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/create" element={<AssignmentCreator />} />
          <Route path="/assignments" element={<AssignmentsList />} />
          <Route path="/student-portal" element={<StudentPortal />} />
          <Route path="/analytics" element={<AnalyticsDashboard />} />
        </Route>

        {/* Catch-all: Redirect unknown URLs to Login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </HashRouter>
  );
};

export default App;