// /frontend/src/pages/Demo.jsx
import { useState } from "react";

export default function Demo() {
  const [step, setStep] = useState(1);
  return (
    <div className="container">
      <h1 className="title">AfterLife — Create Your Own Avatar</h1>
      <p className="subtitle">Wizard preview (Sprint 2 wires the backend).</p>

      <ol className="steps mb-4">
        <li className={step>=1?"on":""}>1) Photos</li>
        <li className={step>=2?"on":""}>2) Voice</li>
        <li className={step>=3?"on":""}>3) Memories (RAG)</li>
        <li className={step>=4?"on":""}>4) Build</li>
        <li className={step>=5?"on":""}>5) Chat</li>
      </ol>

      {step===1 && <div className="card"><h3>Upload Photos</h3><p>Drag & drop images of your loved one.</p></div>}
      {step===2 && <div className="card"><h3>Choose Voice</h3><p>Use default TTS or bring your own key.</p></div>}
      {step===3 && <div className="card"><h3>Memories</h3><p>Paste texts/letters/stories. This powers grounded answers.</p></div>}
      {step===4 && <div className="card"><h3>Build</h3><p>We assemble avatar + memory bank locally.</p></div>}
      {step===5 && <div className="card"><h3>Chat</h3><p>Talk with the avatar—answers cite memories.</p></div>}

      <div className="mt-3 flex gap-2">
        <button className="btn" onClick={()=>setStep(s=>Math.max(1,s-1))}>Back</button>
        <button className="btn" onClick={()=>setStep(s=>Math.min(5,s+1))}>Next</button>
      </div>
    </div>
  );
}