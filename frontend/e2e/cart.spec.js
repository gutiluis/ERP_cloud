// file: cart.spec.js
// descr: testing isolation, hooks


import { test, expect } from '@playwright/test';


// test.describe is a hook to declare a group of tests
test.describe('Product catalog', () => {
    // page belongs to an isolated browsercontext, creted for this specific test
    test('displays the product catalog', async ({ page }) => {
        // navigate to a url. and afterwards interact with page elements
        await page.goto('/');
        // expect a title to contain a substring
        // wait until the page gets the title containing "ERP"
        // await expect(page).toHaveTitle(/ERP/);
        // enable auto-waiting and retry-ability with locators
        // locator returns an element that can be used to perform actions on the page/frame
        // ensures locator points to an attached and visible DOM node
        await expect(page.locator('body')).toBeVisible();
    });
});


test.describe('Product catalog', () => {
    test('displays products and navigates to the cart', async ({ page }) => {
        await page.goto('/');

        await expect(
            page.getByRole('heading', { name: 'Products' })
        ).toBeVisible();

        console.log(await page.locator('body').innerText());

    });
});

