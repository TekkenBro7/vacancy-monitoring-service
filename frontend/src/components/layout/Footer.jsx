import { Link } from 'react-router-dom';
import {
  Search,
  GitCompare,
  Bookmark,
  User,
  Building,
  Zap,
  Mail,
  Github,
  Linkedin,
  Heart,
  Star,
  Shield,
  Globe,
  ArrowUpRight,
  Sparkles,
  Database,
  Clock,
  Award,
} from 'lucide-react';
import Logo from '@/components/ui_my/Logo';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const navigation = [
    { label: 'Поиск вакансий', href: '/vacancies', icon: Search },
    { label: 'Сравнения', href: '/comparisons', icon: GitCompare },
    { label: 'Закладки', href: '/bookmarks', icon: Bookmark },
    { label: 'Профиль', href: '/profile', icon: User },
  ];

  const sources = [
    { name: 'HeadHunter', color: 'from-red-500 to-rose-600' },
    { name: 'SuperJob', color: 'from-blue-500 to-indigo-600' },
    { name: 'Praca.by', color: 'from-emerald-500 to-green-600' },
    { name: 'EPAM', color: 'from-cyan-500 to-blue-600' },
    { name: 'Wargaming', color: 'from-orange-500 to-amber-600' },
    { name: 'Telegram', color: 'from-sky-400 to-blue-500' },
  ];

  const stats = [
    { value: '10K+', label: 'Вакансий', icon: Building, color: 'from-blue-500 to-cyan-500' },
    { value: '500+', label: 'Компаний', icon: Globe, color: 'from-purple-500 to-pink-500' },
    { value: '6', label: 'Источников', icon: Database, color: 'from-emerald-500 to-teal-500' },
    { value: '24/7', label: 'Мониторинг', icon: Clock, color: 'from-amber-500 to-orange-500' },
  ];

  const socialLinks = [
    { icon: Github, href: 'https://github.com', label: 'GitHub' },
    { icon: Linkedin, href: 'https://linkedin.com', label: 'LinkedIn' },
    { icon: Mail, href: 'mailto:support@jobhub.by', label: 'Email' },
  ];

  return (
    <footer
      className="relative overflow-hidden"
      style={{ backgroundColor: 'rgb(var(--bg-header))' }}
    >
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: 'linear-gradient(to right, transparent, rgb(var(--accent)), transparent)',
        }}
      />

      <div
        className="absolute -top-20 -left-20 w-96 h-96 rounded-full blur-3xl opacity-20"
        style={{ background: 'radial-gradient(circle, rgb(var(--accent)) 0%, transparent 70%)' }}
      />
      <div
        className="absolute -bottom-32 -right-32 w-[500px] h-[500px] rounded-full blur-3xl opacity-10"
        style={{ background: 'radial-gradient(circle, rgb(168, 85, 247) 0%, transparent 70%)' }}
      />

      <div className="absolute inset-0 opacity-[0.02] pointer-events-none">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `
              linear-gradient(rgb(var(--text-primary)) 1px, transparent 1px),
              linear-gradient(90deg, rgb(var(--text-primary)) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      <div className="container mx-auto px-6 py-16 relative z-10">
        <div
          className="grid grid-cols-1 lg:grid-cols-12 gap-12 pb-12"
          style={{ borderBottom: '1px solid rgb(var(--border))' }}
        >
          <div className="lg:col-span-5 space-y-6">
            <Logo size="default" showText />

            <p className="text-base leading-relaxed" style={{ color: 'rgb(var(--text-muted))' }}>
              Умная платформа для поиска работы в IT. Агрегируем вакансии из лучших источников,
              анализируем с помощью AI и помогаем найти идеальную работу.
            </p>

            <div className="flex flex-wrap gap-3">
              {[
                { icon: Sparkles, text: 'AI-анализ' },
                { icon: Zap, text: 'Мгновенный поиск' },
                { icon: Shield, text: 'Актуальные данные' },
              ].map((feature) => (
                <div
                  key={feature.text}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full border"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                    borderColor: 'rgb(var(--border))',
                  }}
                >
                  <feature.icon className="h-3.5 w-3.5" style={{ color: 'rgb(var(--accent))' }} />
                  <span
                    className="text-xs font-medium"
                    style={{ color: 'rgb(var(--text-primary))' }}
                  >
                    {feature.text}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-3 pt-2">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group p-3 rounded-xl border transition-all duration-300 hover:scale-110 hover:shadow-lg"
                  style={{
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                    borderColor: 'rgb(var(--border))',
                  }}
                  aria-label={social.label}
                >
                  <social.icon
                    className="h-5 w-5 transition-colors group-hover:scale-110"
                    style={{ color: 'rgb(var(--text-muted))' }}
                  />
                </a>
              ))}
            </div>
          </div>

          <div className="lg:col-span-3">
            <h4
              className="text-sm font-bold uppercase tracking-widest mb-6"
              style={{ color: 'rgb(var(--accent))' }}
            >
              Навигация
            </h4>
            <ul className="space-y-2">
              {navigation.map((link) => (
                <li key={link.label}>
                  <Link
                    to={link.href}
                    className="group flex items-center gap-3 p-3 rounded-xl border transition-all duration-300 hover:translate-x-1 hover:shadow-md"
                    style={{
                      borderColor: 'rgb(var(--border))',
                      backgroundColor: 'transparent',
                    }}
                  >
                    <div
                      className="p-2 rounded-lg transition-transform group-hover:scale-110"
                      style={{
                        background:
                          'linear-gradient(135deg, rgb(var(--icon-gradient-from)), rgb(var(--icon-gradient-to)))',
                      }}
                    >
                      <link.icon className="h-4 w-4 text-white" />
                    </div>
                    <span
                      className="flex-1 text-sm font-medium"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {link.label}
                    </span>
                    <ArrowUpRight
                      className="h-4 w-4 opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0"
                      style={{ color: 'rgb(var(--accent))' }}
                    />
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div className="lg:col-span-4">
            <h4
              className="text-sm font-bold uppercase tracking-widest mb-6"
              style={{ color: 'rgb(var(--accent))' }}
            >
              Источники вакансий
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {sources.map((source) => (
                <div
                  key={source.name}
                  className="group relative overflow-hidden p-3 rounded-xl border transition-all duration-300 hover:scale-[1.02] hover:shadow-md cursor-default"
                  style={{
                    borderColor: 'rgb(var(--border))',
                    backgroundColor: 'rgb(var(--bg-header-muted))',
                  }}
                >
                  <div
                    className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity bg-gradient-to-r ${source.color}`}
                  />
                  <div className="relative flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${source.color}`} />
                    <span
                      className="text-sm font-medium"
                      style={{ color: 'rgb(var(--text-primary))' }}
                    >
                      {source.name}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div
              className="mt-4 p-4 rounded-xl border"
              style={{
                background:
                  'linear-gradient(135deg, rgb(var(--accent) / 0.05), rgb(var(--accent) / 0.1))',
                borderColor: 'rgb(var(--accent) / 0.2)',
              }}
            >
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4" style={{ color: 'rgb(var(--accent))' }} />
                <span
                  className="text-sm font-semibold"
                  style={{ color: 'rgb(var(--text-primary))' }}
                >
                  Обновление каждый день
                </span>
              </div>
              <p className="text-xs" style={{ color: 'rgb(var(--text-muted))' }}>
                Автоматический парсинг и AI-обработка новых вакансий
              </p>
            </div>
          </div>
        </div>

        <div className="py-4" style={{ borderBottom: '1px solid rgb(var(--border))' }}>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="group relative overflow-hidden p-4 rounded-2xl border transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted))',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <div
                  className={`absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity bg-gradient-to-br ${stat.color}`}
                />
                <div className="relative">
                  <div className="flex items-center gap-3 mb-1">
                    <div className={`p-2.5 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}>
                      <stat.icon className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <div
                        className="text-2xl font-black"
                        style={{ color: 'rgb(var(--text-primary))' }}
                      >
                        {stat.value}
                      </div>
                      <div
                        className="text-xs font-medium"
                        style={{ color: 'rgb(var(--text-muted))' }}
                      >
                        {stat.label}
                      </div>
                    </div>
                  </div>
                  <div
                    className="h-1 w-full rounded-full overflow-hidden"
                    style={{ backgroundColor: 'rgb(var(--border))' }}
                  >
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${stat.color} transition-all duration-700 w-0 group-hover:w-full`}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-8">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <span
                className="text-lg font-black"
                style={{
                  background: 'linear-gradient(135deg, rgb(var(--accent)), rgb(168, 85, 247))',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                © {currentYear} JobHub
              </span>
              <div
                className="hidden sm:block h-5 w-px"
                style={{
                  background:
                    'linear-gradient(to bottom, transparent, rgb(var(--border)), transparent)',
                }}
              />
              <p
                className="text-xs text-center sm:text-left max-w-md"
                style={{ color: 'rgb(var(--text-muted))' }}
              >
                Сервис по поиску вакансий и анализу рынка труда. Данные агрегируются из открытых
                источников.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border transition-all hover:scale-105"
                style={{
                  background:
                    'linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(168, 85, 247, 0.05))',
                  borderColor: 'rgba(168, 85, 247, 0.3)',
                }}
              >
                <Award className="h-3.5 w-3.5" style={{ color: 'rgb(168, 85, 247)' }} />
                <span className="text-xs font-semibold" style={{ color: 'rgb(168, 85, 247)' }}>
                  Дипломный проект
                </span>
              </div>

              <div
                className="flex items-center gap-2 px-4 py-2 rounded-full border"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted) / 0.5)',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                  Сделано с
                </span>
                <Heart className="h-4 w-4 text-red-500 fill-red-500 animate-pulse" />
                <span className="text-sm" style={{ color: 'rgb(var(--text-muted))' }}>
                  в Беларуси
                </span>
                <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
