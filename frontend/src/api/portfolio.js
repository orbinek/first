export async function fetchDashboard() {
  const res = await fetch("http://127.0.0.1:8000/portfolio/dashboard");
  if (!res.ok) {
    throw new Error("Failed to load portfolio");
  }
  return res.json();
}