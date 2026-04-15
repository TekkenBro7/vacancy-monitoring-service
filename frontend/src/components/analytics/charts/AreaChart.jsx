import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function AreaChart({
  data,
  xKey = 'date',
  yKey = 'count',
  title,
  color = '#6366f1',
  height = 300,
  gradient = true,
}) {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  };

  const gradientId = `colorGradient-${yKey}`;

  return (
    <div style={{ width: '100%', height }}>
      {title && (
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'rgb(var(--text-primary))' }}>
          {title}
        </h3>
      )}
      <ResponsiveContainer>
        <RechartsAreaChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
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
          <Area
            type="monotone"
            dataKey={yKey}
            stroke={color}
            strokeWidth={2}
            fill={gradient ? `url(#${gradientId})` : color}
            fillOpacity={gradient ? 1 : 0.3}
          />
        </RechartsAreaChart>
      </ResponsiveContainer>
    </div>
  );
}
