---
title: How to create a NodeJS NPM package
abstract: See how to create a simple NodeJS NPM package. We'll first create a simple program, add some node_modules  to it and walk through the process of creating a NPM package, publishing it and upgrading it. We'll also walk through see some common issues that you might face for the first time.
tags: nodejs, javascript, npm, package, publish, deploy
date: 2013-09-19
---

In this tutorial we will create a simple NodeJS program, create a NPM package, publish it. In the second part we will add dependencies to our package and upgrade it.


This tutorial assumes that you are familiar with NodeJS and at least written a bit more than just a "Hello World" program with NodeJS.

If you are new to NodeJS, I encourage you to go through the links below:

* Series of good tutorials on NodeJS: [NodeJS tutorial](http://www.youtube.com/watch?v=jo_B4LTHi3I).

* [Introduction to NodeJS](http://www.youtube.com/watch?v=jo_B4LTHi3I) with Ryan Dahl (NodeJS creator)


Let's begin


## Creating a simple NodeJS program

First let us create a very simple NodeJS program. This program will read a file "myfile.txt" and convert its contents to uppercase.

Let's create a directory ```test``` and create a new file ```uppercaseme.js```

```
// uppercaseme.js
"use strict"
var fs = require('fs');
var myfile = "myfile.txt";

if(fs.existsSync(myfile)) {
	var content = fs.readFileSync(myfile, 'utf8');
	fs.writeFileSync(myfile, content.toUpperCase());
	console.log("Done");
} else {
	console.log("File does not exist - " + myfile);
}
```

The code above looks for a file ```myfile.txt``` and converts its content to upper case.

To execute this program type the command below. A file ```myfile.txt``` must also exist in the same directory.
```
node uppercaseme
```

It should successfully convert(upper-case) contents of ```myfile.txt```


#### Reading command line arguments

Hardcoding the filename within the program is not so cool. Let us modify our program a bit to accept the file name as a command line argument to the program. We will use the ```process.argv``` array like below.

```
0: node
1: <name-of-your-js-file>
2+....<additional arguments passed>
```

The update code will look like:

```
"use strict"
var fs = require('fs');
if(process.argv.length > 2) {
	// Read the first additional argument passed to the program
	var myfile = process.argv[2]; 
	
	if(fs.existsSync(myfile)) {
		var content = fs.readFileSync(myfile, 'utf8');
		fs.writeFileSync(myfile, content.toUpperCase());
		console.log("Done");
	} else {
		console.log("File does not exist - " + myfile);
	}
} else {
	console.log("ERROR: Pass on a file name/path");
}

```

We now accept the filename, and if a filename is not passed, we show an error.


To execute this program type the command below. A file ```myfile.txt``` must also exist in the same directory.
```
node uppercaseme myfile.txt
```

## Creating a Node module

Now that we have created this exciting new program to upper-case files, we want to publish this to the internet so that other developers/people can use it with NodeJS.

We want to allow other developers to do the below.

* Installation via NPM

	```
	npm install uppercase
	```

* Use on shell/command prompt

	```
	uppercaseme <filename>
	```

* Use within other NodeJS programs

	```
	require('uppercaseme');
	```

To do the above, we will create a package for NPM (Node Package Manager).

To begin with, we will create the following directory structure in our ```test``` directory

```note

test
	src
	  -- bin
		-- uppercaseme 
	  -- lib
		-- uppercaseme.js
	  -- package.json
	  -- README.md
	
	myfile.txt

```

Move the ```uppercaseme.js``` that we created earlier into the ```lib``` directory. Let the test file ```myfile.txt``` stay in its original path.

For all the other files, create blank files with the name mentioned. We'll put in content into those further.

The structure in the ```src``` is used for our NodeJS NPM package.

* ```Package.json``` : Holds the configuration for the package. 
	This is the only file that must exist here with its name and appropriate contents. All other files could be arranged in a different manner.
	
* ```README.md``` : This is an optional file, however NPM will generate a warning if this does not exist. 
	
	Holds the description in [markdown format](http://en.wikipedia.org/wiki/Markdown)


Now since we moved our program, let us test the program again
(Assuming that you are still in the ```test``` directory at your shell/command prompt)

```
node ./src/lib/uppercaseme ./myfile.txt
```

And it works the same. *If it does not, check again what you missed or if the path was incorrect.*


Now let's create the file ```src/bin/uppercaseme``` as shown below. Note that we **DONOT** have the extension ```.js``` on this file.

```
#!/usr/bin/env node

"use strict";
var path = require('path');
var fs = require('fs');
var lib = path.join(path.dirname(fs.realpathSync(__filename)), '../lib');

require(lib+'/uppercaseme.js').convert();

```

The above file will enable the usage of this program from command line. We'll also have to configure that in ```package.json``` later.

Now let's test this file:

```
node ./src/bin/uppercaseme ./myfile.txt
```

It'll throw an error like below:

```
require(lib+'/uppercaseme.js').convert();
                               ^
TypeError: Object #<Object> has no method 'convert'
    at Object.<anonymous> (...\src\bin\uppercaseme:8:32)
    at Module._compile (module.js:456:26)
    at Object.Module._extensions..js (module.js:474:10)
    at Module.load (module.js:356:32)
    at Function.Module._load (module.js:312:12)
    at Function.Module.runMain (module.js:497:10)
    at startup (node.js:119:16)
    at node.js:901:3
```


This occurs because we have not converted our ```uppercaseme.js``` to a Node module and we have not defined a method ```convert()```. Let's do that.

In your file ```uppercaseme.js```, we'll simply wrap the existing code within a function ```convert```

```
"use strict"
var fs = require('fs');

function convertThis() {
	if(process.argv.length > 2) {
		var myfile = process.argv[2];

		if(fs.existsSync(myfile)) {
			var content = fs.readFileSync(myfile, 'utf8');
			fs.writeFileSync(myfile, content.toUpperCase());
			console.log("Done");
		} else {
			console.log("File does not exist - " + myfile);
		}
	} else {
		console.log("Pass on a file name/path");
	}
}

exports.convert = convertThis;
```

Once we wrap the function we also do ```exports.convert = convertThis;```. This exposes our method from the ```uppercaseme``` module as ```convert```

<small>In the above code, we created a ```convertThis``` wrapping function. For the sake of simplicity, I did not use the name ```convert``` for the wrapping function too. You can do that, but an ```exports.convert``` will be required in that case too.</small>


Alright, let's test it again

```
node ./src/bin/uppercaseme ./myfile.txt
```

Awesome! It works now. We have successfully created a Node module and can start packaging it.


## Creating a NPM package

From our package directory list, we have worked on ```src/bin/uppercaseme``` and ```src/lib/uppercaseme.js``` files.

Now we need to create ```src/package.json``` file and ```src/README.md```

---

The ```package.json``` is a [JSON](http://en.wikipedia.org/wiki/JSON) configuration file shown below
```
{
  "author": "Anup Shinde",
  "name": "uppercaseme",
  "description": "Converts files to uppercase",
  "version": "0.1.1",
  "repository": {
    "url": ""
  },
  "main": "./lib/uppercaseme",
  "keywords": [
    "upper",
    "case",
    "file"
  ],
  "bin": {
    "uppercaseme": "./bin/uppercaseme"
  },
  "dependencies": {},
  "engines": {
    "node": "*"
  }
}
```

In the above you can set different parameters for your package. Most of these are self-explanatory. Let's look at a few first.

 **```main```** is a module ID that is the primary entry point to our program. In our example, our package is named ```uppercaseme```. After a user installs it, and then does ```require("uppercaseme")```, then our main module's exports object will be returned.


 **```bin```** We'd like to execute our package via command line from anywhere and therefore installed into the PATH. npm makes this pretty easy. On install, npm will symlink the ```bin/uppercaseme``` file for global installs, or to ```./node_modules/.bin/``` for local installs.

 **```dependencies```** Here we mention a list of dependencies for our package. Currently we have none. We'll be adding a dependency later in this tutorial.

**More details** related to the configuration parameters in ```package.json```  at [NPM-JS Documentation](https://npmjs.org/doc/json.html)


---

Let's also create the ```README.md``` file shown below.

```readme

upper-case-me
-------------

This is a cool program to upper-case files

```

---

Now that we have completed our package structure, let's publish the package.

Before you publish your package to NPM registry, you must have an user. If you do not have a user, you can add a user.

```
npm adduser
```

Provide your username, email address. This will register a new user. 

Assuming that you are still in your ```test``` directory, do the following

```
cd src
npm publish
```

It would show some info like below

```debug
npm http PUT https://registry.npmjs.org/uppercaseme
npm http 201 https://registry.npmjs.org/uppercaseme
npm http GET https://registry.npmjs.org/uppercaseme
npm http 200 https://registry.npmjs.org/uppercaseme
npm http PUT https://registry.npmjs.org/uppercaseme/-/uppercaseme-0.1.1.tgz/-rev/1-74d3bb0b59747a421
5b7b3778dcc02c0
npm http 201 https://registry.npmjs.org/uppercaseme/-/uppercaseme-0.1.1.tgz/-rev/1-74d3bb0b59747a421
5b7b3778dcc02c0
npm http PUT https://registry.npmjs.org/uppercaseme/0.1.1/-tag/latest
npm http 201 https://registry.npmjs.org/uppercaseme/0.1.1/-tag/latest
+ uppercaseme@0.1.1
```

**Congratulations**, you have successfully published your first NPM package.


## Installing our NPM package

Now let's create another directory, outside of our ```test``` directory. We call it ```testpack```. 

Change to your ```testpack``` directory, and on the command line type this:

```
npm install uppercaseme
```

It should fetch the ```uppercaseme``` package and create a **local install** for that. It is a local install so we cannot call it from any location yet. The installation is done within the ```node_modules``` directory. Check that directory, it has a directory created for our ```uppercaseme``` module. And links created within the ```.bin``` directory.


Back in our ```testpack``` directory, create a new file that we want to upper-case

```
echo "my-lowercase-file" > myfile.txt
```

Then convert it with our lib

```
./node_modules/.bin/uppercaseme myfile.txt

OR

"./node_modules/.bin/uppercaseme" myfile.txt
```

Check the file. It works!

---

Now, let's make a global install for the package. Before that you can uninstall it from local.

```
npm uninstall uppercaseme
```

Once you uninstall, the local install is cleared - That is the module is removed from ```node_modules``` directory

Now do a global install using the ```-g``` option
```
npm install -g uppercaseme
```

Once its installed, you can now do, from any location.
```
uppercaseme myfile.txt
```

Awesome! Now let's try to use this module in another program.

## Reusing the package in another program

In our ```testpack``` directory, let's create a new file ```test.js``` as shown below

```
var ucm = require("uppercaseme");
ucm.convert();
```

Or it could be a one liner like

```
require("uppercaseme").convert();
```

Now on your shell/command prompt, type the following:

```
node test myfile.txt
```
Nicey. It works.

If this last bit did not work for you, correct the **Errors in NODE_PATH** section below


While this works, I do not recommend global install of  your program's ```require``` dependencies . You can do a ```npm uninstall -g uppercaseme``` and then do a ```npm install uppercaseme```


---

#### Errors in NODE_PATH

If it gives an error ```Error: Cannot find module '...'```, it is because NodeJS is not able to refer to that module.
Remember that we did a global install for our package with the ```-g``` option. NodeJS uses  NODE_PATH to find globally installed packages.

Check the current NODE_PATH

```
Linux:
echo $NODE_PATH

Windows:
echo %NODE_PATH%

```

If ```echo``` returns blank values, you can correct the NODE_PATH using the following.

```
Linux:
export NODE_PATH=/usr/local/lib/node_modules


Windows:
set NODE_PATH=%USERPROFILE%\AppData\Roaming\npm\node_modules
```

Now try the above command again ``` node test myfile.txt ```

---

In the next part(coming soon) we will see how to add dependencies to your program and NPM package

---

If you found this useful, please share or rate it or leave a comment/question/suggestion below. 


Happy coding <i class="icon-smile"></i>

