// /frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import Landing from "./pages/Landing";
import Demo from "./pages/Demo";
import Settings from "./pages/Settings";
import "./App.css";
import "./index.css";

export default function App() {
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
      <footer className="footer">© {new Date().getFullYear()} LinkOps AfterLife</footer>
    </BrowserRouter>
  );
}