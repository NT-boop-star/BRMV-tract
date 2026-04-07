const API_URL = 'http://localhost:8000/api/v1';

/**
 * Fonction helper pour les appels fetch avec gestion d'erreur.
 */
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${API_URL}${endpoint}`;
  try {
    const res = await fetch(url, { ...options, next: { revalidate: 0 } });
    if (!res.ok) {
      throw new Error(`Erreur API: ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`Fetch error on ${url}:`, error);
    throw error;
  }
}

export interface ChartQueryParams {
  from_date?: string;   // ISO: "YYYY-MM-DD"
  to_date?: string;     // ISO: "YYYY-MM-DD"
  days?: number;        // Rétrocompat: N jours glissants
}

export const brvmAPI = {
  getMarketSummary: () => fetchAPI('/market/summary'),
  getScreener: () => fetchAPI('/actions/screener'),
  getActions: () => fetchAPI('/actions/'),
  getActionDetails: (ticker: string) => fetchAPI(`/actions/${ticker}`),

  /**
   * Historique des cours d'une action.
   * - Sans paramètre : tout l'historique depuis 2000.
   * - from_date / to_date : plage précise (ISO YYYY-MM-DD).
   * - days : N jours glissants depuis aujourd'hui (rétrocompat).
   */
  getActionChart: (ticker: string, params: ChartQueryParams = {}) => {
    const qs = new URLSearchParams();
    if (params.from_date) qs.set('from_date', params.from_date);
    if (params.to_date)   qs.set('to_date',   params.to_date);
    if (params.days !== undefined && !params.from_date) {
      qs.set('days', String(params.days));
    }
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return fetchAPI(`/actions/${ticker}/chart${query}`);
  },

  getMarketNews: (limit: number = 50, offset: number = 0) =>
    fetchAPI(`/market/news?limit=${limit}&offset=${offset}`),

  getSectorPerformance: () => fetchAPI('/market/sectors'),
  
  getMacroIndicators: () => fetchAPI('/macro/indicators'),
  getMacroCommodities: () => fetchAPI('/macro/commodities'),
};
