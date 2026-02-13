"use client";

import Image from "next/image";
import { PlusIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useState, useRef, useEffect } from "react";

const images = [
  { id: 1, src: "https://picsum.photos/500/700?random=1" },
  { id: 2, src: "https://picsum.photos/500/600?random=2" },
  { id: 3, src: "https://picsum.photos/500/800?random=3" },
  { id: 4, src: "https://picsum.photos/500/500?random=4" },
  { id: 5, src: "https://picsum.photos/500/750?random=5" },
  { id: 6, src: "https://picsum.photos/500/650?random=6" },
  { id: 7, src: "https://picsum.photos/500/900?random=7" },
  { id: 8, src: "https://picsum.photos/500/550?random=8" },
  { id: 9, src: "https://picsum.photos/500/720?random=9" },
  { id: 10, src: "https://picsum.photos/500/720?random=10" },
  { id: 11, src: "https://picsum.photos/500/720?random=11" },
  { id: 12, src: "https://picsum.photos/500/720?random=12" },
  { id: 13, src: "https://picsum.photos/500/720?random=13" },
  { id: 14, src: "https://picsum.photos/500/720?random=14" },
  { id: 15, src: "https://picsum.photos/500/720?random=15" },
  { id: 16, src: "https://picsum.photos/500/720?random=16" },
  { id: 17, src: "https://picsum.photos/500/720?random=17" },
  { id: 18, src: "https://picsum.photos/500/720?random=18" },
  { id: 19, src: "https://picsum.photos/500/720?random=19" },
  { id: 20, src: "https://picsum.photos/500/720?random=20" },
  { id: 21, src: "https://picsum.photos/500/720?random=21" },
  { id: 22, src: "https://picsum.photos/500/720?random=22" },
  { id: 23, src: "https://picsum.photos/500/720?random=23" },
  { id: 24, src: "https://picsum.photos/500/720?random=24" },
  { id: 25, src: "https://picsum.photos/500/720?random=25" },
  { id: 26, src: "https://picsum.photos/500/720?random=26" },
  { id: 27, src: "https://picsum.photos/500/720?random=27" },
  { id: 28, src: "https://picsum.photos/500/720?random=28" },
  { id: 29, src: "https://picsum.photos/500/720?random=29" },
  { id: 30, src: "https://picsum.photos/500/720?random=30" },
  { id: 31, src: "https://picsum.photos/500/720?random=31" },
  { id: 32, src: "https://picsum.photos/500/720?random=32" },
  { id: 33, src: "https://picsum.photos/500/720?random=33" },
  { id: 34, src: "https://picsum.photos/500/720?random=34" },
  { id: 35, src: "https://picsum.photos/500/720?random=35" },
  { id: 36, src: "https://picsum.photos/500/720?random=36" },
  { id: 37, src: "https://picsum.photos/500/720?random=37" },
  { id: 38, src: "https://picsum.photos/500/720?random=38" },
  { id: 39, src: "https://picsum.photos/500/720?random=39" },
  { id: 40, src: "https://picsum.photos/500/720?random=40" },
  { id: 41, src: "https://picsum.photos/500/720?random=41" },


];

export default function Home() {
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const menuRef = useRef();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowAccountMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ===== Navbar ===== */}
      <nav className="flex items-center justify-between px-4 md:px-8 py-4 bg-white shadow-sm sticky top-0 z-50">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Image src="/logo.png" alt="VisionVault Logo" width={40} height={40} />
          <h1 className="text-xl md:text-2xl font-bold text-gray-800">VisionVault</h1>
        </div>

        {/* Search Bar */}
        <div className="flex-1 mx-4 max-w-2xl hidden sm:flex items-center bg-gray-100 rounded-full px-4 py-2">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent outline-none px-3 w-full"
          />
        </div>

        {/* Right Icons */}
        <div className="flex items-center gap-4 relative">
          {/* Upload Button */}
          <button className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 transition">
            <PlusIcon className="h-5 w-5" />
            <span className="hidden md:inline">Upload</span>
          </button>

          {/* Account Image */}
          <div className="relative" ref={menuRef}>
            <Image
              src="/no-account.png"
              alt="Account"
              width={40}
              height={40}
              className="rounded-full cursor-pointer"
              onClick={() => setShowAccountMenu((prev) => !prev)}
            />

            {/* Dropdown */}
            {showAccountMenu && (
              <div className="absolute right-0 mt-2 w-32 bg-white shadow-lg rounded-lg border border-gray-200 z-50">
                <button className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded-t-lg">
                  Sign Up
                </button>
                <button className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded-b-lg">
                  Login
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* ===== Masonry Grid ===== */}
      <main className="px-4 md:px-8 py-6">
        <div className="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-4 space-y-4">
          {images.map((img) => (
            <div key={img.id} className="break-inside-avoid rounded-xl overflow-hidden hover:opacity-90 transition">
              <img src={img.src} alt="Random" className="w-full rounded-xl" />
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
