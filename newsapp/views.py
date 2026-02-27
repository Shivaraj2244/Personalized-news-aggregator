from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserPreference
import requests
import random


# -------------------- HOME --------------------
@login_required
def home(request):
    query = request.GET.get("q", "").strip().lower()
    selected_category = request.GET.get("category")

    # Get user's saved preferences
    pref = UserPreference.objects.filter(user=request.user).first()
    user_categories = pref.get_categories_list() if pref else []

    # Case 1: No preferences → show random mixed categories
    if not user_categories:
        default_categories = ["technology", "sports", "business", "entertainment", "science", "health"]
        # Keep same random 3 for this session
        if "temp_categories" not in request.session:
            request.session["temp_categories"] = random.sample(default_categories, 3)
        user_categories = request.session["temp_categories"]

    # Case 2: User clicked a category manually
    if selected_category:
        user_categories = [selected_category]

    # Fetch news for each category
    news_list = []
    for category in user_categories:
        try:
            response = requests.get(f"http://127.0.0.1:5000/news?category={category}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                news_list.extend(data.get("data", []))
        except Exception as e:
            print(f"⚠️ Error fetching {category} news:", e)

    # Search filter
    if query:
        news_list = [
            n for n in news_list
            if query in n.get("title", "").lower() or query in n.get("content", "").lower()
        ]

    return render(request, "newsapp/home.html", {
        "news": news_list,
        "categories": user_categories,
        "query": query,
    })


# -------------------- REGISTER --------------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("/register/")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("/register/")

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Registration successful! Please login.")
        return redirect("/login/")

    return render(request, "newsapp/register.html")


# -------------------- LOGIN --------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("/login/")

    return render(request, "newsapp/login.html")


# -------------------- LOGOUT --------------------
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("/login/")


# -------------------- PREFERENCES --------------------
@login_required
def preferences(request):
    categories = ["technology", "sports", "business", "entertainment", "science", "health"]

    pref, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == "POST":
        selected = request.POST.getlist("categories")  # multiple selected values
        pref.categories = ",".join(selected)
        pref.save()
        messages.success(request, f"Preferences updated: {', '.join(selected).title()}")
        return redirect("/")

    current_categories = pref.get_categories_list()

    return render(request, "newsapp/preferences.html", {
        "current_categories": current_categories,
        "categories": categories
    })
