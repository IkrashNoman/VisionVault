"use client";
import { useState, useEffect } from "react";
import { MagnifyingGlassIcon, SparklesIcon } from "@heroicons/react/24/outline";
import Image from "next/image";
import Upload from "./Upload";
import Login from "./Login";

export default function NavBar({ onSearchResults }: { onSearchResults: (results: any[]) => void }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

  // Handle Suggestions (YouTube style)
  useEffect(() => {
    const getSuggestions = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/search/?mode=suggest&q=${query}`);
        const data = await res.json();
        setSuggestions(data);
      } catch (e) { 
        console.error("Suggestion error:", e); 
      }
    };
    const delay = setTimeout(getSuggestions, 200);
    return () => clearTimeout(delay);
  }, [query, API_BASE]);

 const triggerSearch = async (term: string) => {
  setQuery(term);
  setShowDropdown(false);
  try {
    const res = await fetch(`${API_BASE}/search/?q=${term}`);
    const data = await res.json();
    // ✅ Pass both the response object and the search term
    onSearchResults(data, term);
  } catch (e) {
    console.error("Search error:", e);
  }
};

  const handleGenerateAI = async () => {
    if (!query || isGenerating) return;

    setIsGenerating(true); // Start Cooldown/Loading State
    try {
      const res = await fetch(`${API_BASE}/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: query }),
      });

      if (!res.ok) throw new Error("Generation failed");

      const data = await res.json();
      // data should be the list of new ImageStore objects from Django
      onSearchResults(data); 
      setQuery(""); // Clear input on success
      setShowDropdown(false);
    } catch (e) {
      console.error("AI Generation failed:", e);
      alert("AI Generation failed. Your GPU might be overloaded.");
    } finally {
      setIsGenerating(false); // Release Cooldown
    }
  };

  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-white shadow-sm sticky top-0 z-50">
      {/* Logo Section */}
      <div 
        className="flex items-center gap-2 cursor-pointer" 
        onClick={() => window.location.href = "/"}
      >
        <Image src="/logo.png" alt="Logo" width={40} height={40} />
        <h1 className="text-2xl font-bold text-gray-800">VisionVault</h1>
      </div>

      {/* Search and Generate Section */}
      <div className="flex-1 mx-10 max-w-2xl relative">
        <div className="flex items-center bg-gray-100 rounded-full px-4 py-2 ring-1 ring-gray-200 focus-within:ring-2 focus-within:ring-black focus-within:bg-white transition">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          <input 
            type="text" 
            className="bg-transparent outline-none px-3 w-full text-black placeholder-gray-500"
            placeholder="Search or type a prompt to generate..."
            value={query}
            onFocus={() => setShowDropdown(true)}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && triggerSearch(query)}
          />

          {/* Action Button: Conditional Rendering based on Query */}
          {query.length > 0 && (
            <button
              onClick={handleGenerateAI}
              disabled={isGenerating}
             className={`ml-2 px-4 py-1.5 rounded-full text-sm font-medium transition flex items-center gap-2 whitespace-nowrap
                ${isGenerating 
                  ? "bg-gray-400 cursor-not-allowed text-white" 
                  : "bg-black text-white hover:bg-gray-800 active:scale-95"
                }`}
            >
              {isGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Generating...
                </>
              ) : (
                <>
                  <SparklesIcon className="h-4 w-4" />
                  Generate with AI
                </>
              )}
            </button>
          )}
        </div>

        {/* The Dropdown Menu */}
        {showDropdown && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white shadow-2xl rounded-2xl border border-gray-100 overflow-hidden z-[100]">
            {suggestions.map((s, i) => (
              <button 
                key={i} 
                onClick={() => triggerSearch(s)}
                className="w-full text-left px-5 py-3 hover:bg-gray-50 text-gray-700 flex items-center gap-3 border-b last:border-none transition-colors"
              >
                <MagnifyingGlassIcon className="h-4 w-4 text-gray-300" />
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4">
        <Upload />
        <Login />
      </div>
    </nav>
  );
}