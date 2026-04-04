"use client";
import { useState } from "react";
import ImageCard from "./ImageCard";
import ImageDetailModal from "./ImageDetailModal";

export default function Gallery({ images }: { images: any[] }) {
  const [selectedImage, setSelectedImage] = useState<any | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

  const handleImageClick = async (img: any) => {
    setIsModalLoading(true);
    try {
      const response = await fetch(`${API_BASE}/gallery/${img.id}/`);
      const details = await response.json();
      
      setSelectedImage({
        src: details.image_file.startsWith('http') 
             ? details.image_file 
             : `${new URL(API_BASE).origin}${details.image_file}`,
        tags: details.tags,
        captions: details.captions
      });
    } catch (error) {
      console.error("Detail fetch failed:", error);
    } finally {
      setIsModalLoading(false);
    }
  };

  return (
    <>
      <div className="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-4 space-y-4">
        {images.map((img) => (
          <div key={img.id} onClick={() => handleImageClick(img)}>
            <ImageCard img={img} />
          </div>
        ))}
      </div>

      <ImageDetailModal 
        isOpen={!!selectedImage} 
        onClose={() => setSelectedImage(null)} 
        image={selectedImage} 
      />

      {isModalLoading && (
        <div className="fixed inset-0 z-[120] bg-black/40 flex items-center justify-center cursor-wait backdrop-blur-sm">
            <div className="bg-white px-6 py-4 rounded-2xl shadow-2xl font-bold animate-pulse text-black">
              VisionVault is analyzing...
            </div>
        </div>
      )}
    </>
  );
}