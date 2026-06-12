import NavBar from "./NavBar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <NavBar />
      <main style={{ maxWidth: "960px", margin: "0 auto", padding: "0 24px 24px" }}>
        {children}
      </main>
    </div>
  );
}
