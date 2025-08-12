// /frontend/src/components/ChatBox.jsx
import { useState } from "react";

export default function ChatBox({ placeholder="Ask about my build…" }) {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");

  const ask = async () => {
    setAnswer("");
    const res = await fetch("/api/chat", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({question: q, k: 4})
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      setAnswer(prev => prev + chunk);
    }
  };

  return (
    <div className="card">
      <h3 className="text-xl font-semibold mb-2">Ask Me Anything (RAG‑grounded)</h3>
      <div className="flex gap-2">
        <input className="input flex-1" value={q} onChange={e=>setQ(e.target.value)} placeholder={placeholder}/>
        <button className="btn" onClick={ask} disabled={!q.trim()}>Ask</button>
      </div>
      <pre className="mt-3 p-3 bg-black/5 rounded whitespace-pre-wrap">{answer}</pre>
    </div>
  );
}