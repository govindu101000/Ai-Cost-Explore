export const createSocket = (analysisId: string) => {
  return new WebSocket(
    `ws://localhost:8000/ws/progress/${analysisId}`
  );
};