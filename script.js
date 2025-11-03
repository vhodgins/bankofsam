let balance = 100;

document.getElementById("earn").addEventListener("click", () => {
  const bonus = Math.floor(Math.random() * 50) + 1;
  balance += bonus;
  document.getElementById("balance").textContent = `💵 ${balance} Sam Bucks`;
  alert(`You earned ${bonus} Sam Bucks!`);
});
