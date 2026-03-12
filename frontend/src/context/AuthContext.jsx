import { createContext, useContext, useState, useCallback } from 'react';

const ADMIN_USER = 'admin';
const ADMIN_PASS = 'admin@2025';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAdmin, setIsAdmin] = useState(false);

  const login = useCallback((username, password) => {
    if (username === ADMIN_USER && password === ADMIN_PASS) {
      setIsAdmin(true);
      return { ok: true };
    }
    return { ok: false, error: 'Invalid username or password.' };
  }, []);

  const logout = useCallback(() => {
    setIsAdmin(false);
  }, []);

  return (
    <AuthContext.Provider value={{ isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
