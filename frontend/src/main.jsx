import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/utils/AuthContext';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
        <Toaster
          position="top-right"
          containerStyle={{
            top: '100px',
            right: '20px',
          }}
          toastOptions={{
            duration: 4000,
            className: 'backdrop-blur-sm',
            style: {
              background: 'rgb(var(--bg-header))',
              color: 'rgb(var(--text-primary))',
              border: '1px solid rgb(var(--border))',
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            },
            success: {
              iconTheme: {
                primary: 'rgb(16, 185, 129)',
                secondary: 'white',
              },
            },
            error: {
              iconTheme: {
                primary: 'rgb(244, 63, 94)',
                secondary: 'white',
              },
            },
            warning: {
              iconTheme: {
                primary: 'rgb(245, 158, 11)',
                secondary: 'white',
              },
            },
            info: {
              iconTheme: {
                primary: 'rgb(59, 130, 246)',
                secondary: 'white',
              },
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
