"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import Gallery from "./components/Gallery";
import NavBar from "./components/Navbar";

export default function Home() {
  const [images, setImages] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";
  const BACKEND_URL = "http://127.0.0.1:8000";
  const loaderRef = useRef(null);

  const formatImages = (data: any[]) => {
    return data.map((img: any) => {
      const rawSrc = img.src || img.image_file;
      if (!rawSrc) return null;
      return {
        id: img.id,
        src: rawSrc.startsWith('http') ? rawSrc : `${BACKEND_URL}${rawSrc}`,
        tags: img.tags || [],
        captions: img.captions || [],
        source: img.source || "DATABASE"
      };
    }).filter(Boolean);
  };

  const loadImages = useCallback(async (isNewSearch = false) => {
    if (loading || (!hasMore && !isNewSearch)) return;
    setLoading(true);
    
    const targetPage = isNewSearch ? 1 : page;
    
    try {
      const response = await fetch(`${API_BASE}/search/?q=${query}&page=${targetPage}`);
      const data = await response.json();
      
      if (data.length === 0) {
        setHasMore(false);
      } else {
        const formatted = formatImages(data);
        setImages(prev => {
          if (isNewSearch) return formatted;
          // Filter out any IDs already present in the state
          const existingIds = new Set(prev.map(i => i.id));
          return [...prev, ...formatted.filter(i => !existingIds.has(i.id))];
        });
      }
    } catch (e) {
      console.error("Fetch error", e);
    } finally {
      setLoading(false);
    }
  }, [page, query, loading, hasMore, API_BASE]);

  useEffect(() => { loadImages(true); }, [query]);

  useEffect(() => { if (page > 1) loadImages(false); }, [page]);

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !loading) {
        setPage(p => p + 1);
      }
    }, { threshold: 0.1 });
    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, [hasMore, loading]);

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar onSearchResults={(res, q) => { setQuery(q); setImages(formatImages(res)); setPage(1); setHasMore(true); }} />
      <main className="px-4 md:px-8 py-6">
        <Gallery images={images} />
        <div ref={loaderRef} className="h-20 flex justify-center items-center">
          {loading && <div className="w-8 h-8 border-4 border-t-black rounded-full animate-spin"></div>}
        </div>
      </main>
    </div>
  );
}