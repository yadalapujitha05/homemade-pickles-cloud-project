/**
 * HomeMade Pickles & Snacks – Main JavaScript
 * Client-side enhancements: cart counter, alerts, UX polish.
 */

// ===== AUTO-DISMISS FLASH ALERTS =====
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // ===== CART COUNT BADGE =====
  updateCartCount();
});


/**
 * Fetch cart item count from the server and update the navbar cart link.
 */
function updateCartCount() {
  fetch("/cart/count")
    .then((res) => res.json())
    .then((data) => {
      const cartLink = document.querySelector('a[href*="/cart/"]');
      if (cartLink && data.count > 0) {
        cartLink.textContent = `🛒 Cart (${data.count})`;
      }
    })
    .catch(() => {});  // Silently fail if user not logged in
}


/**
 * Confirm before cancelling subscriptions (also used inline via onclick="return confirm(...)").
 */
function confirmCancel(message) {
  return confirm(message || "Are you sure?");
}
