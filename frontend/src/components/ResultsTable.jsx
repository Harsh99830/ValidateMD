import React, { useState } from 'react';

const ResultsTable = ({ results }) => {
  const [expandedRow, setExpandedRow] = useState(null);

  const toggleRow = (index) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PERFECT_MATCH':
        return { icon: '✅', color: '#2ecc71', text: 'Perfect Match' };
      case 'NOT_FOUND':
        return { icon: '❌', color: '#e74c3c', text: 'NPI Not Found' };
      case 'ERROR':
        return { icon: '⚠️', color: '#f39c12', text: 'Lookup Error' };
      default:
        return { icon: '🟡', color: '#f39c12', text: `${status.replace('_', ' ')}` };
    }
  };

  return (
    <div className="space-y-3">
      <h2 className="text-xl font-semibold">📋 Validation Results</h2>
      
      <div className="overflow-hidden rounded-md border bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Provider</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">NPI Number</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Mismatches</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">AI Insights</th>
              <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {results.map((result, index) => {
              const statusInfo = getStatusIcon(result.match_status);
              
              return (
                <React.Fragment key={index}>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-2">
                      <strong>{result.csv_data.first_name} {result.csv_data.last_name}</strong>
                    </td>
                    <td className="px-4 py-2">{result.csv_data.npi_number}</td>
                    <td className="px-4 py-2">
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium text-white" style={{ backgroundColor: statusInfo.color }}>
                        <span>{statusInfo.icon}</span> {statusInfo.text}
                      </span>
                    </td>
                    <td className="px-4 py-2">{result.mismatches.length}</td>
                    <td className="px-4 py-2">{result.ai_insights.length}</td>
                    <td className="px-4 py-2">
                      <button 
                        className="text-blue-600 hover:underline"
                        onClick={() => toggleRow(index)}
                      >
                        {expandedRow === index ? '▲ Hide' : '▼ Details'}
                      </button>
                    </td>
                  </tr>
                  
                  {expandedRow === index && (
                    <tr className="bg-gray-50">
                      <td colSpan="6" className="px-4 py-3">
                        <div className="space-y-4">
                          <div>
                            <h4 className="mb-2 text-sm font-semibold text-gray-800">Data Comparison</h4>
                            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                              <div className="rounded-md border bg-white p-3">
                                <label className="text-xs font-medium text-gray-600">Status</label>
                                <div className="mt-1 text-sm">
                                  <span className="mr-3 text-gray-700">CSV: {result.csv_data.Status}</span>
                                  <span className="text-gray-700">NPI: {result.npi_data.Status}</span>
                                </div>
                              </div>
                              <div className="rounded-md border bg-white p-3">
                                <label className="text-xs font-medium text-gray-600">Specialty</label>
                                <div className="mt-1 text-sm">
                                  <span className="mr-3 text-gray-700">CSV: {result.csv_data.Speciality}</span>
                                  <span className="text-gray-700">NPI: {result.npi_data.Speciality}</span>
                                </div>
                              </div>
                              <div className="rounded-md border bg-white p-3">
                                <label className="text-xs font-medium text-gray-600">License</label>
                                <div className="mt-1 text-sm">
                                  <span className="mr-3 text-gray-700">CSV: {result.csv_data.License_number}</span>
                                  <span className="text-gray-700">NPI: {result.npi_data.License_number}</span>
                                </div>
                              </div>
                              <div className="rounded-md border bg-white p-3">
                                <label className="text-xs font-medium text-gray-600">Address</label>
                                <div className="mt-1 text-sm">
                                  <span className="mr-3 text-gray-700">CSV: {result.csv_data.Address}</span>
                                  <span className="text-gray-700">NPI: {result.npi_data.Address}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {result.mismatches.length > 0 && (
                            <div>
                              <h4 className="mb-1 text-sm font-semibold text-gray-800">⚠️ Data Mismatches</h4>
                              <ul className="list-disc space-y-1 pl-5 text-sm text-gray-700">
                                {result.mismatches.map((mismatch, idx) => (
                                  <li key={idx}>{mismatch}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {result.ai_insights.length > 0 && (
                            <div>
                              <h4 className="mb-1 text-sm font-semibold text-gray-800">🧠 AI Insights</h4>
                              <ul className="list-disc space-y-1 pl-5 text-sm text-gray-700">
                                {result.ai_insights.map((insight, idx) => (
                                  <li key={idx}>{insight}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsTable;