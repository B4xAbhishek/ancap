import type { Language } from "@/locales/translations";

/** A presentation taxonomy; not a claim that every linked project is an executable offer. */
export const solutionPortfolio = [
  { id: "crypto", kind: "core", routes: [["/markets", "Markets"], ["/business", "Business"], ["/growth", "Growth"], ["/agency", "Agency"]] },
  { id: "business", kind: "partner", routes: [["/startups", "Startups"], ["/counsel", "Counsel"], ["/insurance", "Insurance"], ["/compliance", "Compliance"], ["/careers", "Careers"]] },
  { id: "commerce", kind: "partner", routes: [["/flora", "FLORA"], ["/literary", "Literary"], ["/marketplace", "Marketplace"], ["/field-services", "Field services"], ["/starlink-install", "Starlink"], ["/antique-fire-restore", "Antique conservation"], ["/humanitarian", "Humanitarian"]] },
  { id: "life", kind: "research", routes: [["/aeterna", "AETERNA"], ["/dna-bank", "DNA bank"], ["/cryo", "Cryo"], ["/saliva-rx", "Saliva Rx"], ["/fauna", "FAUNA"]] },
  { id: "infrastructure", kind: "research", routes: [["/tech", "Technology"], ["/perimeter", "Perimeter"], ["/galaxy", "Galaxy"], ["/lunar", "Lunar"], ["/stardust", "Stardust"], ["/quantum-sim", "Quantum SIM"]] },
  { id: "community", kind: "pilot", routes: [["/nexus", "Nexus"], ["/dating", "Dating"], ["/entertainment", "Entertainment"], ["/arena", "Arena"], ["/feed", "Feed"]] },
] as const;

export function workflowArea(category: string): typeof solutionPortfolio[number]["id"] {
  if (/aeterna|health|life|dna|cryo/i.test(category)) return "life";
  if (/counsel|governance|audit|business|compliance/i.test(category)) return "business";
  if (/developer|agent commerce|infrastructure|quantum|space/i.test(category)) return "infrastructure";
  if (/conservation|concierge|commerce|flora|literary/i.test(category)) return "commerce";
  if (/entertainment|community|media/i.test(category)) return "community";
  return "crypto";
}

type AreaCopy = { title: string; body: string; deliverable: string };
type PortfolioCopy = { kinds: Record<"core" | "partner" | "research" | "pilot", string>; areas: AreaCopy[] };
export const portfolioByLang: Record<Language, PortfolioCopy> = {
  en: { kinds: { core: "Initial commercial focus", partner: "Partner / planning briefs", research: "Research briefs", pilot: "Pilot applications" }, areas: [
    { title: "Crypto research & growth", body: "For token teams preparing a launch, listing or campaign. The first commercial focus for paid execution.", deliverable: "Risk reports, listing materials and campaign plans." },
    { title: "Business & professional services", body: "For founders preparing a business case or a handoff to a qualified adviser.", deliverable: "Business briefs, requirements and adviser intake documents." },
    { title: "Commerce & field operations", body: "Preparation for procurement, creative work and service-provider handoffs.", deliverable: "Specifications, catalog copy and partner request briefs." },
    { title: "Life sciences · AETERNA", body: "Research and partner-intake documents. Medical decisions and biological services require qualified providers.", deliverable: "Research summaries and questions for professional review." },
    { title: "Infrastructure & frontier research", body: "Concept exploration and planning. Space, weather and quantum pages do not establish deployed physical capabilities.", deliverable: "Feasibility briefs, requirements and concept comparisons." },
    { title: "Community & media", body: "Pilot applications for community, audience and content operations.", deliverable: "Content plans, moderation guides and event briefs." },
  ] },
  ru: { kinds: { core: "Начальный коммерческий фокус", partner: "Брифы для планирования и партнёров", research: "Исследовательские брифы", pilot: "Пилотные направления" }, areas: [
    { title: "Криптоанализ и продвижение", body: "Для команд токенов, готовящих запуск, листинг или кампанию. Начальный фокус платного выполнения.", deliverable: "Отчёты о рисках, материалы для листинга и планы кампаний." },
    { title: "Бизнес и профессиональные услуги", body: "Для основателей, готовящих бизнес-проект или обращение к профильному консультанту.", deliverable: "Бизнес-брифы, требования и документы для консультаций." },
    { title: "Торговля и выездные работы", body: "Подготовка закупок, творческих задач и требований к исполнителям.", deliverable: "Спецификации, описания каталога и запросы партнёрам." },
    { title: "Науки о жизни · AETERNA", body: "Исследования и обращения к партнёрам. Медицинские решения и биологические услуги требуют профильных специалистов.", deliverable: "Обзоры исследований и вопросы для профессиональной проверки." },
    { title: "Инфраструктура и перспективные исследования", body: "Проработка концепций. Страницы космоса, погоды и квантовых проектов не подтверждают физическую реализацию.", deliverable: "Брифы реализуемости, требования и сравнение концепций." },
    { title: "Сообщества и медиа", body: "Пилотные применения для сообществ, аудиторий и производства контента.", deliverable: "Контент-планы, правила модерации и сценарии мероприятий." },
  ] },
  uk: { kinds: { core: "Початковий комерційний фокус", partner: "Брифи для планування та партнерів", research: "Дослідницькі брифи", pilot: "Пілотні напрями" }, areas: [
    { title: "Криптоаналіз і просування", body: "Для команд токенів, що готують запуск, лістинг чи кампанію. Початковий фокус платного виконання.", deliverable: "Звіти про ризики, матеріали лістингу та плани кампаній." },
    { title: "Бізнес і професійні послуги", body: "Для засновників, що готують бізнес-проєкт чи звернення до фахівця.", deliverable: "Бізнес-брифи, вимоги та документи для консультацій." },
    { title: "Торгівля та виїзні роботи", body: "Підготовка закупівель, творчих завдань і вимог до виконавців.", deliverable: "Специфікації, описи каталогу та запити партнерам." },
    { title: "Науки про життя · AETERNA", body: "Дослідження та звернення до партнерів. Медичні рішення й біологічні послуги потребують профільних фахівців.", deliverable: "Огляди досліджень і запитання для професійної перевірки." },
    { title: "Інфраструктура й перспективні дослідження", body: "Опрацювання концепцій. Космічні, погодні та квантові сторінки не підтверджують фізичну реалізацію.", deliverable: "Брифи здійсненності, вимоги та порівняння концепцій." },
    { title: "Спільноти й медіа", body: "Пілотні застосування для спільнот, аудиторій і контенту.", deliverable: "Контент-плани, правила модерації та сценарії подій." },
  ] },
  de: { kinds: { core: "Erster kommerzieller Fokus", partner: "Planungs- und Partnerbriefings", research: "Forschungsbriefings", pilot: "Pilotanwendungen" }, areas: [
    { title: "Krypto-Recherche & Wachstum", body: "Für Token-Teams bei Launch, Listing oder Kampagnen. Erster Fokus für bezahlte Ausführungen.", deliverable: "Risikoberichte, Listing-Unterlagen und Kampagnenpläne." },
    { title: "Unternehmen & Fachberatung", body: "Für Gründer bei Geschäftsvorbereitung und Übergabe an Fachberater.", deliverable: "Geschäftsbriefings, Anforderungen und Beratungsunterlagen." },
    { title: "Handel & Außendienst", body: "Vorbereitung von Beschaffung, kreativen Aufgaben und Dienstleisteranfragen.", deliverable: "Spezifikationen, Katalogtexte und Partneranfragen." },
    { title: "Biowissenschaften · AETERNA", body: "Recherche und Partneranfragen. Medizinische Entscheidungen und biologische Leistungen brauchen qualifizierte Anbieter.", deliverable: "Forschungsübersichten und Fragen zur fachlichen Prüfung." },
    { title: "Infrastruktur & Zukunftsforschung", body: "Konzeptprüfung. Raumfahrt-, Wetter- und Quantenseiten belegen keine physische Umsetzung.", deliverable: "Machbarkeitsbriefings, Anforderungen und Konzeptvergleiche." },
    { title: "Community & Medien", body: "Pilotanwendungen für Community-, Zielgruppen- und Inhaltsarbeit.", deliverable: "Inhaltspläne, Moderationsleitfäden und Veranstaltungsbriefings." },
  ] },
  "zh-Hant": { kinds: { core: "初期商業重點", partner: "規劃與合作簡報", research: "研究簡報", pilot: "試點應用" }, areas: [
    { title: "加密研究與行銷", body: "適合準備啟動、上架或行銷活動的代幣團隊，為初期付費執行重點。", deliverable: "風險報告、上架資料與活動計畫。" },
    { title: "商業與專業服務", body: "協助創辦人準備商業案例及提交專業顧問的資料。", deliverable: "商業簡報、需求與諮詢資料。" },
    { title: "商務與現場作業", body: "準備採購、創意任務及服務供應商需求。", deliverable: "規格、目錄文案與合作請求簡報。" },
    { title: "生命科學 · AETERNA", body: "研究與合作方文件。醫療決策及生物服務需由合格提供者處理。", deliverable: "研究摘要與供專業審查的問題。" },
    { title: "基礎設施與前沿研究", body: "概念探索。太空、天氣及量子頁面不證明已部署實體能力。", deliverable: "可行性簡報、需求與概念比較。" },
    { title: "社群與媒體", body: "用於社群、受眾及內容營運的試點應用。", deliverable: "內容計畫、管理指南與活動簡報。" },
  ] },
};

export function projectPresentation(lang: Language, href: string) {
  const index = solutionPortfolio.findIndex(area => area.routes.some(([route]) => route === href));
  if (index < 0) throw new Error("Unknown project presentation route");
  const area = solutionPortfolio[index];
  const name = area.routes.find(([route]) => route === href)![1];
  const copy = portfolioByLang[lang];
  return {
    title: `${name} · ${copy.kinds[area.kind]}`,
    lead: `${copy.areas[index].body} ${copy.areas[index].deliverable}`,
  };
}
