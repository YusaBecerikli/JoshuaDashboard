const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  dashboard: () => fetchAPI("/api/dashboard/"),
  budget: () => fetchAPI("/api/budget/"),
  budgetSummary: () => fetchAPI("/api/budget/summary"),
  addBudget: (data: any) => fetchAPI("/api/budget/", { method: "POST", body: JSON.stringify(data) }),
  study: () => fetchAPI("/api/study/"),
  studySummary: () => fetchAPI("/api/study/summary"),
  addStudy: (data: any) => fetchAPI("/api/study/", { method: "POST", body: JSON.stringify(data) }),
  sleep: () => fetchAPI("/api/sleep/"),
  sleepSummary: () => fetchAPI("/api/sleep/summary"),
  addSleep: (data: any) => fetchAPI("/api/sleep/", { method: "POST", body: JSON.stringify(data) }),
  habits: () => fetchAPI("/api/habits/"),
  addHabit: (data: any) => fetchAPI("/api/habits/", { method: "POST", body: JSON.stringify(data) }),
  logHabit: (id: number, data: any) => fetchAPI(`/api/habits/${id}/log`, { method: "POST", body: JSON.stringify(data) }),
  goals: () => fetchAPI("/api/goals/"),
  addGoal: (data: any) => fetchAPI("/api/goals/", { method: "POST", body: JSON.stringify(data) }),
  updateGoal: (id: number, data: any) => fetchAPI(`/api/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  income: () => fetchAPI("/api/income/"),
  incomeSummary: () => fetchAPI("/api/income/summary"),
  addIncome: (data: any) => fetchAPI("/api/income/", { method: "POST", body: JSON.stringify(data) }),
  social: () => fetchAPI("/api/social/"),
  addSocial: (data: any) => fetchAPI("/api/social/", { method: "POST", body: JSON.stringify(data) }),
  daily: () => fetchAPI("/api/daily/"),
  updateDaily: (data: any) => fetchAPI("/api/daily/", { method: "POST", body: JSON.stringify(data) }),
  modules: () => fetchAPI("/api/modules/"),
  addModule: (data: any) => fetchAPI("/api/modules/", { method: "POST", body: JSON.stringify(data) }),
  getModuleData: (key: string) => fetchAPI(`/api/modules/${key}/data`),
  addModuleData: (key: string, data: any) => fetchAPI(`/api/modules/${key}/data`, { method: "POST", body: JSON.stringify(data) }),
};
