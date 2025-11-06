import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { ChevronDown, ChevronUp } from 'lucide-react';

const Sidebar = ({ onUploadClick }) => {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  
  // Sample history data - in a real app, this would come from your state management
  const historyItems = [
    { id: 1, name: 'Today', path: '/history/today' },
    { id: 2, name: 'Yesterday', path: '/history/yesterday' },
    { id: 3, name: 'Last 7 days', path: '/history/last-week' },
    { id: 4, name: 'Last 30 days', path: '/history/last-month' },
  ];
  const menuItems = [
    { 
      name: 'Upload Data', 
      path: '/upload', 
      icon: '📤',
      className: 'mb-4' // Add margin bottom to create space after this item
    },
    { name: 'Dashboard', path: '/', icon: '📊' },
    
    { name: 'Validation Reports', path: '/validation-reports', icon: '📋' },
    { name: 'Provider Needed Review', path: '/provider-review', icon: '👨‍⚕️' },
    { name: 'See All Providers', path: '/providers', icon: '👥' },
    { 
      name: 'History', 
      path: '/history', 
      icon: '⏱️',
      hasDropdown: true
    },
  ];

  const bottomMenuItems = [
    { name: 'Settings', path: '/settings', icon: '⚙️' },
    { name: 'Logout', path: '/logout', icon: '🚪' },
  ];

  const activeLink = 'bg-blue-50 text-blue-600 border-r-4 border-blue-500';
  const normalLink = 'hover:bg-gray-100 text-gray-700';

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-[calc(100vh-4rem)] overflow-y-auto">
      {/* Sidebar content */}
      
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {menuItems.map((item) => (
            <li key={item.name}>
              {item.path === '/upload' ? (
                <div className={`${item.className || ''}`}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg transition-colors bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 w-[90%] mx-auto text-sm h-8 ${isActive ? 'ring-2 ring-offset-2 ring-blue-500' : ''}`
                    }
                  >
                    <span className="text-base">{item.icon}</span>
                    <span>{item.name}</span>
                  </NavLink>
                </div>
              ) : item.hasDropdown ? (
                <div>
                  <button
                    onClick={() => item.name === 'History' && setIsHistoryOpen(!isHistoryOpen)}
                    className={`flex items-center justify-between w-full px-4 py-3 rounded-lg transition-colors ${normalLink}`}
                  >
                    <div className="flex items-center">
                      <span className="mr-3 text-lg">{item.icon}</span>
                      <span className="font-medium">{item.name}</span>
                    </div>
                    {isHistoryOpen ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </button>
                  {isHistoryOpen && (
                    <div className="ml-8 mt-1 space-y-1">
                      {historyItems.map((historyItem) => (
                        <NavLink
                          key={historyItem.id}
                          to={historyItem.path}
                          className={({ isActive }) =>
                            `block px-3 py-2 text-sm rounded-md transition-colors ${isActive ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`
                          }
                        >
                          {historyItem.name}
                        </NavLink>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center px-4 py-3 rounded-lg transition-colors ${isActive ? activeLink : normalLink}`
                  }
                >
                  <span className="mr-3 text-lg">{item.icon}</span>
                  <span className="font-medium">{item.name}</span>
                </NavLink>
              )}
            </li>
          ))}
        </ul>
      </nav>

      <div className="border-t p-4">
        <ul className="space-y-1">
          {bottomMenuItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg transition-colors ${isActive ? activeLink : normalLink}`
                }
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;
