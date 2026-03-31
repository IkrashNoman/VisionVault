"use client";
import Gallery from "./components/Gallery";
import NavBar from "./components/Navbar";


const images = [
  { id: 1, src: "https://picsum.photos/900/1000?random=1" },
  { id: 2, src: "https://picsum.photos/500/100?random=2" },
  { id: 3, src: "https://picsum.photos/500/800?random=3" },
  { id: 4, src: "https://picsum.photos/100/500?random=4" },
  { id: 5, src: "https://picsum.photos/500/750?random=5" },
  { id: 6, src: "https://picsum.photos/100/650?random=6" },
  { id: 7, src: "https://picsum.photos/500/900?random=7" },
  { id: 8, src: "https://picsum.photos/500/550?random=8" },
  { id: 9, src: "https://picsum.photos/100/720?random=9" },
  { id: 10, src: "https://picsum.photos/500/720?random=10" },
  { id: 11, src: "https://picsum.photos/500/720?random=11" },
  { id: 12, src: "https://picsum.photos/100/720?random=12" },
  { id: 13, src: "https://picsum.photos/500/720?random=13" },
  { id: 14, src: "https://picsum.photos/200/720?random=14" },
  { id: 15, src: "https://picsum.photos/500/320?random=15" },
  { id: 16, src: "https://picsum.photos/500/720?random=16" },
  { id: 17, src: "https://picsum.photos/200/720?random=17" },
  { id: 18, src: "https://picsum.photos/520/720?random=18" },
  { id: 19, src: "https://picsum.photos/500/720?random=19" },
  { id: 20, src: "https://picsum.photos/590/720?random=20" },
  { id: 21, src: "https://picsum.photos/500/1100?random=21" },
  { id: 22, src: "https://picsum.photos/500/720?random=22" },
  { id: 23, src: "https://picsum.photos/500/720?random=23" },
  { id: 24, src: "https://picsum.photos/500/720?random=24" },
  { id: 25, src: "https://picsum.photos/500/720?random=25" },
  { id: 26, src: "https://picsum.photos/500/720?random=26" },
  { id: 27, src: "https://picsum.photos/500/720?random=27" },
  { id: 28, src: "https://picsum.photos/500/720?random=28" },
  { id: 29, src: "https://picsum.photos/500/720?random=29" },
  { id: 30, src: "https://picsum.photos/500/720?random=30" },
  { id: 31, src: "https://picsum.photos/500/720?random=31" },
  { id: 32, src: "https://picsum.photos/500/720?random=32" },
  { id: 33, src: "https://picsum.photos/500/720?random=33" },
  { id: 34, src: "https://picsum.photos/500/720?random=34" },
  { id: 35, src: "https://picsum.photos/500/720?random=35" },
  { id: 36, src: "https://picsum.photos/500/720?random=36" },
  { id: 37, src: "https://picsum.photos/500/720?random=37" },
  { id: 38, src: "https://picsum.photos/500/720?random=38" },
  { id: 39, src: "https://picsum.photos/500/720?random=39" },
  { id: 40, src: "https://picsum.photos/500/720?random=40" },
  { id: 41, src: "https://picsum.photos/500/720?random=41" },
];


export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="px-4 md:px-8 py-6">
        <Gallery images={images} />
      </main>
    </div>
  );
}