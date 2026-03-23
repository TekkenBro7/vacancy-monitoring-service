import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Pagination({ pagination, onPageChange }) {
  const { page, page_size, total_items, total_pages, has_next, has_prev } = pagination;

  if (total_pages <= 1) return null;

  const startItem = (page - 1) * page_size + 1;
  const endItem = Math.min(page * page_size, total_items);

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;

    if (total_pages <= maxVisible) {
      for (let i = 1; i <= total_pages; i++) {
        pages.push(i);
      }
    } else {
      if (page <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(total_pages);
      } else if (page >= total_pages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = total_pages - 3; i <= total_pages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = page - 1; i <= page + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(total_pages);
      }
    }

    return pages;
  };

  return (
    <div
      className="flex flex-col sm:flex-row items-center justify-between gap-4 py-6"
      style={{ color: 'rgb(var(--text-muted))' }}
    >
      <div className="text-sm">
        Показано с{' '}
        <span style={{ color: 'rgb(var(--text-primary))', fontWeight: 600 }}>{startItem}</span> по{' '}
        <span style={{ color: 'rgb(var(--text-primary))', fontWeight: 600 }}>{endItem}</span> из{' '}
        <span style={{ color: 'rgb(var(--text-primary))', fontWeight: 600 }}>{total_items}</span>{' '}
        вакансий
      </div>

      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(1)}
          disabled={!has_prev}
          className="transition-all duration-300 hover:scale-105"
          style={{
            borderColor: 'rgb(var(--border))',
            color: has_prev ? 'rgb(var(--text-primary))' : 'rgb(var(--text-muted))',
            opacity: has_prev ? 1 : 0.5,
          }}
        >
          <ChevronsLeft className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page - 1)}
          disabled={!has_prev}
          className="transition-all duration-300 hover:scale-105"
          style={{
            borderColor: 'rgb(var(--border))',
            color: has_prev ? 'rgb(var(--text-primary))' : 'rgb(var(--text-muted))',
            opacity: has_prev ? 1 : 0.5,
          }}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <div className="flex items-center gap-1 mx-2">
          {getPageNumbers().map((pageNum, index) =>
            pageNum === '...' ? (
              <span
                key={`ellipsis-${index}`}
                className="px-2"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                ...
              </span>
            ) : (
              <Button
                key={pageNum}
                variant={pageNum === page ? 'default' : 'outline'}
                size="sm"
                onClick={() => onPageChange(pageNum)}
                className="transition-all duration-300 hover:scale-105 min-w-[40px]"
                style={
                  pageNum === page
                    ? {
                        background:
                          'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                        color: 'white',
                        borderColor: 'transparent',
                      }
                    : {
                        borderColor: 'rgb(var(--border))',
                        color: 'rgb(var(--text-primary))',
                      }
                }
              >
                {pageNum}
              </Button>
            )
          )}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page + 1)}
          disabled={!has_next}
          className="transition-all duration-300 hover:scale-105"
          style={{
            borderColor: 'rgb(var(--border))',
            color: has_next ? 'rgb(var(--text-primary))' : 'rgb(var(--text-muted))',
            opacity: has_next ? 1 : 0.5,
          }}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(total_pages)}
          disabled={!has_next}
          className="transition-all duration-300 hover:scale-105"
          style={{
            borderColor: 'rgb(var(--border))',
            color: has_next ? 'rgb(var(--text-primary))' : 'rgb(var(--text-muted))',
            opacity: has_next ? 1 : 0.5,
          }}
        >
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
