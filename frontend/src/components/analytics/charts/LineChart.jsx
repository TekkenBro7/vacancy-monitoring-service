import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function LineChart({
  data,
  xKey = 'date',
  yKey = 'count',
  title,
  color = 'rgb(var(--accent))',
  height = 300,
}) {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  };

  return (
    <div style={{ width: '100%', height }}>
      {title && (
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'rgb(var(--text-primary))' }}>
          {title}
        </h3>
      )}
      <ResponsiveContainer>
        <RechartsLineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border))" />
          <XAxis
            dataKey={xKey}
            tickFormatter={formatDate}
            stroke="rgb(var(--text-muted))"
            fontSize={12}
          />
          <YAxis stroke="rgb(var(--text-muted))" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgb(var(--bg-header))',
              border: '1px solid rgb(var(--border))',
              borderRadius: '8px',
              color: 'rgb(var(--text-primary))',
            }}
            labelFormatter={formatDate}
          />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke={color}
            strokeWidth={2}
            dot={{ fill: color, strokeWidth: 2 }}
            activeDot={{ r: 6, fill: color }}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}
