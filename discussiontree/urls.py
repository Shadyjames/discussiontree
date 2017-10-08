"""discussiontree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from discussiontree import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^about/?', views.about),
    url(r'^dump_refutations/?', views.dump_refutations),
    url(r'^tree_index/?', views.tree_index),
    url(r'^view_node/(?P<node_id>\d+)/?', views.view_node),
    url(r'^create_node/?', views.create_node),
    url(r'^create_proposition/?', views.create_proposition),
    url(r'^create_question/?', views.create_question),
    url(r'^/?', views.about),
]
