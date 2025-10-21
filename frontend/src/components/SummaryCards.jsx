import React from 'react';

const SummaryCards = ({ summary }) => {
  const cards = [
    {
      title: 'Total Providers',
      value: summary.total_providers,
      icon: '👥',
      color: '#3498db'
    },
    {
      title: 'Successful Lookups',
      value: summary.successful_lookups,
      icon: '✅',
      color: '#2ecc71',
      subtitle: `${summary.success_rate.toFixed(1)}% success rate`
    },
    {
      title: 'Perfect Matches',
      value: summary.perfect_matches,
      icon: '🎯',
      color: '#9b59b6',
      subtitle: `${summary.match_rate.toFixed(1)}% match rate`
    },
    {
      title: 'AI Insights',
      value: summary.ai_insights_count,
      icon: '🧠',
      color: '#e74c3c'
    }
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <div key={index} className="flex items-center gap-4 rounded-md border bg-white p-4 shadow-sm">
          <div className="flex h-12 w-12 items-center justify-center rounded-md text-xl" style={{ backgroundColor: card.color }}>
            {card.icon}
          </div>
          <div>
            <h3 className="text-2xl font-bold">{card.value}</h3>
            <p className="text-sm text-gray-600">{card.title}</p>
            {card.subtitle && <span className="text-xs text-gray-500">{card.subtitle}</span>}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SummaryCards;