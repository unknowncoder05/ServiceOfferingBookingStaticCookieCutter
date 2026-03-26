from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20260126_0456'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='wallet',
        ),
    ]
