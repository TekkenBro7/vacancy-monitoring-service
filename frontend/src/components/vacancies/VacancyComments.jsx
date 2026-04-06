import { useState, useEffect, useCallback } from 'react';
import {
  MessageSquare,
  Star,
  Send,
  Trash2,
  User,
  Loader2,
  MessageSquarePlus,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/utils/AuthContext';
import CommentService from '@/api/services/CommentService';
import useNotification from '@/hooks/useNotification';

function StarRating({ rating, onRate, interactive = false, size = 'md', error = false }) {
  const [hovered, setHovered] = useState(0);
  const stars = [1, 2, 3, 4, 5];

  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  return (
    <div className={`flex gap-1 p-1 rounded ${error ? 'ring-2 ring-red-500/50' : ''}`}>
      {stars.map((star) => (
        <button
          key={star}
          type="button"
          disabled={!interactive}
          onClick={() => interactive && onRate(star)}
          onMouseEnter={() => interactive && setHovered(star)}
          onMouseLeave={() => interactive && setHovered(0)}
          className={`transition-all duration-200 ${interactive ? 'cursor-pointer hover:scale-110' : 'cursor-default'}`}
        >
          <Star
            className={sizeClasses[size]}
            style={{
              fill: (hovered || rating) >= star ? 'rgb(var(--accent))' : 'transparent',
              color:
                (hovered || rating) >= star
                  ? 'rgb(var(--accent))'
                  : error
                    ? 'rgb(239 68 68)'
                    : 'rgb(var(--text-muted))',
            }}
          />
        </button>
      ))}
    </div>
  );
}

function CommentCard({ comment, currentUser, onDelete, isDeleting }) {
  const isAuthor = currentUser?.id === comment.user_id;
  const isAdmin = currentUser?.role_name === 'admin';
  const canDelete = isAuthor || isAdmin;

  const authorName = comment.user?.username || 'Пользователь';
  const authorInitial = authorName.charAt(0).toUpperCase();

  const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'только что';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} мин назад`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} ч назад`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} дн назад`;

    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  return (
    <div
      className="group p-5 rounded-xl transition-all duration-300 hover:shadow-lg"
      style={{
        backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
        border: '1px solid rgb(var(--border)/0.5)',
      }}
    >
      <div className="flex items-start gap-4">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
          style={{
            background: 'linear-gradient(135deg, rgb(var(--accent)), rgb(var(--accent)/0.7))',
          }}
        >
          <span className="text-white font-bold text-sm">{authorInitial}</span>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-3">
              <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
                {authorName}
              </span>
              <span className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                {timeAgo(comment.created_at)}
              </span>
              {comment.rating && (
                <div className="flex items-center gap-1">
                  <StarRating rating={comment.rating} size="sm" />
                </div>
              )}
            </div>

            {canDelete && (
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(comment.id)}
                  disabled={isDeleting}
                  className="h-8 w-8 p-0 hover:text-red-500"
                  style={{ color: 'rgb(var(--text-muted))' }}
                  title={isAdmin && !isAuthor ? 'Удалить как админ' : 'Удалить'}
                >
                  {isDeleting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            )}
          </div>

          <p
            className="text-sm leading-relaxed whitespace-pre-wrap"
            style={{ color: 'rgb(var(--text-muted))' }}
          >
            {comment.content}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function VacancyComments({ vacancyId }) {
  const { isAuthenticated, user } = useAuth();
  const notification = useNotification();

  const [comments, setComments] = useState([]);
  const [stats, setStats] = useState({ total_comments: 0, avg_rating: null });
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [newRating, setNewRating] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [ratingError, setRatingError] = useState(false);

  const loadComments = useCallback(async () => {
    try {
      setLoading(true);
      const [commentsData, statsData] = await Promise.all([
        CommentService.getVacancyComments(vacancyId),
        CommentService.getVacancyStats(vacancyId),
      ]);
      setComments(commentsData);
      setStats(statsData);
    } catch {
      console.error('Error loading comments');
    } finally {
      setLoading(false);
    }
  }, [vacancyId]);

  useEffect(() => {
    loadComments();
  }, [loadComments]);

  useEffect(() => {
    if (newRating) {
      setRatingError(false);
    }
  }, [newRating]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!newComment.trim() || !isAuthenticated) return;

    if (!newRating) {
      setRatingError(true);
      notification.error('Ошибка', 'Пожалуйста, поставьте оценку');
      return;
    }

    setSubmitting(true);
    try {
      const created = await CommentService.createComment(vacancyId, newComment.trim(), newRating);
      setComments([created, ...comments]);
      setNewComment('');
      setNewRating(null);
      setRatingError(false);
      notification.success('Комментарий добавлен');
      const statsData = await CommentService.getVacancyStats(vacancyId);
      setStats(statsData);
    } catch {
      notification.error('Ошибка', 'Не удалось добавить комментарий');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (commentId) => {
    setDeletingId(commentId);
    try {
      await CommentService.deleteComment(commentId);
      setComments(comments.filter((c) => c.id !== commentId));
      notification.success('Комментарий удалён');
      const statsData = await CommentService.getVacancyStats(vacancyId);
      setStats(statsData);
    } catch {
      notification.error('Ошибка', 'Не удалось удалить комментарий');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
          <h2 className="text-xl font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
            Комментарии
          </h2>
          <span
            className="px-2.5 py-0.5 rounded-full text-sm font-medium"
            style={{
              backgroundColor: 'rgb(var(--accent)/0.1)',
              color: 'rgb(var(--accent))',
            }}
          >
            {stats.total_comments}
          </span>
        </div>

        {stats.avg_rating > 0 && (
          <div className="flex items-center gap-2">
            <StarRating rating={Math.round(stats.avg_rating)} size="sm" />
            <span className="font-semibold" style={{ color: 'rgb(var(--text-primary))' }}>
              {stats.avg_rating}
            </span>
          </div>
        )}
      </div>

      {isAuthenticated ? (
        <form onSubmit={handleSubmit} className="mb-8">
          <div
            className="p-5 rounded-xl"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
              border: '1px solid rgb(var(--border)/0.5)',
            }}
          >
            <div className="flex items-start gap-4">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                style={{
                  background: 'linear-gradient(135deg, rgb(var(--accent)), rgb(var(--accent)/0.7))',
                }}
              >
                <span className="text-white font-bold text-sm">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>

              <div className="flex-1 space-y-3">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Поделитесь своим мнением о вакансии..."
                  rows={3}
                  className="w-full p-3 rounded-lg resize-none focus:outline-none focus:ring-2 transition-all placeholder:text-[rgb(var(--text-muted))]"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                    color: 'rgb(var(--text-primary))',
                    border: '1px solid rgb(var(--border))',
                  }}
                />

                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <span
                        className="text-sm"
                        style={{ color: ratingError ? 'rgb(239 68 68)' : 'rgb(var(--text-muted))' }}
                      >
                        Оценка:
                        <span className="text-red-500 ml-0.5">*</span>
                      </span>
                      <StarRating
                        rating={newRating}
                        onRate={setNewRating}
                        interactive
                        error={ratingError}
                      />
                    </div>
                    {ratingError && (
                      <div className="flex items-center gap-1 text-red-500 text-sm">
                        <AlertCircle className="h-4 w-4" />
                        <span>Обязательно</span>
                      </div>
                    )}
                  </div>

                  <Button
                    type="submit"
                    disabled={submitting || !newComment.trim()}
                    className="text-white transition-all duration-300 hover:scale-105"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                    }}
                  >
                    {submitting ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4 mr-2" />
                    )}
                    Отправить
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </form>
      ) : (
        <div
          className="p-6 rounded-xl text-center mb-8"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
            border: '1px solid rgb(var(--border)/0.5)',
          }}
        >
          <MessageSquarePlus
            className="h-8 w-8 mx-auto mb-3"
            style={{ color: 'rgb(var(--text-muted))' }}
          />
          <p style={{ color: 'rgb(var(--text-muted))' }}>
            <a
              href="/login"
              className="font-medium hover:underline"
              style={{ color: 'rgb(var(--accent))' }}
            >
              Войдите
            </a>
            , чтобы оставить комментарий
          </p>
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 rounded-xl animate-pulse"
              style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.3)' }}
            />
          ))}
        </div>
      ) : comments.length > 0 ? (
        <div className="space-y-4">
          {comments.map((comment) => (
            <CommentCard
              key={comment.id}
              comment={comment}
              currentUser={user}
              onDelete={handleDelete}
              isDeleting={deletingId === comment.id}
            />
          ))}
        </div>
      ) : (
        <div
          className="p-12 rounded-xl text-center"
          style={{
            backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
            border: '1px solid rgb(var(--border)/0.3)',
          }}
        >
          <MessageSquare
            className="h-12 w-12 mx-auto mb-4"
            style={{ color: 'rgb(var(--text-muted)/0.5)' }}
          />
          <h3 className="text-lg font-medium mb-2" style={{ color: 'rgb(var(--text-primary))' }}>
            Пока нет комментариев
          </h3>
          <p style={{ color: 'rgb(var(--text-muted))' }}>
            Будьте первым, кто поделится мнением об этой вакансии
          </p>
        </div>
      )}
    </div>
  );
}
