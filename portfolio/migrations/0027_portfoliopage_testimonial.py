# Generated by Django 2.0 on 2019-03-14 16:01

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0026_auto_20190314_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliopage',
            name='testimonial',
            field=wagtail.core.fields.StreamField((('testimonial', wagtail.core.blocks.StructBlock(())),), blank=True, null=True),
        ),
    ]