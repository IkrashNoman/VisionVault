"use client";
import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import LoginModal from "./LoginModal";
import SignupModal from "./SignupModal";

export default function Login() {
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSignupOpen, setIsSignupOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowAccountMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleAuthSuccess = () => {
    setIsLoggedIn(true);
    setIsLoginOpen(false);
    setIsSignupOpen(false);
    setShowAccountMenu(false);
  };

  return (
    <div className="relative" ref={menuRef}>
      <Image
        src={isLoggedIn ? "/user.png" : "/no-account.png"}
        alt="Account"
        width={40}
        height={40}
        className="rounded-full cursor-pointer border border-gray-200 object-cover aspect-square"
        onClick={() => setShowAccountMenu((prev) => !prev)}
      />

      {showAccountMenu && (
        <div className="absolute right-0 mt-2 w-40 bg-white shadow-xl rounded-xl border border-gray-100 z-[60] py-2">
          {!isLoggedIn ? (
            <>
              <button 
                onClick={() => { setIsSignupOpen(true); setShowAccountMenu(false); }}
                className="w-full text-left px-4 py-2 hover:bg-gray-50 font-medium"
              >Sign Up</button>
              <button 
                onClick={() => { setIsLoginOpen(true); setShowAccountMenu(false); }}
                className="w-full text-left px-4 py-2 hover:bg-gray-50 font-medium"
              >Login</button>
            </>
          ) : (
            <button 
              onClick={() => setIsLoggedIn(false)}
              className="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 font-medium"
            >Logout</button>
          )}
        </div>
      )}

      {/* Modals */}
      <LoginModal 
        isOpen={isLoginOpen} 
        onClose={() => setIsLoginOpen(false)} 
        onSwitchToSignup={() => { setIsLoginOpen(false); setIsSignupOpen(true); }}
        onLoginSuccess={handleAuthSuccess}
      />
    <SignupModal 
        isOpen={isSignupOpen} 
        onClose={() => setIsSignupOpen(false)}
        onSignupSuccess={handleAuthSuccess}
        onSwitchToLogin={() => { 
            setIsSignupOpen(false); 
            setIsLoginOpen(true); 
        }} 
        />
    </div>
  );
}