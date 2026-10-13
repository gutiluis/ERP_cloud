// file: checkout.spec.js
// descr: successfull payment


import { test, expect } from "@playwright/test";

test("completes a Stripe test payment", async ({ page }) => {
    test.setTimeout(90000);

    await page.goto("/");

    const product = page.locator("article").filter({
        hasText: "cart-test-product",
    });

    await expect(product).toBeVisible();

    await product.getByRole("button", { name: "Add to cart" }).click();
    await page.getByRole("link", { name: "View cart" }).click();

    await expect(
        page.getByRole("heading", { name: /cart/i }),
    ).toBeVisible();

    await page.locator("#shipping-address-1").fill("123 Test Street");
    await page.locator("#shipping-country").fill("MX");
    await page.locator("#shipping-state").fill("Jalisco");
    await page.locator("#shipping-city").fill("Guadalajara");
    await page.locator("#shipping-zip-code").fill("45000");

    const stripeNavigation = page.waitForURL(/checkout\.stripe\.com/, {
        timeout: 30000,
    });

    await page.getByRole("button", { name: "Checkout" }).click();
    await stripeNavigation;

    await expect(page.locator('input[name="email"]')).toBeVisible({
        timeout: 15000,
    });

    await page.locator('input[name="email"]').fill("customer@example.com");

    await page
        .locator('input[aria-label="Card number"]')
        .fill("4242424242424242");

    await page.locator('input[aria-label="Expiration"]').fill("1230");

    await page
        .locator('input[aria-label="Credit or debit card CVC/CVV"]')
        .fill("123");

    await page.locator("#billingName").fill("E2E Test Customer");
    await page.locator("#billingCountry").selectOption("MX");

    const successNavigation = page.waitForURL(
        /\/checkout\/success(?:\?.*)?$/,
        {
            timeout: 45000,
            waitUntil: "commit",
        },
    );

    await page.getByRole("button", { name: /pay/i }).click();

    try {
        await successNavigation;
    } catch (error) {
        console.log("URL after payment:", page.url());
        console.log("Page title:", await page.title());

        console.log(
            "Visible text:",
            (await page.locator("body").innerText()).slice(0, 3000),
        );

        throw error;
    }

    await expect(
        page.getByRole("heading", { name: "Checkout Successful" }),
    ).toBeVisible({ timeout: 15000 });

    await expect(
        page.getByText(
            "Your payment was successful. Thank you for your order.",
        ),
    ).toBeVisible({ timeout: 15000 });
});
