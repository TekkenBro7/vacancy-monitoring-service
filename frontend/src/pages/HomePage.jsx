import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  TrendingUp,
  Users,
  Zap,
  Target,
  Sparkles,
  ArrowRight,
  Briefcase,
  Building,
  MapPin,
  DollarSign,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import useNotification from '@/hooks/useNotification';
import VacancyService from '@/api/services/VacancyService';
import VacancyList from '@/components/vacancies/VacancyList';

export default function HomePage() {
  const notification = useNotification();
  const [vacancies, setVacancies] = useState([]);
  const [loadingVacancies, setLoadingVacancies] = useState(false);

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
      const data = await VacancyService.getVacancies({ page: 1, page_size: 3 });
      setVacancies(data.items || []); // Берем только items из пагинированного ответа
    } catch (error) {
      console.error('Error loading vacancies:', error);
    } finally {
      setLoadingVacancies(false);
    }
  };
  const categories = [
    {
      title: 'Backend разработка',
      count: '1.2K+',
      icon: Target,
      color: 'bg-gradient-to-r from-blue-400 to-cyan-400 dark:from-blue-500 dark:to-cyan-500',
    },
    {
      title: 'Frontend разработка',
      count: '850+',
      icon: Zap,
      color: 'bg-gradient-to-r from-purple-400 to-pink-400 dark:from-purple-500 dark:to-pink-500',
    },
    {
      title: 'Data Science',
      count: '420+',
      icon: TrendingUp,
      color: 'bg-gradient-to-r from-emerald-400 to-teal-400 dark:from-emerald-500 dark:to-teal-500',
    },
    {
      title: 'DevOps',
      count: '380+',
      icon: Sparkles,
      color: 'bg-gradient-to-r from-amber-400 to-orange-400 dark:from-amber-500 dark:to-orange-500',
    },
  ];

  const stats = [
    { value: '12K+', label: 'Активных вакансий', icon: Briefcase },
    { value: '850+', label: 'Компаний-партнеров', icon: Building },
    { value: '50K+', label: 'Пользователей', icon: Users },
    { value: '99%', label: 'Удовлетворенности', icon: Sparkles },
  ];

  return (
    <div className="min-h-screen transition-colors duration-300">
      <section className="relative overflow-hidden pt-20 pb-16">
        <div
          className="absolute top-0 left-0 right-0 h-px"
          style={{
            background:
              'linear-gradient(to right, transparent, rgb(var(--accent))/30, transparent)',
          }}
        />
        <div
          className="absolute -top-20 -right-20 w-80 h-80 rounded-full blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgb(var(--accent))/10 0%, transparent 70%)',
          }}
        />
        <div
          className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgb(var(--accent))/5 0%, transparent 70%)',
          }}
        />

        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div
              className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full backdrop-blur-sm border"
              style={{
                backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                borderColor: 'rgb(var(--border))',
              }}
            >
              <Sparkles className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
              <span className="text-sm" style={{ color: 'rgb(var(--accent))' }}>
                Платформа нового поколения
              </span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span
                className="bg-clip-text text-transparent"
                style={{
                  backgroundImage:
                    'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                }}
              >
                Находите лучшие
              </span>
              <br />
              <span style={{ color: 'rgb(var(--text-primary))' }}>вакансии в одном месте</span>
            </h1>

            <p
              className="text-xl mb-10 max-w-2xl mx-auto"
              style={{ color: 'rgb(var(--text-muted))' }}
            >
              Мониторинг, сравнение и анализ вакансий с разных платформ. Умный поиск,
              персонализированные рекомендации и актуальная аналитика рынка.
            </p>

            <div className="max-w-3xl mx-auto mb-12">
              <div className="relative">
                <Search
                  className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5"
                  style={{ color: 'rgb(var(--accent))' }}
                />
                <Input
                  type="search"
                  placeholder="Должность, навыки, компания или ключевые слова..."
                  className="pl-12 pr-32 h-14 rounded-2xl border-2 text-lg shadow-xl"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                  }}
                />
                <Button
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-6 rounded-xl text-white shadow-lg"
                  style={{
                    background:
                      'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                >
                  Найти вакансии
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-8">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <div
                    className="text-2xl font-bold bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                    }}
                  >
                    {stat.value}
                  </div>
                  <div className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4" style={{ color: 'rgb(var(--text-primary))' }}>
              Популярные категории
            </h2>
            <p className="max-w-2xl mx-auto" style={{ color: 'rgb(var(--text-muted))' }}>
              Ищите вакансии по интересующим направлениям с актуальной статистикой
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {categories.map((category) => (
              <Card
                key={category.title}
                className="backdrop-blur-sm hover:shadow-xl transition-all border"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border)/0.5)',
                }}
              >
                <CardHeader>
                  <div
                    className={`p-3 rounded-xl w-12 h-12 flex items-center justify-center mb-4 ${category.color}`}
                  >
                    <category.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl" style={{ color: 'rgb(var(--text-primary))' }}>
                    {category.title}
                  </CardTitle>
                  <CardDescription style={{ color: 'rgb(var(--text-muted))' }}>
                    {category.count} вакансий
                  </CardDescription>
                </CardHeader>
                <CardFooter>
                  <Button variant="ghost" style={{ color: 'rgb(var(--accent))' }}>
                    Смотреть все <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-6">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl font-bold mb-2" style={{ color: 'rgb(var(--text-primary))' }}>
                Последние вакансии
              </h2>
              <p style={{ color: 'rgb(var(--text-muted))' }}>
                Актуальные предложения от работодателей
              </p>
            </div>
            <Button
              className="text-white"
              style={{
                background:
                  'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
              }}
              asChild
            >
              <Link to="/vacancies">
                Показать все вакансии <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>

          <VacancyList vacancies={vacancies} loading={loadingVacancies} />
        </div>
      </section>

      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div
              className="p-8 rounded-3xl backdrop-blur-sm border shadow-2xl"
              style={{
                background:
                  'linear-gradient(135deg, rgb(var(--bg-header-muted)/0.5), rgb(var(--bg-header)/0.5))',
                borderColor: 'rgb(var(--border)/0.5)',
              }}
            >
              <h2 className="text-4xl font-bold mb-6">
                <span
                  className="bg-clip-text text-transparent"
                  style={{
                    backgroundImage:
                      'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                  }}
                >
                  Начните карьерный рост
                </span>
                <br />
                <span style={{ color: 'rgb(var(--text-primary))' }}>уже сегодня</span>
              </h2>

              <p
                className="mb-8 text-lg max-w-2xl mx-auto"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                Присоединяйтесь к тысячам профессионалов, которые уже нашли свою идеальную работу
                через JobHub
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  size="lg"
                  className="h-14 px-8 rounded-xl text-white text-lg font-semibold shadow-xl"
                  style={{
                    background:
                      'linear-gradient(to right, rgb(var(--button-from)), rgb(var(--button-to)))',
                  }}
                >
                  <Briefcase className="mr-2 h-5 w-5" />
                  Найти вакансии
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="h-14 px-8 rounded-xl hover:bg-gray-800/50"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    color: 'rgb(var(--text-primary))',
                  }}
                >
                  Создать профиль
                </Button>
              </div>

              <p className="text-sm mt-6" style={{ color: 'rgb(var(--text-muted))' }}>
                Регистрация займет меньше минуты. Без скрытых платежей.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
