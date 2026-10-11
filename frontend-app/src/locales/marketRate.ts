type Language = "en" | "ru" | "uk" | "de" | "zh-Hant";
type Tree = { [key: string]: string };

export const marketRateBarByLang: Record<Language, Tree> = {
  en: {
    label: "Live rates",
    loading: "Loading rates…",
    error: "Rates unavailable",
    wrapRatio: "1 ACP = 10 wACP",
    gecko: "GeckoTerminal",
    legal: "Market data",
  },
  ru: {
    label: "Живые курсы",
    loading: "Загрузка курсов…",
    error: "Курсы недоступны",
    wrapRatio: "1 ACP = 10 wACP",
    gecko: "GeckoTerminal",
    legal: "Рыночные данные",
  },
  uk: {
    label: "Живі курси",
    loading: "Завантаження курсів…",
    error: "Курси недоступні",
    wrapRatio: "1 ACP = 10 wACP",
    gecko: "GeckoTerminal",
    legal: "Ринкові дані",
  },
  de: {
    label: "Live-Kurse",
    loading: "Kurse werden geladen…",
    error: "Kurse nicht verfügbar",
    wrapRatio: "1 ACP = 10 wACP",
    gecko: "GeckoTerminal",
    legal: "Marktdaten",
  },
  "zh-Hant": {
    label: "即時匯率",
    loading: "載入匯率…",
    error: "匯率不可用",
    wrapRatio: "1 ACP = 10 wACP",
    gecko: "GeckoTerminal",
    legal: "市場數據",
  },
};

/** @deprecated use marketRateBarByLang */
export const marketRateBar = marketRateBarByLang;
