'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, CandlestickSeries, HistogramSeries, LineSeries, ColorType, CrosshairMode } from 'lightweight-charts';
import { Card } from '../ui/Card';

interface ChartDataPoint {
  date: string;
  prix: number;
  open?: number | null;
  high?: number | null;
  low?: number | null;
  volume?: number | null;
}

interface StockChartProps {
  data: ChartDataPoint[];
}

const PERIODS = [
  { label: '1M',  days: 30 },
  { label: '3M',  days: 90 },
  { label: '6M',  days: 180 },
  { label: '1A',  days: 365 },
  { label: '3A',  days: 1095 },
  { label: '5A',  days: 1825 },
  { label: '10A', days: 3650 },
  { label: '20A', days: 7300 },
  { label: 'MAX', days: 99999 },
];

export function StockChart({ data }: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof createChart> | null>(null);
  const candleSeriesRef = useRef<any>(null);
  const lineSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);
  const [activePeriod, setActivePeriod] = useState('1A');
  const [chartType, setChartType] = useState<'line' | 'candle'>('line');

  // Filter data by period
  const getFilteredData = useCallback((periodLabel: string) => {
    const period = PERIODS.find(p => p.label === periodLabel)!;
    if (period.days >= 99999) return data;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - period.days);
    return data.filter(d => new Date(d.date) >= cutoff);
  }, [data]);

  // Si on est sur 1A par défaut mais qu'il y a moins de 2 points de données, on passe sur MAX
  useEffect(() => {
    if (data && data.length > 0 && activePeriod === '1A') {
      const filtered1A = getFilteredData('1A');
      if (filtered1A.length < 2) {
        setActivePeriod('MAX');
      }
    }
  }, [data, getFilteredData, activePeriod]);

  // Check if we have OHLC data
  const hasOHLC = data && data.some(d => d.open != null && d.high != null && d.low != null);

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) return;

    // Cleanup previous chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const container = chartContainerRef.current;

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: 'hsl(220, 18%, 51%)',
        fontFamily: "'Syne', 'Inter', sans-serif",
        fontSize: 12,
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.03)' },
        horzLines: { color: 'rgba(255,255,255,0.03)' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: 'rgba(201, 168, 76, 0.5)', labelBackgroundColor: '#C9A84C' },
        horzLine: { color: 'rgba(201, 168, 76, 0.5)', labelBackgroundColor: '#C9A84C' },
      },
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.08)',
        // Laisser de l'espace en haut (8%) et en bas pour le volume (30%)
        scaleMargins: { top: 0.06, bottom: 0.28 },
        autoScale: true,
      },
      timeScale: {
        borderColor: 'rgba(255,255,255,0.08)',
        timeVisible: true,
        secondsVisible: false,
        // Zoom/scroll au touch et à la molette
        rightOffset: 5,
        barSpacing: 6,          // espacement initial entre barres
        minBarSpacing: 1,       // zoom max (bougies très serrées)
        fixLeftEdge: false,
        fixRightEdge: false,
      },
      // Permettre le zoom à la molette et le scroll
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
      width: container.clientWidth,
      height: container.clientHeight,
    });

    // Candlestick series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    const lineSeries = chart.addSeries(LineSeries, {
      color: '#C9A84C',
      lineWidth: 2,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 4,
    });

    // Volume histogram — sur une echelle séparée
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: 'rgba(201, 168, 76, 0.25)',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });
    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.80, bottom: 0 },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    lineSeriesRef.current = lineSeries;
    volumeSeriesRef.current = volumeSeries;

    // Load initial data
    const filtered = getFilteredData(activePeriod);
    updateSeries(filtered, candleSeries, lineSeries, volumeSeries, hasOHLC, chartType);

    // Adapter l'espacement des barres selon le nb de points (meilleur zoom initial)
    const nb = filtered.length;
    const spacing = nb > 2000 ? 2 : nb > 500 ? 4 : nb > 200 ? 6 : 8;
    chart.timeScale().applyOptions({ barSpacing: spacing });
    chart.timeScale().fitContent();

    // Resize observer
    const resizeObserver = new ResizeObserver(() => {
      if (chartRef.current && container) {
        chartRef.current.applyOptions({ width: container.clientWidth });
      }
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, hasOHLC]);

  // Update on period / chart-type change
  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || !lineSeriesRef.current) return;
    const filtered = getFilteredData(activePeriod);
    updateSeries(filtered, candleSeriesRef.current, lineSeriesRef.current, volumeSeriesRef.current, hasOHLC, chartType);

    // Toggle visibility
    candleSeriesRef.current.applyOptions({ visible: chartType === 'candle' });
    lineSeriesRef.current.applyOptions({ visible: chartType === 'line' });

    // Adapter l'espacement selon le nb de points visible
    if (chartRef.current) {
      const nb = filtered.length;
      const spacing = nb > 2000 ? 2 : nb > 500 ? 4 : nb > 200 ? 6 : 8;
      chartRef.current.timeScale().applyOptions({ barSpacing: spacing });
      chartRef.current.timeScale().fitContent();
    }
  }, [activePeriod, chartType, getFilteredData, hasOHLC]);

  if (!data || data.length === 0) {
    return (
      <Card style={{ height: '460px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'hsl(var(--text-muted))' }}>Aucune donnée graphique disponible.</p>
      </Card>
    );
  }

  return (
    <Card style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>
          Historique du Cours
          {!hasOHLC && (
            <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginLeft: '0.5rem', fontWeight: 400 }}>
              (données OHLC partielles)
            </span>
          )}
        </h3>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Chart Type Toggle */}
          <div style={{ display: 'flex', gap: '0.25rem', backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.25rem', borderRadius: '8px' }}>
            <button
              onClick={() => setChartType('line')}
              style={{
                padding: '0.25rem 0.5rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                border: 'none',
                backgroundColor: chartType === 'line' ? 'hsl(var(--accent-primary))' : 'transparent',
                color: chartType === 'line' ? '#fff' : 'hsl(var(--text-muted))',
                transition: 'all 0.2s',
              }}
            >
              Ligne
            </button>
            <button
              onClick={() => setChartType('candle')}
              style={{
                padding: '0.25rem 0.5rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                border: 'none',
                backgroundColor: chartType === 'candle' ? 'hsl(var(--accent-primary))' : 'transparent',
                color: chartType === 'candle' ? '#fff' : 'hsl(var(--text-muted))',
                transition: 'all 0.2s',
              }}
            >
              🕯 Bougies
            </button>
          </div>

          {/* Period buttons */}
          <div style={{ display: 'flex', gap: '0.25rem', alignItems: 'center', flexWrap: 'wrap' }}>
            {PERIODS.map(p => (
              <button
                key={p.label}
                onClick={() => setActivePeriod(p.label)}
                style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid',
                  transition: 'all 0.15s ease',
                  borderColor: activePeriod === p.label ? 'hsl(var(--accent-primary))' : 'rgba(255,255,255,0.1)',
                  backgroundColor: activePeriod === p.label ? 'hsl(var(--accent-primary) / 0.2)' : 'transparent',
                  color: activePeriod === p.label ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-muted))',
                }}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Hint zoom */}
      <p style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))', margin: 0, opacity: 0.7 }}>
        🖱 Molette pour zoomer · Cliquer-glisser pour naviguer · Pinch sur mobile
      </p>

      {/* Chart container */}
      <div
        ref={chartContainerRef}
        style={{ width: '100%', height: '400px', position: 'relative' }}
      />
    </Card>
  );
}

function updateSeries(
  filtered: ChartDataPoint[],
  candleSeries: any,
  lineSeries: any,
  volumeSeries: any,
  hasOHLC: boolean,
  chartType: 'line' | 'candle',
) {
  const candleData = filtered.map(d => {
    const time = d.date as any;
    if (hasOHLC && d.open != null && d.high != null && d.low != null) {
      return { time, open: d.open, high: d.high, low: d.low, close: d.prix };
    }
    // Fallback: bougie plate
    return { time, open: d.prix, high: d.prix, low: d.prix, close: d.prix };
  });

  const volumeData = filtered.map(d => ({
    time: d.date as any,
    value: d.volume ?? 0,
    color: d.open != null && d.prix >= d.open
      ? 'rgba(34, 197, 94, 0.45)'
      : 'rgba(239, 68, 68, 0.45)',
  }));

  const lineData = filtered.map(d => ({
    time: d.date as any,
    value: d.prix,
  }));

  candleSeries.setData(candleData);
  lineSeries.setData(lineData);
  volumeSeries.setData(volumeData);
}
