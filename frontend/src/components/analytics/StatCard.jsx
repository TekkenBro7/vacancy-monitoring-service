import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

export default function StatCard({
  title,
  value,
  change,
  changePercent,
  trend,
  icon: Icon,
  color = 'from-blue-500 to-cyan-500',
  subtitle,
}) {
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="h-3 w-3" />;
    if (trend === 'down') return <TrendingDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  const getTrendColor = () => {
    if (trend === 'up') return 'text-emerald-500';
    if (trend === 'down') return 'text-red-500';
    return 'text-gray-500';
  };

  const formatValue = (val) => {
    if (typeof val === 'number') {
      return val.toLocaleString('ru-RU');
    }
    return val;
  };

  return (
    <Card
      className="backdrop-blur-sm border transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:border-[rgb(var(--accent))/50]"
      style={{
        backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
        borderColor: 'rgb(var(--border))',
      }}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium mb-1" style={{ color: 'rgb(var(--text-muted))' }}>
              {title}
            </p>
            <p className="text-2xl font-bold" style={{ color: 'rgb(var(--text-primary))' }}>
              {formatValue(value)}
            </p>
            {(change !== undefined || subtitle) && (
              <div className="flex items-center gap-2 mt-2">
                {change !== undefined && (
                  <div className={`flex items-center gap-1 ${getTrendColor()}`}>
                    {getTrendIcon()}
                    <span className="text-xs font-medium">
                      {changePercent !== undefined
                        ? `${changePercent > 0 ? '+' : ''}${changePercent}%`
                        : change}
                    </span>
                  </div>
                )}
                {subtitle && (
                  <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                    {subtitle}
                  </span>
                )}
              </div>
            )}
          </div>
          {Icon && (
            <div className={`p-3 rounded-xl bg-gradient-to-br ${color}`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
