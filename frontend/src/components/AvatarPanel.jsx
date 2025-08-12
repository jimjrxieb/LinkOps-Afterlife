// /frontend/src/components/AvatarPanel.jsx
import { useEffect, useState } from "react";

export default function AvatarPanel({ script }) {
  const [audioUrl, setAudioUrl] = useState("");
  const [engines, setEngines] = useState({tts:"local", avatar:"local"});

  useEffect(() => {
    fetch("/api/engines").then(r=>r.json()).then(setEngines).catch(()=>{});
  }, []);

  const speak = async () => {
    const res = await fetch("/api/avatar/sync", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({text: script})
    });
    const data = await res.json();
    if (data?.audio_url) setAudioUrl(data.audio_url);
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xl font-semibold">Your Avatar</h3>
        <span className="text-xs opacity-70">TTS: {engines.tts} · Avatar: {engines.avatar}</span>
      </div>
      <div className="border rounded p-4 bg-black/5">
        {/* Placeholder portrait area (video later) */}
        <div className="h-40 flex items-center justify-center rounded bg-black/10 mb-3">
          <span className="opacity-70">Avatar video placeholder</span>
        </div>
        <p className="text-sm mb-3">{script}</p>
        <div className="flex gap-2">
          <button className="btn" onClick={speak}>Play Intro</button>
          {audioUrl && <audio className="ml-2" controls src={audioUrl} />}
        </div>
      </div>
    </div>
  );
}