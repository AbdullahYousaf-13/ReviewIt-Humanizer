import { Suspense } from "react";
import { connection } from "next/server";
import Navbar from "@/components/Navbar";
import Studio from "@/components/Studio";
import { DEFAULT_API_URL } from "@/lib/api";

// Read on the server at request time (not inlined at build time), so changing the
// backend URL only needs a restart. NEXT_PUBLIC_API_URL is still honoured as a fallback.
async function StudioWithApiUrl() {
  await connection();
  const apiUrl = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
  return <Studio apiUrl={apiUrl} />;
}

export default function Home() {
  return (
    <>
      <Navbar />
      <Suspense fallback={null}>
        <StudioWithApiUrl />
      </Suspense>
    </>
  );
}
