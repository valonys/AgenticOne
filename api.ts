import { auth } from './auth';

export async function authorizedFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
    const currentUser = auth.getCurrentUser();
    const headers = new Headers(init.headers || {});
    if (currentUser) {
        const authHeader = auth.getAuthHeader();
        if (authHeader) {
            headers.set('Authorization', authHeader);
        }
    }
    return fetch(input, { ...init, headers });
}

export async function getJson<T>(url: string, init: RequestInit = {}): Promise<T> {
    const res = await authorizedFetch(url, init);
    if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`Request failed: ${res.status} ${res.statusText} ${text}`);
    }
    return res.json() as Promise<T>;
}

