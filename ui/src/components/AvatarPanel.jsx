import { useEffect, useState } from "react";

export default function AvatarPanel({ script }){
  const [audioUrl, setAudioUrl] = useState("");
  const [engines, setEngines] = useState({tts:"local", avatar:"local"});

  useEffect(()=>{ fetch("/api/engines").then(r=>r.json()).then(setEngines).catch(()=>{}); },[]);
  const speak = async () => {
    const r = await fetch("/api/avatar/sync",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:script})});
    const d = await r.json(); if (d?.audio_url) setAudioUrl(d.audio_url);
  };

  return (
    <div className="card">
      <div className="flex">
        <h3 className="title-sm">Avatar</h3>
        <span className="badge">TTS: {engines.tts} · Avatar: {engines.avatar}</span>
      </div>
      <div className="placeholder">Avatar video placeholder</div>
      <p className="desc">{script}</p>
      <button className="btn" onClick={speak}>Play Intro</button>
      {audioUrl && <audio controls src={audioUrl} className="mt-2"/>}
    </div>
  );
}