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
        color: 'icon',
      },
      {
        label: 'Сравнение предложений',
        href: '/comparisons',
        icon: Zap,
        color: 'icon',
      },
      {
        label: 'Аналитика рынка',
        href: '/analytics',
        icon: TrendingUp,
        color: 'icon',
      },
      {
        label: 'Персональные рекомендации',
        href: '/recommendations',
        icon: Rocket,
        color: 'icon',
      },
      {
        label: 'Мобильное приложение',
        href: '/mobile',
        icon: Rocket,
        color: 'icon',
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
      color: 'dark:hover:bg-gradient-to-br hover:from-gray-800 hover:to-gray-900',
    },
    {
      icon: Twitter,
      label: 'Twitter',
      href: 'https://twitter.com',
      color: 'dark:hover:bg-gradient-to-br hover:from-sky-500 hover:to-blue-500',
    },
    {
      icon: Linkedin,
      label: 'LinkedIn',
      href: 'https://linkedin.com',
      color: 'dark:hover:bg-gradient-to-br hover:from-blue-600 hover:to-blue-700',
    },
    {
      icon: Mail,
      label: 'Email',
      href: 'mailto:hello@jobhub.com',
      color: 'dark:hover:bg-gradient-to-br hover:from-rose-500 hover:to-pink-500',
    },
  ];

  return (
    <footer
      className="relative overflow-hidden transition-colors duration-300"
      style={{
        backgroundColor: 'rgb(var(--bg-header))',
        color: 'rgb(var(--text-primary))',
      }}
    >
      <div
        className="absolute top-0 left-0 right-0 h-1"
        style={{
          background: 'linear-gradient(to right, transparent, rgb(var(--accent))/50, transparent)',
        }}
      />

      <div
        className="absolute top-20 left-10 w-64 h-64 rounded-full blur-3xl"
        style={{
          background: 'radial-gradient(circle, rgb(var(--accent))/10 0%, transparent 70%)',
        }}
      />
      <div
        className="absolute bottom-20 right-10 w-56 h-56 rounded-full blur-3xl"
        style={{
          background: 'radial-gradient(circle, rgb(var(--accent))/5 0%, transparent 70%)',
        }}
      />

      <div className="absolute inset-0 opacity-[0.03] dark:opacity-[0.02] pointer-events-none">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgb(var(--text-primary)) 1px, transparent 1px),
              linear-gradient(to bottom, rgb(var(--text-primary)) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div
          className="py-10"
          style={{
            borderBottom: '1px solid rgb(var(--border)/0.5)',
          }}
        >
          <div className="flex flex-col lg:flex-row items-start justify-between gap-10">
            <div className="max-w-lg">
              <div className="mb-5">
                <Logo size="default" showText={true} />
              </div>

              <p
                className="mb-6 leading-relaxed"
                style={{
                  color: 'rgb(var(--text-muted))',
                }}
              >
                Современная платформа для поиска работы и развития карьеры. Мы помогаем
                профессионалам находить идеальные возможности для роста.
              </p>

              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <div
                    className="p-1.5 rounded-md border"
                    style={{
                      background:
                        'linear-gradient(135deg, rgb(var(--accent))/20, rgb(var(--accent))/40)',
                      borderColor: 'rgb(var(--accent)/0.3)',
                    }}
                  >
                    <TrendingUp
                      className="h-4 w-4"
                      style={{
                        color: 'rgb(var(--accent))',
                      }}
                    />
                  </div>
                  <span
                    className="font-semibold bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                    }}
                  >
                    Лучшие вакансии первыми
                  </span>
                </div>

                <div className="flex gap-2">
                  <input
                    type="email"
                    placeholder="Ваш email для уведомлений"
                    className="flex-1 px-4 py-2.5 rounded-lg text-sm h-11 backdrop-blur-sm focus:outline-none"
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                      border: '1px solid rgb(var(--border))',
                      color: 'rgb(var(--text-primary))',
                    }}
                  />
                  <Button
                    className="
                      px-6 py-2.5 h-11 text-sm font-medium rounded-lg
                      transition-all duration-300
                      shadow-md
                      hover:shadow-xl
                      hover:scale-[1.02]
                      active:scale-[0.98]
                      focus-visible:ring-2 focus-visible:ring-offset-2
                    "
                    style={{
                      background: `
                        linear-gradient(
                          135deg,
                          rgb(var(--button-from)),
                          rgb(var(--button-to))
                        )
                      `,
                      color: 'white',
                      boxShadow: `
                        0 8px 24px rgb(var(--accent) / 0.25)
                      `,
                    }}
                  >
                    Подписаться
                  </Button>
                </div>
                <p
                  className="text-xs mt-2"
                  style={{
                    color: 'rgb(var(--text-muted))',
                  }}
                >
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
                    className="
                      p-2.5 rounded-lg backdrop-blur-sm border
                      transition-all duration-300
                      hover:scale-110
                      hover:shadow-xl
                      hover:border-[rgb(var(--accent)/0.4)]
                    "
                    style={{
                      backgroundColor: 'rgb(var(--bg-header-muted)/0.5)',
                      borderColor: 'rgb(var(--border))',
                    }}
                    aria-label={social.label}
                  >
                    <social.icon
                      className="h-5 w-5 transition-colors"
                      style={{
                        color: 'rgb(var(--text-muted))',
                      }}
                    />
                  </a>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              {Object.entries(footerLinks).map(([category, links]) => (
                <div key={category}>
                  <h4
                    className="font-bold mb-4 pb-2 border-b bg-clip-text text-transparent"
                    style={{
                      backgroundImage:
                        'linear-gradient(to right, rgb(var(--text-primary)), rgb(var(--text-muted)))',
                      borderColor: 'rgb(var(--border)/0.5)',
                    }}
                  >
                    {category === 'product' && 'Продукт'}
                    {category === 'company' && 'Компания'}
                  </h4>
                  <ul className="space-y-3">
                    {links.map((link) => (
                      <li key={link.label}>
                        <Link
                          to={link.href}
                          className="
                            group flex items-center gap-3 p-2.5 rounded-lg
                            transition-all duration-300
                            border
                            hover:translate-x-1
                            hover:shadow-md
                          "
                          style={{
                            borderColor: 'rgb(var(--border)/0.5)',
                            backgroundColor: 'transparent',
                          }}
                        >
                          <div
                            className="
                              p-2 rounded-md shadow-md
                              transition-all duration-300
                              group-hover:scale-110
                              group-hover:shadow-lg
                            "
                            style={{
                              background: `
                                linear-gradient(
                                  135deg,
                                  rgb(var(--icon-gradient-from)),
                                  rgb(var(--icon-gradient-to))
                                )
                              `,
                            }}
                          >
                            <link.icon className="h-4 w-4 text-white" />
                          </div>
                          <div className="flex-1">
                            <span
                              className="text-sm transition-colors"
                              style={{
                                color: 'rgb(var(--text-primary))',
                              }}
                            >
                              {link.label}
                            </span>
                          </div>
                          <ExternalLink
                            className="h-3.5 w-3.5 transition-colors"
                            style={{
                              color: 'rgb(var(--text-muted))',
                            }}
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
                className="group p-4 rounded-xl backdrop-blur-sm border transition-all duration-300 cursor-pointer"
                style={{
                  backgroundColor: 'rgb(var(--bg-header-muted)/0.3)',
                  borderColor: 'rgb(var(--border)/0.5)',
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`p-2 rounded-lg ${stat.color} shadow-md group-hover:scale-105 transition-transform`}
                  >
                    <stat.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <div className="text-xl font-bold flex items-baseline">
                      {stat.value}
                      {stat.suffix && (
                        <span className="ml-0.5" style={{ color: 'rgb(var(--accent))' }}>
                          {stat.suffix}
                        </span>
                      )}
                    </div>
                    <div
                      className="text-xs transition-colors"
                      style={{
                        color: 'rgb(var(--text-muted))',
                      }}
                    >
                      {stat.label}
                    </div>
                  </div>
                </div>
                <div
                  className="h-1 w-full rounded-full overflow-hidden"
                  style={{
                    backgroundColor: 'rgb(var(--border)/0.3)',
                  }}
                >
                  <div
                    className={`h-full rounded-full transition-all duration-700 group-hover:w-full w-3/4 ${stat.color.split(' ')[0]}`}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="py-5">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <span
                  className="font-bold bg-clip-text text-transparent"
                  style={{
                    backgroundImage:
                      'linear-gradient(to right, rgb(var(--accent)), rgb(var(--accent)/0.8))',
                  }}
                >
                  © {currentYear} JobHub
                </span>
                <div
                  className="h-3 w-px"
                  style={{
                    background:
                      'linear-gradient(to bottom, transparent, rgb(var(--border)), transparent)',
                  }}
                />
                <span
                  className="text-sm"
                  style={{
                    color: 'rgb(var(--text-muted))',
                  }}
                >
                  Все права защищены
                </span>
              </div>
              <p
                className="text-xs mt-2 max-w-2xl"
                style={{
                  color: 'rgb(var(--text-muted))',
                }}
              >
                JobHub предоставляет услуги по поиску вакансий и анализу рынка труда. Данные
                агрегируются из открытых источников.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div
                className="px-3 py-1.5 rounded-full border"
                style={{
                  background:
                    'linear-gradient(to right, rgb(var(--bg-header-muted)), rgb(var(--bg-header)))',
                  borderColor: 'rgb(var(--border))',
                }}
              >
                <div className="flex items-center gap-1.5">
                  <CheckCircle
                    className="h-3.5 w-3.5"
                    style={{
                      color: 'rgb(var(--accent))',
                    }}
                  />
                  <span
                    className="text-xs font-medium"
                    style={{
                      color: 'rgb(var(--accent))',
                    }}
                  >
                    Проверено
                  </span>
                </div>
              </div>

              <div
                className="text-xs px-2.5 py-1 rounded-full border"
                style={{
                  background:
                    'linear-gradient(to right, rgb(var(--accent))/10, rgb(var(--accent))/5)',
                  borderColor: 'rgb(var(--accent)/0.2)',
                }}
              >
                <span
                  className="font-medium"
                  style={{
                    color: 'rgb(var(--accent))',
                  }}
                >
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
