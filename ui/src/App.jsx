import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Landing from "./pages/Landing.jsx";
import Demo from "./pages/Demo.jsx";
import Settings from "./pages/Settings.jsx";
import "./index.css";

export default function App(){
  return (
    <BrowserRouter>
      <nav className="nav">
        <NavLink to="/" end>Home</NavLink>
        <NavLink to="/demo">Demo</NavLink>
        <NavLink to="/settings">Settings</NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Landing/>}/>
        <Route path="/demo" element={<Demo/>}/>
        <Route path="/settings" element={<Settings/>}/>
      </Routes>
      <footer className="footer">© {new Date().getFullYear()} LinkOps Afterlife</footer>
    </BrowserRouter>
  );
}