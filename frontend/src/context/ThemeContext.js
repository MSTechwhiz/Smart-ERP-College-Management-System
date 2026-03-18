import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [themeMode, setThemeMode] = useState(() => {
    return localStorage.getItem('theme-mode') || 'light';
  });

  const [colorScheme, setColorScheme] = useState(() => {
    return localStorage.getItem('color-scheme') || 'blue';
  });

  useEffect(() => {
    const root = window.document.documentElement;

    // Apply Theme Mode (light, dark, system, institutional)
    let appliedTheme = themeMode;
    if (themeMode === 'system') {
      appliedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } else if (themeMode === 'institutional') {
      appliedTheme = 'light'; // Institutional is primarily a branded light theme
    }

    // Update classes for light/dark
    if (appliedTheme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }

    // Apply Color Scheme Class
    // Remove existing theme classes
    const themeClasses = Array.from(root.classList).filter(c => c.startsWith('theme-'));
    themeClasses.forEach(c => root.classList.remove(c));

    // Add new theme class
    if (themeMode === 'institutional') {
      root.classList.add('theme-blue'); // Default institutional color
    } else {
      root.classList.add(`theme-${colorScheme}`);
    }

    // Save to localStorage
    localStorage.setItem('theme-mode', themeMode);
    localStorage.setItem('color-scheme', colorScheme);

    // Listen for system theme changes if in system mode
    if (themeMode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        if (mediaQuery.matches) {
          root.classList.add('dark');
          root.classList.remove('light');
        } else {
          root.classList.add('light');
          root.classList.remove('dark');
        }
      };
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [themeMode, colorScheme]);

  return (
    <ThemeContext.Provider value={{
      theme: themeMode,
      setTheme: setThemeMode, // Keep compatibility with existing code
      themeMode,
      setThemeMode,
      colorScheme,
      setColorScheme
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
