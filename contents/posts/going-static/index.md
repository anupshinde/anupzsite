---
date: 2013-09-07
title: Going Static
abstract: This blog has now been upgraded to use simple static html pages instead of a CMS.  Why did I do that? What tools did I use? And more details within.
tags: static, site-generator, nodejs, javascript
---

This blog has now been upgraded to use simple static html pages instead of a CMS. Just a few days back, I had a good enough CMS in place for my blog powered by Google App Engine / Python 2.5. Having control over the code made it seriously customizable. But soon after I upgraded my blog last year, GAE made Python 2.7 as the latest. 

I don't post on my blog very frequently - and this upgrade meant more work for me to upgrate to 2.7, since GAE Python 2.5 is deprecated now (after a year). They didn't just change the language, but a whole lot of toolset around it. Migration meant a lot of work at my end - Infact I found it was easier to re-write (with bit of re-use) my CMS in GAE Python 2.7 than trying to migrate from GAE Python 2.5

And what happens next? What happens when Python 3 and next stack becomes latest? It would end up being a lot of work again.

Apart from that, I never did enjoy writing online - be it Wordpress or my own CMS - I usually do so in Notepad/Notepad++/Gedit or oddly sometimes in Gmail(drafts). Porting plain text to online CMS meant a bit of HTML formatting work too.

I also did not like the fact that GAE does not give me an FTP like interface where I can download/upload individual files instead of the entire package - Github integration creates a workaround for me.

This blog doesn't contain much dynamic stuff either. And having worked on creating custom static-site-generators earlier - I know almost nothing beats the performance of static pages.

There are many static site generators available - My search came down to a few that I felt comfortable about.

* [Jekyll](http://jekyllrb.com/)

   Widely used. Based on Ruby

* [DocPad](http://docpad.org/)

   Uses NodeJS. Written in CoffeeScript. Lots of functionality

* [Wintersmith](http://wintersmith.io/)

   Uses NodeJS and written in CoffeeScript. Limited compared to DocPad but flexible
     

Jekyll was much easier to use than the other two. There were very few things that I would have to write in Ruby for my needs. But I did not want to go the Ruby way. I'm a webdeveloper and JavaScript is native to me. Any other language is a context-switch for me. And that is what I wanted to avoid when possible ( I am not saying JS is better than Ruby/Python). I also found Jekyll not so flexible - it dictates how you arrange your content.

DocPad was similar to Jekyll but written in CoffeeScript. Many features and many plugins available - However just like Jekyll, it dictates how you arrange your content. I loved its asset-pipelining feature to support multiple conversion formats. However I did not find a real usecase within my requirements.

Wintersmith was flexible in terms of arranging content. It does not have as many features as DocPad - however I found it fit to many of my requirements and got its flexiblity.

With both, DocPad and Wintersmith I would end up writing CoffeeScript at some point. If not, I would be doing workarounds like hacks around the framework.

NOTE: If you are not concerned about the static site-generator language / architecture / whatever... and, at times - redundant work, Jekyll is recommended - Its pretty easy to work with and stable. Also you can host your pages on Github - Very compelling option. 
<a href="https://help.github.com/articles/using-jekyll-with-pages" target="_blank">Find out more here</a>.


At some point, while learning about DocPad and Wintersmith - I realized that I would either have to write plugins for those or write some kind of pre-post-processor hacks to automate some redundant stuff. And I ended up learning another stack of tech (I learnt lots of good stuff). Ultimately, I gave up those two frameworks and decided to write my own static-site-generator. This time in plain JavaScript (with NodeJS). That also gave me a hands on learning NodeJS (but not for web-apps). I knew beforehand that its going to take longer than using the existing frameworks. At the end I got the flexiblity that I needed and did not have to use hacks to get things done. At the time of writing this, the code is just about 700 lines using 8 NodeJS modules.

You can have a look at the code **[here](https://github.com/anupshinde/nirman)**. Some of the features at time of writing this:

1. Flexibility to arrange your site contents - the way you want it. All the stuff goes in "contents" directory.

2. Templating is similar to Jinja templates. Here we use Nunjucks templating

   Additionaly, you can use your content files as your template - This helps avoid cases where you create a one line file just to point to another template file. This feature is optional.
   
3. Content metadata is available to your templates directly.

4. Markdown support via Showdown 

5. Generators - Special script files written in JavaScript that are passed the Scope and content Metadata. 
    
    You can simply add code here to create your own output.

    Example: You want to create a page listing all the Categories in your content.

6. Front Matter - Configuration for a post/document can be placed as a front-matter at the top of the content file. You can add date, title, or anything that is supported as YAML. All this configuration is available to the Scope of the template

7. Code blocks within content ( &lt;script type="application/x-nirman-code" ).

   Sometimes, you want a modified version of your data. For example: Metadata provides you the list of posts. However, in your content, you may require the post to be sorted/filtered by date/title/category/ (whatever) ... Best is to leave this to you. 
   
   With this feature you can add JavaScript-functions to you current template scope. And then use these methods in your template - Helps keeps code clean with code and HTML separation.
   
8. Paging support.

    Simply create a code block within your content, get the items, and mention "scope.paginate(options)". The in your content use the paged-date to render content. You require ApplyTemplateToContent = TRUE to use this feature.
	

Further... 
I am also looking to add stuff like page-breaks within content to paginate through long articles. 



**What about dynamic stuff?**

I do not have any dynamic stuff anyways - Comments are on Disqus. And the contact-me form is used lesser and will be replaced with a static page.

But "dynamic" is not completely optional - there are few cases where I wish create forms. I might use Mongolab/Firebase - or something similar that I developed earlier - without having to create a dynamic site again.


This is the first post written after the change-to-static-site, using Notepad++. So far it has come out perfectly.

Keep Watching and Happy Coding <i class="icon-smile"></i>

