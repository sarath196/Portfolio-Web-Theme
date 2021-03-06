# Generated by Django 2.0 on 2019-03-12 21:07

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0018_auto_20190312_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliopage',
            name='project',
            field=wagtail.core.fields.StreamField((('project', wagtail.core.blocks.StructBlock((('name', wagtail.core.blocks.CharBlock(classname='full title')), ('description', wagtail.core.blocks.RichTextBlock()), ('menu_title', wagtail.core.blocks.CharBlock(classname='full title')), ('project_url', wagtail.core.blocks.URLBlock(classname='full title')), ('project_image', wagtail.images.blocks.ImageChooserBlock())))), ('skills', wagtail.core.blocks.StructBlock((('skills', wagtail.core.blocks.CharBlock(classname='full title')),)))), blank=True, null=True),
        ),
    ]
