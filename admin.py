# -*- coding: utf-8 -*-
import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
import wsgiref.handlers
from django.conf import settings
settings._target = None
from django.utils import simplejson
from django.utils.translation import ugettext as _
import base
from model import *

from app.pingback import autoPingback
from app.trackback import TrackBack
import xmlrpclib
from xmlrpclib import Fault

class Error404(base.BaseRequestHandler):
    #@printinfo
    def get(self,slug=None):
        self.render2('views/admin/404.html')

class setlanguage(base.BaseRequestHandler):
    def get(self):
        lang_code = self.param('language')
        next = self.param('next')
        if (not next) and os.environ.has_key('HTTP_REFERER'):
            next = os.environ['HTTP_REFERER']
        if not next:
            next = '/'
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        from django.utils.translation import check_for_language, activate
        from django.conf import settings
        settings._target = None

        if lang_code and check_for_language(lang_code):
            g_blog.language=lang_code
            activate(g_blog.language)
            g_blog.save()
        self.redirect(next)

##            if hasattr(request, 'session'):
##                request.session['django_language'] = lang_code
##            else:

##            cookiestr='django_language=%s;expires=%s;domain=%s;path=/'%( lang_code,
##                       (datetime.now()+timedelta(days=100)).strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
##                       ''
##                       )
##            self.write(cookiestr)

##          self.response.headers.add_header('Set-Cookie', cookiestr)

def fetch_result(target_uri):
    for RETRY in range(5):
        try:
            response = urlfetch.fetch(target_uri)
            return response
        except urlfetch.DownloadError:
            logging.info('Download Error, Retry %s times'%RETRY)
            continue
        except:
            raise base.PingbackError(16)
    else:
        logging.info('Times Over')
        raise base.PingbackError(16)


class admin_do_action(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        try:
            func=getattr(self,'action_'+slug)
            if func and callable(func):
                func()
            else:
                self.render2('views/admin/error.html',{'message':_('This operate has not defined!')})
        except:
             self.render2('views/admin/error.html',{'message':_('This operate has not defined!')})


    def post(self,slug=None):
        try:
            func=getattr(self,'action_'+slug)
            if func and callable(func):
                func()
            else:
                self.render2('views/admin/error.html',{'message':_('This operate has not defined!')})
        except:
             self.render2('views/admin/error.html',{'message':_('This operate has not defined!')})

    @base.requires_admin
    def action_test(self):
        self.write(os.environ)

    @base.requires_admin
    def action_cacheclear(self):
        memcache.flush_all()
        self.write(_('"Cache cleared successful"'))

    @base.requires_admin
    def action_updatecomments(self):
        for entry in Entry.all():
            cnt=entry.comments().count()
            if cnt<>entry.commentcount:
                entry.commentcount=cnt
                entry.put()
        self.write(_('"All comments updated"'))

    @base.requires_admin
    def action_updatecommentno(self):
        for entry in Entry.all():
            entry.update_commentno()
        self.write(_('"All comments number Updates."'))

    @base.requires_admin
    def action_updatelink(self):
        link_format=self.param('linkfmt')

        if link_format:
            link_format=link_format.strip()
            g_blog.link_format=link_format
            g_blog.save()
            for entry in Entry.all():
                vals={'year':entry.date.year,'month':str(entry.date.month).zfill(2),'day':entry.date.day,
                'postname':entry.slug,'post_id':entry.post_id}

                if entry.slug:
                    newlink=link_format%vals
                else:
                    newlink=g_blog.default_link_format%vals

                if entry.link<>newlink:
                    entry.link=newlink
                    entry.put()
            self.write(_('"Link formated succeed"'))
        else:
            self.write(_('"Please input url format."'))

    @base.requires_admin
    def action_init_blog(self,slug=None):

        for com in Comment.all():
            com.delete()

        for entry in Entry.all():
            entry.delete()

        g_blog.entrycount=0
        self.write(_('"Init has succeed."'))

    @base.requires_admin
    def action_update_tags(self,slug=None):
        for tag in Tag.all():
            tag.delete()
        for entry in Entry.all().filter('entrytype =','post'):
            if entry.tags:
                for t in entry.tags:
                    try:
                        Tag.add(t)
                    except:
                        base.traceback.print_exc()

        self.write(_('"All tags for entry have been updated."'))

    @base.requires_admin
    def action_update_archives(self,slug=None):
        for archive in Archive.all():
            archive.delete()
        entries=Entry.all().filter('entrytype =','post')

        archives={}


        for entry in entries:
            my = entry.date.strftime('%B %Y') # September-2008
            sy = entry.date.strftime('%Y') #2008
            sm = entry.date.strftime('%m') #09
            if archives.has_key(my):
                archive=archives[my]
                archive.entrycount+=1
            else:
                archive = Archive(monthyear=my,year=sy,month=sm,entrycount=1)
                archives[my]=archive

        for ar in archives.values():
            ar.put()

        self.write(_('"All entries have been updated."'))


    def action_trackback_ping(self):
        tbUrl=self.param('tbUrl')
        title=self.param('title')
        excerpt=self.param('excerpt')
        url=self.param('url')
        blog_name=self.param('blog_name')
        tb=TrackBack(tbUrl,title,excerpt,url,blog_name)
        tb.ping()

    def action_pingback_ping(self):
        """Try to notify the server behind `target_uri` that `source_uri`
        points to `target_uri`.  If that fails an `PingbackError` is raised.
        """
        source_uri=self.param('source')
        target_uri=self.param('target')
        try:
            #response =urlfetch.fetch(target_uri)
            response=fetch_result(target_uri) #retry up to 5 times
        except:
            raise base.PingbackError(32)

        try:
            pingback_uri = response.headers['X-Pingback']
        except KeyError:
            _pingback_re = re.compile(r'<link rel="pingback" href="([^"]+)" ?/?>(?i)')
            match = _pingback_re.search(response.content)
            if match is None:
                raise base.PingbackError(33)
            pingback_uri =base.urldecode(match.group(1))

        rpc = xmlrpclib.ServerProxy(pingback_uri)
        try:
            return rpc.pingback.ping(source_uri, target_uri)
        except Fault, e:
            raise base.PingbackError(e.faultCode)
        except:
            raise base.PingbackError(32)




class admin_tools(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current="config"

    @base.requires_admin
    def get(self,slug=None):
        self.render2('views/admin/tools.html')


class admin_sitemap(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current="config"

    @base.requires_admin
    def get(self,slug=None):
        self.render2('views/admin/sitemap.html')


    @base.requires_admin
    def post(self):
        str_options= self.param('str_options').split(',')
        for name in str_options:
            value=self.param(name)
            setattr(g_blog,name,value)

        bool_options= self.param('bool_options').split(',')
        for name in bool_options:
            value=self.param(name)=='on'
            setattr(g_blog,name,value)

        int_options= self.param('int_options').split(',')
        for name in int_options:
            try:
                value=int( self.param(name))
                setattr(g_blog,name,value)
            except:
                pass
        float_options= self.param('float_options').split(',')
        for name in float_options:
            try:
                value=float( self.param(name))
                setattr(g_blog,name,value)
            except:
                pass


        g_blog.save()
        self.render2('views/admin/sitemap.html',{})

class admin_import(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current='config'

    @base.requires_admin
    def get(self,slug=None):
        gblog_init()
        self.render2('views/admin/import.html',{'importitems':
            self.blog.plugins.filter('is_import_plugin',True)})

##    def post(self):
##        try:
##            queue=taskqueue.Queue("import")
##            wpfile=self.param('wpfile')
##            #global imt
##            imt=import_wordpress(wpfile)
##            imt.parse()
##            memcache.set("imt",imt)
##
####            import_data=OptionSet.get_or_insert(key_name="import_data")
####            import_data.name="import_data"
####            import_data.bigvalue=pickle.dumps(imt)
####            import_data.put()
##
##            queue.add(taskqueue.Task( url="/admin/import_next"))
##            self.render2('views/admin/import.html',
##                        {'postback':True})
##            return
##            memcache.set("import_info",{'count':len(imt.entries),'msg':'Begin import...','index':1})
##            #self.blog.import_info={'count':len(imt.entries),'msg':'Begin import...','index':1}
##            if imt.categories:
##                queue.add(taskqueue.Task( url="/admin/import_next",params={'cats': pickle.dumps(imt.categories),'index':1}))
##
##            return
##            index=0
##            if imt.entries:
##                for entry in imt.entries :
##                    try:
##                        index=index+1
##                        queue.add(taskqueue.Task(url="/admin/import_next",params={'entry':pickle.dumps(entry),'index':index}))
##                    except:
##                        pass
##
##        except:
##            self.render2('views/admin/import.html',{'error':'import faiure.'})

class admin_setup(base.BaseRequestHandler):
    def __init__(self):
        self.current='config'

    @base.requires_admin
    def get(self,slug=None):
        vals={'themes':ThemeIterator()}
        self.render2('views/admin/setup.html',vals)

    @base.requires_admin
    def post(self):
        old_theme=g_blog.theme_name
        str_options= self.param('str_options').split(',')
        for name in str_options:
            value=self.param(name)
            setattr(g_blog,name,value)

        bool_options= self.param('bool_options').split(',')
        for name in bool_options:
            value=self.param(name)=='on'
            setattr(g_blog,name,value)

        int_options= self.param('int_options').split(',')
        for name in int_options:
            try:
                value=int( self.param(name))
                setattr(g_blog,name,value)
            except:
                pass
        float_options= self.param('float_options').split(',')
        for name in float_options:
            try:
                value=float( self.param(name))
                setattr(g_blog,name,value)
            except:
                pass


        if old_theme !=g_blog.theme_name:
            g_blog.get_theme()


        g_blog.owner=self.login_user
        g_blog.author=g_blog.owner.nickname()
        g_blog.save()
        gblog_init()
        vals={'themes':ThemeIterator()}
        memcache.flush_all()
        self.render2('views/admin/setup.html',vals)

class admin_entry(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current='write'

    @base.requires_admin
    def get(self,slug='post'):
        action=self.param("action")
        entry=None
        cats=Category.all()
        alltags=Tag.all()
        if action and  action=='edit':
                try:
                    key=self.param('key')
                    entry=Entry.get(key)

                except:
                    pass
        else:
            action='add'

        def mapit(cat):
            return {'name':cat.name,'slug':cat.slug,'select':entry and cat.key() in entry.categorie_keys}

        vals={'action':action,'entry':entry,'entrytype':slug,'cats':map(mapit,cats),'alltags':alltags}
        self.render2('views/admin/entry.html',vals)

    @base.requires_admin
    def post(self,slug='post'):
        action=self.param("action")
        title=self.param("post_title")
        content=self.param('content')
        tags=self.param("tags")
        cats=self.request.get_all('cats')
        key=self.param('key')
        meta_keywords=self.param('meta_keywords')
        image_link=self.param('image_link')
        if self.param('publish')!='':
            published=True
        elif self.param('unpublish')!='':
            published=False
        else:
            published=self.param('published')=='True'

        allow_comment=self.parambool('allow_comment')
        allow_trackback=self.parambool('allow_trackback')
        entry_slug=self.param('slug')
        entry_parent=self.paramint('entry_parent')
        menu_order=self.paramint('menu_order')
        entry_excerpt=self.param('excerpt')#.replace('\n','<br />')
        password=self.param('password')
        sticky=self.parambool('sticky')
        show_shareaholic=self.parambool('show_shareaholic')
        show_entrymeta=self.parambool('show_entrymeta')

        is_external_page=self.parambool('is_external_page')
        target=self.param('target')
        external_page_address=self.param('external_page_address')

        def mapit(cat):
            return {'name':cat.name,'slug':cat.slug,'select':cat.slug in cats}

        vals={'action':action,'postback':True,'cats':Category.all(),'entrytype':slug,
              'cats':map(mapit,Category.all()),
              'entry':{ 'title':title,'content':content,'strtags':tags,'key':key,'published':published,
                         'allow_comment':allow_comment,
                         'allow_trackback':allow_trackback,
                        'slug':entry_slug,
                        'image_link':image_link,
                        'entry_parent':entry_parent,
                        'excerpt':entry_excerpt,
                        'menu_order':menu_order,
                        'is_external_page':is_external_page,
                        'target':target,
                        'external_page_address':external_page_address,
                        'password':password,
                        'show_shareaholic':show_shareaholic,
                        'show_entrymeta':show_entrymeta,
                        'meta_keywords':meta_keywords,
                        'sticky':sticky}
              }

        if not (title and (content or (is_external_page and external_page_address))):
            vals.update({'result':False, 'msg':_('Please input title and content.')})
            self.render2('views/admin/entry.html',vals)
        else:
            if action=='add':
                entry= Entry(title=title,content=content)
                entry.settags(tags)
                entry.entrytype=slug
                entry.slug=entry_slug.replace(" ","_")
                entry.entry_parent=entry_parent
                entry.menu_order=menu_order
                entry.excerpt=entry_excerpt
                entry.is_external_page=is_external_page
                entry.image_link=image_link
                entry.target=target
                entry.external_page_address=external_page_address
                newcates=[]
                entry.allow_comment=allow_comment
                entry.allow_trackback=allow_trackback
                entry.author=self.author.user
                entry.author_name=self.author.dispname
                entry.password=password
                entry.sticky=sticky
                entry.ShowShareaholic=show_shareaholic
                entry.ShowEntryMeta=show_entrymeta
                entry.metaKeywords=meta_keywords
                if cats:

                    for cate in cats:
                        c=Category.all().filter('slug =',cate)
                        if c:
                            newcates.append(c[0].key())
                entry.categorie_keys=newcates;

                entry.save(published)
                if published:
                    smsg=_('Saved ok. <a href="/%(link)s" target="_blank">View it now!</a>')
                else:
                    smsg=_('Saved ok.')

                vals.update({'action':'edit','result':True,'msg':smsg%{'link':str(entry.link)},'entry':entry})
                self.render2('views/admin/entry.html',vals)
                if published and entry.allow_trackback and g_blog.allow_pingback:
                    try:
                        autoPingback(str(entry.fullurl),HTML=content)
                    except:
                        pass
            elif action=='edit':
                try:
                    entry=Entry.get(key)
                    entry.title=title
                    entry.image_link=image_link
                    entry.content=content
                    entry.slug=entry_slug.replace(' ','-')
                    entry.entry_parent=entry_parent
                    entry.menu_order=menu_order
                    entry.excerpt=entry_excerpt
                    entry.is_external_page=is_external_page
                    entry.target=target
                    entry.external_page_address=external_page_address
                    entry.settags(tags)
                    entry.author=self.author.user
                    entry.author_name=self.author.dispname
                    entry.password=password
                    entry.ShowShareaholic=show_shareaholic
                    entry.ShowEntryMeta=show_entrymeta
                    entry.sticky=sticky
                    entry.metaKeywords=meta_keywords
                    newcates=[]

                    if cats:

                        for cate in cats:
                            c=Category.all().filter('slug =',cate)
                            if c:
                                newcates.append(c[0].key())
                    entry.categorie_keys=newcates;
                    entry.allow_comment=allow_comment
                    entry.allow_trackback=allow_trackback

                    entry.save(published)

                    if published:
                        smsg=_('Saved ok. <a href="/%(link)s" target="_blank">View it now!</a>')
                    else:
                        smsg=_('Saved ok.')
                    vals.update({'result':True,'msg':smsg%{'link':str(base.urlencode( entry.link))},'entry':entry})

                    self.render2('views/admin/entry.html',vals)
                    if published and entry.allow_trackback and g_blog.allow_pingback:
                        try:
                            autoPingback(entry.fullurl,HTML=content)
                        except:
                            pass

                except:
                    vals.update({'result':False,'msg':_('Error:Entry can''t been saved.')})
                    self.render2('views/admin/entry.html',vals)


class admin_entries(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug='post'):
        try:
            page_index=int(self.param('page'))
        except:
            page_index=1




        entries=Entry.all().filter('entrytype =',slug).order('-date')
        entries,links=base.Pager(query=entries,items_per_page=15).fetch(page_index)

        self.render2('views/admin/'+slug+'s.html',
         {
           'current':slug+'s',
           'entries':entries,
           'pager':links
          }
        )

    @base.requires_admin
    def post(self,slug='post'):
        try:
            linkcheck= self.request.get_all('checks')
            for id in linkcheck:
                kid=int(id)

                entry=Entry.get_by_id(kid)

                #delete it's comments
                #entry.delete_comments()

                entry.delete()
                g_blog.entrycount-=1
        finally:

            self.redirect('/admin/entries/'+slug)


class admin_categories(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        try:
            page_index=int(self.param('page'))
        except:
            page_index=1




        cats=Category.allTops()
        entries,pager=base.Pager(query=cats,items_per_page=15).fetch(page_index)

        self.render2('views/admin/categories.html',
         {
           'current':'categories',
           'cats':cats,
           'pager':pager
          }
        )

    @base.requires_admin
    def post(self,slug=None):
        try:
            linkcheck= self.request.get_all('checks')
            for key in linkcheck:

                cat=Category.get(key)
                if cat:
                    cat.delete()
        finally:
            self.redirect('/admin/categories')

class admin_sliderimages(base.BaseRequestHandler):
    @base.requires_admin

    def getImg2ForOrdering(self,  filter, simg, sort):
        simg2=None
        results=SliderImage.all().filter(filter,simg.order).order(sort).fetch(2) # this is frustrating - Inequality Filters Are Allowed on One Property Only
        for o in results:
            if o.key().id != simg.key().id:
                simg2=o
                break
        return simg2
        
    def get(self,slug=None):
        action = self.param("action")
        action_id=self.param('id')
        toadd=0
        if(action_id is not None and action_id != ""):
            new_order = -1
            simg=SliderImage.get_by_id(int(action_id))
            if action=="up":
                toadd=-1
                simg2=self.getImg2ForOrdering('order <',simg, '-order')
            elif action=="down":
                toadd=1
                simg2=self.getImg2ForOrdering('order >',simg, 'order')

            #not the best way - may not be well written code- but it works for time being since the default value will cause ordering conflicts
            #-- update - have changed the add method to auto-increment number - this will not create ambiguous Order values - still keeping the code below
            
            if new_order==-1:
                if simg2 is not None and simg.order != simg2.order:
                    new_order = simg2.order
                    simg2.order = simg.order
                    simg2.put()
                else:
                    new_order=simg.order+toadd
                simg.order = new_order                    
                simg.put()
                    
            if action!="":
                self.redirect('/admin/sliderimages')

        self.render2('views/admin/sliderimages.html',
         {
          'current':'sliderimages',
          'sliderimages':SliderImage.all().order('order')#.filter('linktype =','blogroll')#.order('-createdate')
          }
        )
    @base.requires_admin
    def post(self):
        sliderimagecheck= self.request.get_all('sliderimagecheck')
        for sliderimage_id in sliderimagecheck:
            kid=int(sliderimage_id)
            sliderimage_obj=SliderImage.get_by_id(kid)
            sliderimage_obj.delete()
        self.redirect('/admin/sliderimages')

class admin_sliderimage(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        action=self.param("action")
        vals={'current':'sliderimage'}
        if action and  action=='edit':
                try:
                    action_id=int(self.param('id'))
                    sliderimage_obj=SliderImage.get_by_id(action_id)
                    vals.update({'sliderimage':sliderimage_obj})
                except:
                    pass
        else:
            action='add'
        vals.update({'action':action})

        self.render2('views/admin/sliderimage.html',vals)

    @base.requires_admin
    def post(self):
        action=self.param("action")
        title=self.param("sliderimage_title")
        subtitle=self.param("sliderimage_subtitle")
        posthref=self.param("sliderimage_posthref")
        imagehref=self.param("sliderimage_imagehref")
        is_slider_active=self.param("sliderimage_active")=="on"
        vals={'action':action,'postback':True,'current':'sliderimages'}
        if not (title and imagehref):
            vals.update({'result':False,'msg':_('Please input title and image link.')})
            self.render2('views/admin/sliderimage.html',vals)
        else:
            if action=='add':
               simg= SliderImage(title=title, subtitle=subtitle, posthref=posthref, imagehref=imagehref, active=is_slider_active)
               simg.order = SliderImage.all().order('-order').get().order+1
               simg.put()
               vals.update({'result':True,'msg':'Saved ok'})
               self.render2('views/admin/sliderimage.html',vals)
            elif action=='edit':
                try:
                    action_id=int(self.param('id'))
                    simg=SliderImage.get_by_id(action_id)
                    simg.title = title
                    simg.subtitle=subtitle
                    simg.posthref=posthref
                    simg.imagehref=imagehref
                    simg.active=is_slider_active
                    simg.put()
                    #goto link manage page
                    self.redirect('/admin/sliderimages')

                except  Exception, err:
                    logging.error(err);
                    vals.update({'result':False,'msg':_('Error:Slider can''t been saved.')})
                    self.render2('views/admin/sliderimage.html',vals)


class admin_comments(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        try:
            page_index=int(self.param('page'))
        except:
            page_index=1



        cq=self.param('cq')
        cv=self.param('cv')
        if cq and cv:
            query=Comment.all().filter(cq+' =',cv).order('-date')
        else:
            query=Comment.all().order('-date')
        comments,pager=base.Pager(query=query,items_per_page=15).fetch(page_index)

        self.render2('views/admin/comments.html',
         {
           'current':'comments',
           'comments':comments,
           'pager':pager,
           'cq':cq,
           'cv':cv
          }
        )

    @base.requires_admin
    def post(self,slug=None):
        try:
            linkcheck= self.request.get_all('checks')
            entrykeys=[]
            for key in linkcheck:

                comment=Comment.get(key)
                comment.delit()
                entrykeys.append(comment.entry.key())
            entrykeys=set(entrykeys)
            for key in entrykeys:
                e=Entry.get(key)
                e.update_commentno()
                e.removecache()
            memcache.delete("/feed/comments")
        finally:
            self.redirect(self.request.uri)

class admin_links(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        self.render2('views/admin/links.html',
         {
          'current':'links',
          'links':Link.all().filter('linktype =','blogroll')#.order('-createdate')
          }
        )
    @base.requires_admin
    def post(self):
        linkcheck= self.request.get_all('linkcheck')
        for link_id in linkcheck:
            kid=int(link_id)
            link=Link.get_by_id(kid)
            link.delete()
        self.redirect('/admin/links')

class admin_link(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        action=self.param("action")
        vals={'current':'links'}
        if action and  action=='edit':
                try:
                    action_id=int(self.param('id'))
                    link=Link.get_by_id(action_id)
                    vals.update({'link':link})
                except:
                    pass
        else:
            action='add'
        vals.update({'action':action})

        self.render2('views/admin/link.html',vals)

    @base.requires_admin
    def post(self):
        action=self.param("action")
        name=self.param("link_name")
        url=self.param("link_url")
        comment = self.param("link_comment")

        vals={'action':action,'postback':True,'current':'links'}
        if not (name and url):
            vals.update({'result':False,'msg':_('Please input name and url.')})
            self.render2('views/admin/link.html',vals)
        else:
            if action=='add':
               link= Link(linktext=name,href=url,linkcomment=comment)
               link.put()
               vals.update({'result':True,'msg':'Saved ok'})
               self.render2('views/admin/link.html',vals)
            elif action=='edit':
                try:
                    action_id=int(self.param('id'))
                    link=Link.get_by_id(action_id)
                    link.linktext=name
                    link.href=url
                    link.linkcomment = comment
                    link.put()
                    #goto link manage page
                    self.redirect('/admin/links')

                except:
                    vals.update({'result':False,'msg':_('Error:Link can''t been saved.')})
                    self.render2('views/admin/link.html',vals)

class admin_category(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current='categories'

    @base.requires_admin
    def get(self,slug=None):
        action=self.param("action")
        key=self.param('key')
        category=None
        if action and  action=='edit':
                try:

                    category=Category.get(key)

                except:
                    pass
        else:
            action='add'
        vals={'action':action,'category':category,'key':key,'categories':[c for c in Category.all() if not category or c.key()!=category.key()]}
        self.render2('views/admin/category.html',vals)

    @base.requires_admin
    def post(self):
        def check(cate):
            parent=cate.parent_cat
            skey=cate.key()
            while parent:
                if parent.key()==skey:
                    return False
                parent=parent.parent_cat
            return True

        action=self.param("action")
        name=self.param("name")
        slug=self.param("slug")
        parentkey=self.param('parentkey')
        key=self.param('key')


        vals={'action':action,'postback':True}

        try:

                if action=='add':
                    cat= Category(name=name,slug=slug)
                    if not (name and slug):
                        raise Exception(_('Please input name and slug.'))
                    if parentkey:
                        cat.parent_cat=Category.get(parentkey)

                    cat.put()
                    self.redirect('/admin/categories')

                    #vals.update({'result':True,'msg':_('Saved ok')})
                    #self.render2('views/admin/category.html',vals)
                elif action=='edit':

                        cat=Category.get(key)
                        cat.name=name
                        cat.slug=slug
                        if not (name and slug):
                            raise Exception(_('Please input name and slug.'))
                        if parentkey:
                            cat.parent_cat=Category.get(parentkey)
                            if not check(cat):
                                raise Exception(_('A circle declaration found.'))
                        else:
                            cat.parent_cat=None
                        cat.put()
                        self.redirect('/admin/categories')

        except Exception ,e :
            if cat.is_saved():
                cates=[c for c in Category.all() if c.key()!=cat.key()]
            else:
                cates= Category.all()

            vals.update({'result':False,'msg':e.message,'category':cat,'key':key,'categories':cates})
            self.render2('views/admin/category.html',vals)

class admin_status(base.BaseRequestHandler):
    @base.requires_admin
    def get(self):
        self.render2('views/admin/status.html',{'cache':memcache.get_stats(),'current':'status','environ':os.environ})
class admin_authors(base.BaseRequestHandler):
    @base.requires_admin
    def get(self):
        try:
            page_index=int(self.param('page'))
        except:
            page_index=1




        authors=User.all().filter('isAuthor =',True)
        entries,pager=base.Pager(query=authors,items_per_page=15).fetch(page_index)

        self.render2('views/admin/authors.html',
         {
           'current':'authors',
           'authors':authors,
           'pager':pager
          }
        )


    @base.requires_admin
    def post(self,slug=None):
        try:
            linkcheck= self.request.get_all('checks')
            for key in linkcheck:

                author=User.get(key)
                author.delete()
        finally:
            self.redirect('/admin/authors')

class admin_author(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current='authors'

    @base.requires_admin
    def get(self,slug=None):
        action=self.param("action")
        author=None
        if action and  action=='edit':
                try:
                    key=self.param('key')
                    author=User.get(key)

                except:
                    pass
        else:
            action='add'
        vals={'action':action,'author':author}
        self.render2('views/admin/author.html',vals)

    @base.requires_admin
    def post(self):
        action=self.param("action")
        name=self.param("name")
        slug=self.param("email")

        vals={'action':action,'postback':True}
        if not (name and slug):
            vals.update({'result':False,'msg':_('Please input dispname and email.')})
            self.render2('views/admin/author.html',vals)
        else:
            if action=='add':
               author= User(dispname=name,email=slug    )
               author.user=db.users.User(slug)
               author.put()
               vals.update({'result':True,'msg':'Saved ok'})
               self.render2('views/admin/author.html',vals)
            elif action=='edit':
                try:
                    key=self.param('key')
                    author=User.get(key)
                    author.dispname=name
                    author.email=slug
                    author.user=db.users.User(slug)
                    author.put()
                    if author.isadmin:
                        g_blog.author=name
                    self.redirect('/admin/authors')

                except:
                    vals.update({'result':False,'msg':_('Error:Author can''t been saved.')})
                    self.render2('views/admin/author.html',vals)

class admin_plugins(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current='plugins'

    @base.requires_admin
    def get(self,slug=None):
        vals={'plugins':self.blog.plugins}
        self.render2('views/admin/plugins.html',vals)

    @base.requires_admin
    def post(self):
        action=self.param("action")
        name=self.param("plugin")
        ret=self.param("return")
        self.blog.plugins.activate(name,action=="activate")
        if ret:
            self.redirect(ret)
        else:
            vals={'plugins':self.blog.plugins}
            self.render2('views/admin/plugins.html',vals)

class admin_plugins_action(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current='plugins'

    @base.requires_admin
    def get(self,slug=None):
        plugin=self.blog.plugins.getPluginByName(slug)
        if not plugin :
            self.error(404)
            return
        plugins=self.blog.plugins.filter('active',True)
        if not plugin.active:
            pcontent=_('''<div>Plugin '%(name)s' havn't actived!</div><br><form method="post" action="/admin/plugins?action=activate&amp;plugin=%(iname)s&amp;return=/admin/plugins/%(iname)s"><input type="submit" value="Activate Now"/></form>''')%{'name':plugin.name,'iname':plugin.iname}
            plugins.insert(0,plugin)
        else:
            pcontent=plugin.get(self)


        vals={'plugins':plugins,
              'plugin':plugin,
              'pcontent':pcontent}

        self.render2('views/admin/plugin_action.html',vals)

    @base.requires_admin
    def post(self,slug=None):

        plugin=self.blog.plugins.getPluginByName(slug)
        if not plugin :
            self.error(404)
            return
        plugins=self.blog.plugins.filter('active',True)
        if not plugin.active:
            pcontent=_('''<div>Plugin '%(name)s' havn't actived!</div><br><form method="post" action="/admin/plugins?action=activate&amp;plugin=%(iname)s&amp;return=/admin/plugins/%(iname)s"><input type="submit" value="Activate Now"/></form>''')%{'name':plugin.name,'iname':plugin.iname}
            plugins.insert(0,plugin)
        else:
            pcontent=plugin.post(self)


        vals={'plugins':plugins,
              'plugin':plugin,
              'pcontent':pcontent}

        self.render2('views/admin/plugin_action.html',vals)

class WpHandler(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,tags=None):
        try:
            all=self.param('all')
        except:
            all=False

        if(all):
            entries = Entry.all().order('-date')
            filename='micolog.%s.xml'%datetime.now().strftime('%Y-%m-%d')
        else:
            str_date_begin=self.param('date_begin')
            str_date_end=self.param('date_end')
            try:
                date_begin=datetime.strptime(str_date_begin,"%Y-%m-%d")
                date_end=datetime.strptime(str_date_end,"%Y-%m-%d")
                entries = Entry.all().filter('date >=',date_begin).filter('date <',date_end).order('-date')
                filename='micolog.%s.%s.xml'%(str(str_date_begin),str(str_date_end))
            except:
                self.render2('views/admin/404.html')
                return

        cates=Category.all()
        tags=Tag.all()

        self.response.headers['Content-Type'] = 'binary/octet-stream'#'application/atom+xml'
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s'%filename
        self.render2('views/wordpress.xml',{'entries':entries,'cates':cates,'tags':tags})

class Upload(base.BaseRequestHandler):
    @base.requires_admin
    def post(self):
        name = self.param('filename')
        mtype = self.param('fileext')
        bits = self.param('upfile')
        Media(name = name, mtype = mtype, bits = bits).put()

        self.redirect('/admin/filemanager')

class UploadEx(base.BaseRequestHandler):
    @base.requires_admin
    def get(self):
        extstr=self.param('ext')
        ext=extstr.split('|')
        files=Media.all()
        if extstr!='*':
            files=files.filter('mtype IN',ext)
        self.render2('views/admin/upload.html',{'ext':extstr,'files':files})

    @base.requires_admin
    def post(self):
        ufile=self.request.params['userfile']
        #if ufile:
        name=ufile.filename
        mtype =os.path.splitext(name)[1][1:]
        bits = self.param('userfile')
        media=Media(name = name, mtype = mtype, bits = bits)
        media.put()
        self.write(simplejson.dumps({'name':media.name,'size':media.size,'id':str(media.key())}))

class FileManager(base.BaseRequestHandler):
    def __init__(self):
        base.BaseRequestHandler.__init__(self)
        self.current = 'files'

    @base.requires_admin
    def get(self):
        try:
            page_index=int(self.param('page'))
        except:
            page_index=1
        files = Media.all().order('-date')
        files,links=base.Pager(query=files,items_per_page=15).fetch(page_index)
        self.render2('views/admin/filemanager.html',{'files' : files,'pager':links})

    @base.requires_admin
    def post(self): # delete files
        delids = self.request.POST.getall('del')
        if delids:
            for id in delids:
                file = Media.get_by_id(int(id))
                file.delete()

        self.redirect('/admin/filemanager')

class admin_main(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug=None):
        if self.is_admin:
            self.redirect('/admin/setup')
        else:
            self.redirect('/admin/entries/post')

class admin_ThemeEdit(base.BaseRequestHandler):
    @base.requires_admin
    def get(self,slug):
        zfile=zipfile.ZipFile(os.path.join(rootpath,"themes",slug+".zip"))
        newfile=zipfile.ZipFile('')
        for item  in zfile.infolist():
            self.write(item.filename+"<br>")


def main():
    base.webapp.template.register_template_library('app.filter')
    base.webapp.template.register_template_library('app.recurse')

    application = base.webapp.WSGIApplication(
                    [
                    ('/admin/{0,1}',admin_main),
                    ('/admin/setup',admin_setup),
                    ('/admin/entries/(post|page)',admin_entries),
                    ('/admin/links',admin_links),
                    ('/admin/sliderimages',admin_sliderimages),
                    ('/admin/sliderimage',admin_sliderimage),
                    ('/admin/categories',admin_categories),
                    ('/admin/comments',admin_comments),
                    ('/admin/link',admin_link),
                    ('/admin/category',admin_category),
                     ('/admin/(post|page)',admin_entry),
                     ('/admin/status',admin_status),
                     ('/admin/authors',admin_authors),
                     ('/admin/author',admin_author),
                     ('/admin/import',admin_import),
                     ('/admin/tools',admin_tools),
                     ('/admin/plugins',admin_plugins),
                     ('/admin/plugins/(\w+)',admin_plugins_action),
                     ('/admin/sitemap',admin_sitemap),
                     ('/admin/export/micolog.xml',WpHandler),
                     ('/admin/do/(\w+)',admin_do_action),
                     ('/admin/lang',setlanguage),
                     ('/admin/theme/edit/(\w+)',admin_ThemeEdit),
                     ('/admin/upload', Upload),
                     ('/admin/filemanager', FileManager),
                     ('/admin/uploadex', UploadEx),
                     ('.*',Error404),
                     ],debug=True)
    g_blog.application=application
    g_blog.plugins.register_handlerlist(application)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()