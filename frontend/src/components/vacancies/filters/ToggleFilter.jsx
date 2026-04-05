export default function ToggleFilter({ label, icon: Icon, value, count, onChange }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!value)}
      className="flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 transition-all duration-200"
      style={{
        backgroundColor: value ? 'rgb(var(--accent)/0.1)' : 'rgb(var(--bg-header-muted)/0.3)',
        borderColor: value ? 'rgb(var(--accent))' : 'rgb(var(--border))',
      }}
    >
      <Icon
        className="h-4 w-4"
        style={{ color: value ? 'rgb(var(--accent))' : 'rgb(var(--text-muted))' }}
      />
      <span style={{ color: 'rgb(var(--text-primary))' }}>{label}</span>
      {count > 0 && (
        <span
          className="text-xs px-1.5 py-0.5 rounded-full"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted))',
            color: 'rgb(var(--text-muted))',
          }}
        >
          {count.toLocaleString()}
        </span>
      )}
    </button>
  );
}
