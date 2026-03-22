"use client";

import { useQuery } from "@tanstack/react-query";
import { getNorthStar } from "@/lib/services/analytics-service";

export function useNorthStarQuery() {
  return useQuery({
    queryKey: ["analytics", "north-star"],
    queryFn: getNorthStar,
  });
}
