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
  dashboard: (date?: string) => fetchAPI(`/api/dashboard/${date ? `?date=${date}` : ""}`),
  budget: (date?: string) => fetchAPI(`/api/budget/${date ? `?date=${date}` : ""}`),
  budgetSummary: (date?: string) => fetchAPI(`/api/budget/summary${date ? `?date=${date}` : ""}`),
  addBudget: (data: any) => fetchAPI("/api/budget/", { method: "POST", body: JSON.stringify(data) }),
  deleteBudget: (id: number) => fetchAPI(`/api/budget/${id}`, { method: "DELETE" }),
  study: (date?: string) => fetchAPI(`/api/study/${date ? `?date=${date}` : ""}`),
  studySummary: (date?: string) => fetchAPI(`/api/study/summary${date ? `?date=${date}` : ""}`),
  addStudy: (data: any) => fetchAPI("/api/study/", { method: "POST", body: JSON.stringify(data) }),
  deleteStudy: (id: number) => fetchAPI(`/api/study/${id}`, { method: "DELETE" }),
  sleep: (date?: string) => fetchAPI(`/api/sleep/${date ? `?date=${date}` : ""}`),
  sleepSummary: (date?: string) => fetchAPI(`/api/sleep/summary${date ? `?date=${date}` : ""}`),
  addSleep: (data: any) => fetchAPI("/api/sleep/", { method: "POST", body: JSON.stringify(data) }),
  deleteSleep: (id: number) => fetchAPI(`/api/sleep/${id}`, { method: "DELETE" }),
  habits: (date?: string) => fetchAPI(`/api/habits/${date ? `?date=${date}` : ""}`),
  addHabit: (data: any) => fetchAPI("/api/habits/", { method: "POST", body: JSON.stringify(data) }),
  logHabit: (id: number, data: any) => fetchAPI(`/api/habits/${id}/log`, { method: "POST", body: JSON.stringify(data) }),
  deleteHabit: (id: number) => fetchAPI(`/api/habits/${id}`, { method: "DELETE" }),
  goals: () => fetchAPI("/api/goals/"),
  addGoal: (data: any) => fetchAPI("/api/goals/", { method: "POST", body: JSON.stringify(data) }),
  updateGoal: (id: number, data: any) => fetchAPI(`/api/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteGoal: (id: number) => fetchAPI(`/api/goals/${id}`, { method: "DELETE" }),
  income: () => fetchAPI("/api/income/"),
  incomeSummary: () => fetchAPI("/api/income/summary"),
  addIncome: (data: any) => fetchAPI("/api/income/", { method: "POST", body: JSON.stringify(data) }),
  deleteIncome: (id: number) => fetchAPI(`/api/income/${id}`, { method: "DELETE" }),
  social: () => fetchAPI("/api/social/"),
  addSocial: (data: any) => fetchAPI("/api/social/", { method: "POST", body: JSON.stringify(data) }),
  deleteSocial: (id: number) => fetchAPI(`/api/social/${id}`, { method: "DELETE" }),
  daily: (date?: string) => fetchAPI(`/api/daily/${date ? `?date=${date}` : ""}`),
  updateDaily: (data: any) => fetchAPI("/api/daily/", { method: "POST", body: JSON.stringify(data) }),
  modules: () => fetchAPI("/api/modules/"),
  addModule: (data: any) => fetchAPI("/api/modules/", { method: "POST", body: JSON.stringify(data) }),
  getModuleData: (key: string) => fetchAPI(`/api/modules/${key}/data`),
  addModuleData: (key: string, data: any) => fetchAPI(`/api/modules/${key}/data`, { method: "POST", body: JSON.stringify(data) }),
  tytScores: () => fetchAPI("/api/scores/tyt"),
  addTytScore: (data: any) => fetchAPI("/api/scores/tyt", { method: "POST", body: JSON.stringify(data) }),
  aytScores: () => fetchAPI("/api/scores/ayt"),
  addAytScore: (data: any) => fetchAPI("/api/scores/ayt", { method: "POST", body: JSON.stringify(data) }),
  deleteScore: (id: number) => fetchAPI(`/api/scores/${id}`, { method: "DELETE" }),
  chartSleep: () => fetchAPI("/api/charts/sleep"),
  chartStudy: () => fetchAPI("/api/charts/study"),
  settings: () => fetchAPI("/api/settings/"),
  updateSetting: (data: any) => fetchAPI("/api/settings/", { method: "POST", body: JSON.stringify(data) }),
  reminders: () => fetchAPI("/api/reminders/"),
  addReminder: (data: any) => fetchAPI("/api/reminders/", { method: "POST", body: JSON.stringify(data) }),
  deleteReminder: (id: number) => fetchAPI(`/api/reminders/${id}`, { method: "DELETE" }),
};
