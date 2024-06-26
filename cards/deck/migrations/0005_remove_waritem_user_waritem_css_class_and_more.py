# Generated by Django 5.0.3 on 2024-03-23 03:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0004_rename_inventorycard_inventoryitem_waritem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waritem',
            name='user',
        ),
        migrations.AddField(
            model_name='waritem',
            name='css_class',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='waritem',
            name='is_face_down',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='WarGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_won', models.BooleanField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='war_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WarIteration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='iterations', to='deck.wargame')),
            ],
            options={
                'ordering': ['index'],
            },
        ),
        migrations.AddField(
            model_name='waritem',
            name='iteration',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='deck.wariteration'),
            preserve_default=False,
        ),
    ]
