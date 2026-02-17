import { PieChart, Pie, Tooltip, Legend } from "recharts";

export default function SectorPie({ data }) {
  const sectorData = Object.values(
    data.reduce((acc, pos) => {
      acc[pos.sector] ??= { name: pos.sector, value: 0 };
      acc[pos.sector].value += pos.market_value;
      return acc;
    }, {})
  );

  return (
    <PieChart width={400} height={300}>
      <Pie
        data={sectorData}
        dataKey="value"
        nameKey="name"
        cx="50%"
        cy="50%"
        outerRadius={100}
        label
      />
      <Tooltip />
      <Legend />
    </PieChart>
  );
}
