from django.shortcuts import render


def index(request):
    return render(request, "home/index.html")


def error_404(request, exception):
    # Render your custom template; you can pass anything your base needs
    ctx = {"path": request.path}
    return render(request, "404.html", ctx, status=404)
