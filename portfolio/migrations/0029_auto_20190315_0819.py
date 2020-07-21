# Generated by Django 2.0 on 2019-03-15 08:19

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0028_auto_20190315_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postpage',
            name='body',
            field=wagtail.core.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='postpage',
            name='excerpt',
            field=wagtail.core.fields.RichTextField(blank=True, verbose_name='excerpt'),
        ),
    ]