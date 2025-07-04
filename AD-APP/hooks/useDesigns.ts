import { useState, useEffect } from 'react';
import { galleryApi, Design, DesignsResponse } from '@/services/galleryApi';
import { useAuth } from '@/contexts/AuthContext';

interface UseDesignsOptions {
  page?: number;
  limit?: number;
  category?: string;
  searchQuery?: string;
}

export function useDesigns(options: UseDesignsOptions = {}) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [designs, setDesigns] = useState<Design[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(options.page || 1);

  const fetchDesigns = async (pageNum: number = 1, reset: boolean = false) => {
    // Don't fetch if not authenticated
    if (!isAuthenticated) {
      console.log('Not authenticated, skipping design fetch');
      setLoading(false);
      setRefreshing(false);
      return;
    }

    try {
      if (pageNum === 1) {
        setLoading(true);
      }
      setError(null);

      console.log('Fetching designs, authenticated:', isAuthenticated);

      let response: DesignsResponse;
      
      if (options.searchQuery) {
        response = await galleryApi.searchDesigns(
          options.searchQuery,
          options.category
        );
      } else {
        response = await galleryApi.getDesigns(pageNum, options.limit || 20);
      }

      if (reset || pageNum === 1) {
        setDesigns(response.designs);
      } else {
        setDesigns(prev => [...prev, ...response.designs]);
      }

      setHasMore(response.designs.length === (options.limit || 20));
      setPage(pageNum);

    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load designs');
      console.error('Error fetching designs:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const refresh = () => {
    setRefreshing(true);
    fetchDesigns(1, true);
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchDesigns(page + 1, false);
    }
  };

  useEffect(() => {
    // Only fetch when auth is resolved and user is authenticated
    if (!authLoading && isAuthenticated) {
      fetchDesigns(1, true);
    } else if (!authLoading && !isAuthenticated) {
      // Reset state when not authenticated
      setDesigns([]);
      setLoading(false);
      setError(null);
    }
  }, [options.searchQuery, options.category, isAuthenticated, authLoading]);

  return {
    designs,
    loading,
    refreshing,
    error,
    hasMore,
    refresh,
    loadMore,
  };
} 