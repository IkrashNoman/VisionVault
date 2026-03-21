import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import Image from "next/image";
import Login from "./Login";
import Upload from "./Upload";

export default function NavBar(){
    return(
        <nav className="flex items-center justify-between px-4 md:px-8 py-4 bg-white shadow-sm sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <Image src="/logo.png" alt="VisionVault" width={40} height={40} />
          <h1 className="text-xl md:text-2xl font-bold text-gray-800">VisionVault</h1>
        </div>

        <div className="flex-1 mx-4 max-w-2xl hidden sm:flex items-center bg-gray-100 rounded-full px-4 py-2">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-500" />
          <input type="text" placeholder="Search..." className="bg-transparent outline-none px-3 w-full text-black placeholder-gray-400" />
        </div>

        <div className="flex items-center gap-4">
          <Upload />
          <Login />
        </div>
      </nav>
    );
}