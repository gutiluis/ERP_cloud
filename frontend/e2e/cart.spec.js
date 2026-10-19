// file: cart.spec.js
// descr: testing isolation, hooks

import { test, expect } from "@playwright/test";

test.describe("Product catalog", () => {
  test("displays the product catalog", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Products" })).toBeVisible();

    await expect(page.getByText("cart-test-product")).toBeVisible();
  });

test("displays products and navigates to the cart", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Products" })).toBeVisible();

    const product = page.locator("article").filter({
      hasText: "cart-test-product",
    });

    await expect(product).toBeVisible();

    await product.getByRole("button", { name: "Add to cart" }).click();
    await page.getByRole("link", { name: "View cart" }).click();

    await expect(page).toHaveURL(/\/cart(?:\?.*)?$/);

    await expect(page.getByRole("heading", { name: "Your cart", exact: true })).toBeVisible();

    await expect(page.getByText("cart-test-product")).toBeVisible();
  });
});
