from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_initial_admin(sender, **kwargs):
    if not User.objects.filter(username="admin1").exists():
        admin_user = User.objects.create_superuser(
            username="admin1",
            password="admin1",
            email="admin1@example.com",
        )
        admin_user.first_name = "Admin"
        admin_user.last_name = "One"
        admin_user.save()