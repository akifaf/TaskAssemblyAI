# Generated by Django 5.1.5 on 2025-02-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_callrecord_first_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='V2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('assembly_ai_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
            ],
        ),
    ]
