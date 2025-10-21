import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = ({ data }) => {
  const { summary } = data;

  // Data for match status pie chart
  const matchStatusData = [
    { name: 'Perfect Matches', value: summary.perfect_matches, color: '#2ecc71' },
    { name: 'With Mismatches', value: summary.successful_lookups - summary.perfect_matches, color: '#f39c12' },
    { name: 'Lookup Failed', value: summary.total_providers - summary.successful_lookups, color: '#e74c3c' }
  ];

  // Data for mismatch types bar chart
  const mismatchData = Object.entries(summary.mismatch_types || {}).map(([type, count]) => ({
    type,
    count
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`${label}: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Validation Analytics</h2>
      
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-md border bg-white p-4 shadow-sm">
          <h3 className="mb-2 text-sm font-medium text-gray-700">Match Status Distribution</h3>
          <ResponsiveContainer width="100%" height={360}>
            <PieChart margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
              <Pie
                data={matchStatusData}
                cx="40%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                innerRadius={50}
                fill="#8884d8"
                dataKey="value"
                paddingAngle={2}
              >
                {matchStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ paddingLeft: 10 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-md border bg-white p-4 shadow-sm">
          <h3 className="mb-2 text-sm font-medium text-gray-700">Mismatch Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mismatchData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3498db" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-md border bg-white p-4 text-center shadow-sm">
          <span className="block text-sm text-gray-600">Success Rate</span>
          <span className="text-2xl font-bold">{summary.success_rate.toFixed(1)}%</span>
        </div>
        <div className="rounded-md border bg-white p-4 text-center shadow-sm">
          <span className="block text-sm text-gray-600">Match Rate</span>
          <span className="text-2xl font-bold">{summary.match_rate.toFixed(1)}%</span>
        </div>
        <div className="rounded-md border bg-white p-4 text-center shadow-sm">
          <span className="block text-sm text-gray-600">AI Insights</span>
          <span className="text-2xl font-bold">{summary.ai_insights_count}</span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;