# Generated manually - Remove room functionality

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movies', '0004_challenge'),
    ]

    operations = [
        # Delete models that reference Room
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.DeleteModel(
            name='RoomMembership',
        ),
        migrations.DeleteModel(
            name='Room',
        ),
        # Recreate Game model with challenge reference
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('game_type', models.CharField(choices=[('taps', 'Taps'), ('shake', 'Shake')], max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='movies.challenge')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_movie_games', to=settings.AUTH_USER_MODEL)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='movies.movie')),
            ],
        ),
    ]