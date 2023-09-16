import subprocess

from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse_lazy

process_url = reverse_lazy("subprocess-view-process")
main_url = reverse_lazy("subprocess-view-main")


def user_is_superuser(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is superuser and logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser and u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator



@user_is_superuser
def process_view(request):
    try:
        cmd = request.GET.get("command")
        process = subprocess.run(cmd.split(" "), capture_output=True, text=True)
        html = f"""
        <html>
        <body>
        <h1>Subprocess-view (Processed)</h1>
        <h2>stdout</h2>
        <p>{process.stdout}</p>
        <h2>stderr</h2>
        <p>{process.stderr}</p>
        <h2>returncode<h2>
        <p>{process.returncode}</p>
        <a href={main_url}>Return to main</a>
        </body>
        </html>
        """
    except Exception as e:
        html = f"""
        <html>
        <body>
        <h1>Subprocess-view (Processed)</h1>
        <h2>Exception</h2>
        <p>{e}</p>
        <a href={main_url}>Return to main</a>
        </body>
        </html>
        """
    return HttpResponse(html)



@user_is_superuser
def main_view(request):
    html = f"""
    <html>
    <body>
    <h1>Subprocess-view<h1>
    <form method="GET" action="{process_url}">
    <input name="command">
    <button type="submit">Send</button>
    </form>
    </body>
    </html>
    """
    return HttpResponse(html)

