---
title: Online Markdown Showdown Editor 
date: 2013-10-02
abstract: Write your markdown and see the output in real-time. I usually write my posts in Markdown format (specifically Showdown). Its easier and speedier to write my content and see that rendered in real time. The editor is online and stores your content in Local storage
tags: Markdown, Showdown, Online Editor, JavaScript, AngularJS
---

## Usage

Just type your markdown in the textbox. Check out Markdown Cheatsheet for syntax

Chose from multiple themes. These should be available when you open the editor next time

Data is stored locally on your HTML5 storage. Content will reload automatically and is saved every few seconds. Make sure that you **DO NOT** open two different windows - One will overwrite the other

If your content exceeds the available height, a scrollbar will appear and it will scroll automatically as you type. To disable automatic scrolling uncheck the ```Scroll automatically``` checkbox below

You can also write code 

```
/* A simple hello world program */
for(i=0;i<100;i++ {
    console.log("Hello World");
    // And this is a comment here
}
```

This thing also includes Bootstrap CSS and FontAwesome CSS. 

i.e you will be able do say <i class="icon-smile"></i> and <i class="icon-glass"></i>. 

---

## About the code

*This thing is not tested on IE* 

You can do a view-source of the markdown-editor (HTML) to see the code. It is a single large-HTML file and will work if copied to your desktop. All external references are from CDNs. Most of the code is just related to the look-and-feel for this editor.

Here we use AngularJS to get the updates from the textarea via the angular-model. This makes it easier to watch changes - however this can be done by writing a bit of code without AngularJS too.

We use the [Showdown javascript library](https://github.com/coreyti/showdown) to create HTML from input Markdown. Basically you would do that as shown below:

```
var converter = new Showdown.converter();
var html = converter.makeHtml(newstr);
```

---


### If you like it and found it useful, please share this and/or leave a comment below

 