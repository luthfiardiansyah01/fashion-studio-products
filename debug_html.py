"""
Script untuk debug HTML structure dari website Fashion Studio
"""

import requests
from bs4 import BeautifulSoup

URL = "https://fashion-studio.dicoding.dev/"

def debug_website():
    print("=" * 60)
    print("DEBUGGING WEBSITE STRUCTURE")
    print("=" * 60)
    
    try:
        # Fetch halaman pertama
        print(f"\n1. Fetching: {URL}")
        response = requests.get(URL, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Simpan HTML ke file untuk inspeksi manual
        with open("debug_output.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"   HTML saved to: debug_output.html")
        
        # Cari semua kemungkinan struktur produk
        print("\n2. Searching for product containers...")
        
        # Coba berbagai kemungkinan class names
        possible_classes = [
            'product-card', 'product_card', 'productCard',
            'card', 'item', 'product', 'product-item',
            'product-item', 'listing-item', 'catalog-item',
            'fashion-item', 'clothing-item'
        ]
        
        for class_name in possible_classes:
            elements = soup.find_all(class_=class_name)
            if elements:
                print(f"   ✅ Found {len(elements)} elements with class '{class_name}'")
                print(f"      First element HTML (truncated):")
                print(f"      {str(elements[0])[:500]}...")
                print()
        
        # Cari semua div dan lihat pattern-nya
        print("\n3. Analyzing all div classes in the page...")
        all_classes = set()
        for div in soup.find_all('div'):
            if div.get('class'):
                for cls in div['class']:
                    all_classes.add(cls)
        
        print(f"   Total unique classes found: {len(all_classes)}")
        print(f"   Classes containing 'product': {[c for c in all_classes if 'product' in c.lower()]}")
        print(f"   Classes containing 'card': {[c for c in all_classes if 'card' in c.lower()]}")
        print(f"   Classes containing 'item': {[c for c in all_classes if 'item' in c.lower()]}")
        print(f"   Classes containing 'fashion': {[c for c in all_classes if 'fashion' in c.lower()]}")
        
        # Cari semua tag yang mungkin berisi produk
        print("\n4. Searching for common product-related tags...")
        
        # Cari semua h1, h2, h3, h4 yang mungkin berisi judul produk
        for tag in ['h1', 'h2', 'h3', 'h4']:
            elements = soup.find_all(tag)
            if elements:
                print(f"   <{tag}> tags found: {len(elements)}")
                for elem in elements[:5]:  # Show first 5
                    text = elem.get_text(strip=True)[:100]
                    if text:
                        print(f"      - {text}")
        
        # Cari semua elemen dengan teks yang mengandung '$' (harga)
        print("\n5. Searching for price elements (containing '$')...")
        all_text = soup.find_all(string=lambda text: text and '$' in text)
        print(f"   Found {len(all_text)} elements with '$'")
        for text in all_text[:10]:
            parent = text.parent
            print(f"      - Text: '{text.strip()[:50]}' | Parent tag: {parent.name} | Parent class: {parent.get('class')}")
        
        # Cari elemen dengan teks yang mengandung 'Rating'
        print("\n6. Searching for rating elements...")
        rating_elements = soup.find_all(string=lambda text: text and 'Rating' in str(text))
        print(f"   Found {len(rating_elements)} elements with 'Rating'")
        for text in rating_elements[:5]:
            parent = text.parent
            print(f"      - Text: '{text.strip()[:50]}' | Parent tag: {parent.name} | Parent class: {parent.get('class')}")
        
        # Cari elemen dengan teks yang mengandung 'Colors' atau 'Color'
        print("\n7. Searching for color elements...")
        color_elements = soup.find_all(string=lambda text: text and 'Color' in str(text))
        print(f"   Found {len(color_elements)} elements with 'Color'")
        for text in color_elements[:5]:
            parent = text.parent
            print(f"      - Text: '{text.strip()[:50]}' | Parent tag: {parent.name} | Parent class: {parent.get('class')}")
        
        # Cari elemen dengan teks yang mengandung 'Size'
        print("\n8. Searching for size elements...")
        size_elements = soup.find_all(string=lambda text: text and 'Size' in str(text))
        print(f"   Found {len(size_elements)} elements with 'Size'")
        for text in size_elements[:5]:
            parent = text.parent
            print(f"      - Text: '{text.strip()[:50]}' | Parent tag: {parent.name} | Parent class: {parent.get('class')}")
        
        # Cari elemen dengan teks yang mengandung 'Gender'
        print("\n9. Searching for gender elements...")
        gender_elements = soup.find_all(string=lambda text: text and 'Gender' in str(text))
        print(f"   Found {len(gender_elements)} elements with 'Gender'")
        for text in gender_elements[:5]:
            parent = text.parent
            print(f"      - Text: '{text.strip()[:50]}' | Parent tag: {parent.name} | Parent class: {parent.get('class')}")
        
        # Analisis struktur parent dari harga
        print("\n10. Analyzing parent structure of price elements...")
        if all_text:
            first_price_parent = all_text[0].parent
            print(f"    First price parent: <{first_price_parent.name} class='{first_price_parent.get('class')}'>")
            
            # Naik 3 level untuk lihat container
            current = first_price_parent
            for i in range(4):
                if current.parent:
                    current = current.parent
                    print(f"    Level {i+1} parent: <{current.name} class='{current.get('class')}'>")
        
        print("\n" + "=" * 60)
        print("DEBUG COMPLETE!")
        print("Check debug_output.html for full HTML structure")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    debug_website()