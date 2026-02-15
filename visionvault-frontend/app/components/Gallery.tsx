"use client";
import { useState } from "react";

interface ImageItem {
  id: number;
  src: string;
}

interface GalleryProps {
  images: ImageItem[];
}

export default function Gallery({ images }: GalleryProps) {
  return (
    <div className="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-4 space-y-4">
      {images.map((img) => (
        <ImageCard key={img.id} img={img} />
      ))}
    </div>
  );
}

function ImageCard({ img }: { img: ImageItem }) {
  const [liked, setLiked] = useState(false);
  const [disliked, setDisliked] = useState(false);

  const handleLike = () => {
    setLiked(!liked);
    if (disliked) setDisliked(false); // Remove dislike if liking
  };

  const handleDislike = () => {
    setDisliked(!disliked);
    if (liked) setLiked(false); // Remove like if disliking
  };

  return (
    <div className="relative group break-inside-avoid rounded-xl overflow-hidden cursor-pointer">
      {/* Image with blur on hover */}
      <img
        src={img.src}
        alt="Gallery item"
        className="w-full rounded-xl transition-all duration-300 group-hover:blur-sm group-hover:scale-105"
      />

      {/* Icons Overlay */}
      <div className="absolute inset-0 flex items-center justify-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-black/30">
        {/* Like Button */}
        <button 
          onClick={handleLike}
          className="p-2 bg-white/90 rounded-full hover:scale-110 transition active:scale-95"
        >
          <img 
            src={liked ? "/liked.png" : "/like.png"} 
            alt="Like" 
            className="w-6 h-6 object-contain" 
          />
        </button>

        {/* Dislike Button */}
        <button 
          onClick={handleDislike}
          className="p-2 bg-white/90 rounded-full hover:scale-110 transition active:scale-95"
        >
          <img 
            src={disliked ? "/disliked.png" : "/dislike.png"} 
            alt="Dislike" 
            className="w-6 h-6 object-contain" 
          />
        </button>

        {/* Share Button */}
        <button className="p-2 bg-white/90 rounded-full hover:scale-110 transition">
          <img src="/share.png" alt="Share" className="w-6 h-6 object-contain" />
        </button>
      </div>
    </div>
  );
}