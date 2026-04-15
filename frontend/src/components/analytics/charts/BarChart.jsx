import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const COLORS = [
  '#6366f1',
  '#8b5cf6',
  '#a855f7',
  '#d946ef',
  '#ec4899',
  '#f43f5e',
  '#f97316',
  '#eab308',
  '#22c55e',
  '#14b8a6',
];

export default function BarChart({
  data,
  xKey = 'name',
  yKey = 'count',
  title,
  layout = 'vertical',
  height = 300,
}) {
  const isVertical = layout === 'vertical';

  return (
    <div style={{ width: '100%', height }}>
      {title && (
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'rgb(var(--text-primary))' }}>
          {title}
        </h3>
      )}
      <ResponsiveContainer>
        <RechartsBarChart
          data={data}
          layout={isVertical ? 'vertical' : 'horizontal'}
          margin={{ top: 5, right: 30, left: isVertical ? 100 : 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border))" />
          {isVertical ? (
            <>
              <XAxis type="number" stroke="rgb(var(--text-muted))" fontSize={12} />
              <YAxis
                type="category"
                dataKey={xKey}
                stroke="rgb(var(--text-muted))"
                fontSize={12}
                width={90}
                tickFormatter={(value) => (value.length > 15 ? value.slice(0, 15) + '...' : value)}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey={xKey}
                stroke="rgb(var(--text-muted))"
                fontSize={12}
                tickFormatter={(value) => (value.length > 10 ? value.slice(0, 10) + '...' : value)}
              />
              <YAxis type="number" stroke="rgb(var(--text-muted))" fontSize={12} />
            </>
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgb(var(--bg-header))',
              border: '1px solid rgb(var(--border))',
              borderRadius: '8px',
              color: 'rgb(var(--text-primary))',
            }}
            formatter={(value) => [value.toLocaleString(), 'Количество']}
          />
          <Bar dataKey={yKey} radius={[4, 4, 4, 4]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}
