# Generated by Django 5.1.2 on 2024-11-02 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_deletionrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
