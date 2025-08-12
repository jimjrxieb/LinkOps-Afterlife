// /frontend/src/components/ApiKeysPanel.jsx
import { useEffect, useState } from "react";

export default function ApiKeysPanel() {
  const [eleven, setEleven] = useState("");
  const [did, setDid] = useState("");

  useEffect(() => {
    setEleven(localStorage.getItem("ELEVENLABS_API_KEY") || "");
    setDid(localStorage.getItem("DID_API_KEY") || "");
  }, []);

  const save = () => {
    localStorage.setItem("ELEVENLABS_API_KEY", eleven);
    localStorage.setItem("DID_API_KEY", did);
    alert("Saved locally. (Sprint 2 will sync to backend secret endpoint.)");
  };

  return (
    <div className="card">
      <h3 className="text-xl font-semibold mb-2">Optional: Bring Your Own APIs</h3>
      <p className="text-sm opacity-80 mb-3">Not required. Defaults run locally. Add keys if you want provider voices/video in Sprint 2.</p>
      <label className="label">ElevenLabs API Key</label>
      <input className="input mb-3" value={eleven} onChange={e=>setEleven(e.target.value)} placeholder="sk-..." />
      <label className="label">D‑ID API Key</label>
      <input className="input mb-3" value={did} onChange={e=>setDid(e.target.value)} placeholder="did_..." />
      <button className="btn" onClick={save}>Save</button>
    </div>
  );
}