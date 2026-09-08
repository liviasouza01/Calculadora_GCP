export const money = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

export const moneyShort = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

export function signedMoney(value: number): string {
  const formatted = money.format(Math.abs(value));
  if (value > 0.005) {
    return `+${formatted}`;
  }
  if (value < -0.005) {
    return `−${formatted}`;
  }
  return money.format(0);
}
