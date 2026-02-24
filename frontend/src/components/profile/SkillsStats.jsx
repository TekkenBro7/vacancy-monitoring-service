import { Save, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function SkillsStats({ selectedCount, totalCount, initialCount, onSave, saving }) {
  const hasChanges = selectedCount !== initialCount;

  return (
    <Card
      className="backdrop-blur-sm sticky top-24"
      style={{
        backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
        borderColor: 'rgb(var(--border))',
      }}
    >
      <CardHeader>
        <CardTitle style={{ color: 'rgb(var(--text-primary))' }}>Статистика</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 rounded-lg" style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold" style={{ color: 'rgb(var(--accent))' }}>
                {selectedCount}
              </div>
              <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                Выбрано
              </div>
            </div>
            {hasChanges && (
              <div
                className="text-xs px-2 py-1 rounded-full"
                style={{ background: 'rgb(var(--accent)/20)', color: 'rgb(var(--accent))' }}
              >
                {selectedCount > initialCount ? '+' : ''}
                {selectedCount - initialCount}
              </div>
            )}
          </div>
        </div>
        <div className="p-4 rounded-lg" style={{ backgroundColor: 'rgb(var(--bg-header-muted))' }}>
          <div className="text-2xl font-bold" style={{ color: 'rgb(var(--accent))' }}>
            {totalCount}
          </div>
          <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
            Всего навыков
          </div>
        </div>
        {hasChanges && (
          <div className="flex items-center gap-2 text-sm" style={{ color: 'rgb(var(--accent))' }}>
            <CheckCircle2 className="h-4 w-4" />
            <span>Есть несохраненные изменения</span>
          </div>
        )}
        <Button
          onClick={onSave}
          disabled={saving || !hasChanges}
          className="w-full text-white transition-all duration-300 hover:scale-105 hover:shadow-lg active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{
            background: 'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
          }}
        >
          {saving ? (
            <span className="flex items-center gap-2">
              <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Сохранение...
            </span>
          ) : hasChanges ? (
            <span className="flex items-center gap-2">
              <Save className="h-4 w-4" />
              Сохранить изменения
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Сохранено
            </span>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
