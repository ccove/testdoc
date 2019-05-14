from django.conf.urls import url
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    url(r'^login$',Login),
    url(r'^register$',Register,name="register"),
    url(r'^logout$',Logout,name="logout"),
    url(r'^index$',Index,name="index"),
    url(r'^findpwd$',Find_pwd,name="findpwd"),
    url(r'^reset$',Reset,name="reset"),
    url(r'^upload$',file_upload,name="upload"),
    url(r'^show$',file_list),
    url(r'^download/(?P<file_path>.*)/$',file_download),
    url(r'^delete/(?P<id>.*)/$',file_delete),
    url(r'^recycle$',file_recycle),
    url(r'^recover/(?P<id>.*)/$',file_recover),
    url(r'^share/(?P<id>.*)/$',file_share),
    url(r'^all_share$',file_all_share),
    url(r'^me_share$',file_me_share),
    url(r'^share_cacle/(?P<id>.*)/$',file_share_cacle),
    url(r'^person$',person),
    url(r'^reset$',Reset),
    url(r'^one$',one),
    url(r'^two$',two),
    url(r'^three$',three),
    url(r'^four$',four),
    url(r'^five$',five),
    url(r'^serach$',serach)
]