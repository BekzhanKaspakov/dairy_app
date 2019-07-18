import 'dart:convert';

import 'chat_message.dart';
import 'chat_message_outgoing.dart';
import 'dart:io';
import 'dart:async';

// const serverIP = "127.0.0.1";

class ChatService {
  /// Flag is indicating that client is shutting down
  bool _isShutdown = false;

  /// gRPC client channel to send messages to the server
  // ClientChannel _clientSend;

  /// gRPC client channel to receive messages from the server
  // ClientChannel _clientReceive;
  Socket clientSocket;
  String userId;
  final serverIP;
  final serverPort;

  File audio;
  // / Event is raised when message has been sent to the server successfully
  final void Function(MessageOutgoing message) onSentSuccess;

  /// Event is raised when message sending is failed
  final void Function(MessageOutgoing message, String error) onSentError;

  /// Event is raised when message has been received from the server
  final void Function(Message message) onReceivedSuccess;

  /// Event is raised when message receiving is failed
  final void Function(String error) onReceivedError;

  /// Constructor
  ChatService({
    this.onSentSuccess,
    this.onSentError,
    this.onReceivedSuccess,
    this.onReceivedError,
    this.serverIP,
    this.serverPort,
  });

  void startListening() {
    if (clientSocket == null) {
      Future<Socket> future = Socket.connect(serverIP, serverPort);
      future.then((client) {
        print("connected to server! in Listening");
        client.handleError((data) {
          print(data);
        });
        clientSocket = client;
        if (userId == null) {
          client.write('START:NoId');
          client.listen(
            (data) {
              String reply = utf8.decode(data);
              print(reply);
              if (reply.split(':')[0] == 'USERID'){
                userId = reply.split(':')[1];
              } else if (reply == 'OKAUDIO') {
                print('confirm received, sending audio');

                clientSocket.addStream(audio.openRead());
              } else {
                var message = Message(reply);
                onReceivedSuccess(message);
              }
              
            },
            onDone: () {
              print("Done");
            },
            onError: (error) {
              print(error);
            },
          );
        } else {
          client.write('START:$userId');
          client.listen(
            (data) {
              String reply = utf8.decode(data);
              print(utf8.decode(data));
              var message = Message(reply);
              onReceivedSuccess(message);
            },
            onDone: () {
              print("Done");
            },
            onError: (error) {
              print(error);
            },
          );
        }

        // client.writeln("Hello There" + "\n");
      }).catchError((Object error) {
        print('Error connecting');
      });
    }
  }

  Future<void> shutdown() async {
    _isShutdown = true;
    if (clientSocket != null) {
      clientSocket.close();
    }
  }

  void send(MessageOutgoing message) async {
    if (clientSocket == null) {
      Future<Socket> future = Socket.connect(serverIP, serverPort);
      await future.then((client) {
        print("connected to server!");
        client.handleError((data) {
          print(data);
        });
        clientSocket = client;
        // client.writeln("Hello There" + "\n");
      }).catchError((Object error) {
        print('Error connecting');
      });
    }

    clientSocket.write(message);
  }
}
