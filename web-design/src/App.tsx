/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Navbar, Footer, Screen } from "./components/Shared";
import { LandingPage, UserGuide, GenerateWorkspace, Authentication, AboutPage } from "./components/Screens";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("landing");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleNavigate = (screen: Screen) => {
    if (!isLoggedIn && screen !== "landing" && screen !== "auth" && screen !== "about") {
      setCurrentScreen("auth");
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
    setCurrentScreen(screen);
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    handleNavigate("landing");
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case "landing":
        return <LandingPage onNavigate={handleNavigate} isLoggedIn={isLoggedIn} />;
      case "guide":
        return <UserGuide onNavigate={handleNavigate} isLoggedIn={isLoggedIn} />;
      case "about":
        return <AboutPage onNavigate={handleNavigate} isLoggedIn={isLoggedIn} />;
      case "generate":
        return <GenerateWorkspace onNavigate={handleNavigate} isLoggedIn={isLoggedIn} />;
      case "auth":
        return <Authentication onNavigate={handleNavigate} onLogin={handleLogin} />;
      default:
        return <LandingPage onNavigate={handleNavigate} isLoggedIn={isLoggedIn} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar 
        currentScreen={currentScreen} 
        isLoggedIn={isLoggedIn} 
        onNavigate={handleNavigate} 
        onLogout={handleLogout}
      />
      
      <main className="flex-grow">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScreen}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
          >
            {renderScreen()}
          </motion.div>
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
}
