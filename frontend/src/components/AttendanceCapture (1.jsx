import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  Camera, CameraOff, CheckCircle, XCircle, AlertTriangle,
  Users, Download, Mail, Calendar, Loader,
  UserPlus, Shield, Zap, Eye, Activity,
  Lock, LogOut, LogIn, ShieldAlert, UserX, Menu, X,
  Cpu, Database, Fingerprint, Brain
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import AdminLogin from './AdminLogin';

const API_BASE_URL     = 'http://localhost:8000';
const POLL_INTERVAL_MS = 1800;
const COOLDOWN_MS      = 6000;
const RESULT_DISPLAY_MS= 5000;

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
  .cyber-root{background:#020817;background-image:linear-gradient(rgba(0,212,255,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.025) 1px,transparent 1px);background-size:48px 48px;min-height:100vh;font-family:'DM Sans',sans-serif;color:#e2e8f0;}
  .orb{font-family:'Orbitron',monospace;}
  .glass{background:rgba(255,255,255,0.025);backdrop-filter:blur(24px);border:1px solid rgba(0,212,255,0.1);border-radius:16px;}
  .glass-sm{background:rgba(0,0,0,0.3);border:1px solid rgba(0,212,255,0.07);border-radius:12px;}
  .muted{color:#475569;} .sub{color:#94a3b8;}
  .grad-cyan{background:linear-gradient(135deg,#00d4ff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
  .grad-green{background:linear-gradient(135deg,#10b981,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
  .grad-red{background:linear-gradient(135deg,#f43f5e,#fb923c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
  .stat-val{font-family:'Orbitron',monospace;font-size:1.9rem;font-weight:700;line-height:1;}
  .pulse-live{width:8px;height:8px;border-radius:50%;background:#10b981;animation:livePulse 2s infinite;flex-shrink:0;}
  @keyframes livePulse{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0.5)}50%{box-shadow:0 0 0 8px rgba(16,185,129,0)}}
  .auto-ring{position:absolute;inset:-3px;border-radius:13px;border:2px solid rgba(0,212,255,0.4);animation:autoRing 1.8s ease-in-out infinite;pointer-events:none;z-index:6;}
  @keyframes autoRing{0%,100%{border-color:rgba(0,212,255,0.15);box-shadow:none;}50%{border-color:rgba(0,212,255,0.65);box-shadow:0 0 18px rgba(0,212,255,0.2);}}
  .auto-ring-active{border-color:rgba(0,212,255,0.9)!important;animation:activeRing 0.55s ease-in-out infinite!important;}
  @keyframes activeRing{0%,100%{box-shadow:0 0 10px rgba(0,212,255,0.35);}50%{box-shadow:0 0 30px rgba(0,212,255,0.75);}}
  .scan-bar{position:absolute;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#00d4ff,transparent);animation:scanDown 2s linear infinite;pointer-events:none;z-index:5;}
  @keyframes scanDown{0%{top:0;opacity:1}95%{opacity:0.6}100%{top:100%;opacity:0}}
  .corner{position:absolute;width:18px;height:18px;border-color:#00d4ff;border-style:solid;z-index:5;}
  .c-tl{top:8px;left:8px;border-width:2px 0 0 2px}.c-tr{top:8px;right:8px;border-width:2px 2px 0 0}
  .c-bl{bottom:8px;left:8px;border-width:0 0 2px 2px}.c-br{bottom:8px;right:8px;border-width:0 2px 2px 0}
  .cam-status{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);font-family:'Orbitron',monospace;font-size:0.6rem;letter-spacing:0.1em;padding:5px 14px;border-radius:20px;z-index:8;white-space:nowrap;backdrop-filter:blur(8px);}
  .cam-watch{background:rgba(0,0,0,0.6);border:1px solid rgba(0,212,255,0.2);color:#334155;}
  .cam-detect{background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.5);color:#67e8f9;}
  .cam-proc{background:rgba(139,92,246,0.2);border:1px solid rgba(139,92,246,0.5);color:#c4b5fd;}
  .cam-cool{background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);color:#34d399;}
  .cam-off{background:rgba(0,0,0,0.7);border:1px solid rgba(255,255,255,0.07);color:#1e293b;}
  .res-success{border:1px solid rgba(16,185,129,0.35);background:rgba(16,185,129,0.05);box-shadow:0 0 40px rgba(16,185,129,0.1);}
  .res-warn{border:1px solid rgba(251,191,36,0.35);background:rgba(251,191,36,0.05);box-shadow:0 0 40px rgba(251,191,36,0.1);}
  .res-fail{border:1px solid rgba(244,63,94,0.35);background:rgba(244,63,94,0.05);box-shadow:0 0 40px rgba(244,63,94,0.1);}
  .res-spoof{border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.06);box-shadow:0 0 40px rgba(249,115,22,0.12);}
  .res-unreg{border:1px solid rgba(168,85,247,0.4);background:rgba(168,85,247,0.06);box-shadow:0 0 40px rgba(168,85,247,0.12);}
  .res-in{animation:resIn 0.45s cubic-bezier(0.34,1.56,0.64,1) forwards;}
  @keyframes resIn{from{opacity:0;transform:scale(0.9) translateY(12px)}to{opacity:1;transform:scale(1) translateY(0)}}
  .cooldown-bar{height:3px;border-radius:2px;background:rgba(16,185,129,0.1);overflow:hidden;margin-top:8px;}
  .cooldown-fill{height:100%;background:linear-gradient(90deg,#10b981,#06b6d4);transition:width 0.25s linear;}
  .conf-track{height:4px;border-radius:2px;background:rgba(255,255,255,0.06);overflow:hidden;}
  .conf-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,#06b6d4,#10b981);transition:width 1s cubic-bezier(0.34,1.56,0.64,1);}
  .badge{font-family:'Orbitron',monospace;font-size:0.58rem;letter-spacing:0.1em;padding:2px 8px;border-radius:4px;background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.18);color:#67e8f9;}
  .badge-auto{background:rgba(16,185,129,0.1);border-color:rgba(16,185,129,0.3);color:#34d399;}
  .badge-admin{background:rgba(251,191,36,0.1);border-color:rgba(251,191,36,0.3);color:#fbbf24;}
  .menu-btn{width:42px;height:42px;border-radius:10px;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all 0.18s;flex-shrink:0;}
  .menu-btn:hover{background:rgba(0,212,255,0.12);box-shadow:0 0 16px rgba(0,212,255,0.15);}
  .drawer-backdrop{position:fixed;inset:0;background:rgba(0,0,0,0.65);backdrop-filter:blur(5px);z-index:100;animation:fadeIn 0.2s ease;}
  .drawer{position:fixed;top:0;right:0;bottom:0;width:360px;background:#080f1f;border-left:1px solid rgba(0,212,255,0.12);z-index:101;display:flex;flex-direction:column;animation:slideIn 0.28s cubic-bezier(0.34,1.1,0.64,1);overflow-y:auto;}
  @keyframes slideIn{from{transform:translateX(100%)}to{transform:translateX(0)}}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  .drawer-header{display:flex;align-items:center;justify-content:space-between;padding:22px 20px 18px;border-bottom:1px solid rgba(0,212,255,0.08);flex-shrink:0;}
  .drawer-section{padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.04);}
  .drawer-label{font-family:'Orbitron',monospace;font-size:0.6rem;letter-spacing:0.12em;color:#334155;margin-bottom:10px;display:flex;align-items:center;gap:6px;}
  .d-btn{width:100%;display:flex;align-items:center;gap:10px;padding:11px 14px;border-radius:10px;cursor:pointer;font-family:'Orbitron',monospace;font-size:0.68rem;font-weight:600;letter-spacing:0.06em;transition:all 0.15s;border:1px solid transparent;margin-bottom:8px;}
  .d-btn:last-child{margin-bottom:0;}
  .d-btn-cyan{background:rgba(0,212,255,0.07);border-color:rgba(0,212,255,0.15);color:#67e8f9;}
  .d-btn-cyan:hover:not(:disabled){background:rgba(0,212,255,0.13);border-color:rgba(0,212,255,0.3);box-shadow:0 0 16px rgba(0,212,255,0.1);}
  .d-btn-purple{background:rgba(139,92,246,0.07);border-color:rgba(139,92,246,0.18);color:#c4b5fd;}
  .d-btn-purple:hover{background:rgba(139,92,246,0.14);border-color:rgba(139,92,246,0.3);}
  .d-btn-green{background:rgba(16,185,129,0.07);border-color:rgba(16,185,129,0.18);color:#34d399;}
  .d-btn-green:hover:not(:disabled){background:rgba(16,185,129,0.14);border-color:rgba(16,185,129,0.3);}
  .d-btn-amber{background:rgba(251,191,36,0.07);border-color:rgba(251,191,36,0.18);color:#fbbf24;}
  .d-btn-amber:hover{background:rgba(251,191,36,0.13);border-color:rgba(251,191,36,0.3);}
  .d-btn-red{background:rgba(244,63,94,0.07);border-color:rgba(244,63,94,0.18);color:#fb7185;}
  .d-btn-red:hover{background:rgba(244,63,94,0.13);border-color:rgba(244,63,94,0.3);}
  .d-btn:disabled{opacity:0.35;cursor:not-allowed;}
  .cam-toggle{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:9px 16px;border-radius:9px;cursor:pointer;font-family:'Orbitron',monospace;font-size:0.65rem;font-weight:600;letter-spacing:0.06em;transition:all 0.18s;border:1px solid;width:100%;margin-bottom:10px;}
  .cam-toggle-on{background:rgba(244,63,94,0.08);border-color:rgba(244,63,94,0.22);color:#fb7185;}
  .cam-toggle-on:hover{background:rgba(244,63,94,0.15);box-shadow:0 0 14px rgba(244,63,94,0.12);}
  .cam-toggle-off{background:rgba(16,185,129,0.08);border-color:rgba(16,185,129,0.22);color:#34d399;}
  .cam-toggle-off:hover{background:rgba(16,185,129,0.15);box-shadow:0 0 14px rgba(16,185,129,0.12);}
  .sys-card{padding:20px;border-radius:14px;background:rgba(0,0,0,0.22);border:1px solid rgba(0,212,255,0.07);transition:border-color 0.2s;}
  .sys-card:hover{border-color:rgba(0,212,255,0.18);}
  .sys-stat-row{display:flex;align-items:center;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.03);}
  .sys-stat-row:last-child{border-bottom:none;}
  input{background:rgba(0,212,255,0.035)!important;border:1px solid rgba(0,212,255,0.13)!important;color:#e2e8f0!important;border-radius:8px!important;padding:9px 13px!important;font-family:'DM Sans',sans-serif!important;font-size:0.875rem!important;outline:none!important;transition:border-color 0.2s!important;width:100%;box-sizing:border-box;}
  input:focus{border-color:rgba(0,212,255,0.35)!important;box-shadow:0 0 0 3px rgba(0,212,255,0.07)!important;}
  input[type=date]::-webkit-calendar-picker-indicator{filter:invert(0.7);cursor:pointer;}
  ::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:#020817}::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.18);border-radius:2px}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes dotPulse{0%,100%{opacity:0.2}50%{opacity:1}}
`;

const PHASE = { WATCHING:'watching', FACE_FOUND:'face_found', PROCESSING:'processing', COOLDOWN:'cooldown' };

const AttendanceCapture = () => {
  const { isAdmin, logout } = useAuth();
  const navigate        = useNavigate();
  const webcamRef       = useRef(null);
  const pollRef         = useRef(null);
  const cooldownRef     = useRef(null);
  const resultTimerRef  = useRef(null);
  const streamCheckRef  = useRef(null);
  const lastHash        = useRef(0);
  const doScanRef       = useRef(null);
  const motionHistory   = useRef([]);
  const MOTION_FRAMES   = 5;
  const STATIC_THRESH   = 200;

  const [result,          setResult]          = useState(null);
  const [phase,           setPhase]           = useState(PHASE.WATCHING);
  const [stats,           setStats]           = useState(null);
  const [camKey,          setCamKey]          = useState(0);
  const [camError,        setCamError]        = useState(false);
  const [camActive,       setCamActive]       = useState(true);
  const [cooldownPct,     setCooldownPct]     = useState(100);
  const [showLogin,       setShowLogin]       = useState(false);
  const [showMenu,        setShowMenu]        = useState(false);
  const [reportDate,      setReportDate]      = useState(() => new Date().toISOString().split('T')[0]);
  const [emailAddress,    setEmailAddress]    = useState('');
  const [emailLoading,    setEmailLoading]    = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [emailStatus,     setEmailStatus]     = useState(null);

  /* helpers */
  const stopScan = useCallback(() => {
    clearInterval(pollRef.current);
    clearTimeout(cooldownRef.current);
    clearTimeout(resultTimerRef.current);
    setPhase(PHASE.WATCHING);
    setResult(null);
    setCamActive(false);
  }, []);

  const startScan = useCallback(() => {
    setCamKey(k => k + 1);
    setCamActive(true);
  }, []);

  /* stats */
  const fetchStats = useCallback(async () => {
    try { const r = await axios.get(`${API_BASE_URL}/api/stats/dashboard`); setStats(r.data); } catch {}
  }, []);
  useEffect(() => { fetchStats(); const iv = setInterval(fetchStats,30000); return ()=>clearInterval(iv); }, [fetchStats]);

  /* stop camera when menu opens; restart when it closes */
  useEffect(() => {
    if (showMenu) { stopScan(); }
    else          { startScan(); }
  }, [showMenu]); // eslint-disable-line

  /* watchdog */
  useEffect(() => {
    if (!camActive) return;
    const check = () => {
      const video = webcamRef.current?.video;
      if (!video) return;
      const stream = video.srcObject;
      if (stream) {
        const tracks = stream.getVideoTracks();
        if (!tracks.length || tracks.every(t=>t.readyState==='ended')) { setCamKey(k=>k+1); return; }
      }
      if (video.readyState===4 && video.videoWidth>0) {
        try {
          const c=document.createElement('canvas'); c.width=c.height=64;
          const ctx=c.getContext('2d'); ctx.drawImage(video,0,0,64,64);
          const d=ctx.getImageData(0,0,64,64).data;
          let s=0; for(let i=0;i<d.length;i+=4) s+=d[i]+d[i+1]+d[i+2];
          if (s/(d.length/4*3)<5) setCamKey(k=>k+1);
        } catch {}
      }
    };
    streamCheckRef.current = setInterval(check,3000);
    return ()=>clearInterval(streamCheckRef.current);
  }, [camKey,camActive]);

  /* cooldown */
  const enterCooldown = useCallback(()=>{
    setPhase(PHASE.COOLDOWN);
    clearInterval(pollRef.current);
    clearTimeout(resultTimerRef.current);
    const start=Date.now(); setCooldownPct(100);
    const tick=()=>{
      const elapsed=Date.now()-start;
      const pct=Math.max(0,100-(elapsed/COOLDOWN_MS)*100);
      setCooldownPct(pct);
      if (elapsed>=COOLDOWN_MS){
        setPhase(PHASE.WATCHING); setResult(null);
        clearInterval(pollRef.current);
        pollRef.current=setInterval(doScanRef.current,POLL_INTERVAL_MS);
      } else { cooldownRef.current=setTimeout(tick,80); }
    };
    cooldownRef.current=setTimeout(tick,80);
    resultTimerRef.current=setTimeout(()=>setResult(null),RESULT_DISPLAY_MS);
  },[]);

  /* scan */
  const doScan = useCallback(async()=>{
    if (!camActive||!webcamRef.current) return;
    const img=webcamRef.current.getScreenshot({width:640,height:480});
    if (!img) return;
    const canvas=document.createElement('canvas'); canvas.width=16; canvas.height=16;
    const ctx=canvas.getContext('2d');
    const video=webcamRef.current.video;
    if (!video||video.readyState<2) return;
    ctx.drawImage(video,0,0,16,16);
    const pixels=ctx.getImageData(0,0,16,16).data;
    let hash=0;
    for(let i=0;i<pixels.length;i+=4) hash+=pixels[i]+pixels[i+1]+pixels[i+2];
    if (Math.abs(hash-lastHash.current)<800) return;
    lastHash.current=hash;
    setPhase(PHASE.FACE_FOUND);
    setTimeout(()=>setPhase(PHASE.PROCESSING),280);
    try {
      const blob=await fetch(img).then(r=>r.blob());
      const hist=motionHistory.current;
      hist.push(hash);
      if (hist.length>MOTION_FRAMES) hist.shift();
      let isStatic=false;
      if (hist.length>=MOTION_FRAMES){
        const minH=Math.min(...hist),maxH=Math.max(...hist);
        isStatic=(maxH-minH)<STATIC_THRESH;
      }
      const fd=new FormData();
      fd.append('file',blob,'capture.jpg');
      fd.append('is_static',String(isStatic));
      const res=await axios.post(`${API_BASE_URL}/api/mark-attendance`,fd,{headers:{'Content-Type':'multipart/form-data'}});
      const data=res.data;
      if (data.status==='no_face'){setPhase(PHASE.WATCHING);return;}
      setResult(data); fetchStats(); enterCooldown();
    } catch(e){
      const detail=e.response?.data?.detail||'';
      if (detail.toLowerCase().includes('no face')||detail.toLowerCase().includes('no_face')){setPhase(PHASE.WATCHING);return;}
      setResult({status:'error',message:detail||'Processing error',recognized:false});
      enterCooldown();
    }
  },[fetchStats,enterCooldown,camActive]);

  useEffect(()=>{doScanRef.current=doScan;},[doScan]);
  useEffect(()=>{
    if (!camActive){clearInterval(pollRef.current);clearTimeout(cooldownRef.current);return;}
    const t=setTimeout(()=>{pollRef.current=setInterval(doScan,POLL_INTERVAL_MS);},1500);
    return()=>{clearTimeout(t);clearInterval(pollRef.current);clearTimeout(cooldownRef.current);clearTimeout(resultTimerRef.current);};
  },[doScan,camKey,camActive]);

  /* report handlers */
  const handleDownload=async()=>{
    setDownloadLoading(true);
    try {
      const res=await axios.get(`${API_BASE_URL}/api/report/download`,{params:{report_date:reportDate},responseType:'blob'});
      const url=window.URL.createObjectURL(new Blob([res.data]));
      const a=document.createElement('a'); a.href=url;
      a.download=`attendance_report_${reportDate}.csv`;
      document.body.appendChild(a); a.click(); a.remove();
      window.URL.revokeObjectURL(url);
    } catch {alert('Download failed');}
    finally{setDownloadLoading(false);}
  };

  const handleEmail=async()=>{
    if (!emailAddress.trim()){setEmailStatus({type:'error',message:'Enter an email.'});return;}
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailAddress)){setEmailStatus({type:'error',message:'Invalid email.'});return;}
    setEmailLoading(true); setEmailStatus(null);
    try {
      const fd=new FormData();
      fd.append('recipient_email',emailAddress); fd.append('report_date',reportDate);
      const res=await axios.post(`${API_BASE_URL}/api/report/send-email`,fd);
      if(res.data.status==='success'){setEmailStatus({type:'success',message:`Sent to ${emailAddress}`,summary:res.data.summary});setEmailAddress('');}
      else setEmailStatus({type:'error',message:res.data.message});
    } catch(e){setEmailStatus({type:'error',message:e.response?.data?.detail||'Failed.'});}
    finally{setEmailLoading(false);}
  };

  const RC={
    success:        {cls:'res-success',icon:<CheckCircle size={48} color="#10b981"/>,  label:'ACCESS GRANTED'},
    already_marked: {cls:'res-warn',   icon:<AlertTriangle size={48} color="#fbbf24"/>,label:'ALREADY LOGGED'},
    failed:         {cls:'res-fail',   icon:<XCircle size={48} color="#f43f5e"/>,      label:'ACCESS DENIED'},
    spoof_detected: {cls:'res-spoof',  icon:<ShieldAlert size={48} color="#f97316"/>,  label:'ANTI-SPOOF DETECTED'},
    not_registered: {cls:'res-unreg',  icon:<UserX size={48} color="#a855f7"/>,        label:'NOT REGISTERED'},
    error:          {cls:'res-fail',   icon:<XCircle size={48} color="#f43f5e"/>,      label:'SYSTEM ERROR'},
  };
  const rc=result?(RC[result.status]||RC.error):null;

  const camStatusMap={
    [PHASE.WATCHING]:   {cls:'cam-watch', text:'WATCHING FOR FACE...'},
    [PHASE.FACE_FOUND]: {cls:'cam-detect',text:'FACE DETECTED'},
    [PHASE.PROCESSING]: {cls:'cam-proc',  text:'PROCESSING...'},
    [PHASE.COOLDOWN]:   {cls:'cam-cool',  text:'ATTENDANCE MARKED'},
  };
  const camStatus=camActive?camStatusMap[phase]:{cls:'cam-off',text:'CAMERA STOPPED'};
  const S=(g=6)=>({display:'flex',alignItems:'center',gap:`${g}px`});

  /* ─── DRAWER ─── */
  const Drawer=()=>(
    <>
      <div className="drawer-backdrop" onClick={()=>setShowMenu(false)}/>
      <div className="drawer">

        {/* Header */}
        <div className="drawer-header">
          <div>
            <div style={{...S(),marginBottom:'4px'}}><div className="pulse-live"/><span className="badge">MENU</span></div>
            <span className="orb" style={{fontSize:'1rem',fontWeight:900,color:'#f1f5f9',letterSpacing:'0.06em'}}>SMART ATTENDANCE</span>
          </div>
          <button className="menu-btn" onClick={()=>setShowMenu(false)}><X size={16} color="#67e8f9"/></button>
        </div>

        {/* ── ADMIN CONTROLS ── */}
        <div className="drawer-section">
          <div className="drawer-label"><Shield size={11} color="#fbbf24"/>ADMIN CONTROLS</div>

          {isAdmin ? (
            <>
              {/* Session badge */}
              <div style={{display:'flex',alignItems:'center',gap:'8px',padding:'10px 12px',borderRadius:'9px',background:'rgba(251,191,36,0.06)',border:'1px solid rgba(251,191,36,0.15)',marginBottom:'12px'}}>
                <Shield size={13} color="#fbbf24"/>
                <span className="orb" style={{fontSize:'0.65rem',color:'#fbbf24',letterSpacing:'0.06em'}}>ADMIN SESSION ACTIVE</span>
              </div>

              {/* Manage users */}
              <button className="d-btn d-btn-purple" onClick={()=>{navigate('/register');setShowMenu(false);}}>
                <UserPlus size={14}/>MANAGE USERS
              </button>

              {/* ── ATTENDANCE REPORTS (inside admin block) ── */}
              <div style={{marginTop:'4px',padding:'14px',borderRadius:'12px',background:'rgba(0,212,255,0.025)',border:'1px solid rgba(0,212,255,0.08)'}}>
                <div className="drawer-label" style={{marginBottom:'12px',color:'#67e8f9'}}>
                  <Download size={11} color="#67e8f9"/>ATTENDANCE REPORTS
                </div>

                {/* Date */}
                <div style={{...S(),marginBottom:'10px'}}>
                  <Calendar size={12} color="#475569"/>
                  <input type="date" value={reportDate}
                    max={new Date().toISOString().split('T')[0]}
                    onChange={e=>{setReportDate(e.target.value);setEmailStatus(null);}}
                    style={{flex:1}}/>
                </div>

                {/* Download */}
                <button className="d-btn d-btn-cyan" onClick={handleDownload} disabled={downloadLoading} style={{marginBottom:'10px'}}>
                  {downloadLoading?<><Loader size={13} style={{animation:'spin 0.8s linear infinite'}}/>PREPARING...</>:<><Download size={13}/>DOWNLOAD CSV</>}
                </button>

                {/* Email */}
                <input type="email" placeholder="recipient@example.com"
                  value={emailAddress}
                  onChange={e=>{setEmailAddress(e.target.value);setEmailStatus(null);}}
                  style={{marginBottom:'8px'}}/>
                {emailStatus&&(
                  <div style={{marginBottom:'8px',padding:'8px 12px',borderRadius:'7px',fontSize:'0.75rem',
                    background:emailStatus.type==='success'?'rgba(16,185,129,0.08)':'rgba(244,63,94,0.08)',
                    border:`1px solid ${emailStatus.type==='success'?'rgba(16,185,129,0.2)':'rgba(244,63,94,0.2)'}`,
                    color:emailStatus.type==='success'?'#34d399':'#fb7185'}}>
                    {emailStatus.message}
                    {emailStatus.summary&&<div style={{marginTop:'3px',opacity:.7}}>Present: {emailStatus.summary.present}/{emailStatus.summary.total} ({emailStatus.summary.rate}%)</div>}
                  </div>
                )}
                <button className="d-btn d-btn-green" onClick={handleEmail} disabled={emailLoading}>
                  {emailLoading?<><Loader size={13} style={{animation:'spin 0.8s linear infinite'}}/>SENDING...</>:<><Mail size={13}/>SEND REPORT</>}
                </button>
              </div>

              {/* Logout */}
              <button className="d-btn d-btn-red" style={{marginTop:'10px'}} onClick={()=>{logout();setShowMenu(false);}}>
                <LogOut size={14}/>LOGOUT
              </button>
            </>
          ) : (
            <button className="d-btn d-btn-amber" onClick={()=>{setShowLogin(true);setShowMenu(false);}}>
              <LogIn size={14}/>ADMIN LOGIN
              <span style={{marginLeft:'auto',fontSize:'0.6rem',color:'#64748b',fontFamily:'DM Sans,sans-serif',fontWeight:400}}>Unlock reports</span>
            </button>
          )}
        </div>

        <div style={{flex:1}}/>
        <div className="orb" style={{textAlign:'center',padding:'14px',color:'#1e293b',fontSize:'0.55rem',letterSpacing:'0.1em'}}>
          SMART ATTENDANCE SYSTEM · {new Date().getFullYear()}
        </div>
      </div>
    </>
  );

  /* ══════════════════════════ RENDER ══════════════════════════ */
  return (
    <>
      <style>{css}</style>
      <div className="cyber-root" style={{padding:'28px'}}>
        <div style={{maxWidth:'1180px',margin:'0 auto'}}>

          {/* HEADER */}
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'28px',paddingBottom:'20px',borderBottom:'1px solid rgba(0,212,255,0.08)'}}>
            <div>
              <div style={{...S(),marginBottom:'6px'}}>
                <div className="pulse-live"/>
                <span className="badge">SYSTEM ONLINE</span>
                <span className="badge badge-auto" style={{marginLeft:'4px'}}>AUTO-DETECT</span>
                {isAdmin&&<span className="badge badge-admin" style={{marginLeft:'4px'}}><Shield size={9} style={{marginRight:'3px'}}/>ADMIN</span>}
              </div>
              <h1 className="orb" style={{fontSize:'1.6rem',fontWeight:900,color:'#f1f5f9',letterSpacing:'0.06em',margin:0,lineHeight:1}}>SMART ATTENDANCE</h1>
              <p style={{color:'#334155',fontSize:'0.72rem',letterSpacing:'0.08em',marginTop:'5px'}}>FACE RECOGNITION · AUTO-MARK · LIVENESS DETECTION · ANTI-SPOOFING</p>
            </div>
            <button className="menu-btn" onClick={()=>setShowMenu(true)} title="Menu"><Menu size={18} color="#67e8f9"/></button>
          </div>

          {/* STATS */}
          {stats&&(
            <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'14px',marginBottom:'24px'}}>
              {[
                {label:'TOTAL USERS',   val:stats.total_registered_users,cls:'grad-cyan', icon:<Users size={17} color="#67e8f9"/>},
                {label:'PRESENT TODAY', val:stats.present_today,         cls:'grad-green',icon:<CheckCircle size={17} color="#34d399"/>},
                {label:'ABSENT TODAY',  val:stats.absent_today,          cls:'grad-red',  icon:<XCircle size={17} color="#fb7185"/>},
                {label:'RATE',          val:`${stats.attendance_rate}%`, cls:'grad-cyan', icon:<Zap size={17} color="#a78bfa"/>},
              ].map((s,i)=>(
                <div key={i} className="glass" style={{padding:'18px'}}>
                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:'10px'}}>
                    <span className="orb muted" style={{fontSize:'0.6rem',letterSpacing:'0.1em'}}>{s.label}</span>{s.icon}
                  </div>
                  <div className={`stat-val ${s.cls}`}>{s.val}</div>
                </div>
              ))}
            </div>
          )}

          {/* CAMERA + RESULT */}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'20px',marginBottom:'24px'}}>

            {/* Camera panel */}
            <div className="glass" style={{padding:'22px'}}>
              <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'12px'}}>
                <div style={S()}><Camera size={15} color="#67e8f9"/><span className="orb sub" style={{fontSize:'0.68rem',letterSpacing:'0.1em'}}>CAMERA FEED</span></div>
                <div style={S()}>
                  {camActive&&phase===PHASE.PROCESSING&&<Loader size={11} color="#a78bfa" style={{animation:'spin 0.8s linear infinite'}}/>}
                  {camActive&&phase===PHASE.WATCHING&&<Activity size={11} color="#334155"/>}
                  <span className="orb" style={{fontSize:'0.6rem',letterSpacing:'0.08em',
                    color:!camActive?'#1e293b':phase===PHASE.PROCESSING?'#a78bfa':phase===PHASE.COOLDOWN?'#34d399':phase===PHASE.FACE_FOUND?'#67e8f9':'#334155'}}>
                    {!camActive?'STOPPED':phase===PHASE.PROCESSING?'PROCESSING':phase===PHASE.COOLDOWN?'MARKED':phase===PHASE.FACE_FOUND?'FACE FOUND':'SCANNING'}
                  </span>
                </div>
              </div>

              {/* ── START / STOP — ABOVE CAMERA ── */}
              <button
                className={`cam-toggle ${camActive?'cam-toggle-on':'cam-toggle-off'}`}
                onClick={()=>camActive?stopScan():startScan()}
              >
                {camActive?<><CameraOff size={14}/>STOP CAMERA</>:<><Camera size={14}/>START CAMERA</>}
              </button>

              {/* Viewport */}
              <div style={{position:'relative',borderRadius:'10px',overflow:'visible',border:'1px solid rgba(0,212,255,0.12)'}}>
                <div style={{position:'relative',borderRadius:'10px',overflow:'hidden'}}>
                  {camActive?(
                    <Webcam key={camKey} ref={webcamRef} audio={false} screenshotFormat="image/jpeg"
                      style={{width:'100%',display:'block'}}
                      onUserMedia={()=>setCamError(false)} onUserMediaError={()=>setCamError(true)}
                      videoConstraints={{width:640,height:480,facingMode:'user'}}/>
                  ):(
                    <div style={{width:'100%',aspectRatio:'4/3',background:'#020817',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:'12px',borderRadius:'10px'}}>
                      <div style={{width:'60px',height:'60px',borderRadius:'50%',background:'rgba(255,255,255,0.03)',border:'1px solid rgba(255,255,255,0.06)',display:'flex',alignItems:'center',justifyContent:'center'}}>
                        <CameraOff size={26} color="#1e293b"/>
                      </div>
                      <span className="orb" style={{color:'#1e293b',fontSize:'0.65rem',letterSpacing:'0.1em'}}>CAMERA STOPPED</span>
                    </div>
                  )}
                  {camActive&&(phase===PHASE.WATCHING||phase===PHASE.FACE_FOUND)&&<div className="scan-bar"/>}
                  {camActive&&<><div className="corner c-tl"/><div className="corner c-tr"/><div className="corner c-bl"/><div className="corner c-br"/></>}
                  <div className={`cam-status ${camStatus.cls}`}>{camStatus.text}</div>
                  {camActive&&phase===PHASE.PROCESSING&&(
                    <div style={{position:'absolute',inset:0,background:'rgba(2,8,23,0.55)',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:'10px'}}>
                      <div style={{width:'52px',height:'52px',border:'2px solid rgba(139,92,246,0.2)',borderTopColor:'#a78bfa',borderRadius:'50%',animation:'spin 0.9s linear infinite'}}/>
                      <span className="orb" style={{color:'#a78bfa',fontSize:'0.65rem',letterSpacing:'0.1em'}}>IDENTIFYING...</span>
                    </div>
                  )}
                  {camActive&&camError&&(
                    <div style={{position:'absolute',inset:0,background:'rgba(2,8,23,0.92)',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:'10px'}}>
                      <XCircle size={36} color="#f43f5e"/>
                      <p style={{color:'#64748b',fontSize:'0.8rem'}}>Camera unavailable</p>
                      <button style={{padding:'7px 18px',borderRadius:'8px',background:'rgba(0,212,255,0.1)',border:'1px solid rgba(0,212,255,0.2)',color:'#67e8f9',fontSize:'0.65rem',fontFamily:'Orbitron,monospace',cursor:'pointer'}}
                        onClick={()=>{setCamError(false);setCamKey(k=>k+1);}}>RETRY</button>
                    </div>
                  )}
                </div>
                {camActive&&<div className={`auto-ring${phase===PHASE.FACE_FOUND?' auto-ring-active':''}`}/>}
              </div>

              {camActive&&phase===PHASE.COOLDOWN&&(
                <div style={{marginTop:'12px'}}>
                  <div style={{display:'flex',justifyContent:'space-between',marginBottom:'4px'}}>
                    <span className="orb" style={{fontSize:'0.58rem',color:'#34d399',letterSpacing:'0.08em'}}>NEXT SCAN IN</span>
                    <span className="orb" style={{fontSize:'0.58rem',color:'#334155'}}>{Math.ceil(COOLDOWN_MS/1000*cooldownPct/100)}s</span>
                  </div>
                  <div className="cooldown-bar"><div className="cooldown-fill" style={{width:`${cooldownPct}%`}}/></div>
                </div>
              )}
              {camActive&&phase===PHASE.WATCHING&&(
                <div style={{marginTop:'12px',padding:'10px 14px',borderRadius:'8px',background:'rgba(0,212,255,0.03)',border:'1px solid rgba(0,212,255,0.07)',display:'flex',alignItems:'center',gap:'8px'}}>
                  <Activity size={13} color="#334155"/>
                  <span style={{color:'#334155',fontSize:'0.7rem',fontFamily:'Orbitron,monospace',letterSpacing:'0.05em'}}>STAND IN FRONT — ATTENDANCE MARKS AUTOMATICALLY</span>
                </div>
              )}
            </div>

            {/* Result panel */}
            <div className="glass" style={{padding:'22px',display:'flex',flexDirection:'column'}}>
              <div style={{...S(),marginBottom:'14px'}}>
                <Eye size={15} color="#67e8f9"/>
                <span className="orb sub" style={{fontSize:'0.68rem',letterSpacing:'0.1em'}}>RECOGNITION RESULT</span>
              </div>
              {result&&rc?(
                <div className={`res-in ${rc.cls}`} style={{flex:1,borderRadius:'12px',padding:'24px',display:'flex',flexDirection:'column',alignItems:'center',textAlign:'center'}}>
                  <div style={{marginBottom:'10px'}}>{rc.icon}</div>
                  <div className="orb" style={{fontSize:'0.9rem',fontWeight:700,letterSpacing:'0.1em',marginBottom:'5px',color:'#f1f5f9'}}>{rc.label}</div>
                  <p style={{color:'#64748b',fontSize:'0.83rem',marginBottom:'18px'}}>{result.message}</p>
                  {result.recognized&&(
                    <div style={{width:'100%',background:'rgba(0,0,0,0.35)',borderRadius:'10px',padding:'14px',textAlign:'left'}}>
                      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'12px',marginBottom:'14px'}}>
                        {[['NAME',result.name],['EMP ID',result.employee_id],['DEPT',result.department],['TIME',new Date(result.timestamp).toLocaleTimeString()]].map(([k,v])=>(
                          <div key={k}><div className="orb muted" style={{fontSize:'0.55rem',letterSpacing:'0.1em',marginBottom:'3px'}}>{k}</div><div style={{fontSize:'0.83rem',fontWeight:500,color:'#e2e8f0'}}>{v}</div></div>
                        ))}
                      </div>
                      {result.confidence_score&&(
                        <div>
                          <div style={{display:'flex',justifyContent:'space-between',marginBottom:'5px'}}>
                            <span className="orb muted" style={{fontSize:'0.55rem',letterSpacing:'0.1em'}}>CONFIDENCE</span>
                            <span className="orb" style={{fontSize:'0.65rem',color:'#67e8f9'}}>{(result.confidence_score*100).toFixed(2)}%</span>
                          </div>
                          <div className="conf-track"><div className="conf-fill" style={{width:`${result.confidence_score*100}%`}}/></div>
                        </div>
                      )}
                    </div>
                  )}
                  {result.liveness_passed===false&&result.status==='failed'&&(
                    <div style={{marginTop:'10px',padding:'9px 14px',background:'rgba(244,63,94,0.08)',border:'1px solid rgba(244,63,94,0.2)',borderRadius:'8px',width:'100%'}}>
                      <span className="orb" style={{color:'#fda4af',fontSize:'0.62rem',letterSpacing:'0.06em'}}>LIVENESS CHECK FAILED — USE A LIVE CAMERA</span>
                    </div>
                  )}
                </div>
              ):(
                <div style={{flex:1,border:'1px dashed rgba(0,212,255,0.08)',borderRadius:'12px',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:'14px'}}>
                  <div style={{width:'60px',height:'60px',borderRadius:'50%',background:'rgba(0,212,255,0.04)',border:'1px solid rgba(0,212,255,0.08)',display:'flex',alignItems:'center',justifyContent:'center'}}>
                    <Camera size={26} color="#1e3a4a"/>
                  </div>
                  <span className="orb" style={{fontSize:'0.65rem',letterSpacing:'0.1em',color:'#1e3a4a'}}>AWAITING FACE</span>
                  <div style={{display:'flex',gap:'6px'}}>
                    {[0,1,2].map(i=>(
                      <div key={i} style={{width:'5px',height:'5px',borderRadius:'50%',background:'#1e3a4a',animation:`dotPulse 1.5s ${i*0.3}s infinite`}}/>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ══════════ SYSTEM DETAILS ══════════ */}
          <div className="glass" style={{padding:'26px',marginBottom:'20px'}}>
            <div style={{...S(),marginBottom:'20px'}}>
              <Cpu size={15} color="#67e8f9"/>
              <span className="orb sub" style={{fontSize:'0.68rem',letterSpacing:'0.12em'}}>SYSTEM DETAILS</span>
            </div>

            <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'14px',marginBottom:'20px'}}>
              {/* YOLOv9 */}
              <div className="sys-card">
                <div style={{width:'44px',height:'44px',borderRadius:'11px',background:'rgba(0,212,255,0.07)',border:'1px solid rgba(0,212,255,0.14)',display:'flex',alignItems:'center',justifyContent:'center',marginBottom:'12px'}}>
                  <Zap size={20} color="#67e8f9"/>
                </div>
                <div className="orb" style={{fontSize:'0.72rem',fontWeight:700,color:'#e2e8f0',marginBottom:'3px'}}>YOLOv9</div>
                <div style={{fontSize:'0.7rem',color:'#475569',marginBottom:'12px'}}>Face Detection</div>
                {[['Model','YOLOv9-C'],['Confidence','≥ 0.35'],['Speed','30+ FPS'],['Input','640×480']].map(([k,v])=>(
                  <div key={k} className="sys-stat-row">
                    <span style={{fontSize:'0.68rem',color:'#334155'}}>{k}</span>
                    <span className="orb" style={{fontSize:'0.6rem',color:'#67e8f9'}}>{v}</span>
                  </div>
                ))}
              </div>

              {/* ArcFace */}
              <div className="sys-card">
                <div style={{width:'44px',height:'44px',borderRadius:'11px',background:'rgba(139,92,246,0.07)',border:'1px solid rgba(139,92,246,0.14)',display:'flex',alignItems:'center',justifyContent:'center',marginBottom:'12px'}}>
                  <Fingerprint size={20} color="#a78bfa"/>
                </div>
                <div className="orb" style={{fontSize:'0.72rem',fontWeight:700,color:'#e2e8f0',marginBottom:'3px'}}>ArcFace</div>
                <div style={{fontSize:'0.7rem',color:'#475569',marginBottom:'12px'}}>Face Recognition</div>
                {[['Backbone','ResNet-100'],['Embeddings','512-D'],['Accuracy','> 97%'],['Threshold','0.70']].map(([k,v])=>(
                  <div key={k} className="sys-stat-row">
                    <span style={{fontSize:'0.68rem',color:'#334155'}}>{k}</span>
                    <span className="orb" style={{fontSize:'0.6rem',color:'#a78bfa'}}>{v}</span>
                  </div>
                ))}
              </div>

              {/* Liveness */}
              <div className="sys-card">
                <div style={{width:'44px',height:'44px',borderRadius:'11px',background:'rgba(16,185,129,0.07)',border:'1px solid rgba(16,185,129,0.14)',display:'flex',alignItems:'center',justifyContent:'center',marginBottom:'12px'}}>
                  <Shield size={20} color="#34d399"/>
                </div>
                <div className="orb" style={{fontSize:'0.72rem',fontWeight:700,color:'#e2e8f0',marginBottom:'3px'}}>Liveness v5</div>
                <div style={{fontSize:'0.7rem',color:'#475569',marginBottom:'12px'}}>Anti-Spoof</div>
                {[['Method','Dual-gate'],['Signals','3 image'],['Motion','5-frame'],['Block','Static photo']].map(([k,v])=>(
                  <div key={k} className="sys-stat-row">
                    <span style={{fontSize:'0.68rem',color:'#334155'}}>{k}</span>
                    <span className="orb" style={{fontSize:'0.6rem',color:'#34d399'}}>{v}</span>
                  </div>
                ))}
              </div>

              {/* Database */}
              <div className="sys-card">
                <div style={{width:'44px',height:'44px',borderRadius:'11px',background:'rgba(251,191,36,0.07)',border:'1px solid rgba(251,191,36,0.14)',display:'flex',alignItems:'center',justifyContent:'center',marginBottom:'12px'}}>
                  <Database size={20} color="#fbbf24"/>
                </div>
                <div className="orb" style={{fontSize:'0.72rem',fontWeight:700,color:'#e2e8f0',marginBottom:'3px'}}>Database</div>
                <div style={{fontSize:'0.7rem',color:'#475569',marginBottom:'12px'}}>Storage & Index</div>
                {[['DB','PostgreSQL'],['Index','FAISS-IP'],['Rebuild','On startup'],['Dedup','UPSERT']].map(([k,v])=>(
                  <div key={k} className="sys-stat-row">
                    <span style={{fontSize:'0.68rem',color:'#334155'}}>{k}</span>
                    <span className="orb" style={{fontSize:'0.6rem',color:'#fbbf24'}}>{v}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Pipeline */}
            <div style={{padding:'13px 16px',borderRadius:'10px',background:'rgba(0,212,255,0.025)',border:'1px solid rgba(0,212,255,0.07)',display:'flex',alignItems:'center',flexWrap:'wrap',gap:'4px'}}>
              {[
                {label:'WEBCAM INPUT',    c:'#67e8f9'},
                {label:'YOLOV9 DETECT',   c:'#67e8f9'},
                {label:'ALIGN 224px',     c:'#a78bfa'},
                {label:'LIVENESS CHECK',  c:'#34d399'},
                {label:'ARCFACE EMBED',   c:'#a78bfa'},
                {label:'FAISS SEARCH',    c:'#fbbf24'},
                {label:'MARK ATTENDANCE', c:'#10b981'},
              ].map((s,i,arr)=>(
                <React.Fragment key={i}>
                  <div style={{padding:'4px 10px',borderRadius:'6px',background:'rgba(0,0,0,0.3)',border:`1px solid ${s.c}22`}}>
                    <span className="orb" style={{fontSize:'0.54rem',color:s.c,letterSpacing:'0.06em'}}>{s.label}</span>
                  </div>
                  {i<arr.length-1&&<span style={{color:'#1e3a4a',fontSize:'0.75rem',padding:'0 2px'}}>→</span>}
                </React.Fragment>
              ))}
            </div>
          </div>

          <div className="orb" style={{textAlign:'center',marginTop:'8px',color:'#1e293b',fontSize:'0.58rem',letterSpacing:'0.1em'}}>
            SMART ATTENDANCE SYSTEM · AUTO-DETECT · ARCFACE &amp; YOLOV9 · {new Date().getFullYear()}
          </div>

        </div>
      </div>

      {showMenu  && <Drawer/>}
      {showLogin && <AdminLogin onClose={()=>setShowLogin(false)}/>}
    </>
  );
};

export default AttendanceCapture;
