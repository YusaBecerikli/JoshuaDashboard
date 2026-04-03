const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${err}`);
  }
  return res.json();
}

function q(params: Record<string, string | undefined>) {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => { if (v) p.set(k, v); });
  const s = p.toString();
  return s ? `?${s}` : "";
}

function extractData(result: any) {
  if (result && result.data !== undefined) return result.data;
  return result;
}

export const api = {
  dashboard: (date?: string) => fetchAPI(`/api/dashboard${q({ date })}`),
  budget: (date?: string) => fetchAPI(`/api/budget${q({ date })}`).then(extractData),
  budgetSummary: (date?: string) => fetchAPI(`/api/budget/summary${q({ date })}`),
  addBudget: (data: any) => fetchAPI("/api/budget", { method: "POST", body: JSON.stringify(data) }),
  deleteBudget: (id: number) => fetchAPI(`/api/budget/${id}`, { method: "DELETE" }),
  study: (date?: string) => fetchAPI(`/api/study${q({ date })}`).then(extractData),
  studySummary: (date?: string) => fetchAPI(`/api/study/summary${q({ date })}`),
  addStudy: (data: any) => fetchAPI("/api/study", { method: "POST", body: JSON.stringify(data) }),
  deleteStudy: (id: number) => fetchAPI(`/api/study/${id}`, { method: "DELETE" }),
  sleep: (date?: string) => fetchAPI(`/api/sleep${q({ date })}`).then(extractData),
  sleepSummary: (date?: string) => fetchAPI(`/api/sleep/summary${q({ date })}`),
  addSleep: (data: any) => fetchAPI("/api/sleep", { method: "POST", body: JSON.stringify(data) }),
  deleteSleep: (id: number) => fetchAPI(`/api/sleep/${id}`, { method: "DELETE" }),
  habits: (date?: string) => fetchAPI(`/api/habits${q({ date })}`),
  addHabit: (data: any) => fetchAPI("/api/habits", { method: "POST", body: JSON.stringify(data) }),
  logHabit: (id: number, data: any) => fetchAPI(`/api/habits/${id}/log`, { method: "POST", body: JSON.stringify(data) }),
  deleteHabit: (id: number) => fetchAPI(`/api/habits/${id}`, { method: "DELETE" }),
  goals: () => fetchAPI("/api/goals").then(extractData),
  addGoal: (data: any) => fetchAPI("/api/goals", { method: "POST", body: JSON.stringify(data) }),
  updateGoal: (id: number, data: any) => fetchAPI(`/api/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteGoal: (id: number) => fetchAPI(`/api/goals/${id}`, { method: "DELETE" }),
  income: () => fetchAPI("/api/income").then(extractData),
  incomeSummary: () => fetchAPI("/api/income/summary"),
  addIncome: (data: any) => fetchAPI("/api/income", { method: "POST", body: JSON.stringify(data) }),
  deleteIncome: (id: number) => fetchAPI(`/api/income/${id}`, { method: "DELETE" }),
  social: () => fetchAPI("/api/social").then(extractData),
  addSocial: (data: any) => fetchAPI("/api/social", { method: "POST", body: JSON.stringify(data) }),
  deleteSocial: (id: number) => fetchAPI(`/api/social/${id}`, { method: "DELETE" }),
  daily: (date?: string) => fetchAPI(`/api/daily${q({ date })}`),
  updateDaily: (data: any) => fetchAPI("/api/daily", { method: "POST", body: JSON.stringify(data) }),
  modules: () => fetchAPI("/api/modules").then(extractData),
  addModule: (data: any) => fetchAPI("/api/modules", { method: "POST", body: JSON.stringify(data) }),
  getModuleData: (key: string) => fetchAPI(`/api/modules/${key}/data`).then(extractData),
  addModuleData: (key: string, data: any) => fetchAPI(`/api/modules/${key}/data`, { method: "POST", body: JSON.stringify(data) }),
  tytScores: () => fetchAPI("/api/scores/tyt").then(extractData),
  addTytScore: (data: any) => fetchAPI("/api/scores/tyt", { method: "POST", body: JSON.stringify(data) }),
  aytScores: () => fetchAPI("/api/scores/ayt").then(extractData),
  addAytScore: (data: any) => fetchAPI("/api/scores/ayt", { method: "POST", body: JSON.stringify(data) }),
  deleteScore: (id: number) => fetchAPI(`/api/scores/${id}`, { method: "DELETE" }),
  chartSleep: () => fetchAPI("/api/charts/sleep"),
  chartStudy: () => fetchAPI("/api/charts/study"),
  settings: () => fetchAPI("/api/settings"),
  updateSetting: (data: any) => fetchAPI("/api/settings", { method: "POST", body: JSON.stringify(data) }),
  modelsList: () => fetchAPI("/api/settings/models/list"),
  reminders: () => fetchAPI("/api/reminders").then(extractData),
  addReminder: (data: any) => fetchAPI("/api/reminders", { method: "POST", body: JSON.stringify(data) }),
  deleteReminder: (id: number) => fetchAPI(`/api/reminders/${id}`, { method: "DELETE" }),
  notes: () => fetchAPI("/api/notes").then(extractData),
  addNote: (data: any) => fetchAPI("/api/notes", { method: "POST", body: JSON.stringify(data) }),
  deleteNote: (id: number) => fetchAPI(`/api/notes/${id}`, { method: "DELETE" }),
  countdowns: () => fetchAPI("/api/countdowns").then(extractData),
  addCountdown: (data: any) => fetchAPI("/api/countdowns", { method: "POST", body: JSON.stringify(data) }),
  deleteCountdown: (id: number) => fetchAPI(`/api/countdowns/${id}`, { method: "DELETE" }),
};
