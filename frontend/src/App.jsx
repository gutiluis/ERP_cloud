// file: App.jsx
// descr: render public product catalog page. which calls the ProductCatalog api call

import ProductCatalog from './pages/public/ProductCatalog'
import CartPage from './pages/public/CartPage'


function App() {
    if (window.location.pathname === '/cart') {
        return <CartPage />
    }
    return <ProductCatalog />
}

export default App
