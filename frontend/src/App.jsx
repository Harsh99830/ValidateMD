import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import ResultsTable from './components/ResultsTable';
import SummaryCards from './components/SummaryCards';

function App() {
  const [validationData, setValidationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleValidationComplete = (data) => {
    setValidationData(data);
    setError(null);
  };

  const handleValidationError = (errorMsg) => {
    setError(errorMsg);
    setValidationData(null);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b bg-white">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">🏥 NPI Provider Validation Dashboard</h1>
          <p className="text-gray-600 mt-1">Validate healthcare provider data against NPI registry</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {error && (
          <div className="rounded-md border border-red-300 bg-red-50 text-red-700 px-4 py-3">
            ❌ {error}
          </div>
        )}

        <FileUpload
          onValidationComplete={handleValidationComplete}
          onValidationError={handleValidationError}
          onLoading={handleLoading}
        />

        {loading && (
          <div className="flex items-center gap-3 rounded-md border bg-white p-4 shadow-sm">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-blue-500"></div>
            <p className="text-sm text-gray-700">Validating providers against NPI registry...</p>
          </div>
        )}

        {validationData && (
          <div className="space-y-6">
            <SummaryCards summary={validationData.summary} />
            <Dashboard data={validationData} />
            <ResultsTable results={validationData.results} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;