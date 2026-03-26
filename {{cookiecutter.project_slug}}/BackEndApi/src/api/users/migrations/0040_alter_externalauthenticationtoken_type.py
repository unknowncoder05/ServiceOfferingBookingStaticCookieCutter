from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_remove_user_wallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalauthenticationtoken',
            name='type',
            field=models.CharField(
                choices=[
                    ('VA', 'Validate account'),
                    ('SI', 'Sign in'),
                    ('RP', 'Reset password'),
                    ('RA', 'Recover account'),
                ],
                default='SI',
                max_length=5,
            ),
        ),
    ]
