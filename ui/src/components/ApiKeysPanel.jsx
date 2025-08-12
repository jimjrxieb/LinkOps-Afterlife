import { useEffect, useState } from "react";
export default function ApiKeysPanel(){
  const [openai,setOpenai]=useState(""); const [eleven,setEleven]=useState(""); const [did,setDid]=useState("");
  useEffect(()=>{ setOpenai(localStorage.getItem("OPENAI_API_KEY")||"");
                  setEleven(localStorage.getItem("ELEVENLABS_API_KEY")||"");
                  setDid(localStorage.getItem("DID_API_KEY")||""); },[]);
  const save=()=>{ localStorage.setItem("OPENAI_API_KEY",openai);
                   localStorage.setItem("ELEVENLABS_API_KEY",eleven);
                   localStorage.setItem("DID_API_KEY",did);
                   alert("Saved locally. (Provider wiring in Sprint 2)"); };
  return (
    <div className="card">
      <h3 className="title-sm">Bring Your Own API Keys (optional)</h3>
      <label className="label">OpenAI API Key</label><input className="input" value={openai} onChange={e=>setOpenai(e.target.value)} placeholder="sk-..."/>
      <label className="label">ElevenLabs API Key</label><input className="input" value={eleven} onChange={e=>setEleven(e.target.value)} placeholder="..."/>
      <label className="label">D‑ID API Key</label><input className="input" value={did} onChange={e=>setDid(e.target.value)} placeholder="..."/>
      <button className="btn mt-2" onClick={save}>Save</button>
    </div>
  );
}