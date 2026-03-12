import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Upload, X, CheckCircle, Trash2, Users, AlertTriangle, Loader, ArrowLeft, Shield, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = 'http://localhost:8000';

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

  .reg-root {
    background: #020817;
    background-image: linear-gradient(rgba(139,92,246,0.025) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(139,92,246,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    min-height: 100vh;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
    padding: 28px;
  }
  .orb { font-family: 'Orbitron', monospace; }
  .glass { background: rgba(255,255,255,0.025); backdrop-filter: blur(24px); border: 1px solid rgba(139,92,246,0.1); border-radius: 16px; }
  .glass-sm { background: rgba(0,0,0,0.3); border: 1px solid rgba(139,92,246,0.07); border-radius: 12px; }
  .muted { color: #475569; }
  .sub { color: #94a3b8; }

  .grad-purple { background:linear-gradient(135deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

  .pulse-live { width:8px; height:8px; border-radius:50%; background:#a78bfa; animation:pPulse 2s infinite; flex-shrink:0; }
  @keyframes pPulse { 0%,100%{box-shadow:0 0 0 0 rgba(167,139,250,0.5)} 50%{box-shadow:0 0 0 8px rgba(167,139,250,0)} }

  .badge { font-family:'Orbitron',monospace; font-size:0.58rem; letter-spacing:0.1em; padding:2px 8px; border-radius:4px; background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.2); color:#c4b5fd; }

  .field-label { font-size:0.72rem; color:#64748b; letter-spacing:0.06em; font-family:'Orbitron',monospace; margin-bottom:6px; display:block; }

  input[type=text], input[type=email], .rinput {
    background:rgba(139,92,246,0.035) !important; border:1px solid rgba(139,92,246,0.13) !important;
    color:#e2e8f0 !important; border-radius:9px !important; padding:10px 14px !important;
    font-family:'DM Sans',sans-serif !important; font-size:0.875rem !important;
    outline:none !important; transition:border-color 0.2s,box-shadow 0.2s !important;
    width:100%; box-sizing:border-box;
  }
  input[type=text]:focus, input[type=email]:focus, .rinput:focus {
    border-color:rgba(139,92,246,0.4) !important; box-shadow:0 0 0 3px rgba(139,92,246,0.08) !important;
  }

  .btn { display:inline-flex; align-items:center; justify-content:center; gap:7px; padding:11px 20px; border-radius:10px; cursor:pointer; font-family:'Orbitron',monospace; font-size:0.72rem; font-weight:600; letter-spacing:0.06em; transition:all 0.18s; border:1px solid transparent; }
  .btn-p { background:linear-gradient(135deg,#7c3aed,#6d28d9); border-color:rgba(167,139,250,0.25); color:#ede9fe; }
  .btn-p:hover:not(:disabled) { background:linear-gradient(135deg,#8b5cf6,#7c3aed); box-shadow:0 0 24px rgba(139,92,246,0.35); transform:translateY(-1px); }
  .btn-r { background:linear-gradient(135deg,#9f1239,#be123c); border-color:rgba(244,63,94,0.25); color:#ffe4e6; }
  .btn-r:hover:not(:disabled) { background:linear-gradient(135deg,#e11d48,#9f1239); box-shadow:0 0 24px rgba(244,63,94,0.28); transform:translateY(-1px); }
  .btn-ghost { background:transparent; border:1px solid rgba(139,92,246,0.15); color:#64748b; }
  .btn-ghost:hover { border-color:rgba(139,92,246,0.3); color:#a78bfa; transform:translateY(-1px); }
  .btn:disabled { opacity:0.4; cursor:not-allowed; transform:none !important; }

  .upload-zone { border:1.5px dashed rgba(139,92,246,0.2); border-radius:12px; padding:28px; text-align:center; cursor:pointer; transition:all 0.2s; }
  .upload-zone:hover { border-color:rgba(139,92,246,0.4); background:rgba(139,92,246,0.03); }

  .img-thumb { position:relative; border-radius:10px; overflow:hidden; border:1px solid rgba(139,92,246,0.12); aspect-ratio:1; }
  .img-thumb img { width:100%; height:100%; object-fit:cover; display:block; }
  .img-del { position:absolute; top:4px; right:4px; width:20px; height:20px; border-radius:50%; background:rgba(244,63,94,0.85); border:none; color:white; display:flex; align-items:center; justify-content:center; cursor:pointer; opacity:0; transition:opacity 0.15s; }
  .img-thumb:hover .img-del { opacity:1; }
  .img-num { position:absolute; bottom:4px; left:4px; font-family:'Orbitron',monospace; font-size:0.55rem; background:rgba(0,0,0,0.6); color:#a78bfa; padding:2px 5px; border-radius:4px; }

  .res-ok  { background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.25); border-radius:10px; padding:12px 16px; }
  .res-err { background:rgba(244,63,94,0.06);  border:1px solid rgba(244,63,94,0.25);  border-radius:10px; padding:12px 16px; }

  .table-row { border-bottom:1px solid rgba(139,92,246,0.06); transition:background 0.15s; }
  .table-row:hover { background:rgba(139,92,246,0.04); }
  .dept-tag { font-family:'Orbitron',monospace; font-size:0.58rem; letter-spacing:0.08em; padding:3px 9px; border-radius:5px; background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.18); color:#c4b5fd; }

  .modal-bg { position:fixed; inset:0; background:rgba(0,0,0,0.75); backdrop-filter:blur(4px); display:flex; align-items:center; justify-content:center; z-index:50; padding:20px; }
  .modal { background:#0d1117; border:1px solid rgba(244,63,94,0.2); border-radius:18px; padding:32px; max-width:420px; width:100%; box-shadow:0 0 60px rgba(244,63,94,0.1); }

  ::-webkit-scrollbar{width:3px} ::-webkit-scrollbar-track{background:#020817} ::-webkit-scrollbar-thumb{background:rgba(139,92,246,0.2);border-radius:2px}
  @keyframes spin { to{transform:rotate(360deg)} }
  @keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
  .fade-up { animation: fadeUp 0.35s ease forwards; }
`;

const UserRegistration = () => {
  const { isAdmin, logout } = useAuth();
  const [formData, setFormData] = useState({ name:'', employee_id:'', department:'' });
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // Redirect to home if not admin
  useEffect(() => {
    if (!isAdmin) navigate('/', { replace: true });
  }, [isAdmin, navigate]);

  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteStatus, setDeleteStatus] = useState(null);

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    setUsersLoading(true);
    try { const r = await axios.get(`${API_BASE_URL}/api/users`); setUsers(r.data.users||[]); }
    catch(e) { console.error(e); }
    finally { setUsersLoading(false); }
  };

  const handleInput = e => setFormData(p=>({...p,[e.target.name]:e.target.value}));

  const handleFiles = e => {
    const files = Array.from(e.target.files);
    if (images.length+files.length>10) { alert('Max 10 images'); return; }
    setImages(p=>[...p,...files]);
    files.forEach(f => { const r=new FileReader(); r.onloadend=()=>setPreviews(p=>[...p,r.result]); r.readAsDataURL(f); });
    e.target.value='';
  };

  const removeImage = i => { setImages(p=>p.filter((_,j)=>j!==i)); setPreviews(p=>p.filter((_,j)=>j!==i)); };

  const parseError = e => {
    const d = e.response?.data?.detail;
    if(!d) return 'Server not reachable';
    if(Array.isArray(d)) return d[0]?.msg||'Invalid input';
    return typeof d==='string' ? d : 'Invalid request';
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if(!formData.name||!formData.employee_id||!formData.department) { alert('Fill all fields'); return; }
    if(images.length<3) { alert('Upload at least 3 face images'); return; }
    setLoading(true); setResult(null);
    try {
      const fd = new FormData();
      Object.entries(formData).forEach(([k,v])=>fd.append(k,v));
      images.forEach(img=>fd.append('files',img));
      const res = await axios.post(`${API_BASE_URL}/api/register`, fd, { headers:{'Content-Type':'multipart/form-data'} });
      setResult({ success: res.data.status==='success', message: res.data.status==='success'?`User registered (ID: ${res.data.user_id})`:res.data.message });
      if(res.data.status==='success') { setFormData({name:'',employee_id:'',department:''}); setImages([]); setPreviews([]); fetchUsers(); }
    } catch(e) { setResult({ success:false, message:parseError(e) }); }
    finally { setLoading(false); }
  };

  const handleDelete = async () => {
    if(!deleteTarget) return;
    setDeleteLoading(true); setDeleteStatus(null);
    try {
      const res = await axios.delete(`${API_BASE_URL}/api/users/${deleteTarget.id}`);
      if(res.data.status==='success') {
        setDeleteStatus({type:'success',message:`${deleteTarget.name} deleted.`});
        setUsers(p=>p.filter(u=>u.id!==deleteTarget.id));
        setTimeout(()=>{ setDeleteTarget(null); setDeleteStatus(null); },1400);
      } else setDeleteStatus({type:'error',message:res.data.message||'Delete failed.'});
    } catch(e) { setDeleteStatus({type:'error',message:e.response?.data?.detail||'Delete failed.'}); }
    finally { setDeleteLoading(false); }
  };

  return (
    <>
      <style>{css}</style>
      <div className="reg-root">
        <div style={{maxWidth:'1100px',margin:'0 auto'}}>

          {/* HEADER */}
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'28px',paddingBottom:'20px',borderBottom:'1px solid rgba(139,92,246,0.08)'}}>
            <button className="btn btn-ghost" onClick={()=>navigate('/')} style={{gap:'7px',padding:'9px 18px'}}>
              <ArrowLeft size={13}/> BACK
            </button>
            <div style={{textAlign:'right'}}>
              <div style={{display:'flex',alignItems:'center',justifyContent:'flex-end',gap:'8px',marginBottom:'5px'}}>
                <div className="pulse-live"/>
                <span className="badge">USER MANAGEMENT</span>
                <span style={{display:'inline-flex',alignItems:'center',gap:'4px',padding:'2px 8px',borderRadius:'4px',background:'rgba(251,191,36,0.1)',border:'1px solid rgba(251,191,36,0.25)',color:'#fbbf24',fontFamily:'Orbitron,monospace',fontSize:'0.55rem',letterSpacing:'0.08em'}}>
                  <Shield size={8}/> ADMIN SESSION
                </span>
              </div>
              <h1 className="orb" style={{fontSize:'1.5rem',fontWeight:900,color:'#f1f5f9',letterSpacing:'0.06em',margin:0}}>
                REGISTRATION PORTAL
              </h1>
            </div>
            <button
              onClick={()=>{logout();navigate('/');}}
              style={{display:'inline-flex',alignItems:'center',gap:'6px',padding:'9px 18px',borderRadius:'9px',background:'rgba(244,63,94,0.08)',border:'1px solid rgba(244,63,94,0.2)',color:'#fb7185',fontSize:'0.65rem',fontFamily:'Orbitron,monospace',letterSpacing:'0.06em',cursor:'pointer',transition:'all 0.15s'}}
              onMouseOver={e=>{e.currentTarget.style.background='rgba(244,63,94,0.15)';}}
              onMouseOut={e=>{e.currentTarget.style.background='rgba(244,63,94,0.08)';}}
            >
              <LogOut size={12}/> LOGOUT
            </button>
          </div>

          <div style={{display:'grid',gridTemplateColumns:'1fr 1.2fr',gap:'24px'}}>

            {/* REGISTER FORM */}
            <div className="glass fade-up" style={{padding:'24px'}}>
              <div style={{display:'flex',alignItems:'center',gap:'8px',marginBottom:'22px'}}>
                <UserPlus size={15} color="#a78bfa"/>
                <span className="orb sub" style={{fontSize:'0.68rem',letterSpacing:'0.1em'}}>REGISTER NEW USER</span>
              </div>

              <form onSubmit={handleSubmit}>
                <div style={{display:'flex',flexDirection:'column',gap:'14px',marginBottom:'20px'}}>
                  {[
                    {name:'name',label:'FULL NAME',placeholder:'John Doe'},
                    {name:'employee_id',label:'EMPLOYEE ID',placeholder:'EMP001'},
                    {name:'department',label:'DEPARTMENT',placeholder:'Engineering'},
                  ].map(f => (
                    <div key={f.name}>
                      <label className="field-label">{f.label}</label>
                      <input type="text" name={f.name} value={formData[f.name]} onChange={handleInput} placeholder={f.placeholder} required/>
                    </div>
                  ))}
                </div>

                {/* Upload zone */}
                <div className="upload-zone" onClick={()=>fileInputRef.current.click()} style={{marginBottom:'14px'}}>
                  <div style={{width:'42px',height:'42px',borderRadius:'12px',background:'rgba(139,92,246,0.08)',border:'1px solid rgba(139,92,246,0.15)',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto 10px'}}>
                    <Upload size={18} color="#a78bfa"/>
                  </div>
                  <p style={{color:'#475569',fontSize:'0.82rem',marginBottom:'4px'}}>Click to upload face images</p>
                  <p className="orb" style={{fontSize:'0.65rem',color:'#7c3aed',letterSpacing:'0.06em'}}>{images.length} / 10 SELECTED</p>
                  <p style={{color:'#1e293b',fontSize:'0.72rem',marginTop:'4px'}}>Minimum 3 images required</p>
                  <input ref={fileInputRef} type="file" multiple accept="image/*" onChange={handleFiles} style={{display:'none'}}/>
                </div>

                {/* Previews */}
                {previews.length>0 && (
                  <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:'8px',marginBottom:'16px'}}>
                    {previews.map((src,i) => (
                      <div key={i} className="img-thumb">
                        <img src={src} alt=""/>
                        <button type="button" className="img-del" onClick={()=>removeImage(i)}><X size={10}/></button>
                        <span className="img-num">{i+1}</span>
                      </div>
                    ))}
                  </div>
                )}

                {result && (
                  <div className={result.success?'res-ok':'res-err'} style={{marginBottom:'14px',display:'flex',alignItems:'flex-start',gap:'10px'}}>
                    {result.success
                      ? <CheckCircle size={16} color="#10b981" style={{flexShrink:0,marginTop:'1px'}}/>
                      : <AlertTriangle size={16} color="#f43f5e" style={{flexShrink:0,marginTop:'1px'}}/>
                    }
                    <p style={{fontSize:'0.8rem',color:result.success?'#34d399':'#fb7185'}}>{result.message}</p>
                  </div>
                )}

                <button type="submit" disabled={loading} className="btn btn-p" style={{width:'100%'}}>
                  {loading?<><Loader size={13} style={{animation:'spin 0.8s linear infinite'}}/>REGISTERING...</>:<><UserPlus size={13}/>REGISTER USER</>}
                </button>
              </form>
            </div>

            {/* USERS TABLE */}
            <div className="glass fade-up" style={{padding:'24px',animationDelay:'0.1s'}}>
              <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'18px'}}>
                <div style={{display:'flex',alignItems:'center',gap:'8px'}}>
                  <Users size={15} color="#a78bfa"/>
                  <span className="orb sub" style={{fontSize:'0.68rem',letterSpacing:'0.1em'}}>
                    REGISTERED USERS
                    <span style={{color:'#7c3aed',marginLeft:'8px'}}>({users.length})</span>
                  </span>
                </div>
                <button className="btn btn-ghost" onClick={fetchUsers} style={{padding:'6px 14px',fontSize:'0.6rem',borderRadius:'8px'}}>
                  ↺ REFRESH
                </button>
              </div>

              {usersLoading ? (
                <div style={{display:'flex',alignItems:'center',justifyContent:'center',padding:'48px',gap:'10px',color:'#334155'}}>
                  <Loader size={18} style={{animation:'spin 0.8s linear infinite'}}/> 
                  <span className="orb" style={{fontSize:'0.65rem',letterSpacing:'0.1em'}}>LOADING...</span>
                </div>
              ) : users.length===0 ? (
                <div style={{textAlign:'center',padding:'48px'}}>
                  <div style={{width:'56px',height:'56px',borderRadius:'50%',background:'rgba(139,92,246,0.05)',border:'1px solid rgba(139,92,246,0.1)',display:'flex',alignItems:'center',justifyContent:'center',margin:'0 auto 12px'}}>
                    <Users size={24} color="#1e293b"/>
                  </div>
                  <span className="orb" style={{fontSize:'0.65rem',color:'#1e3a4a',letterSpacing:'0.1em'}}>NO USERS REGISTERED</span>
                </div>
              ) : (
                <div style={{overflowX:'auto'}}>
                  <table style={{width:'100%',borderCollapse:'collapse'}}>
                    <thead>
                      <tr style={{borderBottom:'1px solid rgba(139,92,246,0.12)'}}>
                        {['#','NAME','EMP ID','DEPARTMENT','DATE',''].map(h => (
                          <th key={h} className="orb muted" style={{padding:'8px 10px 12px',textAlign:'left',fontSize:'0.58rem',letterSpacing:'0.1em',fontWeight:600}}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((u,i) => (
                        <tr key={u.id} className="table-row">
                          <td style={{padding:'11px 10px',color:'#334155',fontSize:'0.75rem'}}>{i+1}</td>
                          <td style={{padding:'11px 10px',fontWeight:600,fontSize:'0.84rem',color:'#e2e8f0'}}>{u.name}</td>
                          <td style={{padding:'11px 10px',fontFamily:'monospace',fontSize:'0.78rem',color:'#94a3b8'}}>{u.employee_id}</td>
                          <td style={{padding:'11px 10px'}}><span className="dept-tag">{u.department}</span></td>
                          <td style={{padding:'11px 10px',color:'#475569',fontSize:'0.75rem'}}>
                            {u.created_at ? new Date(u.created_at).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}) : '—'}
                          </td>
                          <td style={{padding:'11px 10px',textAlign:'right'}}>
                            <button
                              onClick={()=>{setDeleteTarget(u);setDeleteStatus(null);}}
                              style={{display:'inline-flex',alignItems:'center',gap:'4px',padding:'5px 10px',borderRadius:'7px',background:'rgba(244,63,94,0.07)',border:'1px solid rgba(244,63,94,0.15)',color:'#fb7185',fontSize:'0.65rem',fontFamily:'Orbitron,monospace',letterSpacing:'0.05em',cursor:'pointer',transition:'all 0.15s'}}
                              onMouseOver={e=>{e.currentTarget.style.background='rgba(244,63,94,0.14)';e.currentTarget.style.boxShadow='0 0 12px rgba(244,63,94,0.15)'}}
                              onMouseOut={e=>{e.currentTarget.style.background='rgba(244,63,94,0.07)';e.currentTarget.style.boxShadow='none'}}
                            >
                              <Trash2 size={11}/> DEL
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          <div className="orb" style={{textAlign:'center',marginTop:'18px',color:'#1e293b',fontSize:'0.58rem',letterSpacing:'0.1em'}}>
            SMART ATTENDANCE SYSTEM · USER MANAGEMENT PORTAL · {new Date().getFullYear()}
          </div>
        </div>
      </div>

      {/* DELETE MODAL */}
      {deleteTarget && (
        <div className="modal-bg">
          <div className="modal">
            <div style={{display:'flex',alignItems:'center',gap:'12px',marginBottom:'18px'}}>
              <div style={{width:'40px',height:'40px',borderRadius:'10px',background:'rgba(244,63,94,0.1)',border:'1px solid rgba(244,63,94,0.2)',display:'flex',alignItems:'center',justifyContent:'center'}}>
                <Trash2 size={18} color="#f43f5e"/>
              </div>
              <div>
                <div className="orb" style={{fontSize:'0.9rem',fontWeight:700,color:'#f1f5f9',letterSpacing:'0.06em'}}>CONFIRM DELETE</div>
                <div style={{color:'#475569',fontSize:'0.78rem',marginTop:'2px'}}>This action cannot be undone</div>
              </div>
            </div>

            <div style={{background:'rgba(0,0,0,0.3)',border:'1px solid rgba(139,92,246,0.1)',borderRadius:'10px',padding:'14px',marginBottom:'18px'}}>
              {[['NAME',deleteTarget.name],['EMPLOYEE ID',deleteTarget.employee_id],['DEPARTMENT',deleteTarget.department]].map(([k,v])=>(
                <div key={k} style={{display:'flex',justifyContent:'space-between',padding:'5px 0',borderBottom:'1px solid rgba(255,255,255,0.04)'}}>
                  <span className="orb muted" style={{fontSize:'0.6rem',letterSpacing:'0.08em'}}>{k}</span>
                  <span style={{fontSize:'0.82rem',fontWeight:500,color:'#e2e8f0'}}>{v}</span>
                </div>
              ))}
            </div>

            {deleteStatus && (
              <div style={{marginBottom:'14px',padding:'10px 14px',borderRadius:'8px',fontSize:'0.78rem',
                background:deleteStatus.type==='success'?'rgba(16,185,129,0.08)':'rgba(244,63,94,0.08)',
                border:`1px solid ${deleteStatus.type==='success'?'rgba(16,185,129,0.2)':'rgba(244,63,94,0.2)'}`,
                color:deleteStatus.type==='success'?'#34d399':'#fb7185'}}>
                {deleteStatus.message}
              </div>
            )}

            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'10px'}}>
              <button className="btn btn-ghost" onClick={()=>{setDeleteTarget(null);setDeleteStatus(null);}} disabled={deleteLoading}>
                CANCEL
              </button>
              <button className="btn btn-r" onClick={handleDelete} disabled={deleteLoading}>
                {deleteLoading?<><Loader size={12} style={{animation:'spin 0.8s linear infinite'}}/>DELETING...</>:<><Trash2 size={12}/>DELETE</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default UserRegistration;
