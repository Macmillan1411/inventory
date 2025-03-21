from flask import render_template, request, redirect, flash, url_for, make_response
from app import app, db
from app.models import Product, User
from flask_login import login_user, logout_user, login_required, current_user
from fpdf import FPDF
import io


@app.route("/")
@login_required
def index():
    # Get all products and sort them
    sort = request.args.get("sort", "name")
    category = request.args.get("category", "")

    # Get products, filtered by category if needed
    if category:
        products = Product.get_by_category(category)
    else:
        products = Product.get_all()

    # Sort products
    if sort == "price":
        products.sort(key=lambda p: float(p.price))
    elif sort == "quantity":
        products.sort(key=lambda p: int(p.quantity))
    else:  # Default to name
        products.sort(key=lambda p: p.name)

    total_value = sum(p.get_value() for p in products)

    categories = Product.get_categories()

    return render_template(
        "index.html",
        products=products,
        total_value=round(total_value, 2),
        sort=sort,
        category=category,
        categories=categories,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        category = request.form.get("category", "Other")

        Product.add(name, quantity, price, category)
        flash("Product added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html", categories=Product.CATEGORIES)


@app.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
    product = Product.get_by_id(id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        category = request.form.get("category", "Other")

        product.update(name, quantity, price, category)
        flash("Product updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", product=product, categories=Product.CATEGORIES)


@app.route("/delete/<id>", methods=["POST"])
@login_required
def delete_product(id):
    product = Product.get_by_id(id)

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("index"))

    product.delete()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("index"))


@app.route("/search")
@login_required
def search():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    products = []

    if query:
        # Filter by category first if category is specified
        if category:
            category_products = Product.get_by_category(category)
        else:
            category_products = Product.get_all()

        products = [p for p in category_products if query.lower() in p.name.lower()]

    categories = Product.get_categories()

    return render_template(
        "search.html",
        products=products,
        query=query,
        category=category,
        categories=categories,
    )


@app.route("/export-pdf")
@app.route("/export-pdf/<category>")
@login_required
def export_pdf(category=None):
    # Get products, filtered by category if needed
    if category:
        products = Product.get_by_category(category)
        pdf_title = f"Products in {category} Category"
    else:
        products = Product.get_all()
        pdf_title = "All Products"

    # Sort products by name
    products.sort(key=lambda p: p.name)

    # Create PDF document with explicit encoding
    pdf = FPDF()
    pdf.add_page()

    # Set title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, pdf_title, 0, 1, "C")
    pdf.ln(5)

    # Add date
    pdf.set_font("Arial", "I", 10)
    from datetime import datetime

    pdf.cell(
        0,
        10,
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        0,
        1,
        "R",
    )
    pdf.ln(5)

    # Create table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(70, 10, "Product", 1, 0, "C")
    pdf.cell(30, 10, "Category", 1, 0, "C")
    pdf.cell(30, 10, "Quantity", 1, 0, "C")
    pdf.cell(30, 10, "Price ($)", 1, 0, "C")
    pdf.cell(30, 10, "Value ($)", 1, 1, "C")

    pdf.set_font("Arial", "", 11)
    total_value = 0

    for product in products:
        value = product.get_value()
        total_value += value

        product_name = product.name[:50]

        pdf.cell(70, 10, product_name, 1, 0, "L")
        pdf.cell(30, 10, product.category, 1, 0, "C")
        pdf.cell(30, 10, str(product.quantity), 1, 0, "R")
        pdf.cell(30, 10, f"{float(product.price):.2f}", 1, 0, "R")
        pdf.cell(30, 10, f"{value:.2f}", 1, 1, "R")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(160, 10, "Total Value:", 1, 0, "R")
    pdf.cell(30, 10, f"${total_value:.2f}", 1, 1, "R")

    if not products:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "No products found in this category", 0, 1, "C")

    pdf_binary = pdf.output(dest="S").encode("latin-1")

    response = make_response(pdf_binary)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'attachment; filename=inventory_{category or "all"}.pdf'
    )

    return response


# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.get_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not username or not password:
            flash("Username and password are required", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        existing_user = User.get_by_username(username)
        if existing_user:
            flash("Username already exists", "danger")
            return render_template("register.html")

        user = User.register(username, password)
        if user:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        flash("Registration failed", "danger")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("login"))


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)
