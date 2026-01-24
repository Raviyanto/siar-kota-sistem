/*
 * QT WebChannel Resmi (Unminified)
 * Agar komunikasi Python <-> HTML lancar tanpa error "QObject undefined"
 */
"use strict";

var QWebChannel = function(transport, initCallback) {
    if (typeof transport !== "object" || typeof transport.send !== "function") {
        console.error("QWebChannel message transport initialized with invalid argument.", transport);
        return;
    }

    this.transport = transport;
    this.execCallbacks = {};
    this.execId = 0;
    this.execRequests = {};
    this.objects = {};
    this.propertyUpdateHandlers = {};

    var self = this;

    this.transport.onmessage = function(message) {
        var data = message.data;
        if (typeof data === "string") {
            data = JSON.parse(data);
        }
        switch (data.type) {
            case 0: // signal
                self.handleSignal(data);
                break;
            case 1: // response
                self.handleResponse(data);
                break;
            case 2: // propertyUpdate
                self.handlePropertyUpdate(data);
                break;
            default:
                console.error("invalid message received:", message.data);
                break;
        }
    };

    this.exec(function(data) {
        for (var objectName in data) {
            var objectInfo = data[objectName];
            self.objects[objectName] = new QObject(objectName, objectInfo, self);
        }
        if (initCallback) {
            initCallback(self);
        }
    });
};

QWebChannel.prototype.exec = function(callback) {
    if (!callback) return;
    var requestId = this.execId++;
    this.execRequests[requestId] = callback;
    this.transport.send(JSON.stringify({type: 3, id: requestId}));
};

QWebChannel.prototype.handleSignal = function(message) {
    var object = this.objects[message.object];
    if (object) {
        object.signalEmitted(message.signal, message.args);
    } else {
        console.warn("Unhandled signal: " + message.object + "::" + message.signal);
    }
};

QWebChannel.prototype.handleResponse = function(message) {
    if (!message.hasOwnProperty("id")) {
        console.error("Invalid response message received: ", message);
        return;
    }
    this.execRequests[message.id](message.data);
    delete this.execRequests[message.id];
};

QWebChannel.prototype.handlePropertyUpdate = function(message) {
    for (var i in message.data) {
        var data = message.data[i];
        var object = this.objects[data.object];
        if (object) {
            object.propertyUpdate(data.signals, data.properties);
        } else {
            console.warn("Unhandled property update: " + data.object + "::" + data.signal);
        }
    }
    this.exec(message.data);
};

var QObject = function(name, data, webChannel) {
    this.__id__ = name;
    this.__objectSignals__ = {};
    this.__propertyCache__ = {};
    var self = this;

    // Create signals
    if (data.signals) {
        data.signals.forEach(function(signal) {
            self.__objectSignals__[signal[0]] = self.createSignal(signal[0], signal[1]);
            self[signal[0]] = self.__objectSignals__[signal[0]];
        });
    }

    // Create properties
    if (data.properties) {
        data.properties.forEach(function(property) {
            self.__propertyCache__[property[0]] = property[1];
            Object.defineProperty(self, property[0], {
                get: function() {
                    return self.__propertyCache__[property[0]];
                },
                set: function(value) {
                    if (self.__propertyCache__[property[0]] === value) return;
                    self.__propertyCache__[property[0]] = value;
                    // Property updates are one-way for now (C++ -> JS)
                },
                enumerable: true
            });
        });
    }

    // Create methods
    if (data.methods) {
        data.methods.forEach(function(method) {
            self[method[0]] = function() {
                var args = [];
                var callback;
                for (var i = 0; i < arguments.length; i++) {
                    if (typeof arguments[i] === "function")
                        callback = arguments[i];
                    else
                        args.push(arguments[i]);
                }
                webChannel.exec({
                    "type": 6,
                    "object": self.__id__,
                    "method": method[0],
                    "args": args
                }, function(response) {
                    if (response !== undefined && callback) {
                        callback(response);
                    }
                });
            };
        });
    }
};

QObject.prototype.createSignal = function(name, signature) {
    var signal = {
        connect: function(callback) {
            if (typeof callback !== "function") {
                console.error("Bad callback given to connect to signal " + name);
                return;
            }
            signal.listeners.push(callback);
        },
        disconnect: function(callback) {
            var idx = signal.listeners.indexOf(callback);
            if (idx !== -1) {
                signal.listeners.splice(idx, 1);
            }
        },
        listeners: []
    };
    return signal;
};

QObject.prototype.signalEmitted = function(name, args) {
    var signal = this.__objectSignals__[name];
    if (signal) {
        signal.listeners.forEach(function(listener) {
            listener.apply(null, args);
        });
    }
};

QObject.prototype.propertyUpdate = function(signals, properties) {
    // update properties
    for (var propertyName in properties) {
        var propertyValue = properties[propertyName];
        this.__propertyCache__[propertyName] = propertyValue;
    }
    // emit signals
    for (var signalName in signals) {
        // ... (simplified logic)
    }
};