import { Link } from 'react-router-dom';
import {
  TrendingUp,
  Users,
  Building,
  Shield,
  Mail,
  Github,
  Twitter,
  Linkedin,
  ExternalLink,
  Zap,
  Star,
  Target,
  Rocket,
  Heart,
  Award,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import Logo from '@/components/ui_my/Logo';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      {
        label: 'Поиск вакансий',
        href: '/vacancies',
        icon: Target,
        color: 'from-blue-500 to-cyan-500',
      },
      {
        label: 'Сравнение предложений',
        href: '/comparisons',
        icon: Zap,
        color: 'from-purple-500 to-pink-500',
      },
      {
        label: 'Аналитика рынка',
        href: '/analytics',
        icon: TrendingUp,
        color: 'from-emerald-500 to-teal-500',
      },
      {
        label: 'Персональные рекомендации',
        href: '/recommendations',
        icon: Rocket,
        color: 'from-amber-500 to-orange-500',
      },
      {
        label: 'Мобильное приложение',
        href: '/mobile',
        icon: Rocket,
        color: 'from-rose-500 to-fuchsia-500',
      },
    ],
    company: [
      { label: 'О проекте', href: '/about', icon: Building, color: 'from-indigo-500 to-blue-500' },
      { label: 'Команда', href: '/team', icon: Users, color: 'from-sky-500 to-cyan-500' },
      { label: 'Карьера', href: '/careers', icon: Heart, color: 'from-green-500 to-emerald-500' },
      { label: 'Партнеры', href: '/partners', icon: Heart, color: 'from-pink-500 to-rose-500' },
      { label: 'Контакты', href: '/contact', icon: Mail, color: 'from-violet-500 to-purple-500' },
    ],
  };

  const stats = [
    {
      value: '12,589+',
      label: 'активных вакансий',
      icon: Building,
      color: 'bg-gradient-to-r from-blue-500 to-cyan-500',
    },
    {
      value: '850+',
      label: 'компаний-партнеров',
      icon: Building,
      color: 'bg-gradient-to-r from-purple-500 to-pink-500',
    },
    {
      value: '4.9',
      label: 'рейтинг пользователей',
      icon: Star,
      color: 'bg-gradient-to-r from-amber-500 to-orange-500',
      suffix: '★',
    },
    {
      value: '24/7',
      label: 'поддержка',
      icon: Shield,
      color: 'bg-gradient-to-r from-emerald-500 to-teal-500',
    },
  ];

  const socialLinks = [
    {
      icon: Github,
      label: 'GitHub',
      href: 'https://github.com',
      color: 'hover:bg-gradient-to-br hover:from-gray-800 hover:to-gray-900',
    },
    {
      icon: Twitter,
      label: 'Twitter',
      href: 'https://twitter.com',
      color: 'hover:bg-gradient-to-br hover:from-sky-500 hover:to-blue-500',
    },
    {
      icon: Linkedin,
      label: 'LinkedIn',
      href: 'https://linkedin.com',
      color: 'hover:bg-gradient-to-br hover:from-blue-600 hover:to-blue-700',
    },
    {
      icon: Mail,
      label: 'Email',
      href: 'mailto:hello@jobhub.com',
      color: 'hover:bg-gradient-to-br hover:from-rose-500 hover:to-pink-500',
    },
  ];

  return (
    <footer className="relative bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
      <div className="absolute top-20 left-10 w-64 h-64 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 right-10 w-56 h-56 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl"></div>

      <div className="absolute inset-0 opacity-5">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `linear-gradient(to right, white 1px, transparent 1px),
                           linear-gradient(to bottom, white 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        ></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="py-10 border-b border-gray-700/50">
          <div className="flex flex-col lg:flex-row items-start justify-between gap-10">
            <div className="max-w-lg">
              <div className="mb-5">
                <Logo size="default" showText={true} />
              </div>

              <p className="text-gray-300 mb-6 leading-relaxed">
                Современная платформа для поиска работы и развития карьеры. Мы помогаем
                профессионалам находить идеальные возможности для роста.
              </p>

              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <div className="p-1.5 rounded-md bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
                    <TrendingUp className="h-4 w-4 text-blue-300" />
                  </div>
                  <span className="font-semibold bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">
                    Лучшие вакансии первыми
                  </span>
                </div>
                <div className="flex gap-2">
                  <input
                    type="email"
                    placeholder="Ваш email для уведомлений"
                    className="flex-1 px-4 py-2.5 rounded-lg border border-gray-700 
                             bg-gray-800/50 backdrop-blur-sm focus:outline-none 
                             focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 
                             placeholder:text-gray-500 text-white text-sm h-11"
                  />
                  <Button
                    className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 
                                   hover:from-blue-600 hover:to-purple-600 text-white font-medium
                                   shadow-md hover:shadow-lg transition-all duration-300 h-11 text-sm"
                  >
                    Подписаться
                  </Button>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  Только полезные уведомления. Без спама.
                </p>
              </div>

              <div className="flex items-center gap-3">
                {socialLinks.map((social) => (
                  <a
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`p-2.5 rounded-lg bg-gray-800/50 backdrop-blur-sm border border-gray-700 
                             hover:scale-105 hover:shadow-lg transition-all duration-300 ${social.color}`}
                    aria-label={social.label}
                  >
                    <social.icon className="h-5 w-5 text-gray-300" />
                  </a>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              {Object.entries(footerLinks).map(([category, links]) => (
                <div key={category}>
                  <h4
                    className="font-bold mb-4 pb-2 border-b border-gray-700/50 
                               bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent"
                  >
                    {category === 'product' && 'Продукт'}
                    {category === 'company' && 'Компания'}
                  </h4>
                  <ul className="space-y-3">
                    {links.map((link) => (
                      <li key={link.label}>
                        <Link
                          to={link.href}
                          className="group flex items-center gap-3 p-2.5 rounded-lg 
                                   hover:bg-gray-800/50 hover:backdrop-blur-sm 
                                   border border-transparent hover:border-gray-700
                                   transition-all duration-300"
                        >
                          <div
                            className={`p-2 rounded-md bg-gradient-to-br ${link.color} 
                                       shadow-md group-hover:scale-105 transition-transform`}
                          >
                            <link.icon className="h-4 w-4 text-white" />
                          </div>
                          <div className="flex-1">
                            <span
                              className="text-gray-200 group-hover:text-white 
                                           text-sm transition-colors"
                            >
                              {link.label}
                            </span>
                          </div>
                          <ExternalLink
                            className="h-3.5 w-3.5 text-gray-500 group-hover:text-blue-400 
                                                 transition-colors"
                          />
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="py-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="group p-4 rounded-xl bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 
                         hover:bg-gray-800/50 hover:border-gray-600 hover:shadow-lg 
                         transition-all duration-300 cursor-pointer"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`p-2 rounded-lg ${stat.color} shadow-md group-hover:scale-105 transition-transform`}
                  >
                    <stat.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <div className="text-xl font-bold text-white flex items-baseline">
                      {stat.value}
                      {stat.suffix && <span className="text-amber-300 ml-0.5">{stat.suffix}</span>}
                    </div>
                    <div className="text-xs text-gray-400 group-hover:text-gray-300 transition-colors">
                      {stat.label}
                    </div>
                  </div>
                </div>
                <div className="h-1 w-full bg-gradient-to-r from-gray-700 to-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${stat.color.split(' ')[0]} rounded-full transition-all duration-700 group-hover:w-full w-3/4`}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="py-5 border-gray-700/50">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
            <div className="text-gray-400">
              <div className="flex items-center gap-3">
                <span className="font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  © {currentYear} JobHub
                </span>
                <div className="h-3 w-px bg-gradient-to-b from-transparent via-gray-600 to-transparent"></div>
                <span className="text-sm">Все права защищены</span>
              </div>
              <p className="text-xs text-gray-500 mt-2 max-w-2xl">
                JobHub предоставляет услуги по поиску вакансий и анализу рынка труда. Данные
                агрегируются из открытых источников.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div
                className="px-3 py-1.5 rounded-full bg-gradient-to-r from-gray-800 to-gray-900 
                            border border-gray-700"
              >
                <div className="flex items-center gap-1.5">
                  <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-xs text-emerald-300 font-medium">Проверено</span>
                </div>
              </div>

              <div
                className="text-xs px-2.5 py-1 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 
                            border border-blue-500/20"
              >
                <span className="font-medium text-blue-300">
                  <Award className="h-3 w-3 inline mr-1" />
                  Премиум качество
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
