---
title: Adding dependencies and data to Node-NPM package
abstract: In the first part we created a package with no dependencies. In this part, we'll add some dependencies to our program and package. We'll also look at some additional tips that you may require when creating your first NPM package.
tags: nodejs, javascript, npm, package, publish, deploy
date: 2013-09-20T00:02
---


### [<< Continued from - How to create a NodeJS NPM package](/posts/how-to-create-nodejs-npm-package)

---

## Adding package dependencies

Now that we created the package, let's add some dependencies to it. 


We also want the user to create a file automatically  ```file.txt``` with a ```--new``` option.
For this, we will have to package a default file with the package.

We will change the command line options for our program as shown below

To convert a file we pass it as a named argument with ```--file```
```
uppercaseme --file file.txt
```

And to create a new file ```file.txt``` in the working directory
```
uppercaseme --new
```


To achieve this, we will install the [```commander```](https://npmjs.org/package/commander) module. 

```
npm install commander
```

Note that this is a local install for ```commander```

---

## Modifying code to include ```commander```

This is not a tutorial on using ```commander``` module - so we'll look at the basic usage required in our case.

First we ```require("commander")``` in our code and then set the options like version, command line named arguments. This module then parses the arguments and gives us some usable info.

```

"use strict"
var fs = require('fs');
var path = require('path');

var program = require('commander');

program.version('0.1.1')
	.option('-n, --new', 'Create a test file')
	.option('--file [filename]', 'Filename to convert')
	.parse(process.argv);
	
```	

Then we use the ```program``` variable to access the options

```
if(program.new) {
....

var myfile = program.file;

```

Commander also automatically generates command line help for our program when used with ```--help``` option

---

#### Updated code

Change back to our ```test``` directory and open ```src/lib/uppercaseme.js```. Change the code to:


```
"use strict"
var fs = require('fs');
var path = require('path');

var program = require('commander');

/* Define configuration for commander */
program.version('0.1.1')
	.option('-n, --new', 'Create a test file')
	.option('--file [filename]', 'Filename to convert')
	.parse(process.argv);
	
function copyFile(from, to) {
	return fs.createReadStream(from).pipe(fs.createWriteStream(to));
}

function convertThis() {

	if(program.new) {
		var newfile = path.join(path.dirname(fs.realpathSync(__filename)), '../lib/examples/file.txt');
		copyFile(newfile, path.join(process.cwd(), "file.txt"));
	} else if(program.file) {
		var myfile = program.file;
		if(fs.existsSync(myfile)) {
			var content = fs.readFileSync(myfile, 'utf8');
			fs.writeFileSync(myfile, content.toUpperCase());
			console.log("Done");
		} else {
			console.log("File does not exist - " + myfile);
			console.log("OR Create a new file with the --new option");
		}
	} else {
		console.log("Pass a file name/path");
	}
}

exports.convert = convertThis;
```

To test this update, change back to our ```test``` directory and type

```
node ./src/bin/uppercaseme --new
```

This creates a file ```file.txt``` in our current directory with regular text. And then we can convert it to uppercase using

```
node ./src/bin/uppercaseme --file file.txt
```


Finally, let's add these dependencies to our ```package.json```

```
{
  "author": "Anup Shinde",
  "name": "uppercaseme",
  "description": "Converts files to uppercase",
  "version": "0.1.2",
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
  "dependencies": {
	"commander": "2.0.0"
  },
  "engines": {
    "node": "*"
  }
}
```

Here we updated our package version and added a dependency ```commander```. The version for these dependencies from ```node_modules/<dependency>/package.json```

---

We can now publish it from the ```src``` directory using  
``` 
npm publish 
```


And then we can do a global install using 
```
npm install -g uppercaseme
```


We can now use our exciting new program to do one of these, preferably in some other directory

```
uppercaseme --help

uppercaseme --new

uppercaseme --file file.txt


```

---

#### NOTE on not-polluting NPM registry with examples.

While NPM makes it easier for us to distribute packages, I would recommend that you unpublished **each and every** version of the sample packages that you created during this tutorial

You can do so from your ```src``` directory

```
npm unpublish --force

```

NPM also maintains a local cache so that it does not download stuff everytime you do ```npm install```. You can clean this cache using


```
npm cache clean
```

---

**Common issues when creating NPM packages for first time:**

* NPM caching can cause "old-code" issues in testing if you are "just testing" publishing same version multiple times (in combination with install, unpublish). This is because npm installed from local cache - which is probably from your first install of that specific version.

* If you are using Windows for development - make sure you test it on Linux/Mac environments too. Line-feed-character mismatches in your ```bin``` files may result in errors like ```node - command not found```

_I faced the above two in combination and cost me a whole night <i class="icon-frown"></i>_


---

If you found this useful, please share or rate it or leave a comment/question/suggestion below. 


Happy coding <i class="icon-smile"></i>

