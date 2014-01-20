---
title: Building real time web apps with AngularJS, NodeJS and MongoDB
abstract: This is a demo implementation of creating real time web apps with AngularJS and MongoDB. In here we implement a todo list that is synchronised in real time for all the users
tags: nodejs, javascript, realtime, mongodb, angularjs
date: 2014-01-19
---

---

After looking at the [FireBase + AngularJS demo](http://www.youtube.com/watch?v=C7ZI7z7qnHU), few months back, I wished for something similar with MongoDB. And simple to use AngularJS integration.

**FYI**: You may find [Meteor](https://www.meteor.com/) as a better option for "real-time"


The demo implementation here is todo app with real time sync.

#### [Demo here](http://livebase.anupshinde.com)

#### [Code at GitHub](https://github.com/anupshinde/livebase)

---

##Components:

1. Server code that allows real time sync and storage. We use SocketIO for this.

2. Client side JS lib that allows connection, raises events and exposes methods for data manipulation. We want to keep this JavaScript file independent of AngularJS.

3. AngularJS service factory implementation that consumes the JS created above

4. A Todo app that consumes all of the above for the demo. 

The following gives a brief idea related to each component:


---

###Server.js - Server code
Server opens up a connection to MongoDB and loads the Socket.
The socket receives events and performs updates on the collection (todos). After each update via SocketIO the data is broadcast to all the connected clients.

This file also defines a type *MongoConnection* which can be moved to a module.

*In this demo, all the data is fetched and sent again - in real world apps, you would send only the required data.*


---
###Livebase.js - Client JS lib that works with SocketIO client lib

Livebase.js works with SocketIO client library and exposes methods to update the collection, handles the socket events and fires events to be handled by its consumer.

---
###livebase-angular.js: AngularJS service factory 

This service factory implementation works with the livebase.js to update the scope. This is defined as *angularBase* in the*livebase* module


**NOTE**: All the three server.js->MongoConnection, livebase.js and livebase-angular.js are collection independent. With an exception that server.js


---
###Todo App
The todo app pretty much looks like the AngularJS todo list demo. The controller *TodoCtrl* uses *angularBase* and the code snippet is shown below. 

```

var todo_app = angular.module('TodoApp',['livebase']);

todo_app.controller("TodoCtrl", function($scope, angularBase) {
	var Todos = angularBase("http://localhost:9338","todos"); // NOTE: The configuration here must match with the server - obviously

	$scope.todos = Todos.getAll();

	$scope.addTodo = function() {
		var todo = { text:$scope.todoInput, done:false};
		Todos.put(todo);
		$scope.todoInput = "";
	}
	
	$scope.deleteTodo = function(index) {
		var todo = $scope.todos[index];
		Todos.remove(todo);		
	}
	
	$scope.changeTodo = function(index) {
		var todo = $scope.todos[index];
		todo = { _id: todo._id, done: todo.done };
		Todos.put(todo);
	}
});

```

In the demo code, I am using a different port for SocketIO. You could use the same port with ExpressJS.
Different ports occur in my code because of the way this thing was developed and was used with local files earlier.

---

#### [Demo here](http://livebase.anupshinde.com)

#### [Code at GitHub](https://github.com/anupshinde/livebase)


If you liked this stuff, go ahead and share this or leave a comment below.


---
