"use client";
import { useState } from "react";

interface ImageItem {
  id: string | number;
  src: string;
}

export default function ImageCard({ img }: { img: ImageItem }) {
  const [liked, setLiked] = useState(false);
  const [disliked, setDisliked] = useState(false);

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevents the modal from opening when clicking like
    setLiked(!liked);
    if (disliked) setDisliked(false);
  };

  const handleDislike = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevents the modal from opening when clicking dislike
    setDisliked(!disliked);
    if (liked) setLiked(false);
  };

  return (
    <div className="relative group break-inside-avoid rounded-xl overflow-hidden cursor-pointer bg-gray-200 min-h-[100px]">
      <img
        src={img.src}
        alt="Gallery item"
        className="w-full rounded-xl transition-all duration-300 group-hover:blur-sm group-hover:scale-105"
      />

      <div className="absolute inset-0 flex items-center justify-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-black/30">
        <button onClick={handleLike} className="p-2 bg-white/90 rounded-full hover:scale-110 transition">
          <img src={liked ? "/liked.png" : "/like.png"} alt="Like" className="w-6 h-6 object-contain" />
        </button>

        <button onClick={handleDislike} className="p-2 bg-white/90 rounded-full hover:scale-110 transition">
          <img src={disliked ? "/disliked.png" : "/dislike.png"} alt="Dislike" className="w-6 h-6 object-contain" />
        </button>

        <button className="p-2 bg-white/90 rounded-full hover:scale-110 transition" onClick={(e) => e.stopPropagation()}>
          <img src="/share.png" alt="Share" className="w-6 h-6 object-contain" />
        </button>
      </div>
    </div>
  );
}