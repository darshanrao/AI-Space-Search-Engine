// Base URL configuration
export const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic GET request helper
 * @param path - API endpoint path (without base URL)
 * @returns Promise with parsed JSON response
 */
export async function getJSON<T>(path: string): Promise<T> {
  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('GET request failed:', error);
    throw error;
  }
}

/**
 * Generic POST request helper
 * @param path - API endpoint path (without base URL)
 * @param body - Request body object
 * @returns Promise with parsed JSON response
 */
export async function postJSON<T>(path: string, body: any): Promise<T> {
  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('POST request failed:', error);
    throw error;
  }
}

/**
 * Generic PUT request helper
 * @param path - API endpoint path (without base URL)
 * @param body - Request body object
 * @returns Promise with parsed JSON response
 */
export async function putJSON<T>(path: string, body: any): Promise<T> {
  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('PUT request failed:', error);
    throw error;
  }
}

// Google Scholar Search Types
export interface ScholarSearchRequest {
  query?: string;
  context?: string;
  num_results?: number;
}

export interface ScholarSearchResponse {
  query: string;
  results: string;
  num_results: number;
  timestamp: string;
}

/**
 * Search Google Scholar for academic papers
 * @param request - Search request with query and optional result count
 * @returns Promise with search results
 */
export async function searchGoogleScholar(request: ScholarSearchRequest): Promise<ScholarSearchResponse> {
  return postJSON<ScholarSearchResponse>('/api/scholar/search', request);
}
