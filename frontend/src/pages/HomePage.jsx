import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Sparkles,
  ArrowRight,
  Briefcase,
  Zap,
  Shield,
  TrendingUp,
  Star,
  Database,
  Layers,
  CheckCircle,
  User,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import useNotification from '@/hooks/useNotification';
import VacancyService from '@/api/services/VacancyService';
import VacancyCard from '@/components/vacancies/VacancyCard';
import { useAuth } from '@/utils/AuthContext';

export default function HomePage() {
  const navigate = useNavigate();
  const notification = useNotification();
  const { isAuthenticated } = useAuth();
  const [vacancies, setVacancies] = useState([]);
  const [loadingVacancies, setLoadingVacancies] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const oauthLogin = localStorage.getItem('oauthLogin');
    if (oauthLogin === 'true') {
      localStorage.removeItem('oauthLogin');
      notification.success('Вход выполнен успешно', 'Добро пожаловать в систему');
    }
  }, [notification]);

  useEffect(() => {
    loadVacancies();
  }, []);

  const loadVacancies = async () => {
    try {
      setLoadingVacancies(true);
      const data = await VacancyService.getVacancies({ page: 1, page_size: 4 });
      setVacancies(data.items || []);
    } catch (error) {
      console.error('Error loading vacancies:', error);
    } finally {
      setLoadingVacancies(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(
      `/vacancies${searchQuery.trim() ? `?search=${encodeURIComponent(searchQuery.trim())}` : ''}`
    );
  };

  const sources = [
    { name: 'HeadHunter', color: 'from-red-500 to-rose-600' },
    { name: 'SuperJob', color: 'from-blue-500 to-indigo-600' },
    { name: 'Praca.by', color: 'from-emerald-500 to-green-600' },
    { name: 'Telegram', color: 'from-sky-400 to-blue-500' },
    { name: 'EPAM', color: 'from-cyan-500 to-blue-600' },
    { name: 'Wargaming', color: 'from-orange-500 to-amber-600' },
  ];

  const features = [
    { icon: Database, title: '6 источников', color: 'from-blue-500 to-cyan-500' },
    { icon: Sparkles, title: 'AI-анализ', color: 'from-violet-500 to-purple-500' },
    { icon: TrendingUp, title: 'Аналитика', color: 'from-emerald-500 to-teal-500' },
    { icon: Zap, title: 'Ежедневно', color: 'from-amber-500 to-orange-500' },
  ];

  const steps = [
    { num: '01', title: 'Ищите', desc: 'Введите должность или навыки', icon: Search },
    { num: '02', title: 'Сравнивайте', desc: 'Анализируйте предложения', icon: Layers },
    { num: '03', title: 'Откликайтесь', desc: 'Переходите на источник', icon: CheckCircle },
  ];

  return (
    <div className="min-h-screen">
      <section className="relative pt-10 pb-6 lg:pt-16 lg:pb-10">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] rounded-full blur-3xl opacity-12 dark:opacity-6"
            style={{
              background: 'radial-gradient(ellipse, rgb(var(--accent)) 0%, transparent 60%)',
            }}
          />
        </div>

        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-2xl mx-auto text-center">
            <Badge
              className="mb-5 px-3 py-1.5 text-sm border gap-2"
              style={{
                background: 'linear-gradient(135deg, rgb(var(--accent))/10, rgb(var(--accent))/5)',
                borderColor: 'rgb(var(--accent))/0.2',
                color: 'rgb(var(--accent))',
              }}
            >
              <span className="relative flex h-2 w-2">
                <span
                  className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                  style={{ backgroundColor: 'rgb(var(--accent))' }}
                />
                <span
                  className="relative inline-flex rounded-full h-2 w-2"
                  style={{ backgroundColor: 'rgb(var(--accent))' }}
                />
              </span>
              10,000+ вакансий
            </Badge>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 leading-tight">
              <span style={{ color: 'rgb(var(--text-primary))' }}>Все IT-вакансии </span>
              <span
                className="bg-clip-text text-transparent"
                style={{
                  backgroundImage: 'linear-gradient(135deg, rgb(var(--accent)), rgb(168, 85, 247))',
                }}
              >
                в одном месте
              </span>
            </h1>

            <p
              className="text-base lg:text-lg mb-6 max-w-lg mx-auto"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              Агрегируем вакансии с лучших площадок. AI помогает найти идеальные предложения.
            </p>

            <form onSubmit={handleSearch} className="max-w-xl mx-auto mb-6">
              <div
                className="flex items-center gap-2 p-1.5 rounded-2xl border shadow-lg transition-all focus-within:shadow-xl focus-within:border-[rgb(var(--accent))]/30"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <div
                  className="flex items-center justify-center w-10 h-10 rounded-xl flex-shrink-0"
                  style={{ backgroundColor: 'rgb(var(--accent))/10' }}
                >
                  <Search className="h-5 w-5" style={{ color: 'rgb(var(--accent))' }} />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="React, Python, DevOps, Минск..."
                  className="flex-1 h-10 bg-transparent text-base outline-none border-none"
                  style={{ color: 'rgb(var(--text-primary))' }}
                />
                <Button
                  type="submit"
                  className="h-10 px-6 rounded-xl text-white font-semibold transition-all hover:scale-[1.02]"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                >
                  Найти
                </Button>
              </div>
            </form>

            <div className="flex flex-wrap justify-center gap-2 mb-6">
              {sources.map((source) => (
                <div
                  key={source.name}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                  }}
                >
                  <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-r ${source.color}`} />
                  {source.name}
                </div>
              ))}
            </div>

            <div className="flex justify-center gap-3 flex-wrap">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl border"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.4)',
                    borderColor: 'rgb(var(--border)/0.5)',
                  }}
                >
                  <div className={`p-1.5 rounded-lg bg-gradient-to-br ${feature.color}`}>
                    <feature.icon className="h-3.5 w-3.5 text-white" />
                  </div>
                  <span
                    className="text-sm font-medium"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    {feature.title}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-6">
        <div className="container mx-auto px-6">
          <div
            className="max-w-4xl mx-auto p-6 rounded-2xl border"
            style={{
              backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
              borderColor: 'rgb(var(--border)/0.5)',
            }}
          >
            <div className="grid grid-cols-3 gap-6">
              {steps.map((step, i) => (
                <div key={step.num} className="relative text-center">
                  {i < steps.length - 1 && (
                    <div
                      className="hidden md:block absolute top-7 left-[55%] w-[90%] h-px"
                      style={{
                        background:
                          'linear-gradient(90deg, rgb(var(--accent))/50, rgb(var(--accent))/5)',
                      }}
                    />
                  )}
                  <div
                    className="relative inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--accent))/15, rgb(var(--accent))/5)',
                      border: '1px solid rgb(var(--accent))/0.3',
                    }}
                  >
                    <step.icon className="h-6 w-6" style={{ color: 'rgb(var(--accent))' }} />
                  </div>
                  <div
                    className="text-[10px] font-bold tracking-widest mb-1.5"
                    style={{ color: 'rgb(var(--accent))' }}
                  >
                    ШАГ {step.num}
                  </div>
                  <h3 className="font-bold mb-1" style={{ color: 'rgb(var(--text-primary))' }}>
                    {step.title}
                  </h3>
                  <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                    {step.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Badge
                  className="border text-xs"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--accent))/10, rgb(var(--accent))/5)',
                    borderColor: 'rgb(var(--accent))/0.2',
                    color: 'rgb(var(--accent))',
                  }}
                >
                  <Zap className="h-3 w-3 mr-1" />
                  Свежие
                </Badge>
                <h2
                  className="text-xl lg:text-2xl font-bold"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Последние вакансии
                </h2>
              </div>
              <Button
                size="sm"
                className="text-white transition-all hover:scale-[1.02]"
                style={{
                  background:
                    'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                }}
                asChild
              >
                <Link to="/vacancies">
                  Все вакансии
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </div>

            <div className="space-y-4">
              {loadingVacancies
                ? [...Array(4)].map((_, i) => (
                    <div
                      key={i}
                      className="h-44 rounded-2xl animate-pulse"
                      style={{ backgroundColor: 'rgb(var(--bg-header-muted)/0.3)' }}
                    />
                  ))
                : vacancies
                    .slice(0, 4)
                    .map((vacancy) => <VacancyCard key={vacancy.id} vacancy={vacancy} />)}
            </div>

            <div className="mt-8 text-center">
              <Button
                variant="outline"
                className="h-11 px-8 rounded-xl border-2 transition-all hover:scale-[1.02]"
                style={{ borderColor: 'rgb(var(--border))', color: 'rgb(var(--text-primary))' }}
                asChild
              >
                <Link to="/vacancies">
                  <Briefcase className="h-4 w-4 mr-2" />
                  Смотреть все вакансии
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-6">
          <div
            className="max-w-6xl mx-auto relative overflow-hidden rounded-2xl p-6 lg:p-8"
            style={{
              background:
                'linear-gradient(135deg, rgb(var(--bg-header-muted)/0.5), rgb(var(--accent))/5)',
              border: '1px solid rgb(var(--border)/0.5)',
            }}
          >
            <div
              className="absolute top-0 right-0 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none"
              style={{
                background: 'radial-gradient(circle, rgb(var(--accent)) 0%, transparent 50%)',
              }}
            />

            <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="text-xl lg:text-2xl font-bold mb-1">
                  <span style={{ color: 'rgb(var(--text-primary))' }}>
                    {isAuthenticated ? 'Продолжайте поиск ' : 'Начните поиск '}
                  </span>
                  <span
                    className="bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(135deg, rgb(var(--accent)), rgb(168, 85, 247))',
                    }}
                  >
                    прямо сейчас
                  </span>
                </h2>
                <p className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                  {isAuthenticated
                    ? 'Ваш профиль поможет найти лучшие вакансии'
                    : 'Тысячи IT-специалистов уже нашли работу мечты'}
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  className="h-11 px-6 rounded-xl text-white font-medium transition-all hover:scale-[1.02]"
                  style={{
                    background:
                      'linear-gradient(135deg, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                  asChild
                >
                  <Link to="/vacancies">
                    <Briefcase className="h-4 w-4 mr-2" />
                    Вакансии
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  className="h-11 px-6 rounded-xl border-2 transition-all hover:scale-[1.02]"
                  style={{ borderColor: 'rgb(var(--border))', color: 'rgb(var(--text-primary))' }}
                  asChild
                >
                  <Link to={isAuthenticated ? '/profile' : '/register'}>
                    <User className="h-4 w-4 mr-2" />
                    {isAuthenticated ? 'Профиль' : 'Регистрация'}
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-6 pb-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-wrap justify-center gap-8">
            {[
              { icon: Shield, text: 'Проверенные источники' },
              { icon: Zap, text: 'Обновления каждый день' },
              { icon: Star, text: 'Полностью бесплатно' },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-2">
                <item.icon className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                  {item.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
