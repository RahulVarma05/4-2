import { useState } from "react";
import { motion } from "motion/react";

export type Screen = "landing" | "guide" | "generate" | "auth" | "about";

interface NavbarProps {
  currentScreen: Screen;
  isLoggedIn: boolean;
  onNavigate: (screen: Screen) => void;
  onLogout: () => void;
}

export function Navbar({ currentScreen, isLoggedIn, onNavigate, onLogout }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 w-full z-50 bg-stone-50/70 backdrop-blur-xl shadow-[0_20px_40px_rgba(14,14,14,0.06)]">
      <div className="flex justify-between items-center px-8 py-4 w-full max-w-[1440px] mx-auto">
        <div 
          className="flex flex-col leading-[0.7] cursor-pointer group select-none items-center justify-center"
          onClick={() => onNavigate("landing")}
        >
          <img 
            src="/logo.png" 
            alt="Motion Mimic" 
            onError={(e) => {
              e.currentTarget.style.display = 'none';
              e.currentTarget.nextElementSibling?.classList.remove('hidden');
            }}
            className="h-16 md:h-20 opacity-90 group-hover:opacity-100 transition-opacity" 
          />
          <span className="font-black text-xl hidden">Motion Mimic</span>
        </div>
        <div className="hidden md:flex items-center space-x-8">
          <button 
            onClick={() => onNavigate("generate")}
            className={`text-sm font-bold uppercase tracking-widest transition-colors ${
              currentScreen === "generate" ? "text-primary border-b-2 border-primary pb-1" : "text-stone-600 hover:text-stone-900"
            }`}
          >
            Generate
          </button>
          <button 
            onClick={() => onNavigate("guide")}
            className={`text-sm font-bold uppercase tracking-widest transition-colors ${
              currentScreen === "guide" ? "text-primary border-b-2 border-primary pb-1" : "text-stone-600 hover:text-stone-900"
            }`}
          >
            User Guide
          </button>
          <button 
            onClick={() => onNavigate("about")}
            className={`text-sm font-bold uppercase tracking-widest transition-colors ${
              currentScreen === "about" ? "text-primary border-b-2 border-primary pb-1" : "text-stone-600 hover:text-stone-900"
            }`}
          >
            About
          </button>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            className="md:hidden p-2"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <span className="block w-6 h-0.5 bg-stone-900 mb-1" />
            <span className="block w-6 h-0.5 bg-stone-900 mb-1" />
            <span className="block w-6 h-0.5 bg-stone-900" />
          </button>
          {isLoggedIn ? (
            <button 
              onClick={onLogout}
              className="text-stone-600 font-bold uppercase tracking-widest text-sm hover:text-stone-900 px-4 py-2 active:scale-95 transition-all"
            >
              Sign Out
            </button>
          ) : (
            <button 
              onClick={() => onNavigate("auth")}
              className="text-stone-600 font-bold uppercase tracking-widest text-sm hover:text-stone-900 px-4 py-2 active:scale-95 transition-all"
            >
              Login
            </button>
          )}
        </div>
      </div>
      
      {menuOpen && (
        <div className="md:hidden absolute top-full left-0 w-full bg-white shadow-lg py-4 flex flex-col items-center gap-4">
          <button onClick={() => { onNavigate("generate"); setMenuOpen(false); }} className="font-bold uppercase tracking-widest text-sm">Generate</button>
          <button onClick={() => { onNavigate("guide"); setMenuOpen(false); }} className="font-bold uppercase tracking-widest text-sm">User Guide</button>
          <button onClick={() => { onNavigate("about"); setMenuOpen(false); }} className="font-bold uppercase tracking-widest text-sm">About</button>
        </div>
      )}
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="w-full py-8">
      <div className="max-w-[1440px] mx-auto px-8 flex justify-center">
        {/* Content removed as per request */}
      </div>
    </footer>
  );
}
