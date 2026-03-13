/**
 * Development entry point for testing the widget
 */

import * as React from 'react';
import ReactDOM from 'react-dom/client';
import { AskDocsWidget } from './AskDocsWidget';

const root = document.getElementById('root');

if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <AskDocsWidget
        baseUrl="http://localhost:8000"
        showStatus={true}
        showTokenBudget={true}
        placeholder="Ask about your documentation..."
      />
    </React.StrictMode>
  );
}
