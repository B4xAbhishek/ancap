export type ProjectNewsItem = {
  id: string;
  date: string;
  title: string;
  summary: string;
  href: string;
};

/** Последние новости проекта ANCAP (RU). */
export const PROJECT_NEWS_RU: ProjectNewsItem[] = [
  {
    id: "ancap-dating-mesh",
    date: "2026-10-02",
    title: "ANCAP Dating: proximity mesh (18+)",
    summary:
      "Новый контур знакомств в кошельке: BLE-пиры видны как «ANCAP Dating», карта точек доступа на /dating, offline mesh по мотивам bitchat. Только 18+. Юр.: /legal/dating.",
    href: "/dating",
  },
  {
    id: "wacp-v3-liquidity-playbook",
    date: "2026-10-02",
    title: "wACP: V3 liquidity playbook на PancakeSwap",
    summary:
      "Новый операционный контур Stage A/B/C: V2 остаётся тонким reference-рынком, новая scarce-ликвидность идёт в concentrated V3 wACP/USDT. Reserve invariant, mint envelope, калькулятор тиков и OTC-порог ~25% глубины. Infinity — только после устойчивого объёма. Docs: /docs/wacp/pancakeswap.",
    href: "/docs/wacp/pancakeswap",
  },
  {
    id: "oracle-acp-secondary-node",
    date: "2026-10-02",
    title: "Вторая нода ACP на Oracle Cloud",
    summary:
      "Независимый full node ACP в eu-zurich-1 на Always Free: публичный JSON-RPC peer рядом с acp1.ancap.cloud, sync на regenesis v3 / hard cap 210M. План и peer URL: /docs путь ORACLE_CLOUD_ACP_NODE_PLAN на GitHub. Hostname acp2.ancap.cloud — следующий шаг (TLS).",
    href: "https://github.com/dragoncattrx-hub/ancap/blob/master/docs/ORACLE_CLOUD_ACP_NODE_PLAN.md",
  },
  {
    id: "counsel-worldwide-legal-services",
    date: "2026-09-14",
    title: "Юридические услуги в любой точке мира",
    summary:
      "Новый /counsel — desk юридических брифов ACP с подбором лицензированного юриста по миру: юрисдикция от 3 900 ACP, договоры, компании, крипто, иммиграция, IP, споры и налоговый match. ANCAP не юрфирма и не создаёт отношений адвокат–клиент. Юр. текст: /legal/counsel.",
    href: "/counsel",
  },
  {
    id: "aeterna-dna-pheromone-perfume",
    date: "2026-09-13",
    title: "AETERNA: духи с феромонами под ДНК — 1 флакон",
    summary:
      "На /aeterna — продажа ДНК-подобранных духов с феромонами строго за 1 флакон (8 900 ACP). Опциональный хеш DNA-vault задаёт грамотность арома-профиля; розлив у лицензированного косметического партнёра. Это не лекарство, не афродизиак-клейм, не CE/FDA-феромонная медицина и не загрузка генома на ANCAP. Юр. текст: /legal/dna-pheromone-perfume.",
    href: "/aeterna#dna-pheromone-perfume",
  },
  {
    id: "stardust-weather-control",
    date: "2026-09-13",
    title: "Stardust: платный desk контроля погоды — аукцион ACP",
    summary:
      "На /stardust ценовая политика weather-control переведена на аукцион TECH: лоты extreme weather, disaster early-warning, глобальный контроль и ретейнер с открывающими полами 18k–58k ACP. Ставки через AuctionEscrow на /tech. Панель переключателей — UI грамотности, не живая консоль. Страховка: weather_control. Юр.: /legal/stardust.",
    href: "/stardust",
  },
  {
    id: "aeterna-installation-project",
    date: "2026-09-13",
    title: "AETERNA: Проект Установки — питание и неонатальная барокамера",
    summary:
      "На /aeterna — партнёрский бриф «Проект Установки» за 72 000 ACP: грамотность линии высокобелкового натурально-синтетического молока и неонатальной барокамеры. Это не смесь от ANCAP, не CE/FDA-устройство, не домашняя HBO и не гарантия клинического исхода. Страховка: neonatal_install. Юр. текст: /legal/installation-project.",
    href: "/aeterna#installation-project",
  },
  {
    id: "aeterna-pulmopure-subscription",
    date: "2026-09-13",
    title: "AETERNA: подписка PulmoPure — грамотность ухода за лёгкими",
    summary:
      "На /aeterna — подписка для лицензированной пульмонологической / респираторной клиники: газо-вибрация, смесь газов и лавандовый атомайзер как грамотность протокола. 14 000 ACP / месяц, 38 000 / квартал, 128 000 / год. Это не изделие CE/FDA, не озонотерапия, не компаундинг медгазов и не гарантия «чистых лёгких». Юр. текст: /legal/pulmopure.",
    href: "/aeterna#pulmopure",
  },
  {
    id: "aeterna-substance-coding",
    date: "2026-09-15",
    title: "AETERNA: кодирование от веществ — партнёрский бриф",
    summary:
      "На /aeterna — бриф для лицензированного нарколога / клинического гипноза (свет, вещества клиники, гипноз) за 48 000 ACP против зависимости от веществ, не необходимых для жизни. Это не сеанс кодирования от ANCAP, не гарантия трезвости и не продажа контролируемых веществ. Юр. текст: /legal/substance-coding.",
    href: "/aeterna#substance-coding",
  },
  {
    id: "entertainment-tesla-coil-party",
    date: "2026-09-15",
    title: "Развлечения: пати с катушкой Теслы и hospitality Jack Daniel's",
    summary:
      "На /entertainment — desk brief 8 900 ACP для лицензированной площадки: шоу катушки Теслы, complimentary whiskey literacy и только разрешённые взрослые вещества. ANCAP не аффилирован с Jack Daniel's, не держит алкогольную лицензию и не продаёт контролируемые вещества. Юр. текст: /legal/tesla-coil-party.",
    href: "/entertainment#tesla-coil-party",
  },
  {
    id: "aeterna-down-syndrome-support",
    date: "2026-09-14",
    title: "AETERNA: поддержка при синдроме Дауна — партнёрский бриф",
    summary:
      "На /aeterna — бриф для лицензированного клинициста (развивающая педиатрия / генетика / детская неврология) по поддержке при синдроме Дауна за 42 000 ACP. Это не излечение, не диагноз, не генная терапия или CRISPR от ANCAP и не гарантия результата развития. Юр. текст: /legal/down-syndrome-support.",
    href: "/aeterna#down-syndrome-support",
  },
  {
    id: "humanitarian-africa",
    date: "2026-09-14",
    title: "Гуманитарный стол: Африка — брифы и партнёры",
    summary:
      "На /humanitarian добавлены африканские коридоры помощи (еда, вода, медпоставки, livelihood) и листинги национальных обществ Красного Креста / Красного Полумесяца (Кения, ЮАР, Эфиопия, Сенегал, Египет). Это desk listing, не подписанное партнёрство с МФОКК и не лицензия на эмблему. Юр. текст: /legal/humanitarian.",
    href: "/humanitarian",
  },
  {
    id: "aeterna-adhd-support",
    date: "2026-09-13",
    title: "AETERNA: поддержка при СДВГ — партнёрский бриф",
    summary:
      "На /aeterna — бриф для лицензированного клинициста (детская психиатрия / неврология) по поддержке при СДВГ за 42 000 ACP. Инфографика про фокус, планирование и «путь к миллиарду» — мотивационная грамотность, не обещание диагноза, рецепта, стимуляторов или финансового результата. Юр. текст: /legal/adhd-support.",
    href: "/aeterna#adhd-support",
  },
  {
    id: "aeterna-synthetic-blood-mamba",
    date: "2026-09-12",
    title: "AETERNA: архитектура синтетической крови с компонентом Чёрной Мамбы",
    summary:
      "На /aeterna — партнёрский бриф многослойной частицы (ядро HBOC/PFC, липидная оболочка, полимерная сетка, модифицированные пептиды Чёрной Мамбы как грамотность, доставка и сенсоры) за 98 000 ACP. На /tech — лот лицензии этой архитектуры (старт 98 000 ACP). Это не кровезаменитель, не компаундинг яда или гемоглобина/PFC, не изделие CE/FDA и не SOP токсинов. Юр. текст: /legal/synthetic-blood-mamba.",
    href: "/aeterna#synthetic-blood-mamba",
  },
  {
    id: "tech-aeterna-synthetic-blood-mamba",
    date: "2026-09-12",
    title: "TECH: лицензия архитектуры синтетической крови / Чёрной Мамбы",
    summary:
      "В аукционе /tech добавлены лоты AETERNA: oxygen-carrier (старт 92 000 ACP) и synthetic-blood / Black Mamba (старт 98 000 ACP). Это лицензии партнёрских брифов в ACP через AuctionEscrow — не продажа крови, яда или CE/FDA-изделия.",
    href: "/tech",
  },
  {
    id: "aeterna-oxygen-carrier",
    date: "2026-09-12",
    title: "AETERNA: искусственный переносчик кислорода",
    summary:
      "На /aeterna — партнёрский бриф гемоглобиновой везикулы или эмульсии перфторуглерода за 92 000 ACP. Инфографика описывает ядро, оболочку, регулятор сродства к O₂, буферы и стерильный розлив как грамотность архитектуры, не как SOP производства. Это не кровезаменитель, не компаундинг гемоглобина или PFC, не изделие CE/FDA и не инфузионный продукт ANCAP. Юр. текст: /legal/oxygen-carrier.",
    href: "/aeterna#oxygen-carrier",
  },
  {
    id: "perimeter-security-watch",
    date: "2026-09-12",
    title: "Периметр: система охраны и раннего обнаружения",
    summary:
      "На /perimeter — новый рейл охраны: камеры IP/PTZ/тепловизор, датчики, тревожный кабель, лазерные барьеры, ограждение, контроль доступа, освещение и 24/7 SOC-бриф за 8 500 ACP. Инфографика — концептуальная архитектура лицензированного партнёра. Это не ЧОП, не гарантия «никто не пройдёт» и не продажа камер ANCAP.",
    href: "/perimeter#security-watch",
  },
  {
    id: "aeterna-m-receptor-subscription",
    date: "2026-09-12",
    title: "AETERNA: подписка на доставку к M-рецепторам",
    summary:
      "На /aeterna — подписка на мультимодальную доставку и нейромодуляцию M-рецепторов: трансдермальный пластырь, ионофорез, ингалятор/небулайзер и стимуляция блуждающего нерва. 12 000 ACP / месяц, 32 000 / квартал, 108 000 / год. Это не компаундинг скополамина, не изделие CE/FDA, не лечение Паркинсона, астмы, ХОБЛ, аритмии или внутриглазного давления. Юр. текст: /legal/m-receptor.",
    href: "/aeterna#m-receptor",
  },
  {
    id: "aeterna-vascular-transdermal",
    date: "2026-09-12",
    title: "AETERNA: Vascular Care и трансдермальный пистолет",
    summary:
      "На /aeterna — три новых партнёрских рейла: Vascular Care+ (безвредный поток N2+O2 и световая волна, 54 000 ACP), Vascular Care (УЗ / РЧ / тепло, 58 000 ACP) и безыгольный трансдермальный пистолет (аэрозоль плюс газ-носитель, 46 000 ACP). Это не CE/FDA-изделие, не лечение тромбоза, не рецептурный дозатор и не гарантированный результат по варикозу или жиру. Юр. тексты: /legal/vascular-care-plus, /legal/vascular-care, /legal/transdermal.",
    href: "/aeterna#vascular-care-plus",
  },
  {
    id: "aeterna-biofusion-dpsc",
    date: "2026-09-12",
    title: "AETERNA: камера BioFusion и биоматериал из DPSC",
    summary:
      "На /aeterna — партнёрский бриф камеры микроманипуляций BioFusion за 88 000 ACP (ЭКО/ICSI, опыление растений, наблюдение эмбриона, работа с микроорганизмами в BSL-лабе) и отдельный рейл биоматериала из стволовых клеток пульпы зуба мудрости за 65 000 ACP. Это не клиника ЭКО, не гарантированная беременность, не полноразмерный орган (печать органа остаётся 250 000 ACP) и не набор для дома. Юр. тексты: /legal/biofusion и /legal/dpsc.",
    href: "/aeterna#biofusion",
  },
  {
    id: "aeterna-microwave-body-contouring",
    date: "2026-09-12",
    title: "AETERNA: микроволновой контур тела",
    summary:
      "На /aeterna — партнёрский бриф контактно-охлаждаемого аппликатора 2,45 / 5,8 ГГц за 52 000 ACP. Инфографика описывает избирательный нагрев адипоцитов и лимфодренаж как грамотность протокола, не как гарантированный результат. Это не липосакция, не CE/FDA-изделие и не программа похудения. Юр. текст: /legal/body-contouring.",
    href: "/aeterna#microwave-body",
  },
  {
    id: "aeterna-vinci-light-chamber",
    date: "2026-09-12",
    title: "AETERNA: световая камера Vinci для тканей",
    summary:
      "На /aeterna — партнёрский бриф полноростовой LED-камеры (красный / ближний ИК как грамотность фотобиомодуляции, UVA только после скрининга) за 48 000 ACP. Инфографика вдохновлена заметками Леонардо о свете и теле: это не реконструкция изобретения, не CE/FDA-изделие и не «безопасный загар». Юр. текст: /legal/light-chamber.",
    href: "/aeterna#vinci-light",
  },
  {
    id: "perimeter-blast-radius-proof",
    date: "2026-09-12",
    title: "Периметр: blast-radius proof против ключей DNA и паспорта",
    summary:
      "GET /perimeter-cleanup/blast-radius — живой failed-decrypt тест: снимок SHA-384 отпечатков ключей DNA/passport/perimeter на хосте, попытка открыть canary-бриф чужими namespace. Владелец своей заявки может повторить проверку без публикации plaintext. Разделение отсеков измеряется, не предполагается.",
    href: "/perimeter",
  },
  {
    id: "perimeter-small-operator-access",
    date: "2026-09-12",
    title: "Периметр: малый SKU и прозрачность без DeFi-обёртки",
    summary:
      "На /perimeter добавлен small-site тариф от 400 ACP для небольших площадок. Шифрование AES-256-GCM остаётся at-rest на хосте оператора (форма, не key-ceremony). Каталог публичный. Это не пул Aave, не Maker vault и не RWA-yield вокруг уборки — хеш SHA-384 заявки виден без расшифровки заметок.",
    href: "/perimeter",
  },
  {
    id: "humanitarian-red-cross-desk",
    date: "2026-09-12",
    title: "Гуманитарный стол: еда, вода, одежда, медпрепараты, подъёмная работа",
    summary:
      "Новый /humanitarian — ACP-брифы помощи с листингами МФКК и национальных обществ Красного Креста / Красного Полумесяца (РФ, Украина, Германия, США). Это не подписанное партнёрство, не лицензия эмблемы Женевских конвенций и не благотворительная организация ANCAP по 135-ФЗ. Грант 100 ACP при регистрации по-прежнему не является пожертвованием. Юр. текст: /legal/humanitarian.",
    href: "/humanitarian",
  },
  {
    id: "aeterna-vet-regen-pod",
    date: "2026-09-12",
    title: "AETERNA: выращивание органов для кошек и собак",
    summary:
      "В раздел печати органов добавлены ветеринарные рейлы: криоконсерватор-восстановитель тканей кошки (75 000 ACP) и камера VET REGEN POD для собаки (180 000 ACP). Инфографики — концептуальная архитектура партнёра, не медизделие и не обещание «возвращения к жизни». Только лицензированный ветеринар. Юр. текст: /legal/vet-regen.",
    href: "/aeterna#vet-regen",
  },
  {
    id: "welcome-grant-100-acp",
    date: "2026-09-12",
    title: "Грант 100 ACP при регистрации — доступ, не пожертвование",
    summary:
      "Новый аккаунт получает 100 ACP на леджер (номинальная метка $100, не выплата USD). Смысл — снизить барьер входа к платным AI-workflow. Это промо-кредит, не благотворительный взнос по 135-ФЗ / ст. 582 ГК, не налоговый вычет. Юр. текст: /legal/welcome-grant.",
    href: "/legal/welcome-grant",
  },
  {
    id: "startup-invest-desk",
    date: "2026-09-12",
    title: "Инвестиции в стартапы — IT-газели 2026",
    summary:
      "Новый /startups: literacy и ACP-брифы по ИИ/ML, IT для ритейла и e-commerce, SECaaS, агротеху. Цитаты CNews/Spark-Interfax (Джиэй Тэктим / «Золотое яблоко»), Forbes/ФРИИ, Sky.pro. Не оферта ценных бумаг. Юр. §9: /legal/research-refs.",
    href: "/startups",
  },
  {
    id: "chalmers-floquet-bosonic",
    date: "2026-09-11",
    title: "Стек: Floquet / бозонные коды (~1000× меньше циклов)",
    summary:
      "В технологический стек /tech добавлены single-period Floquet + quantum lattice gates для бозонных кодов (Huang–Du–Guo, PRL 2026; сюжет «Науки» 10.09.2026). Literacy, не квантовый компьютер ANCAP. Юр. раскрытие: /legal/research-refs §8.",
    href: "/tech",
  },
  {
    id: "aeterna-mrna-reprogramming",
    date: "2026-09-11",
    title: "AETERNA: частичное перепрограммирование клеток (мРНК / LNP)",
    summary:
      "В /aeterna добавлен consult-workflow на 1 000 000 ACP: грамотность по доставке мРНК в липидных наночастицах и частичному омоложению без потери идентичности клетки. Цитата USPTO notice of allowance (Daewoong eTurna, авг. 2026) — не выданный патент и не лекарство. Юр. раскрытие: /legal/research-refs.",
    href: "/aeterna",
  },
  {
    id: "nexus-social",
    date: "2026-09-11",
    title: "Nexus — соцсеть людей и роботов",
    summary:
      "Новый /nexus: общая лента постов людей и агентов, ответы в тредах, пост от имени owned agent. Activity runs остаётся на /feed.",
    href: "/nexus",
  },
  {
    id: "saliva-rx-desk",
    date: "2026-09-11",
    title: "Saliva Rx — анализ слюны + персональный Rx",
    summary:
      "Новый /saliva-rx: пайплайн слюна → multi-omics → индивидуальный дизайн препарата → лицензированный compounding/synthesis. Не медицина и не гарантия излечения. Юр. заметка: /legal/saliva-rx-notice.",
    href: "/saliva-rx",
  },
  {
    id: "gitlab-cve-2026-85706",
    date: "2026-09-11",
    title: "GitLab CVSS 10 — проверка ANCAP",
    summary:
      "CVE-2026-85706: неаутентифицированное чтение файлов на self-managed GitLab при наличии public project. Стек ANCAP (GitHub + SourceCraft) не затронут. Операторская заметка: docs/GITLAB_CVE_2026_85706.md.",
    href: "https://thehackernews.com/2026/09/gitlab-cvss-10-file-read-flaw-draws-in.html",
  },
  {
    id: "quantum-principles-p1-p8",
    date: "2026-09-11",
    title: "Принципы квантовой приватной ёмкости P1–P8",
    summary:
      "В проект внесены принципы из iXBT Live (0+0>0 / супераддитивность): на /quantum-sim и в docs/QUANTUM_PRIVATE_CAPACITY_PRINCIPLES.md. Literacy для mesh sat+БС+ретрансляторы, не warranty QKD.",
    href: "/quantum-sim",
  },
  {
    id: "quantum-sim-ixbt",
    date: "2026-09-11",
    title: "Цифровая SIM + квантовая связь",
    summary:
      "Новый /quantum-sim: eSIM-интенты, PQC/квантово-готовые каналы и глобальный low-ping mesh (спутники, БС, ретрансляторы). Research-цитата iXBT Live про квантовый парадокс в защите данных — /legal/research-refs.",
    href: "/quantum-sim",
  },
  {
    id: "cryo-literary-reviews",
    date: "2026-09-11",
    title: "Крионика + литаукцион + отзывы",
    summary:
      "Новый /cryo: криоконсервация с research-протоколом по тихоходкам; партнёры КриоРус и Tomorrow.bio. Аукцион литработ /literary. Отзывы пользователей и ИИ по услугам. Юр. заметка: /legal/cryo-constitution.",
    href: "/cryo",
  },
  {
    id: "perimeter-cleanup-abrams",
    date: "2026-09-11",
    title: "Уборка периметра + Abrams Suite-B сейф",
    summary:
      "Новая услуга /perimeter: очистка периметра от всех видов загрязнений. Брифы заявок at-rest AES-256-GCM + HKDF-SHA384 (Abrams Suite-B). Страховка perimeter_cleanup на /insurance.",
    href: "/perimeter",
  },
  {
    id: "exchange-auth-settle",
    date: "2026-09-11",
    title: "Exchange: auth-settle USDT→ACP",
    summary:
      "Тикеты Exchange открывают linked swap desk. /buy-acp ведёт с crypto-first рельсов. Монетизация ACP-first — не freeze.",
    href: "/buy-acp",
  },
  {
    id: "zeiss-lightfield-4d",
    date: "2026-09-11",
    title: "ZEISS Lightfield 4D — научная ссылка",
    summary:
      "В проект добавлена публичная ссылка на ZEISS LSM Lightfield 4D technology note. Юридическое раскрытие: /legal/research-refs (без аффилиации, PDF не хостим).",
    href: "/legal/research-refs",
  },
  {
    id: "legal-entertainment",
    date: "2026-09-11",
    title: "Легальные развлечения по миру",
    summary:
      "Карта /entertainment: музеи, фестивали, спорт, лотереи и курорты только с лицензией; on-platform — Arena. Серые букмекеры вне скоупа.",
    href: "/entertainment",
  },
  {
    id: "dna-rna-bank",
    date: "2026-09-11",
    title: "Цифровой банк ДНК и РНК",
    summary:
      "Отдельный сейф /dna-bank: метаданные ДНК/РНК at-rest AES-256-GCM + HKDF-SHA384 (v1). Полные геномы не принимаются.",
    href: "/dna-bank",
  },
  {
    id: "ancap-ai-agency",
    date: "2026-09-11",
    title: "ANCAP AI Agency",
    summary:
      "Отдельное рекламное агентство для ИИ-сектора: кампании, креативы, Telegram/X/email и proof-backed spend. Блок на главной и /agency.",
    href: "/agency",
  },
  {
    id: "ancap-promo-2026-09",
    date: "2026-09-11",
    title: "ANCAP: AI-native capital allocation",
    summary:
      "Платные AI-workflow, ACP wallet, Digital Passport, bridge wACP/sACP. Старт: token snapshot, каталог workflows, /passport.",
    href: "/",
  },
  {
    id: "passport-education-docs",
    date: "2026-09-11",
    title: "Паспорт: документы об образовании",
    summary:
      "Дипломы и сертификаты в Digital Passport — at-rest ChaCha20-Poly1305 (v2). UI /passport, API education-docs.",
    href: "/passport",
  },
  {
    id: "crypto-benchmark",
    date: "2026-09-10",
    title: "Crypto Benchmark Scorecard",
    summary:
      "Открытый QOBLIB-стиль scorecard для ACP/wACP/sACP: публичные baselines и live-измерения на /reserves.",
    href: "/reserves",
  },
  {
    id: "embodied-security",
    date: "2026-09-10",
    title: "Безопасность embodied AI",
    summary:
      "Адаптеры UnifoLM выключены по умолчанию. Реестр моделей и политика изоляции от ключей ACP.",
    href: "/reserves",
  },
  {
    id: "lunar-desk",
    date: "2026-09-10",
    title: "Lunar Land desk",
    summary:
      "Каталог селенографических участков с научными темами NASA–IBM LFM и ACP interest desk.",
    href: "/lunar",
  },
  {
    id: "bridge-deposit-scan",
    date: "2026-09-10",
    title: "Мост ACP→wACP: депозиты",
    summary:
      "Инкрементальный сканер депозитов ускоряет выход из PENDING_DEPOSIT и догоняет tip цепочки.",
    href: "/bridge/acp-bsc",
  },
  {
    id: "bridge-cancel-requeue",
    date: "2026-09-10",
    title: "Отмена и requeue mint",
    summary:
      "Пользователи могут отменить неоплаченные intents; операторы — requeue FAILED mint.",
    href: "/bridge/acp-bsc",
  },
  {
    id: "markets-matrix",
    date: "2026-09-09",
    title: "Матрица листингов wACP",
    summary:
      "Опубликована полная free-placement матрица для wACP на рынках и агрегаторах.",
    href: "/markets",
  },
  {
    id: "coingecko-ticker",
    date: "2026-09-09",
    title: "CoinGecko маркет-тикер",
    summary:
      "На главной — живая лента цен через CoinGecko рядом с рельсами ACP/wACP.",
    href: "/",
  },
  {
    id: "dextools-live",
    date: "2026-09-09",
    title: "DexTools и контракт",
    summary:
      "DexTools отмечен live; задокументирован CA для Coin/DexTools форм и доверия к адресу.",
    href: "/docs/wacp/contracts",
  },
];
