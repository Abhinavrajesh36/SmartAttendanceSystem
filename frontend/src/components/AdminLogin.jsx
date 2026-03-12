import { useState, useEffect, useRef } from 'react';
import { Lock, User, Eye, EyeOff, Shield, X, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const css = `
  .login-overlay {
    position: fixed; inset: 0;
    background: rgba(2, 8, 23, 0.88);
    backdrop-filter: blur(10px);
    display: flex; align-items: center; justify-content: center;
    z-index: 9999; padding: 20px;
    animation: overlayIn 0.2s ease;
  }
  @keyframes overlayIn { from{opacity:0} to{opacity:1} }

  .login-card {
    background: #0a1628;
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 20px;
    padding: 36px;
    width: 100%; max-width: 400px;
    box-shadow: 0 0 80px rgba(0,212,255,0.08), 0 0 0 1px rgba(0,212,255,0.05);
    animation: cardIn 0.3s cubic-bezier(0.34,1.56,0.64,1);
  }
  @keyframes cardIn { from{opacity:0;transform:scale(0.92) translateY(16px)} to{opacity:1;transform:scale(1) translateY(0)} }

  .login-input-wrap {
    position: relative; margin-bottom: 14px;
  }
  .login-input {
    width: 100%; box-sizing: border-box;
    background: rgba(0,212,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.14) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 11px 42px 11px 40px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    outline: none !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
  }
  .login-input:focus {
    border-color: rgba(0,212,255,0.45) !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.08) !important;
  }
  .login-input::placeholder { color: #334155 !important; }
  .login-input-icon {
    position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
    pointer-events: none;
  }
  .login-input-action {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    background: none; border: none; cursor: pointer; padding: 4px;
    color: #334155; transition: color 0.15s;
  }
  .login-input-action:hover { color: #67e8f9; }

  .login-btn {
    width: 100%; padding: 13px;
    background: linear-gradient(135deg, #0891b2, #0e7490);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 10px; color: #e0f9ff;
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem; font-weight: 700;
    letter-spacing: 0.1em; cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    transition: all 0.18s; margin-top: 6px;
  }
  .login-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #06b6d4, #0891b2);
    box-shadow: 0 0 28px rgba(0,212,255,0.3);
    transform: translateY(-1px);
  }
  .login-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  .login-error {
    background: rgba(244,63,94,0.08);
    border: 1px solid rgba(244,63,94,0.25);
    border-radius: 8px; padding: 10px 14px;
    color: #fb7185; font-size: 0.82rem;
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 14px;
    animation: shakeErr 0.35s ease;
  }
  @keyframes shakeErr {
    0%,100%{transform:translateX(0)}
    20%{transform:translateX(-6px)}
    40%{transform:translateX(6px)}
    60%{transform:translateX(-4px)}
    80%{transform:translateX(4px)}
  }

  .login-close {
    position: absolute; top: 16px; right: 16px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; width: 30px; height: 30px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; color: #475569; transition: all 0.15s;
  }
  .login-close:hover { background: rgba(244,63,94,0.1); color: #fb7185; border-color: rgba(244,63,94,0.2); }

  @keyframes spin { to{transform:rotate(360deg)} }
  @keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0   rgba(0,212,255,0.5); }
    70%  { box-shadow: 0 0 0 12px rgba(0,212,255,0); }
    100% { box-shadow: 0 0 0 0   rgba(0,212,255,0); }
  }
`;

const AdminLogin = ({ onClose }) => {
  const { login } = useAuth();
  const [username,  setUsername]  = useState('');
  const [password,  setPassword]  = useState('');
  const [showPass,  setShowPass]  = useState(false);
  const [error,     setError]     = useState('');
  const [loading,   setLoading]   = useState(false);
  const [success,   setSuccess]   = useState(false);
  const userRef = useRef(null);

  useEffect(() => { userRef.current?.focus(); }, []);

  // Close on Escape key
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  const handleSubmit = async e => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Please fill in both fields.'); return;
    }
    setLoading(true); setError('');
    // Small artificial delay for UX feel
    await new Promise(r => setTimeout(r, 600));
    const result = login(username.trim(), password);
    if (result.ok) {
      setSuccess(true);
      setTimeout(onClose, 800);
    } else {
      setError(result.error);
      setLoading(false);
    }
  };

  return (
    <>
      <style>{css}</style>
      <div className="login-overlay" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
        <div className="login-card" style={{ position: 'relative' }}>

          {/* Close button */}
          <button className="login-close" onClick={onClose}><X size={14}/></button>

          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '28px' }}>
            <div style={{
              width: '60px', height: '60px', borderRadius: '16px',
              background: 'rgba(0,212,255,0.07)', border: '1px solid rgba(0,212,255,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 14px',
              animation: success ? 'pulse-ring 0.6s ease' : 'none',
            }}>
              <Shield size={26} color={success ? '#10b981' : '#00d4ff'}
                style={{ transition: 'color 0.3s' }}/>
            </div>
            <h2 style={{
              fontFamily: 'Orbitron, monospace', fontSize: '1.1rem',
              fontWeight: 900, color: '#f1f5f9', letterSpacing: '0.1em',
              margin: '0 0 5px',
            }}>
              ADMIN ACCESS
            </h2>
            <p style={{ color: '#475569', fontSize: '0.8rem', margin: 0 }}>
              Enter credentials to unlock admin features
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="login-error" key={error}>
              <Lock size={14} style={{ flexShrink: 0 }}/> {error}
            </div>
          )}

          {/* Success */}
          {success && (
            <div style={{
              background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.3)',
              borderRadius: '8px', padding: '10px 14px', color: '#34d399',
              fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '8px',
              marginBottom: '14px',
            }}>
              <Shield size={14}/> Admin access granted — welcome!
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {/* Username */}
            <div className="login-input-wrap">
              <span className="login-input-icon"><User size={15} color="#334155"/></span>
              <input
                ref={userRef}
                className="login-input"
                type="text"
                placeholder="Username"
                value={username}
                onChange={e => { setUsername(e.target.value); setError(''); }}
                autoComplete="username"
                disabled={loading || success}
              />
            </div>

            {/* Password */}
            <div className="login-input-wrap">
              <span className="login-input-icon"><Lock size={15} color="#334155"/></span>
              <input
                className="login-input"
                type={showPass ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={e => { setPassword(e.target.value); setError(''); }}
                autoComplete="current-password"
                disabled={loading || success}
              />
              <button
                type="button"
                className="login-input-action"
                onClick={() => setShowPass(v => !v)}
                tabIndex={-1}
              >
                {showPass ? <EyeOff size={15}/> : <Eye size={15}/>}
              </button>
            </div>

            {/* Hint */}
            <p style={{ color: '#1e3a4a', fontSize: '0.7rem', marginBottom: '14px',
              fontFamily: 'Orbitron, monospace', letterSpacing: '0.05em', textAlign: 'center' }}>
              DEFAULT: admin / admin@2025
            </p>

            <button className="login-btn" type="submit" disabled={loading || success}>
              {loading ? (
                <>
                  <div style={{ width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#67e8f9', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}/>
                  AUTHENTICATING...
                </>
              ) : success ? (
                <><Shield size={14}/> ACCESS GRANTED</>
              ) : (
                <><LogIn size={14}/> LOGIN</>
              )}
            </button>
          </form>

        </div>
      </div>
    </>
  );
};

export default AdminLogin;
