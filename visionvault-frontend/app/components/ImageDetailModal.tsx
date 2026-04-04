"use client";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface ImageDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  image: {
    src: string;
    tags: string[];
    captions: { text: string; score: number; is_primary: boolean }[];
  } | null;
}

export default function ImageDetailModal({ isOpen, onClose, image }: ImageDetailModalProps) {
  if (!isOpen || !image) return null;

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/70 backdrop-blur-md p-4 md:p-10">
      <div className="bg-white w-full max-w-5xl rounded-3xl overflow-hidden shadow-2xl flex flex-col md:flex-row relative animate-in fade-in zoom-in duration-300">
        
        {/* Close Button */}
        <button onClick={onClose} className="absolute right-4 top-4 z-10 p-2 bg-white/80 rounded-full hover:bg-white transition">
          <XMarkIcon className="h-6 w-6 text-black" />
        </button>

        {/* Left Side: Image Section */}
        <div className="w-full md:w-2/3 bg-gray-100 flex items-center justify-center">
          <img src={image.src} alt="Detail" className="max-h-[80vh] w-full object-contain" />
        </div>

        {/* Right Side: Data Section */}
        <div className="w-full md:w-1/3 p-6 md:p-8 flex flex-col h-[50vh] md:h-auto overflow-y-auto">
          <h2 className="text-xl font-bold text-gray-800 mb-6">AI Insights</h2>

          {/* AI Captions */}
            <div className="mb-8">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Generated Captions</h3>
            <div className="space-y-3">
                {/* ADDED OPTIONAL CHAINING HERE TO PREVENT CRASH */}
               {image.captions?.map((cap: any, idx: number) => (
  <div key={idx} className={`p-3 rounded-xl border ${cap.is_primary ? 'bg-black text-white' : 'bg-gray-50'}`}>
    <p className="text-sm">{cap.text}</p>
    <p className="text-[10px] opacity-60">Score: {cap.score?.toFixed(2)}</p>
  </div>
))}
            </div>
            </div>

            {/* AI Tags */}
            <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Detected Tags</h3>
                <div className="flex flex-wrap gap-2">
                    {/* ADDED OPTIONAL CHAINING HERE TO PREVENT CRASH */}
                    {image.tags?.map((tag, idx) => (
                    <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">
                        #{tag}
                    </span>
                    ))}
                </div>
            </div>       
        </div>
      </div>
    </div>
  );
}