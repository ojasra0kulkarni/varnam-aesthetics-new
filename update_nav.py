import os
import glob

files = glob.glob('public/*.html') + glob.glob('templates/*.html')
files = list(set(files))

mobile_cart_html_template = """<div class="mobile-cart-container" style="display: flex; align-items: center; margin-left: auto; gap: 15px; margin-right: 15px;">
                <a href="{cart_href}" class="cart-icon" style="font-size: 1.3rem; color: var(--color-maroon); position: relative; text-decoration: none;">
                    🛒<span class="cart-count" style="display: none; position: absolute; top: -8px; right: -10px; background-color: var(--color-gold); color: white; font-size: 0.75rem; padding: 2px 6px; border-radius: 50%; font-weight: bold;">0</span>
                </a>
            </div>
            <button class="nav-toggle\""""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    if '<button class="nav-toggle"' in content and 'mobile-cart-container' not in content:
        # Determine cart URL
        is_template = "{% extends" in content or "{{ url_for" in content
        cart_href = "{{ url_for('main.cart') }}" if is_template else "cart.html"
        
        replacement = mobile_cart_html_template.format(cart_href=cart_href)
        
        # Hide the desktop cart's list item on mobile
        content = content.replace('<li>\n                    <a href="cart.html" class="cart-icon">', '<li class="desktop-cart-item">\n                    <a href="cart.html" class="cart-icon">')
        content = content.replace('<li>\n                    <a href="{{ url_for(\'main.cart\') }}" class="cart-icon">', '<li class="desktop-cart-item">\n                    <a href="{{ url_for(\'main.cart\') }}" class="cart-icon">')
        
        # Inject mobile cart
        content = content.replace('<button class="nav-toggle"', replacement)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
