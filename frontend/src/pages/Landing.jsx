// /frontend/src/pages/Landing.jsx
import AvatarPanel from "../components/AvatarPanel";
import ChatBox from "../components/ChatBox";

const introScript = `Hey—I'm <Your Name>. This portfolio shows two sides of my work:
• DevOps: building and deploying this platform (containers, CI/CD, Kubernetes).
• AI/ML: a lightweight LLM with RAG over my profile and projects for precise Q&A.
Ask me anything about how I built it, from LangGraph/RAG to monitoring.`;

export default function Landing() {
  return (
    <div className="container">
      <h1 className="title">LinkOps AfterLife — Portfolio</h1>
      <p className="subtitle">Avatar + RAG about me and how I built this.</p>
      <div className="grid">
        <AvatarPanel script={introScript}/>
        <ChatBox />
      </div>
    </div>
  );
}