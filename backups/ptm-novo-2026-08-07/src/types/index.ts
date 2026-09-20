export type QuizAnswer = {
  objective: "weight_loss" | "performance" | "longevity" | "sleep_hormones";
  previousAttempts: "first_time" | "no_results" | "no_followup" | "ready_to_start";
  medicalConditions: "none" | "diabetes" | "hypertension" | "other";
  age: "18-30" | "31-45" | "46-60" | "60+";
  startDate: "asap" | "two_weeks" | "comparing" | "info_only";
};

export type QuizResult = {
  program: "WEIGHT_LOSS" | "LONGEVITY" | "PERFORMANCE";
  answers: QuizAnswer;
};

export type ConsultationRoom = {
  roomUrl: string;
  token: string;
};
