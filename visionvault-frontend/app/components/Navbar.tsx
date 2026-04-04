"use client";
import { useState, useEffect, useRef } from "react";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import Image from "next/image";
import Upload from "./Upload";
import Login from "./Login";

export default function NavBar({ onSearchResults }: { onSearchResults: (results: any[]) => void }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
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
      } catch (e) { console.error(e); }
    };
    const delay = setTimeout(getSuggestions, 200);
    return () => clearTimeout(delay);
  }, [query]);

  const triggerSearch = async (term: string) => {
    setQuery(term);
    setShowDropdown(false);
    try {
      const res = await fetch(`${API_BASE}/search/?q=${term}`);
      const data = await res.json();
      onSearchResults(data);
    } catch (e) { console.error(e); }
  };

  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-white shadow-sm sticky top-0 z-50">
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => window.location.reload()}>
        <Image src="/logo.png" alt="Logo" width={40} height={40} />
        <h1 className="text-2xl font-bold text-gray-800">VisionVault</h1>
      </div>

      <div className="flex-1 mx-10 max-w-2xl relative">
        <div className="flex items-center bg-gray-100 rounded-full px-4 py-2 ring-1 ring-gray-200 focus-within:ring-2 focus-within:ring-black focus-within:bg-white transition">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          <input 
            type="text" 
            className="bg-transparent outline-none px-3 w-full text-black"
            placeholder="Search for 'boy', 'beach', etc..."
            value={query}
            onFocus={() => setShowDropdown(true)}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && triggerSearch(query)}
          />
        </div>

        {/* The Dropdown Menu */}
        {showDropdown && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white shadow-2xl rounded-2xl border border-gray-100 overflow-hidden z-[100]">
            {suggestions.map((s, i) => (
              <button 
                key={i} 
                onClick={() => triggerSearch(s)}
                className="w-full text-left px-5 py-3 hover:bg-gray-50 text-gray-700 flex items-center gap-3 border-b last:border-none"
              >
                <MagnifyingGlassIcon className="h-4 w-4 text-gray-300" />
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <Upload />
        <Login />
      </div>
    </nav>
  );
}