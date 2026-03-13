/**
 * Development entry point for testing the widget
 */

import * as React from 'react';
import ReactDOM from 'react-dom/client';
import { AskDocsWidget } from './AskDocsWidget';
import './styles/globals.css';

const root = document.getElementById('root');

if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <AskDocsWidget
            baseUrl="http://localhost:8000"
            showStatus={true}
            showTokenBudget={true}
            showThemeToggle={true}
            placeholder="Ask about your documentation..."
          />
        </div>
      </div>
    </React.StrictMode>
  );
}
