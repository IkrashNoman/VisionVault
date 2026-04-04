"use client";
import { useState, useRef } from "react";
import { PlusIcon, PhotoIcon, CameraIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import { toast } from "react-toastify";

export default function Upload() {
  const [isOpen, setIsOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("image_file", file);
    formData.append("source", "HUMAN");

    setIsUploading(true);
    setIsOpen(false);

    try {
      const response = await fetch(`${API_BASE}/upload/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        toast.success("Image uploaded and analyzed by AI!");
        // Refresh the page to show the new image in the gallery
        window.location.reload();
      } else {
        const errorData = await response.json();
        toast.error(`Upload failed: ${JSON.stringify(errorData)}`);
      }
    } catch (error) {
      console.error("Upload Error:", error);
      toast.error("Could not connect to the server.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const triggerInput = (captureType?: string) => {
    if (fileInputRef.current) {
      if (captureType === "camera") {
        fileInputRef.current.setAttribute("capture", "environment");
      } else {
        fileInputRef.current.removeAttribute("capture");
      }
      fileInputRef.current.click();
    }
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        accept="image/*" 
        className="hidden" 
      />

      <button 
        onClick={() => setIsOpen(!isOpen)}
        disabled={isUploading}
        className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 transition disabled:bg-gray-400"
      >
        {isUploading ? (
          <ArrowPathIcon className="h-5 w-5 animate-spin" />
        ) : (
          <PlusIcon className="h-5 w-5" />
        )}
        <span className="hidden md:inline">{isUploading ? "Processing..." : "Upload"}</span>
      </button>

      {/* Uploading Overlay Animation */}
      {isUploading && (
        <div className="fixed inset-0 z-[150] bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center">
          <div className="bg-white p-8 rounded-3xl shadow-2xl flex flex-col items-center max-w-sm w-full mx-4">
            <div className="w-16 h-16 border-4 border-gray-100 border-t-black rounded-full animate-spin mb-4"></div>
            <h2 className="text-xl font-bold text-gray-800">VisionVault AI</h2>
            <p className="text-gray-500 text-center mt-2 text-sm">
              Uploading image and generating smart tags and captions...
            </p>
            <div className="w-full bg-gray-100 h-2 rounded-full mt-6 overflow-hidden">
              <div className="bg-black h-full animate-[loading_2s_ease-in-out_infinite] w-1/2"></div>
            </div>
          </div>
        </div>
      )}

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white shadow-xl rounded-xl border border-gray-100 z-[60] overflow-hidden">
          <button 
            onClick={() => triggerInput()}
            className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-50 border-b border-gray-50"
          >
            <PhotoIcon className="h-5 w-5 text-gray-600" />
            <span className="text-black">Upload Gallery</span>
          </button>
          <button 
            onClick={() => triggerInput("camera")}
            className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-50"
          >
            <CameraIcon className="h-5 w-5 text-gray-600" />
            <span className="text-black">Live Capture</span>
          </button>
        </div>
      )}
    </div>
  );
}