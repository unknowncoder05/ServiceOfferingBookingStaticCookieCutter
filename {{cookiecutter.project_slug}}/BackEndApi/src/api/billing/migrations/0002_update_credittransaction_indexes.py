from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='credittransaction',
            new_name='billing_cre_user_id_b1ca8c_idx',
            old_name='billing_ctx_user_idx',
        ),
        migrations.RenameIndex(
            model_name='credittransaction',
            new_name='billing_cre_transac_d45d1c_idx',
            old_name='billing_ctx_type_idx',
        ),
        migrations.RenameIndex(
            model_name='credittransaction',
            new_name='billing_cre_stripe__ea99ad_idx',
            old_name='billing_ctx_pi_idx',
        ),
        migrations.RenameIndex(
            model_name='credittransaction',
            new_name='billing_cre_stripe__646846_idx',
            old_name='billing_ctx_cs_idx',
        ),
        migrations.RenameIndex(
            model_name='credittransaction',
            new_name='billing_cre_context_bc2ca0_idx',
            old_name='billing_ctx_ref_idx',
        ),
    ]
