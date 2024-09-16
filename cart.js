document.addEventListener('DOMContentLoaded', () => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalContainer = document.getElementById('cart-total');

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p>Your cart is empty!</p>';
        return;
    }

    let total = 0;
    cart.forEach(item => {
        const productElement = document.createElement('div');
        productElement.className = 'cart-item';
        productElement.innerHTML = `
            <p>Product ID: ${item.id}</p>
            <p>Quantity: ${item.quantity}</p>
        `;
        cartItemsContainer.appendChild(productElement);

        // Assuming you have a function getProductPrice that takes a product ID and returns its price
        const price = getProductPrice(item.id);
        total += price * item.quantity;
    });

    const totalElement = document.createElement('div');
    totalElement.className = 'cart-total';
    totalElement.innerHTML = `<p>Total: $${total.toFixed(2)}</p>`;
    cartTotalContainer.appendChild(totalElement);
});

function getProductPrice(productId) {
    // This function should return the price of the product based on its ID
    // For simplicity, we'll assume a fixed price for demonstration purposes
    return 10.00; // Replace with actual price fetching logic
}

function goToCheckout() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    if (cart.length === 0) {
        alert('Your cart is empty!');
        return;
    }
    // Redirect to checkout page
    window.location.href = "{{ url_for('checkout') }}";
}
