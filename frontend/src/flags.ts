export interface AppFlags {
  shareCalculator: boolean;
  clientCalculatorOnly: boolean;
}

export const DEFAULT_FLAGS: AppFlags = {
  shareCalculator: true,
  clientCalculatorOnly: false,
};
