import { expect, test } from '@playwright/test'


test('completes a Stripe test payment', async ({ page }) => {
    test.setTimeout(60000)
    await page.goto('/')

    await expect(
        page.getByRole('heading', { name: 'Products' })
    ).toBeVisible()

    const product = page.locator('article').filter({
        hasText: 'cart-test-product',
    })

    await expect(product).toBeVisible()

    await product.getByRole('button', { name: 'Add to cart' }).click()

    await page.getByRole('link', { name: 'View cart' }).click()

    await expect(
        page.getByRole('heading', { name: /cart/i })
    ).toBeVisible()

    console.log('CHECKOUT URL:', page.url());
    console.log(
        'CHECKOUT BODY:',
        await page.locator('body').innerText(),
    );

    await page.locator('#shipping-address-1').fill('123 Test Street')
    await page.locator('#shipping-country').fill('MX')
    await page.locator('#shipping-state').fill('Jalisco')
    await page.locator('#shipping-city').fill('Guadalajara')
    await page.locator('#shipping-zip-code').fill('45000')

    await page.getByRole('button', { name: 'Checkout' }).click()



    await expect(page).toHaveURL(/checkout\.stripe\.com/, {
        timeout: 15000,
    })


    await page.locator('input[name="email"]').fill('e2e@example.test')
    await page.locator(
        'input[aria-label="Card number"]'
    ).fill('4242424242424242')
    await page.locator(
        'input[aria-label="Expiration"]'
    ).fill('1234')
    await page.locator(
        'input[aria-label="Credit or debit card CVC/CVV"]'
    ).fill('123')
    await page.locator('#billingName').fill('E2E Test Customer')
    // pay
    const payButton = page.getByRole('button', { name: /Pay/ })

    await expect(payButton).toBeVisible()
    await expect(payButton).toBeEnabled()


    await payButton.click()

    try {
        await expect(page).toHaveURL(/\/checkout\/success/, {
            timeout: 30000,
        })
    } finally {
        console.log('URL after payment:', page.url())
        console.log('Page text:', await page.locator('body').innerText())
    }

})
