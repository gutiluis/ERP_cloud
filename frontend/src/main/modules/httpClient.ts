import { fetch, Agent, setGlobalDispatcher } from 'undici';

/**
 * Create a global agent only for external SaaS APIs
 */
const externalAgent = new Agent({
  keepAliveTimeout: 5000,
  pipelining: 1,
});
setGlobalDispatcher(externalAgent);

/**
 * Determines if a URL is external (not localhost)
 */
function isExternal(url: string) {
  return !url.startsWith('http://localhost') && !url.startsWith('http://127.0.0.1');
}

/**
 * Generic HTTP request function
 */
export async function httpRequest<T>(
  url: string,
  options?: {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    headers?: Record<string, string>;
    body?: any;
    retries?: number;
  }
): Promise<T> {
  const { method = 'GET', headers = {}, body: payload, retries = 2 } = options || {};

  // Local requests can skip the agent
  const fetchOptions: RequestInit = {
    method,
    headers,
    body: payload ? JSON.stringify(payload) : undefined,
  };

  try {
    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} - ${response.statusText}`);
    }

    const data = await response.json();
    return data as T;
  } catch (err) {
    if (retries > 0) {
      console.warn(`Request failed, retrying... (${retries} left)`, err);
      return httpRequest<T>(url, { ...options, retries: retries - 1 });
    }
    throw err;
  }
}

/**
 * Centralized ERP Services
 */
export const ERPServices = {
  internal: {
    auth: (path: string) => `http://localhost:3000/auth/${path}`,
    inventory: (path: string) => `http://localhost:3000/inventory/${path}`,
    finance: (path: string) => `http://localhost:3000/finance/${path}`,
    crm: (path: string) => `http://localhost:3000/crm/${path}`,
  },
  external: {
    stripe: (path: string) => `https://api.stripe.com/v1/${path}`,
    quickbooks: (path: string) => `https://quickbooks.api.intuit.com/${path}`,
    twilio: (path: string) => `https://api.twilio.com/2010-04-01/${path}`,
  },
};