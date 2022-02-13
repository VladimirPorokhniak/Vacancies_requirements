# from nltk import ne_chunk, sent_tokenize, pos_tag, word_tokenize
sentence = '— 3+ years of intensive experience in infrastructure architecture and security management, experience as a consultant, security engineer or similar responsibilities;— Mange following solutions: servers running Windows Server, Linux, VMware, Hyper-V, SQL, Active Directory, NGFW, NAC, EDR, SIEM, IPS, WAF;— Experience with site vulnerability assessments utilizing NIST or ISO 27k framework;— Experience with the implementation of continuous monitoring of network and server resources, to include the configuration and tuning of monitoring applications;— Solid network security and Data Center security architectural design and hands-on engineering experience— We appreciate if candidates will have CISSP and/or CCSK certifications;— Candidate must be able to effectively communicate in English (written & verbal).'
sentence_ua = '''Мы в поиске IT Security Engineer для улучшения и развития наших систем безопасности. 
В Welltech мы делаем мобильные приложения в категории Health & Fitness, которые входят в мировой TOP3 по доходам от продаж. 

Расти вместе с нами: 
4+ года на мировом рынке 
400+ специалистов (за прошлый год мы выросли в х2 раза 😱) 
10+ приложений 
150М+ скачиваний
Наши приложения продаются по всему миру с фокусом на США, Латинскую Америку, Европу, активно выходим на Азиатские рынки 

Ключевые задачи: 
Внедрение контролей безопасности внутренних ресурсов компании (сеть, ПК сотрудников, облачные сервисы) 
Анализ и внедрение архитектуры безопасности сервисов в AWS 
Внедрение и улучшение контролей безопасности в AWS (SecurityHub, CloudWatch) 
Поиск уязвимостей внешнего периметра и рекомендации по улучшению защищенности
Внедрение процессов Application Sy Консультация сотрудников по вопросам технической безопасности 

Навыки и опыт: 
Опыт работы в IT / Information Security не менее 3х лет
Опыт внедрения секьюрити контролей
Знание ОС Windows, Linux, Mac OS на уровне администратора
Знание протоколов DNS / DHCP / SMTP / SNMP / TCP / IP 
Опыт работы с секьюрити утилитами (Vulnerability Scanner, DLP, Malware Protection, MDM etc.) 
Знание облачных технологий (AWS)
Знание и понимание современных трендов в IT Security

Будет плюсом:
Опыт работы с лог системами и системами мониторинга
Опыт внедрение процессов Application Security 
Наличие международных сертификатов в области ИБ (AWS, ISACA, (ISC)² и т.п.)

В нашей команде мы ценим:
Коммуникабельность. Апдейт команды, регулярная коммуникация с рабочей группой по текущим проектам в письменном (в чатах), и устном форматах (стендапы и другие митинги). Открытость к общению. Умение формулировать задачу четко и лаконично. 
Ориентация на результат. Готовность выстраивать свои задачи в соответствии с глобальными целями команды и компании, продвигать необходимые изменения.
Ответственность. Самостоятельность, готовность брать на себя обязательства и соблюдать договоренности.
Проактивность. Способность устанавливать цели и работать над их достижением. Создание возможностей, не дожидаясь их появления. 

Мы предлагаем:
Комфортные я Гибридный формат на время пандемии. Можно самостоятельно выбирать место, где удобнее работать. Мы запустили корпоративный трансфер, который привезет вас из дома в спейс и обратно
Гибкий старт: день можно начинать с 8:00 до 11:00, ориентируясь на личные предпочтения и командные встречи
Обеды за счет компании: ты можешь формировать меню, основываясь на личных предпочтениях
20 дней оплачиваемого отдыха 

Заботу о здоровье 
Возможность бесплатно пользоваться нашими мобильными приложениями (йога, бег, фитнес и др.)
Медицинская страховка с первого месяца сотрудничества 
Ежедневные занятия йогой 
Индивидуальный бюджет для занятий спортом/покупки инвентаря 
Оплачиваемые больничные 

Профессиональное развитие 
Индивидуальный бюджет на внешние тренинги и курсы, митапы и семинары 
Корпоративная онлайн и оффлайн библиотека 
Индивидуальные онлайн уроки по изучению английского языкаа 
Шеринг опытом и знаниями между командами
Welcom

'''
# for sent in sent_tokenize(sentence):
#     words = word_tokenize(sent)
#     # print(words)

from googletrans import Translator

translator = Translator()

translation = translator.translate(sentence, src='en', dest='ru')
print(f"({translation.src}) ({translation.dest})")
print(translation.text)
translation = translator.translate(translation.text)
print(f"({translation.src}) ({translation.dest})")
print(translation.text)