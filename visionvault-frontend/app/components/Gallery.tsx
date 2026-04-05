"use client";
import { useState } from "react";
import ImageCard from "./ImageCard";
import ImageDetailModal from "./ImageDetailModal";

// components/Gallery.tsx
export default function Gallery({ images }: { images: any[] }) {
  const [selectedImage, setSelectedImage] = useState<any | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

const handleImageClick = async (img: any) => {
  if (img.source === "INTERNET") {
    setSelectedImage(img);
    
    // Trigger the Silent Upload
    fetch(`${API_BASE}/silent-upload/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_url: img.src,
        // Strip prefix so it matches the CharField on backend
        external_id: String(img.id).replace('web_', ''),
        tags: img.tags,
        caption: img.captions[0]?.text
      })
    }).catch(err => console.error("Upload trigger failed", err));
    
    return;
  }
    // Local DB fetch for full tags/captions
    setIsModalLoading(true);
    try {
      const response = await fetch(`${API_BASE}/gallery/${img.id}/`);
      const details = await response.json();
      setSelectedImage({
        src: img.src,
        tags: details.tags,
        captions: details.captions
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsModalLoading(false);
    }
  };

  return (
    <>
      <div className="columns-2 sm:columns-3 md:columns-4 lg:columns-5 gap-4 space-y-4">
        {images.map((img) => (
          // Use a combined key of source + id to be 100% unique
          <div key={`${img.source}-${img.id}`} onClick={() => handleImageClick(img)}>
            <ImageCard img={img} />
          </div>
        ))}
      </div>
      <ImageDetailModal isOpen={!!selectedImage} onClose={() => setSelectedImage(null)} image={selectedImage} />
    </>
  );
}