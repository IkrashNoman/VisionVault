"use client";
import { useState, useEffect } from "react";
import Gallery from "./components/Gallery";
import NavBar from "./components/Navbar";

export default function Home() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  // Use the .env variable. Ensure it is ONLY "http://127.0.0.1:8000/api" in your .env file.
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

  useEffect(() => {
  const fetchImages = async () => {
    try {
      // Use a template literal but be careful with slashes
      // If API_BASE is http://.../api, this becomes http://.../api/gallery/
      const response = await fetch(`${API_BASE}/gallery/`);
      
      if (!response.ok) {
          // If this still hits 404, look at the URL printed here:
          console.error("404 at URL:", `${API_BASE}/gallery/`);
          return;
      }

        const data = await response.json();
        
        const formattedData = data.map((img: any) => ({
          id: img.public_id,
          // Extract the host from the API_BASE to keep it dynamic and unexposed
          src: img.image_file.startsWith('http') 
               ? img.image_file 
               : `${new URL(API_BASE).origin}${img.image_file}`,
          tags: [], 
          captions: [] 
        }));

        setImages(formattedData);
      } catch (error) {
        console.error("Connection failed. Is the Django server running?", error);
      } finally {
        setLoading(false);
      }
    };
    fetchImages();
  }, [API_BASE]);

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="px-4 md:px-8 py-6">
        {loading ? (
          <div className="flex justify-center py-20 text-gray-400">Loading VisionVault...</div>
        ) : (
          <Gallery images={images} />
        )}
      </main>
    </div>
  );
}