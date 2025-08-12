import AvatarPanel from "../components/AvatarPanel.jsx";
import ChatBox from "../components/ChatBox.jsx";

const intro = `Welcome to LinkOps Afterlife demo.
This shows DevOps (build/deploy) + AI/ML (Qwen2.5-1.5B + RAG). 
Ask how it works, what RAG does, or how to create your own avatar.`;

export default function Landing(){
  return (
    <div className="container">
      <h1 className="title">LinkOps Afterlife — OSS Demo</h1>
      <p className="subtitle">Local companion LLM + RAG with optional provider keys.</p>
      <div className="grid">
        <AvatarPanel script={intro}/>
        <ChatBox />
      </div>
    </div>
  );
}