"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

export type DemoState = "completed" | "empty" | "loading" | "error";

interface StateContextType {
  demoState: DemoState;
  setDemoState: (state: DemoState) => void;
}

const StateContext = createContext<StateContextType | undefined>(undefined);

export function StateProvider({ children }: { children: ReactNode }) {
  const [demoState, setDemoState] = useState<DemoState>("completed");

  return (
    <StateContext.Provider value={{ demoState, setDemoState }}>
      {children}
    </StateContext.Provider>
  );
}

export function useDemoState(): StateContextType {
  const context = useContext(StateContext);
  if (!context) {
    throw new Error("useDemoState must be used within a StateProvider");
  }
  return context;
}
