from django.shortcuts import render, redirect
from .models import Review
from .forms import ReviewForm


def reviews_list(request):
    reviews = Review.objects.filter(status="approved")
    return render(request, "reviews/list.html", {"reviews": reviews})


def create_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("reviews_list")
    else:
        form = ReviewForm()

    return render(request, "reviews/create.html", {"form": form})
