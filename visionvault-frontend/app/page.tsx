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
        id: img.id || img.public_id,
        src: rawSrc.startsWith('http') ? rawSrc : `${BACKEND_URL}${rawSrc}`,
        tags: img.tags || [],
        captions: img.captions || [],
        source: img.source || "DATABASE"
      };
    }).filter(Boolean);
  };

// Inside Home component in page.tsx
const loadImages = useCallback(async (isNewSearch = false) => {
  // Prevent overlapping calls and dead-end requests
  if (loading || (!hasMore && !isNewSearch)) return;

  setLoading(true);
  const controller = new AbortController();
  // If your hardware is this slow, the browser will timeout. Give it 10 mins.
  const timeoutId = setTimeout(() => controller.abort(), 600000); 

  try {
    const url = `${API_BASE}/search/?q=${encodeURIComponent(query)}&page=${isNewSearch ? 1 : page}`;
    const response = await fetch(url, { signal: controller.signal });
    
    if (!response.ok) {
        setHasMore(false); // STOP requesting if the server is struggling
        throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();
    const results = Array.isArray(data) ? data : (data.results || []);
    
    if (results.length === 0) {
      setHasMore(false);
    } else {
      const formatted = formatImages(results);
      setImages(prev => isNewSearch ? formatted : [...prev, ...formatted]);
      setHasMore(data.has_more ?? (results.length > 0));
    }
  } catch (e: any) {
    console.error("Critical Fetch Error:", e);
    setHasMore(false); // This is the ONLY way to stop the unlimited requests
  } finally {
    clearTimeout(timeoutId);
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
      <NavBar onSearchResults={(response, q) => {
        setQuery(q || '');
        const results = Array.isArray(response) ? response : (response.results || []);
        setImages(formatImages(results));
        setPage(1);
        setHasMore(true);
      }} />
      <main className="px-4 md:px-8 py-6">
        <Gallery images={images} />
        <div ref={loaderRef} className="h-20 flex justify-center items-center">
          {loading && <div className="w-8 h-8 border-4 border-t-black rounded-full animate-spin"></div>}
        </div>
      </main>
    </div>
  );
}