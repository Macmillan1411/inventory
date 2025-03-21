import csv
import os


class Product:
    # File where products will be stored
    PRODUCTS_FILE = "products.csv"

    # Available product categories
    CATEGORIES = ["Electronics", "Clothing", "Food", "Books", "Other"]

    def __init__(self, data):
        self._data = data
        # Set default category if none exists
        if "category" not in self._data:
            self._data["category"] = "Other"

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'Product' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def get_value(self) -> float:
        """Calculate the total value of this product (price × quantity)"""
        return float(self.price) * int(self.quantity)

    @classmethod
    def get_all(cls):
        """Get all products from the CSV file"""
        products = []

        # Create the file if it doesn't exist
        if not os.path.exists(cls.PRODUCTS_FILE):
            with open(cls.PRODUCTS_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "name", "quantity", "price", "category"])
            return products

        # Read all products from the file
        with open(cls.PRODUCTS_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(cls(row))

        return products

    @classmethod
    def get_by_id(cls, id):
        """Get a product by ID"""
        for product in cls.get_all():
            if product.id == str(id):
                return product
        return None

    @classmethod
    def get_by_category(cls, category):
        """Get all products in a category"""
        return [p for p in cls.get_all() if p.category == category]

    @classmethod
    def get_categories(cls):
        """Get list of all categories that have products"""
        products = cls.get_all()
        if not products:
            return []

        # Get unique categories from products
        categories = set(p.category for p in products)
        # Sort categories (put "Other" last)
        sorted_categories = sorted([c for c in categories if c != "Other"])
        if "Other" in categories:
            sorted_categories.append("Other")

        return sorted_categories

    @classmethod
    def save_all(cls, products):
        """Save all products to the CSV file"""
        with open(cls.PRODUCTS_FILE, "w", newline="") as f:
            if not products:
                writer = csv.writer(f)
                writer.writerow(["id", "name", "quantity", "price", "category"])
                return

            writer = csv.DictWriter(f, fieldnames=products[0]._data.keys())
            writer.writeheader()
            for product in products:
                writer.writerow(product._data)

    @classmethod
    def add(cls, name, quantity, price, category):
        """Add a new product"""
        products = cls.get_all()

        # Find the highest ID and add 1, or start with 1 if no products
        next_id = 1
        if products:
            next_id = max(int(p.id) for p in products) + 1

        # Validate category
        if not category or category not in cls.CATEGORIES:
            category = "Other"

        # Create new product
        new_product = cls(
            {
                "id": str(next_id),
                "name": name,
                "quantity": str(quantity),
                "price": str(price),
                "category": category,
            }
        )

        # Add to list and save
        products.append(new_product)
        cls.save_all(products)

        return new_product

    def update(self, name, quantity, price, category):
        """Update this product"""
        self._data["name"] = name
        self._data["quantity"] = str(quantity)
        self._data["price"] = str(price)

        # Validate category
        if not category or category not in Product.CATEGORIES:
            category = "Other"
        self._data["category"] = category

        # Get all products, update this one, and save all
        products = Product.get_all()
        for i, product in enumerate(products):
            if product.id == self.id:
                products[i] = self
                break

        Product.save_all(products)

    def delete(self):
        """Delete this product"""
        products = Product.get_all()
        products = [p for p in products if p.id != self.id]
        Product.save_all(products)
