import React from 'react';
import ChatBox from './ChatBox';
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center">
      <ChatBox />
      <Analytics />
    </div>
  );
}

export default App;