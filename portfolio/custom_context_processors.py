from portfolio.models import URLPage

def portfolio_url(request):
    
    try:
        url_page = URLPage.objects.live().first()
        
        return {
            'git_url':  url_page.git_url,
            'linkedin_url': url_page.linkedin_url,
            'bitbucket_url': url_page.bitbucket_url,
            'facebook_url': url_page.facebook_url,
            'copy_right': url_page.copy_rights,
            }
    except:
        return {
            'git_url':  None,
            'linkedin_url': None,
            'bitbucket_url': None,
            'facebook_url': None,
            'copy_right': None,
            }
    