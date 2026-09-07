// file: ProductCard.jsx
// descr: extract product rendering into reusable ProductCard react component and tailwind CSS after functionality and tests. react controls what gets rendered and tailwind utility classes how it looks. React components file

// 1 react component. component count is based in react component definitions, not the number of jsx elements
function ProductCard({ product }) {
    return (
        // jsx elements
        // tailwind CSS classes
        <article className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                    {product.product_name}
                </h2>

                <p className="mt-1 text-sm text-gray-500">
                    {product.category}
                </p>
                <p className="mt-1 text-sm text-gray-500">
                    {product.brand}
                </p>
            </div>

            <p className="mb-5 text-gray-700">
                {product.description}
            </p>

            <div className="space-y-3">
                {product.variants.map((variant) => (
                    <div
                        key={variant.sku}
                        className="rounded-md bg-gray-50 p-4"
                    >
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-500">
                                SKU: {variant.sku}
                            </span>

                            <span className="font-semibold text-gray-900">
                                Price: ${variant.price}
                            </span>
                        </div>

                        {(variant.color || variant.size) && (
                            <div className="mt-2 text-sm text-gray-600">
                                {variant.color && (
                                    <span>Color: {variant.color}</span>
                                )}

                                {variant.color && variant.size && (
                                    <span className="mx-1">.</span>
                                )}

                                {variant.size && (
                                    <span>Size: {variant.size}</span>
                                )}
                            </div>
                        )}

                        <p
                            className={`mt-2 text-sm font-medium ${variant.is_in_stock
                                ? 'text-green-700'
                                : 'text-red-700'
                                }`}
                        >
                            {variant.is_in_stock
                                ? 'In stock'
                                : 'Out of stock'}
                        </p>
                    </div>
                ))}
            </div>
        </article>
    )
}

export default ProductCard
