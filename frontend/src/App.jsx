import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import FileUpload from './components/FileUpload';
import DashboardPage from './pages/DashboardPage';
import ValidationReport from './pages/ValidationReport';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50 flex-col">
        {/* Full width navbar */}
        <nav className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 w-full">
          <div className="flex items-center h-full">
            <div className="w-64 h-full flex items-center px-4">
              <h1 className="text-xl font-semibold text-gray-800">Validate MD</h1>
            </div>
          </div>
          <div className="flex-1 flex justify-end items-center h-full px-6">
            <div className="flex items-center space-x-4">
              <button className="relative p-2 text-gray-500 hover:text-gray-700 focus:outline-none">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500"></span>
              </button>
              <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-sm font-medium text-gray-600">U</span>
              </div>
            </div>
          </div>
        </nav>

        <div className="flex flex-1 overflow-hidden">
          <Sidebar onUploadClick={() => document.getElementById('file-upload')?.click()} />

          {/* Main content */}
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={
                <DashboardPage />
              } />
              <Route path="/validation-reports" element={
                <ValidationReport />
              } />

              <Route path="/upload" element={
                <FileUpload />
              } />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;