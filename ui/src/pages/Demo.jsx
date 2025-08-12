import { useState } from "react";

export default function Demo(){
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "My Avatar",
    memories: [""],
    personality: { bio: "", tone: "friendly" },
    voiceSample: ""
  });
  const [jobId, setJobId] = useState("");
  const [building, setBuilding] = useState(false);
  const [buildResult, setBuildResult] = useState(null);

  const updateMemory = (index, value) => {
    const newMemories = [...formData.memories];
    newMemories[index] = value;
    setFormData({ ...formData, memories: newMemories });
  };

  const addMemory = () => {
    setFormData({ ...formData, memories: [...formData.memories, ""] });
  };

  const buildAvatar = async () => {
    setBuilding(true);
    try {
      const response = await fetch("/api/wizard/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
          memories: formData.memories.filter(m => m.trim()),
          personality: {
            bio: formData.personality.bio,
            style: { tone: formData.personality.tone }
          },
          voice_sample: formData.voiceSample
        })
      });
      const result = await response.json();
      setJobId(result.job_id);
      setBuildResult(result);
      setStep(5);
    } catch (error) {
      console.error("Build failed:", error);
      alert("Build failed. Please try again.");
    }
    setBuilding(false);
  };

  const downloadPack = () => {
    if (!jobId) return;
    const link = document.createElement('a');
    link.href = `/api/wizard/export/${jobId}.zip`;
    link.download = `${formData.name.replace(/[^a-zA-Z0-9]/g, '_')}_avatar.zip`;
    link.click();
  };

  const deletePack = async () => {
    if (!jobId) return;
    try {
      await fetch(`/api/wizard/purge/${jobId}`, { method: "POST" });
      setJobId("");
      setBuildResult(null);
      alert("Avatar pack deleted.");
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  const resetDemo = () => {
    setStep(1);
    setJobId("");
    setBuildResult(null);
    setFormData({
      name: "My Avatar",
      memories: [""],
      personality: { bio: "", tone: "friendly" },
      voiceSample: ""
    });
  };

  return (
    <div className="container">
      <h1 className="title">Create Your Avatar</h1>
      <p className="subtitle">Build → Download → Auto-Delete (No server storage)</p>
      
      <ol className="steps">
        <li className={step>=1?"on":""}>Basic Info</li>
        <li className={step>=2?"on":""}>Voice Sample</li>
        <li className={step>=3?"on":""}>Memories (RAG)</li>
        <li className={step>=4?"on":""}>Build Pack</li>
        <li className={step>=5?"on":""}>Download</li>
      </ol>

      <div className="card">
        {step===1 && (
          <div>
            <h3>Avatar Name & Personality</h3>
            <label className="label">Avatar Name</label>
            <input 
              className="input" 
              value={formData.name} 
              onChange={e => setFormData({...formData, name: e.target.value})}
              placeholder="e.g., Grandma Rose, Tech Mentor"
            />
            <label className="label">Bio/Description</label>
            <textarea 
              className="input" 
              rows="3"
              value={formData.personality.bio} 
              onChange={e => setFormData({
                ...formData, 
                personality: {...formData.personality, bio: e.target.value}
              })}
              placeholder="Brief description of who this avatar represents..."
            />
            <label className="label">Tone</label>
            <select 
              className="input" 
              value={formData.personality.tone}
              onChange={e => setFormData({
                ...formData,
                personality: {...formData.personality, tone: e.target.value}
              })}
            >
              <option value="friendly">Friendly</option>
              <option value="professional">Professional</option>
              <option value="warm">Warm & Caring</option>
              <option value="witty">Witty & Humorous</option>
            </select>
          </div>
        )}

        {step===2 && (
          <div>
            <h3>Voice Sample</h3>
            <p className="desc">Enter text for a voice sample (optional):</p>
            <textarea 
              className="input" 
              rows="3"
              value={formData.voiceSample} 
              onChange={e => setFormData({...formData, voiceSample: e.target.value})}
              placeholder="Hello, I'm your avatar. This is how I sound..."
            />
            <p className="desc">💡 This creates a short audio sample in your download pack.</p>
          </div>
        )}

        {step===3 && (
          <div>
            <h3>Memories & Knowledge</h3>
            <p className="desc">Add memories, stories, or information for RAG:</p>
            {formData.memories.map((memory, i) => (
              <div key={i} className="mt-1">
                <textarea 
                  className="input" 
                  rows="3"
                  value={memory}
                  onChange={e => updateMemory(i, e.target.value)}
                  placeholder={`Memory ${i+1}: Tell a story, share knowledge, or describe experiences...`}
                />
              </div>
            ))}
            <button className="btn mt-1" onClick={addMemory}>+ Add Memory</button>
          </div>
        )}

        {step===4 && (
          <div>
            <h3>Build Avatar Pack</h3>
            <div className="summary">
              <p><strong>Name:</strong> {formData.name}</p>
              <p><strong>Memories:</strong> {formData.memories.filter(m => m.trim()).length} entries</p>
              <p><strong>Voice Sample:</strong> {formData.voiceSample ? "✓ Included" : "None"}</p>
              <p><strong>Personality:</strong> {formData.personality.tone}</p>
            </div>
            <p className="desc">Ready to build your avatar pack? This creates a downloadable .zip file with all assets.</p>
            <button 
              className="btn btn-primary" 
              onClick={buildAvatar} 
              disabled={building}
              style={{backgroundColor: building ? "#ccc" : "#0066cc", color: "white", width: "100%", marginTop: "1rem"}}
            >
              {building ? "Building..." : "🔨 Build Avatar Pack"}
            </button>
          </div>
        )}

        {step===5 && buildResult && (
          <div>
            <h3>✅ Avatar Pack Ready!</h3>
            <div className="success-box" style={{background: "#e8f5e8", padding: "1rem", borderRadius: "8px", margin: "1rem 0"}}>
              <p><strong>Job ID:</strong> {jobId}</p>
              <p><strong>Files:</strong> {buildResult.files.length} files created</p>
              <p><strong>Expires:</strong> ~{Math.floor(buildResult.expires_in/60)} minutes</p>
            </div>
            
            <div className="download-actions">
              <button 
                className="btn btn-primary" 
                onClick={downloadPack}
                style={{backgroundColor: "#22c55e", color: "white", marginRight: "0.5rem"}}
              >
                📥 Download Avatar Pack (.zip)
              </button>
              <button 
                className="btn" 
                onClick={deletePack}
                style={{backgroundColor: "#dc2626", color: "white", marginRight: "0.5rem"}}
              >
                🗑️ Delete Now
              </button>
              <button className="btn" onClick={resetDemo}>
                🔄 Create Another
              </button>
            </div>

            <div className="info-box" style={{background: "#fef3c7", padding: "1rem", borderRadius: "8px", marginTop: "1rem"}}>
              <h4>What's in your pack:</h4>
              <ul style={{margin: "0.5rem 0", paddingLeft: "1.5rem"}}>
                <li>📄 README.txt - Setup instructions</li>
                <li>🖼️ avatar.png - Profile image</li>
                <li>🎵 sample_speech.wav - Voice sample (if provided)</li>
                <li>💾 memory/ - Your memories + personality config</li>
                <li>⚙️ config.json - Build settings</li>
              </ul>
              <p><strong>💡 Privacy:</strong> No server storage. Files auto-delete in ~30 minutes.</p>
            </div>
          </div>
        )}
      </div>

      <div className="row mt-2">
        {step > 1 && step < 5 && (
          <button className="btn" onClick={() => setStep(s => s - 1)}>Back</button>
        )}
        {step < 4 && (
          <button className="btn" onClick={() => setStep(s => s + 1)}>Next</button>
        )}
        {step === 4 && !building && (
          <div style={{marginLeft: "auto"}}>
            <span style={{fontSize: "0.9rem", color: "#666", marginRight: "1rem"}}>
              Ready to build?
            </span>
          </div>
        )}
      </div>
    </div>
  );
}