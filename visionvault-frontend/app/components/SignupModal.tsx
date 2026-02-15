"use client";
import { useState } from "react";
import { XMarkIcon, EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";

export default function SignupModal({ isOpen, onClose, onSignupSuccess, onSwitchToLogin }: any) {
  const [showPassword, setShowPassword] = useState(false);
  const [password, setPassword] = useState("");
  const [step, setStep] = useState("form"); // form, otp, googleUsername

  const getStrength = (pass: string) => {
    if (!pass) return { label: "None", color: "bg-gray-200", width: "0%" };
    if (pass.length < 4) return { label: "Very Weak", color: "bg-red-500", width: "20%" };
    if (pass.length < 8) return { label: "Weak", color: "bg-orange-500", width: "40%" };
    if (/[A-Z]/.test(pass) && /[0-9]/.test(pass)) return { label: "Strong", color: "bg-green-500", width: "80%" };
    return { label: "Extremely Strong", color: "bg-blue-500", width: "100%" };
  };

  const strength = getStrength(password);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl relative p-8 max-h-[90vh] overflow-y-auto">
        <button onClick={onClose} className="absolute right-4 top-4 text-gray-400 hover:text-black transition">
          <XMarkIcon className="h-6 w-6" />
        </button>

        {step === "form" && (
          <>
            <h2 className="text-2xl font-bold text-gray-800">New to website? SignUp</h2>
            <div className="mt-6 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Choose a cool username</label>
                <input type="text" placeholder="Enter your username" className="w-full px-4 py-2 border rounded-lg outline-none focus:border-black transition" />
                <p className="text-[10px] text-gray-400 mt-1">input field contain only alphabets, numbers, and underscores</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Enter your email</label>
                <input type="email" placeholder="Enter your email" className="w-full px-4 py-2 border rounded-lg outline-none focus:border-black transition" />
              </div>
              <div className="relative">
                <label className="text-sm font-medium text-gray-700">Choose your password</label>
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter Password" 
                  className="w-full px-4 py-2 border rounded-lg outline-none focus:border-black transition" 
                />
                <button onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-9 text-gray-400 hover:text-gray-600">
                  {showPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </button>
                {/* Strength Bar */}
                <div className="mt-2 h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div className={`h-full transition-all duration-500 ${strength.color}`} style={{ width: strength.width }}></div>
                </div>
                <div className="flex justify-between items-center mt-1">
                   <p className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">{strength.label}</p>
                   {password.length > 0 && <p className="text-[10px] font-mono text-gray-400">{strength.width.replace('%','')}</p>}
                </div>
              </div>

              <button onClick={() => setStep("otp")} className="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition active:scale-[0.98]">
                Sign Up
              </button>
              
              <div className="relative py-2 text-center">
                <span className="bg-white px-2 text-gray-400 text-sm z-10 relative">OR</span>
                <div className="absolute top-1/2 left-0 right-0 h-[1px] bg-gray-100"></div>
              </div>

              <button onClick={() => setStep("googleUsername")} className="w-full border py-2 rounded-lg flex items-center justify-center gap-2 hover:bg-gray-50 transition active:scale-[0.98]">
                <img src="/google.png" alt="Google" className="w-5 h-5" />
                <span className="font-medium text-gray-700">SignUp with Google</span>
              </button>

              <p className="text-center text-sm text-gray-500 mt-4">
                Already have an account?{" "}
                <span 
                  onClick={onSwitchToLogin} 
                  className="underline cursor-pointer hover:text-black font-semibold"
                >
                  Login
                </span>
              </p>
            </div>
          </>
        )}

        {(step === "otp" || step === "googleUsername") && (
          <div className="text-center space-y-6 py-4">
            <h2 className="text-xl font-bold text-gray-800">
              {step === "googleUsername" ? "Almost there!" : "Verify OTP"}
            </h2>
            {step === "googleUsername" && (
              <div className="text-left">
                <label className="text-sm font-medium text-gray-700">Choose Username</label>
                <input type="text" placeholder="Enter the user name" className="w-full px-4 py-2 border rounded-lg outline-none focus:border-black" />
              </div>
            )}
            <div>
              <p className="text-sm text-gray-500 mb-4">Enter the OTP we just sent you</p>
              <div className="flex justify-center gap-3">
                {[1,2,3,4].map((i) => (
                  <input key={i} type="text" maxLength={1} className="w-12 h-14 border-2 rounded-xl text-center font-bold text-2xl focus:border-black outline-none transition-colors" />
                ))}
              </div>
            </div>
            <button onClick={() => onSignupSuccess()} className="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition">
              Confirm & Finish
            </button>
            <button onClick={() => setStep("form")} className="text-sm text-gray-400 hover:text-black underline">Go Back</button>
          </div>
        )}
      </div>
    </div>
  );
}