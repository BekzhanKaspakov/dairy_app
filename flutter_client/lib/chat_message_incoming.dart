import 'package:flutter/material.dart';

import 'chat_message.dart';

/// Incoming message author name
const String _server = "Server";

/// ChatMessageIncoming is widget to display incoming from server message
class ChatMessageIncoming extends StatelessWidget implements ChatMessage {
  /// Incoming message content
  final Message message;

  /// Controller of animation for message widget
  final AnimationController animationController;

  /// Constructor
  ChatMessageIncoming({this.message, this.animationController})
      : super(key: new ObjectKey(message.id));

  @override
  Widget build(BuildContext context) {
    return SizeTransition(
      sizeFactor:
          CurvedAnimation(parent: animationController, curve: Curves.easeOut),
      axisAlignment: 0.0,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 10.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Container(
              margin: EdgeInsets.only(right: 16.0),
              child: CircleAvatar(
                  backgroundColor: Colors.pink.shade600,
                  child: Text(_server[0])),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(_server, style: Theme.of(context).textTheme.subhead),
                  Container(
                    margin: EdgeInsets.only(top: 5.0),
                    child: Text(message.text),
                  ),
                ],
              ),
            ),
            
          ],
        ),
      ),
    );
  }
}