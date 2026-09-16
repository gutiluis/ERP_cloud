// file: App.jsx
// descr: render public product catalog page. which calls the ProductCatalog api call. configure router. App.jsx responsible for defining the routes. main.jsx is the main entry point


import { BrowserRouter, Route, Routes } from 'react-router-dom'

import CartPage from './pages/public/CartPage'
import CheckoutCancel from './pages/public/CheckoutCancel'
import CheckoutSuccess from './pages/public/CheckoutSuccess'
import ProductCatalog from './pages/public/ProductCatalog'


function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<ProductCatalog />} />
                <Route path="/cart" element={<CartPage />} />
                <Route path="/checkout/success" element={<CheckoutSuccess />} />
                <Route path="/checkout/cancel" element={<CheckoutCancel />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
