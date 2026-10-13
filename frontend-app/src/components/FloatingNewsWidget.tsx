"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PROJECT_NEWS_RU } from "@/lib/projectNewsRu";
import {
  FLOATING_WIDGET_EVENT,
  emitFloatingWidget,
  type FloatingWidgetEventDetail,
} from "@/lib/floatingWidgets";

const STORAGE_KEY = "ancap_news_widget_collapsed_v2";
const ROTATE_MS = 4500;

export function FloatingNewsWidget() {
  const [index, setIndex] = useState(0);
  const [open, setOpen] = useState(false);
  const [ready, setReady] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const items = PROJECT_NEWS_RU.slice(0, 8);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");
    const apply = () => setIsMobile(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === "0") setOpen(true);
      else if (stored === "1") setOpen(false);
      else setOpen(!mq.matches); // desktop open by default, mobile closed
    } catch {
      setOpen(!mq.matches);
    }
    setReady(true);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    const onPeer = (ev: Event) => {
      const detail = (ev as CustomEvent<FloatingWidgetEventDetail>).detail;
      if (!detail || detail.id === "news") return;
      if (detail.open && isMobile) setOpen(false);
    };
    window.addEventListener(FLOATING_WIDGET_EVENT, onPeer as EventListener);
    return () => window.removeEventListener(FLOATING_WIDGET_EVENT, onPeer as EventListener);
  }, [isMobile]);

  useEffect(() => {
    if (!open || items.length < 2) return;
    const id = window.setInterval(() => {
      setIndex((prev) => (prev + 1) % items.length);
    }, ROTATE_MS);
    return () => window.clearInterval(id);
  }, [open, items.length]);

  const setOpenPersist = (next: boolean) => {
    setOpen(next);
    emitFloatingWidget("news", next);
    try {
      localStorage.setItem(STORAGE_KEY, next ? "0" : "1");
    } catch {
      /* ignore */
    }
  };

  if (!ready || items.length === 0) return null;

  const current = items[index] ?? items[0];

  if (!open) {
    return (
      <div className="pointer-events-none fixed bottom-[max(0.85rem,env(safe-area-inset-bottom))] left-3 z-[90] sm:left-4">
        <button
          type="button"
          onClick={() => setOpenPersist(true)}
          className="pointer-events-auto ancap-fab-slide-in rounded-full border border-emerald-400/30 bg-[#071020]/94 px-3.5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-100 shadow-[0_12px_40px_rgba(0,0,0,0.45)] backdrop-blur-md hover:border-emerald-300/45"
          aria-label="Open ANCAP news"
        >
          News
        </button>
      </div>
    );
  }

  return (
    <aside
      aria-label="ANCAP project news"
      className="pointer-events-none fixed bottom-[max(0.85rem,env(safe-area-inset-bottom))] left-3 z-[90] w-[min(18.5rem,calc(100vw-1.5rem))] sm:left-4"
    >
      <div className="pointer-events-auto ancap-panel-rise overflow-hidden rounded-2xl border border-white/12 bg-[#071020]/95 text-white shadow-[0_18px_50px_rgba(0,0,0,0.48)] backdrop-blur-xl">
        <div className="flex items-center justify-between gap-2 border-b border-white/10 px-3 py-2">
          <div className="min-w-0">
            <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-200/90">
              News
            </div>
            <div className="truncate text-xs text-white/45">
              {index + 1} / {items.length} · ANCAP
            </div>
          </div>
          <button
            type="button"
            onClick={() => setOpenPersist(false)}
            className="rounded-md border border-white/10 px-2 py-1 text-[11px] text-white/55 hover:border-white/25 hover:text-white"
            aria-label="Collapse news"
          >
            {isMobile ? "Close" : "Collapse"}
          </button>
        </div>

        <div className="relative h-[7.6rem] overflow-hidden px-3 py-2.5">
          <div key={current.id} className="ancap-news-float absolute inset-x-3 top-2.5">
            <div className="text-[10px] uppercase tracking-wide text-white/40">{current.date}</div>
            <Link
              href={current.href}
              className="mt-1 block text-sm font-semibold leading-5 text-white hover:text-emerald-200"
            >
              {current.title}
            </Link>
            <p className="mt-1.5 line-clamp-3 text-[12px] leading-4 text-white/62">{current.summary}</p>
          </div>
        </div>

        <div className="flex items-center gap-1 border-t border-white/10 px-3 py-2">
          {items.map((item, i) => (
            <button
              key={item.id}
              type="button"
              aria-label={`News item ${i + 1}`}
              onClick={() => setIndex(i)}
              className={`h-1.5 flex-1 rounded-full transition ${
                i === index ? "bg-emerald-300/80" : "bg-white/15 hover:bg-white/30"
              }`}
            />
          ))}
        </div>
      </div>
    </aside>
  );
}
