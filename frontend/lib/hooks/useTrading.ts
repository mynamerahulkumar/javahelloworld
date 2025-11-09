/**
 * React Query hooks for trading API
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { placeLimitOrderWait } from "../api/trading";
import { PlaceLimitOrderWaitRequest, OrderResponse, ApiError } from "../types";
import { useAuthStore } from "@/store/auth";
import { useCredentialsStore } from "@/store/credentials";

export function usePlaceLimitOrderWait() {
  const queryClient = useQueryClient();
  const { srpClientId, srpClientEmail } = useAuthStore();
  const credentials = useCredentialsStore((state) => state.credentials);
  const deltaApiKey = credentials?.deltaApiKey;
  const deltaApiSecret = credentials?.deltaApiSecret;
  const deltaBaseUrl = credentials?.deltaBaseUrl;

  return useMutation<OrderResponse, ApiError, PlaceLimitOrderWaitRequest>({
    mutationFn: (data) =>
      placeLimitOrderWait(data, {
        srpClientId: srpClientId || undefined,
        srpClientEmail: srpClientEmail || undefined,
        deltaApiKey: deltaApiKey || undefined,
        deltaApiSecret: deltaApiSecret || undefined,
        deltaBaseUrl: deltaBaseUrl || undefined,
      }),
    onSuccess: () => {
      // Invalidate relevant queries on success
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
  });
}

