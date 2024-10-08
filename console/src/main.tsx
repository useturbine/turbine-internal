import React from "react";
import ReactDOM from "react-dom/client";
import "./main.css";
import { ClerkProvider } from "@clerk/clerk-react";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import { QueryClientProvider } from "react-query";
import { queryClient } from "./queries";
import { clerkPubKey } from "./config";
import { NextUIProvider } from "@nextui-org/react";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ClerkProvider
        publishableKey={clerkPubKey}
        signInUrl="/sign-in"
        signUpUrl="/sign-up"
      >
        <NextUIProvider>
          <RouterProvider router={router} />
        </NextUIProvider>
      </ClerkProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
