import { useState } from "react";

export default function ChatBox({ placeholder="Ask about this demo…" }){
  const [q,setQ]=useState(""); const [a,setA]=useState("");

  const ask = async () => {
    setA("");
    const res = await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question:q,k:4})});
    const reader = res.body.getReader(); const dec = new TextDecoder();
    while(true){ const {value,done}=await reader.read(); if(done) break; setA(prev=>prev+dec.decode(value)); }
  };

  return (
    <div className="card">
      <h3 className="title-sm">RAG Chat</h3>
      <div className="row">
        <input className="input" value={q} onChange={e=>setQ(e.target.value)} placeholder={placeholder}/>
        <button className="btn" onClick={ask} disabled={!q.trim()}>Ask</button>
      </div>
      <pre className="answer">{a}</pre>
    </div>
  );
}