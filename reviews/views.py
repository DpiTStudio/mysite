from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm


def reviews_list(request):
    reviews = Review.objects.filter(status="approved").order_by("-created_at")
    return render(request, "reviews/list.html", {"reviews": reviews})


def create_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save()
            messages.success(request, "Спасибо за ваш отзыв! Он будет опубликован после модерации.")
            return redirect("reviews:list")
    else:
        form = ReviewForm()

    return render(request, "reviews/create.html", {"form": form})
