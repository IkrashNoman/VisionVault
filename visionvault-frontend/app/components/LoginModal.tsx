"use client";
import { useState } from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function LoginModal({ isOpen, onClose, onSwitchToSignup, onLoginSuccess }: any) {
  const [identifier, setIdentifier] = useState("");

  const handleForgot = () => {
    if (!identifier) {
      toast.info("Please enter your username in the field so that we can send you the gmail");
    } else {
      toast.success("Hold tight, we are sending you the password. Check your gmail.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <ToastContainer position="top-center" autoClose={3000} />
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl relative p-8">
        <button onClick={onClose} className="absolute right-4 top-4 text-gray-400 hover:text-black">
          <XMarkIcon className="h-6 w-6" />
        </button>

        <h2 className="text-2xl font-bold text-gray-800 mb-6">Login to your account</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              type="text" 
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="Enter your username or gmail" 
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-black outline-none transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              type="password" 
              placeholder="Enter your password" 
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-black outline-none transition"
            />
          </div>

          <button 
            onClick={() => onLoginSuccess()}
            className="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition mt-2"
          >
            Login
          </button>

          <div className="text-center text-sm text-gray-500 space-y-2">
            <p onClick={handleForgot} className="underline cursor-pointer hover:text-black">Forgot your password?</p>
            <p>
              Do not have an account?{" "}
              <span onClick={onSwitchToSignup} className="underline cursor-pointer hover:text-black font-bold">Signup</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}