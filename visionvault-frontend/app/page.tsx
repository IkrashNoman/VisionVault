"use client";
import { useState, useEffect } from "react";
import Gallery from "./components/Gallery";
import NavBar from "./components/Navbar";

export default function Home() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";
  const BACKEND_URL = "http://127.0.0.1:8000";

  const formatImages = (data: any[]) => {
    return data.map((img: any) => {
      // Logic to handle both local 'image_file' and search 'src' fields
      const rawSrc = img.src || img.image_file;
      
      if (!rawSrc) return null; // Defensive check

      return {
        id: img.id || img.public_id,
        src: rawSrc.startsWith('http') ? rawSrc : `${BACKEND_URL}${rawSrc}`,
        tags: img.tags || [],
        captions: img.captions || [],
        source: img.source || "DATABASE"
      };
    }).filter(Boolean); // Remove any nulls
  };

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await fetch(`${API_BASE}/gallery/`);
        if (response.ok) {
          const data = await response.json();
          setImages(formatImages(data));
        }
      } catch (error) {
        console.error("Initial load failed:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchImages();
  }, [API_BASE]);

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar onSearchResults={(results) => setImages(formatImages(results))} />
      <main className="px-4 md:px-8 py-6">
        {loading ? (
          <div className="flex justify-center py-20 text-gray-400 font-bold">VisionVault is opening...</div>
        ) : (
          <Gallery images={images} />
        )}
      </main>
    </div>
  );
}