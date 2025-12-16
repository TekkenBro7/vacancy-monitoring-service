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

export default function HomePage() {
  const categories = [
    {
      title: 'Backend разработка',
      count: '1.2K+',
      icon: Target,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Frontend разработка',
      count: '850+',
      icon: Zap,
      color: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Data Science',
      count: '420+',
      icon: TrendingUp,
      color: 'from-emerald-500 to-teal-500',
    },
    { title: 'DevOps', count: '380+', icon: Sparkles, color: 'from-amber-500 to-orange-500' },
  ];

  const featuredJobs = [
    {
      title: 'Senior React Developer',
      company: 'TechCorp Inc.',
      location: 'Москва',
      salary: '$4000 - $6000',
      skills: ['React', 'TypeScript', 'Redux', 'Node.js'],
      source: 'hh.ru',
      posted: '2 дня назад',
    },
    {
      title: 'Backend Engineer',
      company: 'FinTech Solutions',
      location: 'Санкт-Петербург',
      salary: '₽250 000 - ₽400 000',
      skills: ['Python', 'Django', 'PostgreSQL', 'Docker'],
      source: 'Habr Career',
      posted: '5 дней назад',
    },
    {
      title: 'Data Scientist',
      company: 'AI Research Lab',
      location: 'Удаленно',
      salary: '$5000 - $8000',
      skills: ['Python', 'ML', 'PyTorch', 'SQL'],
      source: 'LinkedIn',
      posted: 'Сегодня',
    },
  ];

  const stats = [
    { value: '12K+', label: 'Активных вакансий', icon: Briefcase },
    { value: '850+', label: 'Компаний-партнеров', icon: Building },
    { value: '50K+', label: 'Пользователей', icon: Users },
    { value: '99%', label: 'Удовлетворенности', icon: Sparkles },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-16">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl"></div>

        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-gray-800/50 backdrop-blur-sm border border-gray-700">
              <Sparkles className="h-4 w-4 text-amber-400" />
              <span className="text-sm text-amber-300">Платформа нового поколения</span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Находите лучшие
              </span>
              <br />
              <span className="text-white">вакансии в одном месте</span>
            </h1>

            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
              Мониторинг, сравнение и анализ вакансий с разных платформ. Умный поиск,
              персонализированные рекомендации и актуальная аналитика рынка.
            </p>

            {/* Search Bar */}
            <div className="max-w-3xl mx-auto mb-12">
              <div className="relative">
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-blue-400" />
                <Input
                  type="search"
                  placeholder="Должность, навыки, компания или ключевые слова..."
                  className="pl-12 pr-32 h-14 rounded-2xl border-2 border-gray-700 
                           bg-gray-800/50 backdrop-blur-sm text-white placeholder:text-gray-500
                           text-lg shadow-xl shadow-blue-500/10"
                />
                <Button
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-6 rounded-xl 
                                 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600
                                 text-white shadow-lg"
                >
                  Найти вакансии
                </Button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="flex flex-wrap justify-center gap-8">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <div className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-400">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Популярные категории</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Ищите вакансии по интересующим направлениям с актуальной статистикой
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {categories.map((category) => (
              <Card
                key={category.title}
                className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 
                         hover:bg-gray-800/50 hover:border-gray-600 hover:shadow-xl transition-all"
              >
                <CardHeader>
                  <div
                    className={`p-3 rounded-xl bg-gradient-to-br ${category.color} w-12 h-12 flex items-center justify-center mb-4`}
                  >
                    <category.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">{category.title}</CardTitle>
                  <CardDescription className="text-gray-400">
                    {category.count} вакансий
                  </CardDescription>
                </CardHeader>
                <CardFooter>
                  <Button variant="ghost" className="text-blue-400 hover:text-blue-300">
                    Смотреть все <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Jobs */}
      <section className="py-16 bg-gradient-to-b from-transparent to-gray-900/50">
        <div className="container mx-auto px-6">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl font-bold mb-2">Рекомендуемые вакансии</h2>
              <p className="text-gray-400">Самые интересные предложения за сегодня</p>
            </div>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
              Показать все вакансии
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {featuredJobs.map((job) => (
              <Card
                key={job.title}
                className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 
                         hover:bg-gray-800/50 hover:border-gray-600 hover:shadow-xl transition-all group"
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl group-hover:text-blue-300 transition-colors">
                        {job.title}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-2">
                        <Building className="h-4 w-4 text-blue-400" />
                        {job.company}
                      </CardDescription>
                    </div>
                    <Badge className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border-blue-500/30">
                      {job.source}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="h-4 w-4 text-gray-400" />
                      <span>{job.location}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign className="h-4 w-4 text-gray-400" />
                      <span className="font-semibold text-emerald-400">{job.salary}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-400">{job.posted}</span>
                    </div>

                    <div className="flex flex-wrap gap-2 pt-3">
                      {job.skills.map((skill) => (
                        <Badge
                          key={skill}
                          variant="outline"
                          className="text-xs border-gray-700 text-gray-300"
                        >
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>

                <CardFooter className="flex justify-between">
                  <Button variant="ghost" className="text-gray-400 hover:text-white">
                    Сохранить
                  </Button>
                  <Button className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                    Подробнее
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div
              className="p-8 rounded-3xl bg-gradient-to-br from-gray-800/50 to-gray-900/50 
                         backdrop-blur-sm border border-gray-700/50 shadow-2xl"
            >
              <h2 className="text-4xl font-bold mb-6">
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Начните карьерный рост
                </span>
                <br />
                <span className="text-white">уже сегодня</span>
              </h2>

              <p className="text-gray-300 mb-8 text-lg max-w-2xl mx-auto">
                Присоединяйтесь к тысячам профессионалов, которые уже нашли свою идеальную работу
                через JobHub
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  size="lg"
                  className="h-14 px-8 rounded-xl 
                           bg-gradient-to-r from-blue-600 to-purple-600 
                           text-white text-lg font-semibold shadow-xl"
                >
                  <Briefcase className="mr-2 h-5 w-5" />
                  Найти вакансии
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="h-14 px-8 rounded-xl 
                           border-gray-700 text-white hover:bg-gray-800/50"
                >
                  Создать профиль
                </Button>
              </div>

              <p className="text-sm text-gray-500 mt-6">
                Регистрация займет меньше минуты. Без скрытых платежей.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
