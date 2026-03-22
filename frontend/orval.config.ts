import { defineConfig } from "orval";

export default defineConfig({
  ideanance: {
    input: {
      target: "http://localhost:8000/openapi.json",
    },
    output: {
      target: "./src/lib/api/generated.ts",
      client: "react-query",
      mode: "tags-split",
      override: {
        query: {
          useQuery: true,
          useMutation: true,
        },
      },
    },
  },
});
