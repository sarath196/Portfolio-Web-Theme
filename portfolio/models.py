from django.db import models

import datetime
from datetime import date

from django import forms
from django.db import models
from django.http import Http404, HttpResponse
from django.utils.dateformat import DateFormat
from django.utils.formats import date_format

import wagtail
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel,
                                         PageChooserPanel, StreamFieldPanel)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.models import Document, AbstractDocument
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.snippets.models import register_snippet

from portfolio.blocks import TwoColumnBlock
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag as TaggitTag
from taggit.models import TaggedItemBase
from wagtailmd.utils import MarkdownField, MarkdownPanel
# Create your models here.

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('PostPage', related_name='post_tags')


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True


class BlogPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=255, blank=True,)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full")
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context['posts'] = self.posts
        context['blog_page'] = self
        context['search_type'] = getattr(self, 'search_type', "")
        context['search_term'] = getattr(self, 'search_term', "")
        return context

    def get_posts(self):
        return PostPage.objects.descendant_of(self).live().order_by('-date')

    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_posts().filter(date__year=year)
        self.search_type = 'date'
        self.search_term = year
        if month:
            self.posts = self.posts.filter(date__month=month)
            df = DateFormat(date(int(year), int(month), 1))
            self.search_term = df.format('F Y')
        if day:
            self.posts = self.posts.filter(date__day=day)
            self.search_term = date_format(date(int(year), int(month), int(day)))
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        post_page = self.get_posts().filter(slug=slug).first()
        if not post_page:
            raise Http404
        return Page.serve(post_page, request, *args, **kwargs)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = self.get_posts().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.posts = self.get_posts().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^search/$')
    def post_search(self, request, *args, **kwargs):
        search_query = request.GET.get('q', None)
        self.posts = self.get_posts()
        if search_query:
            self.posts = self.posts.filter(body__contains=search_query)
            self.search_term = search_query
            self.search_type = 'search'
        return Page.serve(self, request, *args, **kwargs)


class PostPage(Page):
    body = StreamField([('body', blocks.RichTextBlock()),])
    description = models.CharField(max_length=255, blank=True,)
    date = models.DateTimeField(verbose_name="Post date", default=datetime.datetime.today)
    excerpt = RichTextField(
        verbose_name='excerpt', blank=True,
    )

    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    categories = ParentalManyToManyField('portfolio.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through='portfolio.BlogPageTag', blank=True)
    
    content_panels = Page.content_panels + [
        ImageChooserPanel('header_image'),
        StreamFieldPanel("body"),
        FieldPanel("excerpt"),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('date'),
    ]

    @property
    def blog_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(PostPage, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        context['post'] = self
        context['posts'] = self.get_posts
        return context

    def get_posts(self):
        return PostPage.objects.exclude(id = self.id).live().order_by('?')[:3] 
    

    
class LandingPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock(icon="image")),
        ('two_columns', TwoColumnBlock()),
        ('embedded_video', EmbedBlock(icon="media")),
    ], null=True, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    @property
    def blog_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(LandingPage, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        return context



class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='custom_form_fields')


class FormPage(AbstractEmailForm):
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel('custom_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email Notification Config"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(FormPage, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        return context

    def get_form_fields(self):
        return self.custom_form_fields.all()

    @property
    def blog_page(self):
        return self.get_parent().specific
    
    
class PortfolioPage(Page):
    # Title Page
    name = models.CharField(max_length=150, blank=True,)
    phoneno = models.CharField(max_length=150, blank=True,)
    profile_image = models.ForeignKey( 'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+' )
    designation = models.CharField(max_length=150, blank=True,)
    age = models.DateField(verbose_name="Date of Birth", blank=True,)
    email = models.EmailField( max_length=70, blank=True, unique=True )
    location = models.CharField(max_length=150, blank=True,)
    # Header Page
    header_title = models.CharField(max_length=150, blank=True,)
    header_content = MarkdownField( verbose_name='Header Content', blank=True, )
    resume_csv = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    # Education Page
    resume_title = models.CharField(max_length=150, blank=True,)
    resume_content = MarkdownField( verbose_name='Resume Content', blank=True, )
    
    
    education_title = models.CharField(max_length=150, blank=True,)
    class EducationBlock(blocks.StructBlock):
        university = blocks.CharBlock(classname="full title")
        year_passing = blocks.CharBlock(classname="full title")
        education_content = blocks.CharBlock(classname="full title")
    
    education = StreamField([
        ('education', EducationBlock()),
    ], null=True, blank=True)
        
    
    #Employment Page
    employment_title = models.CharField(max_length=150, blank=True,)
    class EmploymentBlock(blocks.StructBlock):
        company_name = blocks.CharBlock(classname="full title")
        experience = blocks.CharBlock(classname="full title")
        designation = blocks.CharBlock(classname="full title")
        
    employment = StreamField([
        ('employment', EmploymentBlock()),
    ], null=True, blank=True)
    
    
    #Skills Page
    skills_title = models.CharField(max_length=150, blank=True,)
    class SkillsBlock(blocks.StructBlock):
        skills = blocks.CharBlock(classname="full title")
        percentage = blocks.CharBlock(classname="full title")
        
    skills = StreamField([
        ('skills', SkillsBlock()),
    ], null=True, blank=True)
    
    
    #Testimonials
    class TestimonialBlock(blocks.StructBlock):
        title = blocks.CharBlock(classname="full title")
        sub_title = blocks.CharBlock(classname="full title")
        content = blocks.RichTextBlock(blank=True)
    
    testimonial = StreamField([
        ('testimonial', TestimonialBlock()),
    ], null=True, blank=True)
    
    
    
    content_panels = Page.content_panels + [
        
        MultiFieldPanel([
            FieldPanel('name'),
            ImageChooserPanel('profile_image'),
            FieldPanel('phoneno'),
            FieldPanel('designation'),
            FieldPanel('age'),
            FieldPanel('email'),
            FieldPanel('location')
        ], "Heading"),
        
        MultiFieldPanel([
            FieldPanel('header_title'),
            MarkdownPanel('header_content'),
            DocumentChooserPanel('resume_csv'),
        ], "Header"),
        
        MultiFieldPanel([
            FieldPanel('resume_title'),
            MarkdownPanel('resume_content'),
            FieldPanel('education_title'),
            StreamFieldPanel('education'),
            FieldPanel('employment_title'),
            StreamFieldPanel('employment'),
            FieldPanel('skills_title'),
            StreamFieldPanel('skills'),    
        ], "Resume"),
         
        MultiFieldPanel([
            StreamFieldPanel('testimonial'),    
        ], "Testimonial"),                                   
                                            
        

    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super(PortfolioPage, self).get_context(request, *args, **kwargs)
        context['portfolio'] = self
        context['posts'] = self.get_posts
        context['blog_page'] = self.get_blogs
        context['projects'] = self.get_projects
        context['parent_projects'] = self.get_parent_project
        context['gits'] = self.get_gits
        context['parent_gits'] = self.get_parent_git
        return context
    
    def get_posts(self):
        return PostPage.objects.live().order_by('date')[:6]
    
    def get_blogs(self):
        return BlogPage.objects.live().first()
    
    def get_projects(self):
        return ProjectPage.objects.live().order_by('?')[:3]
    
    def get_parent_project(self):
        return ProjectParentPage.objects.live().first() 
    
    def get_gits(self):
        return GitPage.objects.live().order_by('?')[:3]
    
    def get_parent_git(self):
        return GitParentPage.objects.live().first() 
    
class ProjectParentPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=255, blank=True,)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full")
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super(ProjectParentPage, self).get_context(request, *args, **kwargs)
        context['parent_project'] = self
        context['projects'] = self.get_projects
        return context
    
    def get_projects(self):
        return ProjectPage.objects.live().order_by('-date')
    
class ProjectPage(Page):
    
    #Project Portfolio Page
    project_title = models.CharField(max_length=150, blank=True,)
    date = models.DateTimeField(verbose_name="Project date", default=datetime.datetime.today)
    class ProjectBlock(blocks.StructBlock):
        name = blocks.CharBlock(classname="full title")
        description = blocks.RichTextBlock()
        excerpt = blocks.RichTextBlock(blank=True)
        menu_title = blocks.CharBlock(classname="full title")
        project_url = blocks.URLBlock(classname="full title")
        project_image = ImageChooserBlock() 
        image_text =  blocks.CharBlock(classname="full title")
        start_date = blocks.CharBlock(classname="full title")
        end_date = blocks.CharBlock(classname="full title")  
        language = blocks.StreamBlock([
            ('skills', blocks.CharBlock()),
            ],icon='user')
        
    project = StreamField([
        ('project', ProjectBlock()),
    ], null=True, blank=True)
    
    
    content_panels = Page.content_panels + [     
           
           MultiFieldPanel([
            FieldPanel('project_title'),
            StreamFieldPanel('project'),
            
        ], "Project"),
    ]
    
    settings_panels = Page.settings_panels + [
        FieldPanel('date'),
    ]
    
    @property
    def parent_project_page(self):
        return self.get_parent().specific
    
    def get_context(self, request, *args, **kwargs):
        context = super(ProjectPage, self).get_context(request, *args, **kwargs)
        context['parent_project'] = self.parent_project_page
        context['project'] = self
        context['projects'] = self.get_projects
        return context
    
    def get_projects(self):
        return ProjectPage.objects.exclude(id = self.id).live().order_by('?')[:3] 
    
    
class GitParentPage(RoutablePageMixin, Page):
    description = models.CharField(max_length=255, blank=True,)

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full")
    ]
    
    def get_context(self, request, *args, **kwargs):  
        context = super(GitParentPage, self).get_context(request, *args, **kwargs)
        context['parent_git'] = self
        context['gits'] = self.get_projects
        return context
    
    def get_projects(self):
        return GitPage.objects.live().order_by('-date')
    
class GitPage(Page):
    
    #Git Portfolio Page
    git_title = models.CharField(max_length=150, blank=True,)
    date = models.DateTimeField(verbose_name="Project date", default=datetime.datetime.today)
    class GitBlock(blocks.StructBlock):
        name = blocks.CharBlock(classname="full title")
        description = blocks.RichTextBlock()
        excerpt = blocks.RichTextBlock(blank=True)
        menu_title = blocks.CharBlock(classname="full title")
        git_url = blocks.URLBlock(classname="full title")
        git_image = ImageChooserBlock() 
        image_text =  blocks.CharBlock(classname="full title")
        start_date = blocks.CharBlock(classname="full title")
        end_date = blocks.CharBlock(classname="full title")  
        language = blocks.StreamBlock([
            ('skills', blocks.CharBlock()),
            ],icon='user')
        
    GIT = StreamField([
        ('GIT', GitBlock()),
    ], null=True, blank=True)
    
    content_panels = Page.content_panels + [     
           
           MultiFieldPanel([
            FieldPanel('git_title'),
            StreamFieldPanel('GIT'),
            
        ], "GIT"),]
    
    settings_panels = Page.settings_panels + [
        FieldPanel('date'),
    ]
    @property
    def parent_git_page(self):
        return self.get_parent().specific
    
    def get_context(self, request, *args, **kwargs):
        context = super(GitPage, self).get_context(request, *args, **kwargs)
        context['parent_project_git'] = self.parent_git_page
        context['git'] = self
        context['gits'] = self.get_projects
        return context
    
    def get_projects(self):
        return GitPage.objects.exclude(id = self.id).live().order_by('?')[:3] 
    
class URLPage(RoutablePageMixin, Page):
    git_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    bitbucket_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    copy_rights = models.CharField(max_length=150,blank=True, null=True)
    content_panels = Page.content_panels + [
        FieldPanel('git_url', classname="full"),
        FieldPanel('linkedin_url', classname="full"),
        FieldPanel('bitbucket_url', classname="full"),
        FieldPanel('facebook_url', classname="full"),
        FieldPanel('copy_rights', classname="full"),
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super(URLPage, self).get_context(request, *args, **kwargs)
        context['url'] = self
        return context