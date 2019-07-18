
import 'dart:io'; 

const serverIP = "127.0.0.1";
const serverPort = 65432;

void main() async {
  var file = File('audio.m4a');

  if (await file.exists()) {

    Socket s = await Socket.connect(serverIP, serverPort);
    int fileLength = await file.length();
    print(fileLength);
    s.write('Audio:$fileLength');
    print("sending request to send audio");
    s.listen(
      (onData) async {
        String reply = new String.fromCharCodes(onData);
        if (reply == 'OK'){
          print('confirm received, sending audio');
          
          await s.addStream(file.openRead());
        } else if (reply == 'Done') {
          
        } else {
          print('something went wrong');
        }
      },
      onDone: () {
        print("Done");
        s.destroy();
        exit(0);
      },
      onError: (error) {
        print(error);
      },
    );
    
    return;
  } else {
    print('file not found');
  }
}