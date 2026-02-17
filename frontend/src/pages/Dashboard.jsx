import { useEffect, useState } from "react";
import { fetchDashboard } from "../api/portfolio";
import SectorPie from "../components/SectorPie";
import AssetClassPie from "../components/AssetClassPie";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard()
      .then(setData)
      .catch(err => setError(err.message));
  }, []);

  if (error) return <p>Error: {error}</p>;
  if (!data) return <p>Loading portfolio…</p>;
  if (!data.positions.length) return <p>No portfolio data</p>;

  return (
    <div style={{ padding: 20 }}>
      <h2>Portfolio Snapshot: {data.snapshot_date}</h2>

      <div style={{ display: "flex", gap: 40 }}>
        <div>
          <h3>By Sector</h3>
          <SectorPie data={data.positions} />
        </div>

        <div>
          <h3>By Asset Class</h3>
          <AssetClassPie data={data.positions} />
        </div>
      </div>
    </div>
  );
}