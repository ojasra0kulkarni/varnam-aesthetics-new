// Cart functionality using localStorage
const cart = JSON.parse(localStorage.getItem('varnam_cart')) || [];

function updateCartCount() {
    const counts = document.querySelectorAll('.cart-count');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    counts.forEach(c => {
        c.textContent = totalItems;
        if (totalItems > 0) {
            c.style.display = 'inline-block';
        } else {
            c.style.display = 'none';
        }
    });
}

function addToCart(productId, productName, price, imageUrl) {
    const existingIndex = cart.findIndex(item => String(item.id) === String(productId));
    if (existingIndex > -1) {
        cart[existingIndex].quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: price,
            image: imageUrl,
            quantity: 1
        });
    }
    localStorage.setItem('varnam_cart', JSON.stringify(cart));
    updateCartCount();

    // Simple visual feedback
    const btn = document.querySelector(`.add-to-cart-btn[data-id="${productId}"]`);
    if (btn) {
        const originalText = btn.textContent;
        btn.textContent = 'Added ✓';
        btn.style.backgroundColor = '#4caf50';
        btn.style.borderColor = '#4caf50';
        btn.style.color = 'white';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.backgroundColor = '';
            btn.style.borderColor = '';
            btn.style.color = '';
        }, 1500);
    }
}

function removeFromCart(productId) {
    const index = cart.findIndex(item => String(item.id) === String(productId));
    if (index > -1) {
        cart.splice(index, 1);
        localStorage.setItem('varnam_cart', JSON.stringify(cart));
        updateCartCount();
        renderCartUI();
    }
}

function updateQuantity(productId, newQty) {
    const index = cart.findIndex(item => String(item.id) === String(productId));
    if (index > -1) {
        newQty = parseInt(newQty);
        if (newQty > 0) {
            cart[index].quantity = newQty;
            localStorage.setItem('varnam_cart', JSON.stringify(cart));
            updateCartCount();
            renderCartUI();
        } else {
            removeFromCart(productId);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();

    // Bind "Add to Cart" buttons
    const addBtns = document.querySelectorAll('.add-to-cart-btn');
    addBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            const price = parseFloat(btn.dataset.price);
            const image = btn.dataset.image;
            addToCart(id, name, price, image);
        });
    });
});
