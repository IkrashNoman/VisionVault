"use client";
import { useState } from "react";
import { PlusIcon, PhotoIcon, CameraIcon } from "@heroicons/react/24/outline";

export default function Upload() {
  const [isOpen, setIsOpen] = useState(false);

  const handleCapture = (type: 'gallery' | 'camera') => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    if (type === 'camera') {
      input.capture = "environment"; // Requests the camera on mobile
    }
    input.click();
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 transition"
      >
        <PlusIcon className="h-5 w-5" />
        <span className="hidden md:inline">Upload</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white shadow-xl rounded-xl border border-gray-100 z-[60] overflow-hidden">
          <button 
            onClick={() => handleCapture('gallery')}
            className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-50 border-b border-gray-50"
          >
            <PhotoIcon className="h-5 w-5 text-gray-600" />
            <span>Upload Gallery</span>
          </button>
          <button 
            onClick={() => handleCapture('camera')}
            className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-50"
          >
            <CameraIcon className="h-5 w-5 text-gray-600" />
            <span>Live Capture</span>
          </button>
        </div>
      )}
    </div>
  );
}