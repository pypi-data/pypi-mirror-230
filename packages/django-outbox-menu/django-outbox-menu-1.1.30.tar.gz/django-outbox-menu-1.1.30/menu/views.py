# from django.shortcuts import render

from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)

        # Menu Group -----------------------------------------
        #  Menu Group untuk membedakan menu site satu dan yg lain
        #  dan membedakan menu front end dan back end
        # Kind = 1 : FrontEND
        # kind = 2; Backend
        # menugroup = MenuGroup.objects.filter(site=self.site_id, kind=1)
        # if menugroup:
        #     context['menugroup'] = int(menugroup[0].id)
        #     # print('menugroup[0].id = ', menugroup[0].id)

        # else:
        #     raise Http404("Menu Group '%s' belum terdaftar, silahkan daftar di halaman <a href='%s'>admin</a>" % (request.get_host(), '/admin'))

        # Agency ---------------------------------------------
        # agency = get_agency_info(self.site_id)
        context['menugroup'] = '2'
        return context

class TestMenuView(TemplateView):
    template_name = 'test-menu.html'