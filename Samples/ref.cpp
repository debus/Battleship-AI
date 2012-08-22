#include <iostream>
#include <string>
#include <fstream>
using namespace std;

int main(){
	string input;
	ofstream f;
	f.open("/home/phil/log.txt", ios_base::trunc);
	while(1){
		input = "";
		getline(cin, input, '\n');
		if(input =="[quit]"){
			cout<<"[quitting]"<<endl;
			break;
		}else if (input == ""){
			continue;
		}
		f<<input<<endl;
		//f<<"[The Narwhal, with the bacon, at midnight]"<<endl;
		cout<<"PRIVMSG :#battleship_testing :THIS IS A MESSAGE SENT BY A BOT!"<<endl;
	}
	f.close();
	return 0;
}