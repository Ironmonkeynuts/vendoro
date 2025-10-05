from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView
from django.utils.http import url_has_allowed_host_and_scheme

User = get_user_model()


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views that only superusers should access."""
    login_url = "account_login"

    def test_func(self):
        return self.request.user.is_superuser


class DashboardView(SuperuserRequiredMixin, TemplateView):
    """Admin dashboard home page."""
    template_name = "admintools/index.html"


class UserListView(SuperuserRequiredMixin, ListView):
    """List of users with search and sort functionality."""
    template_name = "admintools/users.html"
    model = User
    paginate_by = 25
    ordering = "-date_joined"

    SORT_MAP = {
        "username": "username",
        "-username": "-username",
        "email": "email",
        "-email": "-email",
        "date_joined": "date_joined",
        "-date_joined": "-date_joined",
        "is_staff": "is_staff",
        "-is_staff": "-is_staff",
        "is_active": "is_active",
        "-is_active": "-is_active",
        "id": "id",
        "-id": "-id",
    }

    def get_queryset(self):
        """Allow searching and sorting."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        sort = (self.request.GET.get("sort") or "").strip()
        order_by = self.SORT_MAP.get(sort, self.ordering)
        return qs.order_by(order_by)

    def get_context_data(self, **kwargs):
        """Add search and sort parameters to context."""
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["sort"] = (self.request.GET.get("sort") or "").strip()
        return ctx


def _safe_redirect_next(request, fallback_name="admintools:users"):
    """
    Redirect back to ?next=... if it's a safe same-origin URL;
    otherwise fallback.
    """
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(fallback_name)


@require_POST
def user_toggle_staff(request, pk: int):
    """Toggle staff status for a user."""
    # superuser-only (belt-and-suspenders)
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "You do not have permission to do that.")
        return _safe_redirect_next(request)

    target = get_object_or_404(User, pk=pk)

    # Safety rails: don't edit other superusers; don't demote yourself
    if target.is_superuser and target != request.user:
        messages.error(
            request,
            "You cannot change staff status of another superuser."
        )
        return _safe_redirect_next(request)

    if target == request.user:
        messages.error(
            request,
            "You cannot change your own staff status here."
        )
        return _safe_redirect_next(request)

    target.is_staff = not target.is_staff
    target.save(update_fields=["is_staff"])
    messages.success(
        request,
        f"Set staff for {target.username} to "
        f"{'Yes' if target.is_staff else 'No'}."
    )
    return _safe_redirect_next(request)


@require_POST
def user_toggle_suspend(request, pk: int):
    """Toggle suspended (is_active) status for a user."""
    # superuser-only
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "You do not have permission to do that.")
        return _safe_redirect_next(request)

    target = get_object_or_404(User, pk=pk)

    # Safety rails: don't suspend other superusers; don't suspend yourself
    if target.is_superuser and target != request.user:
        messages.error(request, "You cannot suspend another superuser.")
        return _safe_redirect_next(request)

    if target == request.user:
        messages.error(request, "You cannot suspend your own account.")
        return _safe_redirect_next(request)

    # "Suspend" = set is_active False; unsuspend = True
    target.is_active = not target.is_active
    target.save(update_fields=["is_active"])
    messages.success(
        request,
        f"{'Unsuspended' if target.is_active else 'Suspended'} "
        f"{target.username}."
    )
    return _safe_redirect_next(request)
