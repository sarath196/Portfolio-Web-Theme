# Generated by Django 2.0 on 2019-03-14 13:09

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
        ('portfolio', '0021_auto_20190312_2111'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('project_title', models.CharField(blank=True, max_length=150)),
                ('project', wagtail.core.fields.StreamField((('project', wagtail.core.blocks.StructBlock((('name', wagtail.core.blocks.CharBlock(classname='full title')), ('description', wagtail.core.blocks.RichTextBlock()), ('menu_title', wagtail.core.blocks.CharBlock(classname='full title')), ('project_url', wagtail.core.blocks.URLBlock(classname='full title')), ('project_image', wagtail.images.blocks.ImageChooserBlock()), ('language', wagtail.core.blocks.StreamBlock((('skills', wagtail.core.blocks.CharBlock()),), icon='user'))))),), blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='portfoliopage',
            name='project',
        ),
        migrations.RemoveField(
            model_name='portfoliopage',
            name='project_title',
        ),
    ]